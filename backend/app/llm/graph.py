from langgraph.graph import StateGraph, END

from app.llm.state import AgentState
from app.llm.nodes import (
    load_memory,
    classify_intent,
    handle_production,
    handle_downtime,
    handle_ticket,
    format_response,
    persist_memory,
    retrieve_knowledge
)


def build_graph():
    """
    Builds the LangGraph workflow for ProdOps AI.
    This graph supports:
    - Intent classification
    - Tool-based execution
    - Role-based guardrails
    - Persistent memory across sessions
    """

    graph = StateGraph(AgentState)

    # -------------------------
    # Nodes
    # -------------------------
    graph.add_node("load_memory", load_memory)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("production", handle_production)
    graph.add_node("downtime", handle_downtime)
    graph.add_node("ticket", handle_ticket)
    graph.add_node("format", format_response)
    graph.add_node("persist_memory", persist_memory)
    graph.add_node("retrieve_knowledge", retrieve_knowledge)

    # -------------------------
    # Entry point
    # -------------------------
    graph.set_entry_point("load_memory")

    # -------------------------
    # Edges
    # -------------------------
    graph.add_edge("load_memory", "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        lambda state: state.get("intent"),
        {
            "PRODUCTION_QUERY": "production",
            "DOWNTIME_QUERY": "downtime",
            "CREATE_TICKET": "ticket",
            "UNKNOWN": "retrieve_knowledge",
        },
    )
    
    graph.add_edge("production", "format")
    graph.add_edge("downtime", "format")
    graph.add_edge("ticket", "format")
    graph.add_edge("retrieve_knowledge", "format")
    graph.add_edge("format", "persist_memory")
    graph.add_edge("persist_memory", END)

    return graph.compile()
