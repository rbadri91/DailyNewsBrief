from graph.state import BriefState
from tools.news_tools import fetch_tech_news


def tech_agent(state: BriefState) -> dict:
    topics = state["preferences"].get("tech_topics", [])
    try:
        articles = fetch_tech_news(topics, page_size=10)
        return {
            "tech_news": [
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
        }
    except Exception as e:
        return {"tech_news": [], "errors": [f"tech_agent error: {e}"]}
