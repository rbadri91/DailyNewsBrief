import requests
import yfinance as yf
from config import ALPHA_VANTAGE_KEY
from tools.retry import http_retry


def fetch_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    info = stock.info

    current_price = float(hist["Close"].iloc[-1]) if not hist.empty else None
    year_high = float(hist["Close"].max()) if not hist.empty else None
    year_low = float(hist["Close"].min()) if not hist.empty else None

    rsi = None
    if len(hist) >= 14:
        delta = hist["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = round(float((100 - (100 / (1 + rs))).iloc[-1]), 2)

    ma50 = round(float(hist["Close"].rolling(50).mean().iloc[-1]), 2) if len(hist) >= 50 else None
    ma200 = round(float(hist["Close"].rolling(200).mean().iloc[-1]), 2) if len(hist) >= 200 else None

    return {
        "ticker": ticker,
        "name": info.get("longName", ticker),
        "current_price": round(current_price, 2) if current_price else None,
        "52_week_high": round(year_high, 2) if year_high else None,
        "52_week_low": round(year_low, 2) if year_low else None,
        "rsi": rsi,
        "ma50": ma50,
        "ma200": ma200,
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
    }


@http_retry
def fetch_stock_news(ticker: str) -> list[dict]:
    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "limit": 5,
            "apikey": ALPHA_VANTAGE_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("feed", [])
