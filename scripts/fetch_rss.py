#!/usr/bin/env python3
"""
Fetch RSS feeds from amateur radio news sources and generate daily summaries.
Runs daily via GitHub Actions.
"""
import feedparser
import json
from datetime import datetime
from pathlib import Path
from html import unescape
import re

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
FEEDS_FILE = PROJECT_ROOT / "feeds.json"
OUTPUT_DIR = PROJECT_ROOT / "news-summaries"

def load_feeds_config():
    with open(FEEDS_FILE, 'r') as f:
        return json.load(f)

def clean_html(text):
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def truncate_text(text, max_length=300):
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."

def fetch_feed(source):
    try:
        feed = feedparser.parse(source['feed_url'])
        if feed.bozo and not feed.entries:
            print(f"  Warning: Could not parse {source['name']}")
            return None
        items = []
        for entry in feed.entries[:10]:
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6])
            summary = ""
            if hasattr(entry, 'summary'):
                summary = clean_html(entry.summary)
            elif hasattr(entry, 'description'):
                summary = clean_html(entry.description)
            items.append({
                'title': clean_html(entry.get('title', 'No Title')),
                'link': entry.get('link', ''),
                'summary': truncate_text(summary),
                'published': pub_date.isoformat() if pub_date else None,
                'source': source['name']
            })
        return {'source': source['name'], 'category': source.get('category', 'general'), 'items': items}
    except Exception as e:
        print(f"  Error fetching {source['name']}: {e}")
        return None

def generate_markdown(feeds_data, date):
    lines = [
        f"# Amateur Radio News Summary",
        f"## {date.strftime('%B %d, %Y')}",
        "",
        f"*Auto-generated from {len(feeds_data)} sources*",
        "",
        "---",
        "",
        "## 📻 Quick Highlights",
        ""
    ]
    
    highlight_count = 0
    for feed in feeds_data:
        if feed and feed['items'] and highlight_count < 5:
            item = feed['items'][0]
            lines.append(f"- **[{item['title']}]({item['link']})** ({feed['source']})")
            highlight_count += 1
    
    lines.extend(["", "---", "", "## 📰 Full News by Source", ""])
    
    for feed in feeds_data:
        if not feed or not feed['items']:
            continue
        lines.append(f"### {feed['source']}")
        lines.append("")
        for item in feed['items'][:5]:
            lines.append(f"**[{item['title']}]({item['link']})**")
            if item['summary']:
                lines.append(f"> {item['summary']}")
            lines.append("")
        lines.extend(["---", ""])
    
    lines.extend([
        "## 💡 Potential Episode Topics",
        "",
        "*Use this section when brainstorming with Claude*",
        "",
        "---",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"
    ])
    
    return "\n".join(lines)

def main():
    print("=" * 50)
    print("THE EVERYDAY HAM - News Fetcher")
    print("=" * 50)
    
    config = load_feeds_config()
    sources = config['sources']
    
    print(f"\nFetching from {len(sources)} sources...")
    
    feeds_data = []
    for source in sources:
        print(f"  -> {source['name']}...")
        result = fetch_feed(source)
        if result:
            feeds_data.append(result)
            print(f"     ✓ Got {len(result['items'])} items")
        else:
            print(f"     ✗ Failed")
    
    today = datetime.now()
    markdown = generate_markdown(feeds_data, today)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save dated file
    output_file = OUTPUT_DIR / f"{today.strftime('%Y-%m-%d')}.md"
    with open(output_file, 'w') as f:
        f.write(markdown)
    print(f"\n✓ Saved: {output_file}")
    
    # Save latest file
    latest_file = OUTPUT_DIR / "latest.md"
    with open(latest_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {latest_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
