from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.llm.graph import build_graph

router = APIRouter(prefix="/chat", tags=["Chat"])

_graph = None  # lazy-loaded singleton


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


@router.post("/")
def chat(message: str, current_user=Depends(get_current_user)):
    graph = get_graph()

    state = {
        "user_id": current_user["user_id"],
        "roles": current_user["roles"],
        "input": message,
        "intent": None,
        "tool_result": None,
        "response": None,
    }

    final_state = graph.invoke(state)
    return {"reply": final_state["response"]}
