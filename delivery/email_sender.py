import os
from datetime import date

import resend
from jinja2 import Environment, FileSystemLoader
from tenacity import retry, stop_after_attempt, wait_exponential

from config import EMAIL_FROM, EMAIL_TO, RESEND_API_KEY
from graph.state import BriefState

resend.api_key = RESEND_API_KEY

_templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
_jinja_env = Environment(loader=FileSystemLoader(_templates_dir))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8), reraise=True)
def _send(subject: str, html: str):
    resend.Emails.send({"from": EMAIL_FROM, "to": EMAIL_TO, "subject": subject, "html": html})


def send_email_node(state: BriefState) -> dict:
    today = date.today().strftime("%A, %B %d, %Y")
    is_stock_day = state.get("is_stock_day", False)

    template = _jinja_env.get_template("email_template.html")
    html = template.render(
        date=today,
        digest=state.get("digest", ""),
        is_stock_day=is_stock_day,
        errors=state.get("errors", []),
    )

    subject = f"Weekly Brief + Stock Analysis — {today}" if is_stock_day else f"Daily Brief — {today}"

    try:
        _send(subject, html)
        return {"email_sent": True}
    except Exception as e:
        return {"email_sent": False, "errors": [f"email send error: {e}"]}
