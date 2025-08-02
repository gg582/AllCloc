import json
import os
from pathlib import Path
import base64

# Define the SVG template for the banner
SVG_TEMPLATE = """
<svg width="400" height="100" viewBox="0 0 400 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #1C1C1C; }}
    .border {{ stroke: #333333; }}
    .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-weight: 600; font-size: 20px; fill: #EBEBEB; }}
    .stat-value {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-weight: 700; font-size: 36px; fill: #A5FF24; }}
    .stat-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-weight: 400; font-size: 14px; fill: #C4C4C4; }}
  </style>
  <rect x="0.5" y="0.5" width="399" height="99" rx="10" class="bg" stroke-width="1"/>
  <text x="20" y="35" class="title">Total Lines Contributed</text>
  <text x="20" y="75" class="stat-value">{total_lines}</text>
  <text x="20" y="85" class="stat-label">lines in {repo_count} public repos</text>
</svg>
"""

def render_banner():
    """
    Reads the lines.json file and generates an SVG banner.
    """
    lines_file_path = Path('public/lines.json')
    if not lines_file_path.exists():
        print("Error: public/lines.json not found. Please run the counting script first.")
        return

    with open(lines_file_path, 'r') as f:
        data = json.load(f)

    total_lines = data.get('total_lines', 0)
    repo_count = len(data) - 1 if 'total_lines' in data else len(data)

    # Fill the template with dynamic data
    svg_content = SVG_TEMPLATE.format(
        total_lines=f'{total_lines:,}', # Add comma for readability
        repo_count=repo_count
    )

    # Save the SVG file
    svg_output_path = Path('public/banner.svg')
    with open(svg_output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"SVG banner created at {svg_output_path}")

if __name__ == '__main__':
    # Make sure the public directory exists
    Path('public').mkdir(exist_ok=True)
    render_banner()
