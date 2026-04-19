from graph.state import BriefState
from tools.news_tools import fetch_sports_news
from tools.sports_tools import fetch_team_last_result


def sports_agent(state: BriefState) -> BriefState:
    sports_prefs = state["preferences"].get("sports", [])

    all_teams = []
    all_sports = []
    for item in sports_prefs:
        all_sports.append(item["sport"])
        all_teams.extend(item.get("teams", []))

    try:
        articles = fetch_sports_news(all_teams, all_sports, page_size=10)
        state["sports_news"] = [
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
        state["errors"].append(f"sports_agent news error: {e}")
        state["sports_news"] = []

    scores = []
    for team in all_teams:
        try:
            last = fetch_team_last_result(team)
            if last:
                scores.append({
                    "team": team,
                    "event": last.get("strEvent", ""),
                    "date": last.get("dateEvent", ""),
                    "home_score": last.get("intHomeScore", ""),
                    "away_score": last.get("intAwayScore", ""),
                    "won": _did_team_win(team, last),
                })
        except Exception as e:
            state["errors"].append(f"sports_agent scores error for {team}: {e}")

    state["sports_scores"] = scores
    return state


def _did_team_win(team_name: str, event: dict) -> bool:
    home = event.get("strHomeTeam", "")
    home_score = int(event.get("intHomeScore") or 0)
    away_score = int(event.get("intAwayScore") or 0)
    if team_name.lower() in home.lower():
        return home_score > away_score
    return away_score > home_score
