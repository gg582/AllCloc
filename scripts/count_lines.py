import requests
import os
import json

GITHUB_USER = "gg582"
API_URL = f"https://api.github.com/users/{GITHUB_USER}/repos"
HEADERS = {"Accept": "application/vnd.github.v3+json"}

repos = requests.get(API_URL, headers=HEADERS).json()
line_count = 0

for repo in repos:
    if repo.get("private"):
        continue
    clone_url = repo["clone_url"]
    os.system(f"git clone --depth=1 {clone_url} temp_repo")
    for root, _, files in os.walk("temp_repo"):
        for file in files:
            try:
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    line_count += sum(1 for _ in f)
            except:
                pass
    os.system("rm -rf temp_repo")

output = {"public_repos_line_count": line_count}
with open("public/lines.json", "w") as f:
    json.dump(output, f)

