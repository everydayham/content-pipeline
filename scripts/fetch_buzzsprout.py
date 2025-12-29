#!/usr/bin/env python3
"""
Fetch podcast analytics from Buzzsprout API.
Runs weekly via GitHub Actions.

Requires:
- BUZZSPROUT_API_TOKEN environment variable
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
OUTPUT_DIR = PROJECT_ROOT / "analytics" / "buzzsprout"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def fetch_episodes(podcast_id, api_token):
    url = f"https://www.buzzsprout.com/api/podcasts/{podcast_id}/episodes.json"
    headers = {
        "Authorization": f"Token token={api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_stats(podcast_id, api_token):
    url = f"https://www.buzzsprout.com/api/podcasts/{podcast_id}/stats?timeframe=all_time"
    headers = {
        "Authorization": f"Token token={api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def generate_markdown(episodes, stats):
    lines = [
        "# Buzzsprout Analytics",
        "## Everyday Ham Podcast",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "---",
        ""
    ]
    
    if stats:
        lines.extend([
            "## 📈 All-Time Stats",
            "",
            f"- **Total Downloads:** {stats.get('total_downloads', 'N/A'):,}" if isinstance(stats.get('total_downloads'), int) else f"- **Total Downloads:** {stats.get('total_downloads', 'N/A')}",
            "",
            "---",
            ""
        ])
    
    lines.extend([
        "## 📊 Episode List",
        "",
        "| # | Title | Published | Duration |",
        "|---|-------|-----------|----------|"
    ])
    
    sorted_episodes = sorted(
        [e for e in episodes if e.get('published_at')],
        key=lambda x: x.get('published_at', ''),
        reverse=True
    )
    
    for i, ep in enumerate(sorted_episodes[:20], 1):
        title = ep.get('title', 'Untitled')[:50]
        if len(ep.get('title', '')) > 50:
            title += "..."
        pub_date = ep.get('published_at', '')[:10]
        duration = ep.get('duration', 0)
        mins = duration // 60 if duration else 0
        
        lines.append(f"| {i} | {title} | {pub_date} | {mins} min |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📋 Summary",
        "",
        f"- **Total Episodes:** {len(sorted_episodes)}",
        "",
        "---",
        "",
        "## 💡 Insights",
        "",
        "*Use this data when planning content with Claude.*",
        ""
    ])
    
    return "\n".join(lines)

def main():
    print("=" * 50)
    print("THE EVERYDAY HAM - Buzzsprout Analytics")
    print("=" * 50)
    
    api_token = os.environ.get('BUZZSPROUT_API_TOKEN')
    if not api_token:
        print("ERROR: BUZZSPROUT_API_TOKEN not set")
        return
    
    config = load_config()
    podcast_id = config['buzzsprout']['podcast_id']
    
    print(f"\nFetching data for podcast {podcast_id}...")
    
    episodes = []
    stats = None
    
    try:
        episodes = fetch_episodes(podcast_id, api_token)
        print(f"  ✓ Found {len(episodes)} episodes")
    except Exception as e:
        print(f"  ✗ Error fetching episodes: {e}")
    
    try:
        stats = fetch_stats(podcast_id, api_token)
        print(f"  ✓ Got stats")
    except Exception as e:
        print(f"  ✗ Error fetching stats: {e}")
    
    if not episodes and not stats:
        print("\nNo data retrieved. Exiting.")
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    json_file = OUTPUT_DIR / "latest.json"
    with open(json_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'episodes': episodes,
            'stats': stats
        }, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    markdown = generate_markdown(episodes, stats)
    md_file = OUTPUT_DIR / "summary.md"
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {md_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
