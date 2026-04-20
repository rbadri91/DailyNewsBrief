import requests
from tools.retry import http_retry

SPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"


@http_retry
def _get(url: str, params: dict) -> dict:
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_team_last_result(team_name: str) -> dict | None:
    data = _get(f"{SPORTSDB_BASE}/searchteams.php", {"t": team_name})
    teams = data.get("teams")
    if not teams:
        return None
    team_id = teams[0]["idTeam"]

    results = _get(f"{SPORTSDB_BASE}/eventslast.php", {"id": team_id}).get("results", [])
    return results[0] if results else None


def fetch_team_next_event(team_name: str) -> dict | None:
    data = _get(f"{SPORTSDB_BASE}/searchteams.php", {"t": team_name})
    teams = data.get("teams")
    if not teams:
        return None
    team_id = teams[0]["idTeam"]

    events = _get(f"{SPORTSDB_BASE}/eventsnext.php", {"id": team_id}).get("events", [])
    return events[0] if events else None
