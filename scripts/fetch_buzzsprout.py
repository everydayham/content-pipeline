#!/usr/bin/env python3
"""
Fetch podcast analytics from Buzzsprout via Cloud Run proxy.
Runs weekly via GitHub Actions.
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "analytics" / "buzzsprout"

# Your working Cloud Run proxy
PROXY_URL = "https://buzzsprout-ham-549487143584.us-central1.run.app"

def fetch_stats():
    response = requests.get(PROXY_URL)
    response.raise_for_status()
    return response.json()

def generate_markdown(stats):
    lines = [
        "# Buzzsprout Analytics",
        "## Everyday Ham Podcast",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "---",
        "",
        "## 📈 Stats",
        "",
        "```json",
        json.dumps(stats, indent=2),
        "```",
        "",
        "---",
        "",
        "## 💡 Insights",
        "",
        "*Use this data when planning content with Claude.*",
        ""
    ]
    
    return "\n".join(lines)

def main():
    print("=" * 50)
    print("THE EVERYDAY HAM - Buzzsprout Analytics")
    print("=" * 50)
    
    print(f"\nFetching data from proxy...")
    
    try:
        stats = fetch_stats()
        print(f"  ✓ Got stats")
    except Exception as e:
        print(f"  ✗ Error fetching stats: {e}")
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    json_file = OUTPUT_DIR / "latest.json"
    with open(json_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'stats': stats
        }, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    markdown = generate_markdown(stats)
    md_file = OUTPUT_DIR / "summary.md"
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {md_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
