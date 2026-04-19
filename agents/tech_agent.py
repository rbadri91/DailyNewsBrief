from graph.state import BriefState
from tools.news_tools import fetch_tech_news


def tech_agent(state: BriefState) -> BriefState:
    topics = state["preferences"].get("tech_topics", [])
    try:
        articles = fetch_tech_news(topics, page_size=10)
        state["tech_news"] = [
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
        state["errors"].append(f"tech_agent error: {e}")
        state["tech_news"] = []
    return state
