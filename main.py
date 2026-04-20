import os
import time
import yaml
from datetime import date

from graph.orchestrator import build_graph
from graph.state import BriefState


def load_preferences() -> dict:
    prefs_path = os.path.join(os.path.dirname(__file__), "preferences.yaml")
    with open(prefs_path) as f:
        return yaml.safe_load(f)


def is_stock_day(prefs: dict) -> bool:
    stock_day = prefs.get("email", {}).get("stock_day", "Sunday")
    return date.today().strftime("%A") == stock_day


def run():
    prefs = load_preferences()

    initial_state: BriefState = {
        "preferences": prefs,
        "tech_news": [],
        "sports_news": [],
        "sports_scores": [],
        "stock_data": [],
        "digest": "",
        "email_sent": False,
        "is_stock_day": is_stock_day(prefs),
        "errors": [],
    }

    print(f"Running daily brief (stock day: {initial_state['is_stock_day']})")
    graph = build_graph()

    start = time.perf_counter()
    final_state = graph.invoke(initial_state)
    elapsed = time.perf_counter() - start

    print(f"Email sent: {final_state['email_sent']}")
    print(f"Pipeline completed in {elapsed:.1f}s")
    if final_state["errors"]:
        print("Errors encountered:")
        for err in final_state["errors"]:
            print(f"  - {err}")


if __name__ == "__main__":
    run()
