# The Everyday Ham - Content Pipeline

A content intelligence system for **The Everyday Ham** podcast and YouTube channel. This repository automatically aggregates amateur radio news, tracks performance analytics, monitors YouTube trends, and helps with content planning.

## 🎯 What This Does

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                                  │
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│  RSS Feeds   │  Buzzsprout  │  YOUR YouTube │  HAM RADIO YOUTUBE    │
│  (News)      │  (Podcast)   │  (Your stats) │  (Community trends)   │
│              │              │               │                       │
│ • ARRL       │ • Downloads  │ • Your views  │ • Trending videos     │
│ • QRZ        │ • Episodes   │ • Your subs   │ • Popular topics      │
│ • SWLing     │ • Trends     │ • Your growth │ • Rising channels     │
│ • AR Newsline│              │               │ • Content gaps        │
│ • OnAllBands │              │               │                       │
│ • K0NR       │              │               │                       │
│ • EtherHam   │              │               │                       │
└──────────────┴──────────────┴───────────────┴────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     THIS REPOSITORY                                  │
│                                                                      │
│  /news-summaries/     Fresh ham radio news (daily)                   │
│  /analytics/          Performance data (weekly)                      │
│  /calendar/           Content schedule & planning                    │
│  /episode-ideas/      Idea backlog & tracking                        │
│                                                                      │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CLAUDE PROJECT                                   │
│                                                                      │
│  Sync this repo → Get intelligent content suggestions based on:      │
│  • What's trending in ham radio                                      │
│  • What's working for YOUR audience                                  │
│  • What topics you haven't covered yet                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 📅 Content Schedule

| Content | Record | Publish | Frequency |
|---------|--------|---------|-----------|
| YouTube Video | Varies | **Thursdays** | Weekly |
| Audio Podcast | **1st Tuesday** | **1st Thursday** | Monthly |

## 🗂️ Repository Structure

```
everyday-ham-content/
├── .github/workflows/          # Automated actions
│   ├── daily-news.yml          # Runs daily @ 6 AM ET
│   └── weekly-analytics.yml    # Runs Mondays @ 7 AM ET
│
├── scripts/                    # Python scripts for data fetching
│   ├── fetch_rss.py
│   ├── fetch_buzzsprout.py
│   ├── fetch_youtube_stats.py
│   └── fetch_youtube_trends.py
│
├── news-summaries/             # Daily ham radio news
│   └── latest.md
│
├── analytics/
│   ├── buzzsprout/             # Podcast performance
│   └── youtube/                # YouTube performance + trends
│
├── calendar/                   # Content planning
│   ├── schedule.md
│   ├── youtube-queue.md
│   └── podcast-planning.md
│
├── episode-ideas/              # Idea tracking
│   ├── backlog.md
│   ├── audio-podcast.md
│   └── youtube.md
│
├── docs/
│   └── topics.md               # Categories & tags
│
├── config.json                 # YouTube search keywords
└── feeds.json                  # RSS feed sources
```

## 🔐 Required Secrets

Set these in **Settings → Secrets → Actions**:

| Secret Name | Description |
|-------------|-------------|
| `BUZZSPROUT_API_TOKEN` | Your Buzzsprout API token |
| `YOUTUBE_API_KEY` | Google Cloud API key for YouTube Data API |

## 🚀 Setup Instructions

1. **Add GitHub Secrets** (see above)
2. **Enable GitHub Actions** (should be automatic)
3. **Run workflows manually** to test (Actions tab → select workflow → Run)
4. **Connect to Claude Project** via GitHub integration

## 👥 Team

- James (K8JKU)
- Rory (W8KNX)  
- Jim (N8JRD)

---

*73 de The Everyday Ham Team*
