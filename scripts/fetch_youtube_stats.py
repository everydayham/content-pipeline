#!/usr/bin/env python3
"""
Fetch YouTube channel statistics for The Everyday Ham.
Runs weekly via GitHub Actions.

Requires:
- YOUTUBE_API_KEY environment variable
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
OUTPUT_DIR = PROJECT_ROOT / "analytics" / "youtube"

API_BASE = "https://www.googleapis.com/youtube/v3"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_channel_id(handle, api_key):
    """Get channel ID from handle"""
    # Remove @ if present
    handle = handle.lstrip('@')
    
    url = f"{API_BASE}/channels"
    params = {
        "part": "id,snippet,statistics",
        "forHandle": handle,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get('items'):
        return data['items'][0]
    return None

def get_channel_videos(channel_id, api_key, max_results=50):
    """Get recent videos from channel"""
    # First get the uploads playlist
    url = f"{API_BASE}/channels"
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('items'):
        return []
    
    uploads_playlist = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Get videos from uploads playlist
    url = f"{API_BASE}/playlistItems"
    params = {
        "part": "snippet",
        "playlistId": uploads_playlist,
        "maxResults": max_results,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    return data.get('items', [])

def get_video_stats(video_ids, api_key):
    """Get statistics for videos"""
    url = f"{API_BASE}/videos"
    params = {
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('items', [])

def generate_markdown(channel_info, videos_with_stats):
    """Generate markdown summary"""
    stats = channel_info.get('statistics', {})
    snippet = channel_info.get('snippet', {})
    
    lines = [
        "# YouTube Analytics",
        f"## {snippet.get('title', 'Everyday Ham')}",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "---",
        "",
        "## 📊 Channel Stats",
        "",
        f"- **Subscribers:** {int(stats.get('subscriberCount', 0)):,}",
        f"- **Total Views:** {int(stats.get('viewCount', 0)):,}",
        f"- **Total Videos:** {stats.get('videoCount', 'N/A')}",
        "",
        "---",
        "",
        "## 🎬 Recent Video Performance",
        "",
        "| Video | Published | Views | Likes | Comments |",
        "|-------|-----------|-------|-------|----------|"
    ]
    
    # Sort by date
    sorted_videos = sorted(
        videos_with_stats,
        key=lambda x: x.get('snippet', {}).get('publishedAt', ''),
        reverse=True
    )
    
    for video in sorted_videos[:20]:
        snippet = video.get('snippet', {})
        stats = video.get('statistics', {})
        
        title = snippet.get('title', 'Untitled')[:45]
        if len(snippet.get('title', '')) > 45:
            title += "..."
        
        pub_date = snippet.get('publishedAt', '')[:10]
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        lines.append(f"| {title} | {pub_date} | {views:,} | {likes:,} | {comments:,} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 🏆 Top Performing Videos (by views)",
        ""
    ])
    
    # Top by views
    top_videos = sorted(
        videos_with_stats,
        key=lambda x: int(x.get('statistics', {}).get('viewCount', 0)),
        reverse=True
    )[:10]
    
    for i, video in enumerate(top_videos, 1):
        title = video.get('snippet', {}).get('title', 'Untitled')
        views = int(video.get('statistics', {}).get('viewCount', 0))
        lines.append(f"{i}. **{title}** - {views:,} views")
    
    lines.extend([
        "",
        "---",
        "",
        "## 💡 Insights",
        "",
        "*What topics/formats are performing best? Use this when planning content.*",
        ""
    ])
    
    return "\n".join(lines)

def main():
    print("=" * 50)
    print("THE EVERYDAY HAM - YouTube Channel Analytics")
    print("=" * 50)
    
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY not set")
        return
    
    config = load_config()
    channel_handle = config['youtube']['channel_handle']
    
    print(f"\nFetching channel info for {channel_handle}...")
    
    try:
        channel_info = get_channel_id(channel_handle, api_key)
        if not channel_info:
            print("  ✗ Channel not found")
            return
        
        channel_id = channel_info['id']
        print(f"  ✓ Found channel: {channel_info['snippet']['title']}")
        print(f"    Subscribers: {int(channel_info['statistics']['subscriberCount']):,}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return
    
    print("\nFetching videos...")
    try:
        videos = get_channel_videos(channel_id, api_key, max_results=50)
        print(f"  ✓ Found {len(videos)} videos")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return
    
    print("\nFetching video statistics...")
    video_ids = [v['snippet']['resourceId']['videoId'] for v in videos]
    
    # Batch in groups of 50
    videos_with_stats = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        stats = get_video_stats(batch, api_key)
        videos_with_stats.extend(stats)
    
    print(f"  ✓ Got stats for {len(videos_with_stats)} videos")
    
    # Generate output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = OUTPUT_DIR / "channel-stats.json"
    with open(json_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'channel': channel_info,
            'videos': videos_with_stats
        }, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    # Save Markdown
    markdown = generate_markdown(channel_info, videos_with_stats)
    md_file = OUTPUT_DIR / "channel-summary.md"
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {md_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
