# Architecture

## Overview

DailyNewsBrief is a multi-agent pipeline orchestrated by LangGraph. Each agent is a discrete graph node responsible for one data domain. Claude Sonnet aggregates all outputs into a formatted HTML digest delivered via email.

---

## Full Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        Trigger Layer                              │
│                                                                   │
│   GitHub Actions cron          Local APScheduler daemon           │
│   (daily_brief.yml)            (scheduler.py)                     │
│         │                             │                           │
└─────────┼─────────────────────────────┼─────────────────────────┘
          │                             │
          └──────────────┬──────────────┘
                         ▼
                    main.py
                  load_preferences()
                  build initial state
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                     LangGraph StateGraph                          │
│                                                                   │
│   ┌─────────────┐                                                 │
│   │  tech_agent │  NewsAPI → filter → tech_news[]                 │
│   └──────┬──────┘                                                 │
│          │                                                        │
│          ▼                                                        │
│   ┌──────────────┐                                                │
│   │ sports_agent │  NewsAPI + TheSportsDB → sports_news[]         │
│   │              │                          sports_scores[]       │
│   └──────┬───────┘                                                │
│          │                                                        │
│          │  conditional edge                                      │
│          ├─── is_stock_day=True ──► ┌─────────────┐              │
│          │                          │ stock_agent │              │
│          │                          │ yfinance +  │              │
│          │                          │ AlphaVantage│              │
│          │                          └──────┬──────┘              │
│          │                                 │                      │
│          ├─── is_stock_day=False ───────────┘                    │
│          │                                                        │
│          ▼                                                        │
│   ┌───────────────────┐                                           │
│   │ aggregator_agent  │  Claude Sonnet 4.6                        │
│   │                   │  system prompt (cached)                   │
│   │                   │  → HTML digest                            │
│   └─────────┬─────────┘                                           │
│             │                                                     │
│             ▼                                                     │
│   ┌──────────────────┐                                            │
│   │  send_email node │  Jinja2 template → Resend API              │
│   └──────────────────┘                                            │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## LangGraph State

All agents read from and write to a shared `BriefState` TypedDict:

```
BriefState
├── preferences       dict      loaded from preferences.yaml
├── tech_news         list      articles from NewsAPI
├── sports_news       list      articles from NewsAPI
├── sports_scores     list      last results from TheSportsDB
├── stock_data        list      price/RSI/MA data + news per ticker
├── digest            str       Claude-generated HTML
├── email_sent        bool
├── is_stock_day      bool      True on stock_day (default: Friday)
└── errors            list      non-fatal errors from any agent
```

---

## Agent Details

### tech_agent
- Queries NewsAPI `/everything` with topics from `preferences.yaml`
- Filters out removed/null articles
- Writes to `state.tech_news`

### sports_agent
- Queries NewsAPI `/everything` with team + sport names
- Queries TheSportsDB `/eventslast.php` per followed team for scores
- Writes to `state.sports_news` and `state.sports_scores`

### stock_agent *(Fridays only)*
- Fetches 1-year price history via `yfinance`
- Computes RSI (14-period), MA50, MA200 locally
- Fetches sentiment-tagged news from Alpha Vantage
- Writes to `state.stock_data`

### aggregator_agent
- Serialises all state data as JSON into an LLM prompt
- Calls Claude Sonnet 4.6 with an ephemeral-cached system prompt
- Claude returns a structured HTML digest
- Writes to `state.digest`

### send_email (delivery node)
- Renders `templates/email_template.html` via Jinja2
- Dispatches via Resend with retry (3 attempts, exponential backoff)
- Writes `state.email_sent`

---

## Conditional Routing

```python
# graph/orchestrator.py
def _route_after_sports(state):
    return "stock_agent" if state["is_stock_day"] else "aggregator"
```

`is_stock_day` is resolved at runtime in `main.py` by comparing today's weekday against `preferences.yaml → email.stock_day`.

---

## Resilience

| Layer | Strategy |
|---|---|
| HTTP tools (news, sports, stocks) | `@http_retry` — tenacity, 3 attempts, 2→8s exponential backoff |
| Email delivery | `@retry` — tenacity, 3 attempts, 2→8s exponential backoff |
| Agent errors | Caught per-agent, appended to `state.errors`, pipeline continues |
| Email errors | Caught, `state.email_sent = False`, errors surfaced in logs |

---

## Preferences & Personalisation

`preferences.yaml` is the single source of truth for what gets fetched. Managed via `manage.py` CLI or direct file edit:

```
preferences.yaml
├── tech_topics[]       fed into NewsAPI query
├── sports[]
│   ├── sport           fed into NewsAPI query
│   └── teams[]         fed into TheSportsDB + NewsAPI query
├── stocks[]            fed into yfinance + Alpha Vantage
└── email
    ├── send_time       used by local scheduler.py
    ├── timezone        used by local scheduler.py
    └── stock_day       determines is_stock_day flag
```

---

## Deployment Options

| Mode | How | Scheduling |
|---|---|---|
| GitHub Actions | Push to `master`, add 6 secrets | Cron in `daily_brief.yml` (UTC, no DST) |
| Local daemon | `python scheduler.py` | APScheduler, timezone-aware, DST-safe |
| One-shot | `python main.py` or `python scheduler.py --now` | Manual |
