#!/usr/bin/env python3
"""
Fetch hot posts from ham radio subreddits via RSS.
Runs daily via GitHub Actions.
"""
import json
import feedparser
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "news-summaries"

SUBREDDITS = [
    {"name": "amateurradio", "url": "https://www.reddit.com/r/amateurradio/.rss"},
    {"name": "HamRadio", "url": "https://www.reddit.com/r/HamRadio/.rss"}
]

def fetch_subreddit(subreddit):
    """Fetch posts from subreddit RSS feed"""
    feed = feedparser.parse(subreddit['url'])
    if feed.bozo and not feed.entries:
        return None
    return feed.entries

def generate_markdown(all_posts):
    """Generate markdown summary of Reddit posts"""
    lines = [
        "# Ham Radio Reddit Digest",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "Hot posts from the amateur radio communities on Reddit.",
        "",
        "---",
        ""
    ]
    
    all_entries = []
    
    for subreddit_name, posts in all_posts.items():
        lines.append(f"## 🔥 r/{subreddit_name}")
        lines.append("")
        
        for i, post in enumerate(posts[:15], 1):
            title = post.get('title', 'No title')[:80]
            if len(post.get('title', '')) > 80:
                title += "..."
            link = post.get('link', '')
            author = post.get('author', 'unknown')
            
            lines.append(f"**{i}. [{title}]({link})**")
            lines.append(f"by u/{author.replace('/u/', '')}")
            lines.append("")
            
            all_entries.append({
                'title': post.get('title', ''),
                'link': link,
                'subreddit': subreddit_name,
                'author': author
            })
        
        lines.append("---")
        lines.append("")
    
    lines.extend([
        "## 💡 Recent Discussions",
        "",
        "*Latest posts across both subreddits:*",
        ""
    ])
    
    for entry in all_entries[:10]:
        title = entry['title'][:70]
        if len(entry['title']) > 70:
            title += "..."
        lines.append(f"- **[{title}]({entry['link']})** (r/{entry['subreddit']})")
    
    lines.extend([
        "",
        "---",
        "",
        "*Sources: r/amateurradio, r/HamRadio*"
    ])
    
    return "\n".join(lines)

def main():
    print("=" * 50)
    print("THE EVERYDAY HAM - Reddit Fetch")
    print("=" * 50)
    
    all_posts = {}
    
    for subreddit in SUBREDDITS:
        print(f"\nFetching r/{subreddit['name']}...")
        try:
            posts = fetch_subreddit(subreddit)
            if posts:
                all_posts[subreddit['name']] = posts
                print(f"  ✓ Found {len(posts)} posts")
            else:
                print(f"  ✗ No posts found")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    if not all_posts:
        print("\nNo data retrieved. Exiting.")
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = OUTPUT_DIR / "reddit.json"
    json_data = {
        'updated': datetime.now().isoformat(),
        'subreddits': [s['name'] for s in SUBREDDITS],
        'posts': {name: [{'title': p.get('title'), 'link': p.get('link'), 'author': p.get('author')} for p in posts] for name, posts in all_posts.items()}
    }
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"\n✓ Saved: {json_file}")
    
    # Save Markdown
    markdown = generate_markdown(all_posts)
    md_file = OUTPUT_DIR / "reddit.md"
    with open(md_file, 'w') as f:
        f.write(markdown)
    print(f"✓ Saved: {md_file}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
