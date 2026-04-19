import json
from datetime import date

import anthropic

from config import ANTHROPIC_API_KEY
from graph.state import BriefState

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are creating a personalized daily news briefing digest.
Format your response as clean HTML suitable for an email body (no <html>/<body>/<head> tags).
Use <h2> for section headings, <ul>/<li> for article lists, <a href="..."> for links.
Be concise but informative. Write in a friendly, newsletter tone."""


def aggregator_agent(state: BriefState) -> BriefState:
    is_stock_day = state.get("is_stock_day", False)
    today = date.today().strftime("%A, %B %d, %Y")

    sections = [
        f"Today is {today}. Summarize the following data into a digest.\n",
        f"<TECH_NEWS>\n{json.dumps(state.get('tech_news', []), indent=2)}\n</TECH_NEWS>",
        f"<SPORTS_NEWS>\n{json.dumps(state.get('sports_news', []), indent=2)}\n</SPORTS_NEWS>",
        f"<SPORTS_SCORES>\n{json.dumps(state.get('sports_scores', []), indent=2)}\n</SPORTS_SCORES>",
    ]

    if is_stock_day:
        sections.append(
            f"<STOCK_DATA>\n{json.dumps(state.get('stock_data', []), indent=2)}\n</STOCK_DATA>\n"
            "Include a stock section with buy/hold/watch signals based on RSI and MA crossovers. "
            "Label clearly as informational only, not financial advice."
        )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "\n\n".join(sections)}],
    )

    state["digest"] = response.content[0].text
    return state
