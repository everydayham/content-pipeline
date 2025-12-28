#!/usr/bin/env python3
"""
Fetch trending amateur radio videos across YouTube.
Monitors the broader ham radio community to spot trends and opportunities.
Runs weekly via GitHub Actions.

Requires:
- YOUTUBE_API_KEY environment variable
"""
import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
OUTPUT_DIR = PROJECT_ROOT / "analytics" / "youtube"

API_BASE = "https://www.googleapis.com/youtube/v3"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def search_videos(query, api_key, published_after, max_results=25):
    """Search for recent videos matching query"""
    url = f"{API_BASE}/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": published_after,
        "maxResults": max_results,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('items', [])

def get_video_details(video_ids, api_key):
    """Get detailed stats for videos"""
    if not video_ids:
        return []
    
    url = f"{API_BASE}/videos"
    params = {
        "part": "statistics,snippet,contentDetails",
        "id": ",".join(video_ids),
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('items', [])

def generate_markdown(all_videos, keywords_searched):
    """Generate markdown summary of trending ham radio content"""
    lines = [
        "# Ham Radio YouTube Trends",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "What's trending across amateur radio YouTube in the past 7 days.",
        "",
        "---",
        "",
        "## 🔥 Top Performing Videos This Week",
        "",
        "| Video | Channel | Views | Published |",
        "|-------|---------|-------|-----------|"
    ]
    
    # Sort by view count and deduplicate
    seen_ids = set()
    unique_videos = []
    for video in sorted(all_videos, key=lambda x: int(x.get('statistics', {}).get('viewCount', 0)), reverse=True):
        vid_id = video.get('id')
        if vid_id not in seen_ids:
            seen_ids.add(vid_id)
            unique_videos.append(video)
    
    for video in unique_videos[:25]:
        snippet = video.get('snippet', {})
        stats = video.get('statistics', {})
        
        title = snippet.get('title', 'Untitled')[:50]
        if len(snippet.get('title', '')) > 50:
            title += "..."
        
        channel = snippet.get('channelTitle', 'Unknown')[:20]
        views = int(stats.get('viewCount', 0))
        pub_date = snippet.get('publishedAt', '')[:10]
        
        lines.append(f"| {title} | {channel} | {views:,} | {pub_date} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📊 Trending Topics",
        "",
        "Based on search performance this week:",
        ""
    ])
    
    # Analyze topics
    topic_counts = {}
    topic_keywords = {
        "POTA/Portable": ["pota", "portable", "parks on the air", "field"],
        "Gear Reviews": ["review", "unboxing", "vs", "comparison"],
        "Antennas": ["antenna", "dipole", "vertical", "yagi"],
        "Digital Modes": ["ft8", "digital", "js8", "winlink"],
        "License/Learning": ["license", "technician", "general", "exam", "learn"],
        "Contests": ["contest", "field day", "qso party"],
        "QRP": ["qrp", "low power"],
        "HF Operating": ["hf", "dx", "propagation"]
    }
    
    for video in unique_videos:
        title = video.get('snippet', {}).get('title', '').lower()
        desc = video.get('snippet', {}).get('description', '').lower()
        text = title + " " + desc
        
        for topic, keywords in topic_keywords.items():
            for kw in keywords:
                if kw in text:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                    break
    
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    for topic, count in sorted_topics[:8]:
        bar = "█" * min(count, 20)
        lines.append(f"- **{topic}**: {bar} ({count} videos)")
    
    lines.extend([
        "",
        "---",
        "",
        "## 🎯 Content Opportunities",
        "",
        "*Topics with high views but fewer videos = opportunities*",
        "",
        "Look for:",
        "- High-performing videos with topics you haven't covered",
        "- Questions in comments that aren't being answered",
        "- Trending gear you could review",
        "",
        "---",
        "",
        "## 🔍 Keywords Searched",
        ""
    ])
    
    for kw in keywords_searched:
        lines.append(f"- {kw}")
    
    return "\n".join(lines)

def main():
    print("=" * 50)
    print("THE EVERYDAY HAM - YouTube Trends Monitor")
    print("=" * 50)
    
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY not set")
        return
    
    config = load_config()
    keywords = config['youtube']['search_keywords']
    days_back = config['youtube'].get('trending_period_days', 7)
    
    published_after = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"
    
    print(f"\nSearching videos from the last {days_back} days...")
    print(f"Keywords to search: {len(keywords)}")
    
    all_videos = []
    video_ids = set()
    
    # Search for each keyword (limit to avoid API quota)
    keywords_to_search = keywords[:10]  # Limit to conserve API quota
    
    for keyword in keywords_to_search:
        print(f"  -> Searching: {keyword}")
        try:
            results = search_videos(keyword, api_key, published_after, max_results=10)
            for item in results:
                vid_id = item['id']['videoId']
                if vid_id not in video_ids:
                    video_ids.add(vid_id)
            print(f"     ✓ Found {len(results)} results")
        except Exception as e:
            print(f"     ✗ Error: {e}")
    
    print(f"\nTotal unique videos found: {len(video_ids)}")
    
    # Get detailed stats
    print("\nFetching video details...")
    video_ids_list = list(video_ids)
    
    for i in range(0, len(video_ids_list), 50):
        batch = video_ids_list[i:i+50]
        try:
            details = get_video_details(batch, api_key)
            all_videos.extend(details)
            print(f"  ✓ Got details for {len(details)} videos")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Generate output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = OUTPUT_DIR / "trends.json"
    with open(json_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'period_days': days_back,
            'keywords_searched': keywords_to_search,
            'videos': all_videos
        }, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    # Save Markdown
    markdown = generate_markdown(all_videos, keywords_to_search)
    md_file = OUTPUT_DIR / "trends.md"
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {md_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
