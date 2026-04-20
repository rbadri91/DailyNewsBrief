from langgraph.graph import END, START, StateGraph

from agents.aggregator_agent import aggregator_agent
from agents.sports_agent import sports_agent
from agents.stock_agent import stock_agent
from agents.tech_agent import tech_agent
from delivery.email_sender import send_email_node
from graph.state import BriefState


def _route(_state) -> dict:
    """Fan-in node: waits for all parallel branches, then passes through."""
    return {}


def _decide_next(state: BriefState) -> str:
    return "stock_agent" if state.get("is_stock_day") else "aggregator"


def build_graph():
    graph = StateGraph(BriefState)

    graph.add_node("tech_agent", tech_agent)
    graph.add_node("sports_agent", sports_agent)
    graph.add_node("stock_agent", stock_agent)
    graph.add_node("aggregator", aggregator_agent)
    graph.add_node("send_email", send_email_node)
    graph.add_node("route", _route)

    # Fan-out: tech and sports run in parallel from the start
    graph.add_edge(START, "tech_agent")
    graph.add_edge(START, "sports_agent")

    # Fan-in: route node waits for both to complete
    graph.add_edge("tech_agent", "route")
    graph.add_edge("sports_agent", "route")

    # Conditional routing after fan-in
    graph.add_conditional_edges(
        "route",
        _decide_next,
        {"stock_agent": "stock_agent", "aggregator": "aggregator"},
    )
    graph.add_edge("stock_agent", "aggregator")
    graph.add_edge("aggregator", "send_email")
    graph.add_edge("send_email", END)

    return graph.compile()
