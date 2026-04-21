from graph.state import BriefState
from tools.stock_tools import fetch_stock_data, fetch_stock_news


def stock_agent(state: BriefState) -> dict:
    tickers = state["preferences"].get("stocks", [])
    stock_data = []
    errors = []

    for ticker in tickers:
        try:
            data = fetch_stock_data(ticker)
            news = fetch_stock_news(ticker)
            data["news"] = [
                {"title": n.get("title"), "url": n.get("url"), "sentiment": n.get("overall_sentiment_label")}
                for n in news[:3]
            ]
            stock_data.append(data)
        except Exception as e:
            errors.append(f"stock_agent error for {ticker}: {e}")

    result = {"stock_data": stock_data}
    if errors:
        result["errors"] = errors
    return result
