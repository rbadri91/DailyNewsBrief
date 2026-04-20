# DailyNewsBrief

A multi-agent news briefing tool that sends a personalized daily email digest covering tech news, sports scores, and weekly stock analysis — built with LangGraph, Claude AI, and GitHub Actions.

## What it does

- **Daily email** — top tech stories + sports scores/news for your followed teams, delivered every morning
- **Weekly stock analysis** (Fridays) — RSI, moving averages, and buy/hold/watch signals for your watchlist
- **Fully personalized** — follow/unfollow topics, sports, teams, and stocks via a CLI
- **Automated** — runs on a cron schedule via GitHub Actions; no server required

## Architecture

```
GitHub Actions (cron)
        │
        ▼
┌─────────────────────────────────────┐
│         LangGraph Orchestrator       │
│                                      │
│  Tech Agent → Sports Agent ──────┐  │
│                                   ▼  │
│              [Friday only]        │  │
│  Stock Agent ─────────────────────┤  │
│                                   ▼  │
│              Aggregator Agent        │
│           (Claude Sonnet 4.6)        │
└─────────────────┬───────────────────┘
                  │
                  ▼
           Resend (email)
```

## Tech Stack

| Component | Tool |
|---|---|
| Orchestration | LangGraph |
| LLM | Claude Sonnet 4.6 (Anthropic) |
| Tech + Sports news | NewsAPI |
| Sports scores | TheSportsDB (free, no key) |
| Stock data | yfinance (Yahoo Finance) |
| Stock news | Alpha Vantage |
| Email delivery | Resend |
| Scheduler | GitHub Actions cron / APScheduler (local) |
| Preferences | `preferences.yaml` (committed to repo) |

## Project Structure

```
DailyNewsBrief/
├── agents/
│   ├── tech_agent.py          # Fetches and filters tech news
│   ├── sports_agent.py        # Fetches sports news + last results per team
│   ├── stock_agent.py         # Fetches price data + RSI/MA + news
│   └── aggregator_agent.py    # Summarises everything via Claude
├── graph/
│   ├── state.py               # LangGraph state definition
│   └── orchestrator.py        # Graph wiring + conditional stock edge
├── tools/
│   ├── news_tools.py          # NewsAPI wrappers
│   ├── sports_tools.py        # TheSportsDB wrappers
│   ├── stock_tools.py         # yfinance + Alpha Vantage wrappers
│   └── retry.py               # Shared tenacity retry decorator
├── delivery/
│   └── email_sender.py        # Jinja2 render + Resend dispatch
├── templates/
│   └── email_template.html    # Responsive HTML email template
├── .github/
│   ├── workflows/
│   │   ├── daily_brief.yml    # Cron workflow (10am EST daily)
│   │   └── codeql.yml         # Code scanning on every PR
│   └── dependabot.yml         # Weekly dependency updates
├── preferences.yaml           # Your followed topics/teams/stocks
├── manage.py                  # CLI to follow/unfollow preferences
├── scheduler.py               # Local APScheduler daemon
├── main.py                    # Pipeline entry point
└── requirements.txt
```

## Setup

### 1. Clone and install

```bash
git clone https://github.com/rbadri91/DailyNewsBrief.git
cd DailyNewsBrief
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```
ANTHROPIC_API_KEY=...
NEWSAPI_KEY=...
ALPHA_VANTAGE_KEY=...
RESEND_API_KEY=...
EMAIL_FROM=briefing@yourdomain.com
EMAIL_TO=you@email.com
```

| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `NEWSAPI_KEY` | [newsapi.org](https://newsapi.org) — free tier |
| `ALPHA_VANTAGE_KEY` | [alphavantage.co](https://www.alphavantage.co) — free tier |
| `RESEND_API_KEY` | [resend.com](https://resend.com) — free tier |

### 3. Customise preferences

Edit `preferences.yaml` directly, or use the CLI:

```bash
python manage.py list

python manage.py follow topic "Nvidia"
python manage.py unfollow topic "startups"

python manage.py follow sport "Cricket"
python manage.py follow team "India" --sport Cricket
python manage.py unfollow team "Lakers"

python manage.py follow stock "AAPL"
python manage.py unfollow stock "TSLA"
```

### 4. Run locally

```bash
# Run once immediately
python main.py

# Or run via the local scheduler daemon (reads send_time from preferences.yaml)
python scheduler.py        # starts daemon, Ctrl+C to stop
python scheduler.py --now  # run once and exit
```

## GitHub Actions (automated)

Add these secrets to your repo under **Settings → Secrets → Actions**:

`ANTHROPIC_API_KEY` · `NEWSAPI_KEY` · `ALPHA_VANTAGE_KEY` · `RESEND_API_KEY` · `EMAIL_FROM` · `EMAIL_TO`

The workflow runs daily at **10am EST** via cron. Trigger it manually anytime from the **Actions** tab using `workflow_dispatch`.

> **Note:** GitHub Actions cron runs in UTC and does not adjust for daylight saving. The brief fires at 10am EST (Nov–Mar) and 11am EDT (Mar–Nov). Use the local `scheduler.py` daemon for exact local-time scheduling.

## Cost

Running daily, the estimated API spend is **~$0.02–0.05/day**:

- Claude Sonnet 4.6 with prompt caching for repeated system prompt tokens
- NewsAPI, TheSportsDB, yfinance: free tiers
- Alpha Vantage: free tier (25 req/day — sufficient for weekly stock runs)
- Resend: free tier (100 emails/day)
- GitHub Actions: free for public repos

## Contributing

All changes go through pull requests targeting `master`. Dependabot opens weekly PRs for dependency updates.
