import json
from datetime import date

import anthropic

from config import ANTHROPIC_API_KEY
from graph.state import BriefState

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Cached: static across every daily run — saves ~$0.03/day on cache hits.
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
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": "\n\n".join(sections)}],
    )

    cache_stats = response.usage
    print(
        f"Claude usage — input: {cache_stats.input_tokens}, "
        f"cache_read: {getattr(cache_stats, 'cache_read_input_tokens', 0)}, "
        f"cache_write: {getattr(cache_stats, 'cache_creation_input_tokens', 0)}, "
        f"output: {cache_stats.output_tokens}"
    )

    state["digest"] = response.content[0].text
    return state
