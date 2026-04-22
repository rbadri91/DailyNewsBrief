from datetime import date, timedelta

from graph.state import BriefState
from tools.news_tools import fetch_sports_news
from tools.sports_tools import fetch_team_last_result

_MAX_SCORE_AGE_DAYS = 10


def sports_agent(state: BriefState) -> dict:
    sports_prefs = state["preferences"].get("sports", [])

    all_teams = []
    all_sports = []
    for item in sports_prefs:
        all_sports.append(item["sport"])
        all_teams.extend(item.get("teams", []))

    errors = []

    try:
        articles = fetch_sports_news(all_teams, all_sports, page_size=10)
        sports_news = [
            {
                "title": a["title"],
                "description": a.get("description", ""),
                "url": a["url"],
                "source": a["source"]["name"],
                "published_at": a["publishedAt"],
            }
            for a in articles
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]
    except Exception as e:
        errors.append(f"sports_agent news error: {e}")
        sports_news = []

    cutoff = date.today() - timedelta(days=_MAX_SCORE_AGE_DAYS)
    scores = []
    for team in all_teams:
        try:
            last = fetch_team_last_result(team)
            if not last:
                continue
            event_date_str = last.get("dateEvent", "")
            try:
                event_date = date.fromisoformat(event_date_str)
            except (ValueError, TypeError):
                event_date = None
            if event_date and event_date < cutoff:
                continue
            scores.append({
                "team": team,
                "event": last.get("strEvent", ""),
                "date": event_date_str,
                "home_score": last.get("intHomeScore", ""),
                "away_score": last.get("intAwayScore", ""),
                "won": _did_team_win(team, last),
            })
        except Exception as e:
            errors.append(f"sports_agent scores error for {team}: {e}")

    result = {"sports_news": sports_news, "sports_scores": scores}
    if errors:
        result["errors"] = errors
    return result


def _did_team_win(team_name: str, event: dict) -> bool:
    home = event.get("strHomeTeam", "")
    home_score = int(event.get("intHomeScore") or 0)
    away_score = int(event.get("intAwayScore") or 0)
    if team_name.lower() in home.lower():
        return home_score > away_score
    return away_score > home_score
