from langgraph.graph import StateGraph, END
from app.llm.state import AgentState
from app.llm.nodes import (
    classify_intent,
    handle_production,
    handle_downtime,
    handle_ticket,
    format_response,
)


def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("production", handle_production)
    graph.add_node("downtime", handle_downtime)
    graph.add_node("ticket", handle_ticket)
    graph.add_node("format", format_response)

    # Edges
    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        lambda state: state["intent"],
        {
            "PRODUCTION_QUERY": "production",
            "DOWNTIME_QUERY": "downtime",
            "CREATE_TICKET": "ticket",
            "UNKNOWN": "format",
        },
    )

    graph.add_edge("production", "format")
    graph.add_edge("downtime", "format")
    graph.add_edge("ticket", "format")
    graph.add_edge("format", END)

    return graph.compile()
