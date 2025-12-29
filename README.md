# The Everyday Ham - Content Pipeline

A content intelligence system for **The Everyday Ham** podcast and YouTube channel. This repository automatically aggregates amateur radio news, tracks performance analytics, monitors YouTube trends, and helps with content planning.

## 🎯 What This Does

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA SOURCES                                      │
├───────────────┬──────────────┬───────────────┬──────────────┬───────────────┤
│  RSS Feeds    │   Reddit     │  Buzzsprout   │ YOUR YouTube │ HAM RADIO YT  │
│  (News)       │  (Community) │  (Podcast)    │ (Your stats) │ (Trends)      │
│               │              │               │              │               │
│ • ARRL        │ • r/amateur  │ • Episodes    │ • Views      │ • Trending    │
│ • QRZ         │   radio      │ • Play counts │ • Subs       │ • Popular     │
│ • SWLing      │ • r/HamRadio │ • Duration    │ • Growth     │ • Content     │
│ • AR Newsline │              │               │              │   gaps        │
│ • OnAllBands  │              │               │              │               │
│ • K0NR        │              │               │              │               │
│ • EtherHam    │              │               │              │               │
└───────────────┴──────────────┴───────────────┴──────────────┴───────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THIS REPOSITORY                                     │
│                                                                              │
│  /news-summaries/     Fresh ham radio news + Reddit posts (daily)            │
│  /analytics/          Performance data (weekly)                              │
│  /calendar/           Content schedule & planning                            │
│  /episode-ideas/      Idea backlog & tracking                                │
│                                                                              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLAUDE PROJECT                                      │
│                                                                              │
│  Sync this repo → Get intelligent content suggestions based on:              │
│  • What's trending in ham radio news & Reddit                                │
│  • What's working for YOUR audience                                          │
│  • What topics you haven't covered yet                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📅 Content Schedule

| Content | Record | Publish | Frequency |
|---------|--------|---------|-----------|
| **YouTube Video** | Varies | **Thursdays** | Weekly |
| **Audio Podcast** | **1st Tuesday** | **1st Thursday** | Monthly |

## 🗂️ Repository Structure

```
content-pipeline/
├── .github/workflows/          # Automated actions
│   ├── daily-news.yml          # Runs daily @ 6 AM ET
│   └── weekly-analytics.yml    # Runs Mondays @ 7 AM ET
│
├── scripts/                    # Python scripts for data fetching
│   ├── fetch_rss.py            # Ham radio news aggregation
│   ├── fetch_reddit.py         # Reddit community posts
│   ├── fetch_buzzsprout.py     # Podcast analytics
│   ├── fetch_youtube_stats.py  # Channel performance
│   └── fetch_youtube_trends.py # Community trends
│
├── news-summaries/             # Daily content (auto-updated)
│   ├── latest.md               # Today's RSS news
│   ├── reddit.md               # Reddit hot posts
│   └── YYYY-MM-DD.md           # Archived daily summaries
│
├── analytics/
│   ├── buzzsprout/             # Podcast performance
│   │   ├── summary.md
│   │   └── latest.json
│   └── youtube/                # YouTube performance + trends
│       ├── channel-summary.md
│       ├── trends.md
│       └── *.json
│
├── calendar/                   # Content planning
│   ├── schedule.md             # Publishing calendar
│   ├── youtube-queue.md        # Upcoming videos
│   └── podcast-planning.md     # Monthly podcast prep
│
├── episode-ideas/              # Idea tracking
│   ├── backlog.md              # Master idea list
│   ├── audio-podcast.md        # Podcast-specific ideas
│   └── youtube.md              # Video-specific ideas
│
├── docs/
│   └── topics.md               # Categories & tags reference
│
├── config.json                 # YouTube search keywords
└── feeds.json                  # RSS feed sources
```

## 📰 Data Sources

### RSS Feeds (Daily)
- **ARRL** - Official amateur radio news
- **QRZ Forums** - Community discussions
- **SWLing Post** - Shortwave & ham radio
- **AR Newsline** - Weekly news program
- **OnAllBands** - DX Engineering blog
- **K0NR** - Bob Witte's ham radio blog
- **EtherHam** - Amateur radio content

### Reddit (Daily)
- **r/amateurradio** - Main ham radio community
- **r/HamRadio** - General ham radio discussion

### Buzzsprout (Weekly)
- Episode list with play counts
- Total plays and performance

### YouTube (Weekly)
- **Your channel:** Views, subscribers, video performance
- **Community trends:** What's hot in ham radio YouTube

## 🔐 Required Secrets

Set these in **Settings → Secrets → Actions**:

| Secret Name | Description |
|-------------|-------------|
| `BUZZSPROUT_API_TOKEN` | Your Buzzsprout API token |
| `YOUTUBE_API_KEY` | Google Cloud API key for YouTube Data API |

## ⚙️ Workflow Schedule

| Workflow | Schedule | What it does |
|----------|----------|--------------|
| **Daily News Fetch** | 6 AM ET daily | RSS feeds + Reddit |
| **Weekly Analytics** | 7 AM ET Mondays | Buzzsprout + YouTube |

## 🚀 Setup Instructions

1. **Add GitHub Secrets** (see above)
2. **Enable GitHub Actions** (should be automatic)
3. **Set workflow permissions:** Settings → Actions → General → "Read and write permissions"
4. **Run workflows manually** to test (Actions tab → select workflow → Run)
5. **Connect to Claude Project** via GitHub integration

## 🤖 Using with Claude

Connect this repository to a Claude Project for AI-assisted content planning:

1. Create a new project in Claude
2. Add the GitHub integration
3. Select this repository
4. Add custom instructions (see project setup)

Claude can then help you:
- Identify timely topics from news and Reddit
- Analyze what's performing well
- Suggest content based on trends
- Plan your content calendar

## 👥 Team

- **James (K8JKU)** - Host
- **Rory (W8KNX)** - Host
- **Jim (N8JRD)** - Host

---

*73 de The Everyday Ham Team*
