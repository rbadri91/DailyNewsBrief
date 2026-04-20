import requests
from config import NEWSAPI_KEY
from tools.retry import http_retry

NEWSAPI_BASE = "https://newsapi.org/v2"


@http_retry
def fetch_tech_news(topics: list[str], page_size: int = 10) -> list[dict]:
    query = " OR ".join(topics)
    resp = requests.get(
        f"{NEWSAPI_BASE}/everything",
        params={
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": NEWSAPI_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("articles", [])


@http_retry
def fetch_sports_news(teams: list[str], sports: list[str], page_size: int = 10) -> list[dict]:
    query_parts = teams + sports
    query = " OR ".join(query_parts)
    resp = requests.get(
        f"{NEWSAPI_BASE}/everything",
        params={
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": NEWSAPI_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("articles", [])
