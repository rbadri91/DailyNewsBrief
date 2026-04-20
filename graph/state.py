import operator
from typing import Annotated, TypedDict


class BriefState(TypedDict):
    preferences: dict
    tech_news: list
    sports_news: list
    sports_scores: list
    stock_data: list
    digest: str
    email_sent: bool
    is_stock_day: bool
    # Annotated reducer merges error lists from parallel agents instead of overwriting
    errors: Annotated[list, operator.add]
