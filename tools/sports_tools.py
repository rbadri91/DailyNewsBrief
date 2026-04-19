import requests

SPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"


def fetch_team_last_result(team_name: str) -> dict | None:
    resp = requests.get(
        f"{SPORTSDB_BASE}/searchteams.php",
        params={"t": team_name},
        timeout=10,
    )
    resp.raise_for_status()
    teams = resp.json().get("teams")
    if not teams:
        return None
    team_id = teams[0]["idTeam"]

    results_resp = requests.get(
        f"{SPORTSDB_BASE}/eventslast.php",
        params={"id": team_id},
        timeout=10,
    )
    results_resp.raise_for_status()
    results = results_resp.json().get("results", [])
    return results[0] if results else None


def fetch_team_next_event(team_name: str) -> dict | None:
    resp = requests.get(
        f"{SPORTSDB_BASE}/searchteams.php",
        params={"t": team_name},
        timeout=10,
    )
    resp.raise_for_status()
    teams = resp.json().get("teams")
    if not teams:
        return None
    team_id = teams[0]["idTeam"]

    next_resp = requests.get(
        f"{SPORTSDB_BASE}/eventsnext.php",
        params={"id": team_id},
        timeout=10,
    )
    next_resp.raise_for_status()
    events = next_resp.json().get("events", [])
    return events[0] if events else None
