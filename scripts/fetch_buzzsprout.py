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

PODCAST_ID = "2438895"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def fetch_episodes(api_token):
    url = f"https://www.buzzsprout.com/api/{PODCAST_ID}/episodes.json"
    headers = {
        "Authorization": f"Token token={api_token}",
        "User-Agent": "EverydayHam-ContentPipeline/1.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def generate_markdown(episodes):
    lines = [
        "# Buzzsprout Analytics",
        "## Everyday Ham Podcast",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "---",
        "",
        "## 📊 Episode Performance",
        "",
        "| # | Title | Published | Plays | Duration |",
        "|---|-------|-----------|-------|----------|"
    ]
    
    sorted_episodes = sorted(
        [e for e in episodes if e.get('published_at')],
        key=lambda x: x.get('published_at', ''),
        reverse=True
    )
    
    total_plays = 0
    for i, ep in enumerate(sorted_episodes[:20], 1):
        title = ep.get('title', 'Untitled')[:45]
        if len(ep.get('title', '')) > 45:
            title += "..."
        pub_date = ep.get('published_at', '')[:10]
        plays = ep.get('total_plays', 0)
        total_plays += plays
        duration = ep.get('duration', 0)
        mins = duration // 60 if duration else 0
        
        lines.append(f"| {i} | {title} | {pub_date} | {plays:,} | {mins} min |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📈 Summary",
        "",
        f"- **Total Episodes:** {len(sorted_episodes)}",
        f"- **Total Plays (last 20 eps):** {total_plays:,}",
        "",
        "---",
        "",
        "## 🏆 Top Episodes by Plays",
        ""
    ])
    
    top_eps = sorted(sorted_episodes, key=lambda x: x.get('total_plays', 0), reverse=True)[:5]
    for i, ep in enumerate(top_eps, 1):
        title = ep.get('title', 'Untitled')
        plays = ep.get('total_plays', 0)
        lines.append(f"{i}. **{title}** - {plays:,} plays")
    
    lines.extend([
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
    
    print(f"\nFetching episodes for podcast {PODCAST_ID}...")
    
    try:
        episodes = fetch_episodes(api_token)
        print(f"  ✓ Found {len(episodes)} episodes")
    except Exception as e:
        print(f"  ✗ Error fetching episodes: {e}")
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    json_file = OUTPUT_DIR / "latest.json"
    with open(json_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'episodes': episodes
        }, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    markdown = generate_markdown(episodes)
    md_file = OUTPUT_DIR / "summary.md"
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {md_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
