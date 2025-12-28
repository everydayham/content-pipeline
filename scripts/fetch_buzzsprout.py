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
    """Fetch all episodes from Buzzsprout"""
    url = f"https://www.buzzsprout.com/api/{podcast_id}/episodes.json"
      headers = {"Authorization": f"Token {api_token}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_episode_stats(podcast_id, episode_id, api_token):
    """Fetch stats for a specific episode"""
    url = f"https://www.buzzsprout.com/api/{podcast_id}/episodes/{episode_id}/stats.json"
    headers = {"Authorization": f"Token token={api_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except:
        return None

def generate_markdown(episodes, stats_by_episode):
    """Generate markdown summary of podcast performance"""
    lines = [
        "# Buzzsprout Analytics",
        f"## Everyday Ham Podcast",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "---",
        "",
        "## 📊 Episode Performance",
        "",
        "| Episode | Title | Published | Total Downloads |",
        "|---------|-------|-----------|-----------------|"
    ]
    
    # Sort by publish date descending
    sorted_episodes = sorted(
        [e for e in episodes if e.get('published_at')],
        key=lambda x: x.get('published_at', ''),
        reverse=True
    )
    
    total_downloads = 0
    for i, ep in enumerate(sorted_episodes[:20]):  # Last 20 episodes
        episode_num = len(sorted_episodes) - i
        title = ep.get('title', 'Untitled')[:50]
        if len(ep.get('title', '')) > 50:
            title += "..."
        pub_date = ep.get('published_at', '')[:10]
        
        stats = stats_by_episode.get(ep['id'], {})
        downloads = stats.get('total_downloads', 'N/A')
        if isinstance(downloads, int):
            total_downloads += downloads
            downloads = f"{downloads:,}"
        
        lines.append(f"| {episode_num} | {title} | {pub_date} | {downloads} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📈 Summary Stats",
        "",
        f"- **Total Episodes:** {len(sorted_episodes)}",
        f"- **Total Downloads (last 20 eps):** {total_downloads:,}",
        "",
        "---",
        "",
        "## 🎯 Top Performing Episodes",
        "",
    ])
    
    # Find top performers
    episodes_with_downloads = []
    for ep in sorted_episodes:
        stats = stats_by_episode.get(ep['id'], {})
        downloads = stats.get('total_downloads', 0)
        if isinstance(downloads, int) and downloads > 0:
            episodes_with_downloads.append({
                'title': ep.get('title', 'Untitled'),
                'downloads': downloads,
                'published': ep.get('published_at', '')[:10]
            })
    
    top_episodes = sorted(episodes_with_downloads, key=lambda x: x['downloads'], reverse=True)[:5]
    
    for i, ep in enumerate(top_episodes, 1):
        lines.append(f"{i}. **{ep['title']}** - {ep['downloads']:,} downloads ({ep['published']})")
    
    lines.extend([
        "",
        "---",
        "",
        "## 💡 Insights for Content Planning",
        "",
        "*What topics/formats performed best? Use this data when brainstorming with Claude.*",
        ""
    ])
    
    return "\n".join(lines)

def main():
    print("=" * 50)
    print("THE EVERYDAY HAM - Buzzsprout Analytics")
    print("=" * 50)
    
    # Get API token from environment
    api_token = os.environ.get('BUZZSPROUT_API_TOKEN')
    if not api_token:
        print("ERROR: BUZZSPROUT_API_TOKEN not set")
        return
    
    config = load_config()
    podcast_id = config['buzzsprout']['podcast_id']
    
    print(f"\nFetching episodes for podcast {podcast_id}...")
    
    try:
        episodes = fetch_episodes(podcast_id, api_token)
        print(f"  ✓ Found {len(episodes)} episodes")
    except Exception as e:
        print(f"  ✗ Error fetching episodes: {e}")
        return
    
    # Fetch stats for recent episodes
    print("\nFetching episode stats...")
    stats_by_episode = {}
    
    # Sort by date and get recent ones
    sorted_eps = sorted(
        [e for e in episodes if e.get('published_at')],
        key=lambda x: x.get('published_at', ''),
        reverse=True
    )
    
    for ep in sorted_eps[:20]:  # Last 20 episodes
        stats = fetch_episode_stats(podcast_id, ep['id'], api_token)
        if stats:
            stats_by_episode[ep['id']] = stats
            print(f"  ✓ {ep.get('title', 'Untitled')[:40]}...")
    
    # Generate output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = OUTPUT_DIR / "latest.json"
    with open(json_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'episodes': episodes,
            'stats': stats_by_episode
        }, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    # Save Markdown
    markdown = generate_markdown(episodes, stats_by_episode)
    md_file = OUTPUT_DIR / "summary.md"
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {md_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
