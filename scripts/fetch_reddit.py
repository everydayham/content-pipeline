#!/usr/bin/env python3
"""
Fetch hot posts from ham radio subreddits.
Runs daily via GitHub Actions.
"""
import json
import requests
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "news-summaries"

SUBREDDITS = ["amateurradio", "HamRadio"]
USER_AGENT = "EverydayHam-ContentPipeline/1.0"

def fetch_reddit_posts(subreddit, sort="hot", limit=20):
    """Fetch posts from subreddit"""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    headers = {"User-Agent": USER_AGENT}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

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
    
    # Posts by subreddit
    for subreddit, data in all_posts.items():
        posts = data.get('data', {}).get('children', [])
        
        lines.append(f"## 🔥 r/{subreddit}")
        lines.append("")
        
        for i, post in enumerate(posts[:15], 1):
            p = post.get('data', {})
            title = p.get('title', 'No title')[:80]
            if len(p.get('title', '')) > 80:
                title += "..."
            score = p.get('score', 0)
            num_comments = p.get('num_comments', 0)
            permalink = f"https://reddit.com{p.get('permalink', '')}"
            flair = p.get('link_flair_text', '')
            
            flair_str = f" `{flair}`" if flair else ""
            
            lines.append(f"**{i}. [{title}]({permalink})**{flair_str}")
            lines.append(f"⬆️ {score} | 💬 {num_comments} comments")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Combined top discussions
    lines.extend([
        "## 💡 Top Discussions (Combined)",
        "",
        "*Highest engagement posts across both subreddits:*",
        ""
    ])
    
    # Combine and sort by comments
    combined = []
    for subreddit, data in all_posts.items():
        for post in data.get('data', {}).get('children', []):
            post['data']['subreddit_name'] = subreddit
            combined.append(post)
    
    top_engagement = sorted(combined, key=lambda x: x['data'].get('num_comments', 0), reverse=True)[:10]
    
    for post in top_engagement:
        p = post.get('data', {})
        title = p.get('title', 'No title')[:70]
        if len(p.get('title', '')) > 70:
            title += "..."
        comments = p.get('num_comments', 0)
        score = p.get('score', 0)
        sub = p.get('subreddit_name', '')
        permalink = f"https://reddit.com{p.get('permalink', '')}"
        
        lines.append(f"- **[{title}]({permalink})** (r/{sub})")
        lines.append(f"  ⬆️ {score} | 💬 {comments} comments")
        lines.append("")
    
    lines.extend([
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
        print(f"\nFetching r/{subreddit}...")
        try:
            data = fetch_reddit_posts(subreddit, "hot", 20)
            posts = data.get('data', {}).get('children', [])
            all_posts[subreddit] = data
            print(f"  ✓ Found {len(posts)} posts")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    if not all_posts:
        print("\nNo data retrieved. Exiting.")
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = OUTPUT_DIR / "reddit.json"
    with open(json_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'subreddits': SUBREDDITS,
            'posts': all_posts
        }, f, indent=2)
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
