import os
from datetime import date

import resend
from jinja2 import Environment, FileSystemLoader

from config import EMAIL_FROM, EMAIL_TO, RESEND_API_KEY
from graph.state import BriefState

resend.api_key = RESEND_API_KEY

_templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
_jinja_env = Environment(loader=FileSystemLoader(_templates_dir))


def send_email_node(state: BriefState) -> BriefState:
    today = date.today().strftime("%A, %B %d, %Y")
    is_stock_day = state.get("is_stock_day", False)

    template = _jinja_env.get_template("email_template.html")
    html = template.render(
        date=today,
        digest=state.get("digest", ""),
        errors=state.get("errors", []),
    )

    subject = f"Weekly Brief + Stock Analysis — {today}" if is_stock_day else f"Daily Brief — {today}"

    try:
        resend.Emails.send({
            "from": EMAIL_FROM,
            "to": EMAIL_TO,
            "subject": subject,
            "html": html,
        })
        state["email_sent"] = True
    except Exception as e:
        state["errors"].append(f"email send error: {e}")
        state["email_sent"] = False

    return state
