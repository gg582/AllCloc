import os
import json
import subprocess
from pathlib import Path
import tempfile
import shutil
import stat
import time

# Configuration: filtered authors and excluded repositories
# The script will look for authors whose names contain any of these strings
FILTERED_AUTHORS = ['yunjin', 'yoonjin', 'gg582']

# Repositories to be excluded from the analysis
EXCLUDED_REPOS = ['CSharp-Arkanoid-based-Project', 'gg582.github.io', 'tk9.0', 'SampleBlog', 'RIOTOSMiniCarImplementation', 'exampleCodeFromAzureClass']

# GitHub organization/username
GITHUB_USERNAME = 'gg582'

# Custom error handler for shutil.rmtree to handle permission issues, especially on Windows
def onerror(func, path, exc_info):
    """
    Error handler for `shutil.rmtree`.
    If the error is due to an access problem (e.g. windows), it tries to
    change the file permission to be writeable.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

# Retrieve public repository list using GitHub CLI
def get_public_repos():
    """
    Fetches a list of public repositories for the specified GitHub user using the GitHub CLI,
    excluding forked repositories except for 'gobus'.
    """
    try:
        print(f"Fetching public repositories for '{GITHUB_USERNAME}'...")
        result = subprocess.run(
            [
                'gh', 'repo', 'list', GITHUB_USERNAME,
                '--limit', '1000', '--json', 'name,isPrivate,isFork',
                '--jq', '.[] | select(.isPrivate == false and (.isFork == false or .name == "gobus")) | .name'
            ],
            capture_output=True, text=True, check=True
        )
        repos = [line.strip() for line in result.stdout.splitlines() if line.strip() not in EXCLUDED_REPOS]
        print(f"Found {len(repos)} public repositories.")
        return repos
    except subprocess.CalledProcessError as e:
        print(f"Error fetching repositories with gh CLI: {e}")
        print("Please ensure you have authenticated with 'gh auth login'.")
        return []

# Count lines authored by specific authors by parsing commit log
def count_lines(repo_path, authors):
    """
    Counts lines added by specific authors by iterating through all commits
    and checking each commit's author and changes.
    This is a more robust approach than relying on git log's unstable parsing.
    """
    total_lines = 0
    
    try:
        # Get all commit hashes
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'log', '--all', '--pretty=format:%H'],
            capture_output=True, text=True, check=True, errors='replace'
        )
        commit_hashes = result.stdout.splitlines()

        for commit_hash in commit_hashes:
            # Get author name for each commit
            author_result = subprocess.run(
                ['git', '-C', str(repo_path), 'show', '--no-patch', '--pretty=format:%an', commit_hash],
                capture_output=True, text=True, check=True, errors='replace'
            )
            author_name = author_result.stdout.strip().lower()

            # Check if the author is in our filter list
            if any(filtered_author.lower() in author_name for filtered_author in authors):
                # Get shortstat for the commit to count insertions
                stat_result = subprocess.run(
                    ['git', '-C', str(repo_path), 'show', '--shortstat', commit_hash],
                    capture_output=True, text=True, check=True, errors='replace'
                )
                
                for line in stat_result.stdout.splitlines():
                    if ' insertions(+)' in line:
                        parts = line.strip().split(', ')
                        for part in parts:
                            if 'insertions' in part:
                                added_lines = int(part.split()[0])
                                total_lines += added_lines
                                break
    except subprocess.CalledProcessError as e:
        print(f"  -> Error processing git log/show in '{repo_path}': {e.stderr.strip()}")
        return 0
    
    return total_lines

# Main processing function
def main():
    """
    Executes the entire process of cloning repositories and counting lines.
    """
    repos = get_public_repos()
    if not repos:
        return

    output = {}
    total = 0

    for repo in repos:
        print(f'\nProcessing repository: {repo}...')
        temp_dir = tempfile.mkdtemp()
        
        try:
            print(f'  -> Cloning {GITHUB_USERNAME}/{repo} into temporary directory...')
            subprocess.run(
                ['git', 'clone', '--depth=1', f'https://github.com/{GITHUB_USERNAME}/{repo}.git', temp_dir],
                check=True
            )
            
            count = count_lines(Path(temp_dir), FILTERED_AUTHORS)
            output[repo] = count
            total += count
            print(f"  -> Lines added by filtered authors: {count}")

        except subprocess.CalledProcessError as e:
            print(f'Failed to process {repo}, skipping. Error: {e}')
        finally:
            try:
                shutil.rmtree(temp_dir, onerror=onerror)
            except Exception as e:
                print(f"Error removing temporary directory '{temp_dir}': {e}")
                
    output['total_lines'] = total
    
    output_path = Path('public/lines.json')
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print("\n---")
    print(f"All repositories processed. Total lines added: {total}")
    print(f"Results saved to '{output_path}'")

if __name__ == '__main__':
    main()
