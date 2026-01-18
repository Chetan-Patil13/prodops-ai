from fastapi import APIRouter, Depends, HTTPException, Request
from app.auth.dependencies import get_current_user
from app.llm.graph import build_graph
from app.middleware.rate_limiter import chat_rate_limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


@router.post("/")
def chat(
    message: str, 
    request: Request,
    current_user=Depends(get_current_user)
):
    # Rate limiting
    client_id = f"user_{current_user['user_id']}"
    if not chat_rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please slow down."
        )
    
    # Input validation
    if not message or len(message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if len(message) > 1000:
        raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")
    
    # Log request
    logger.info(f"Chat request from user {current_user['user_id']}: {message[:50]}...")
    
    try:
        graph = get_graph()

        state = {
            "user_id": current_user["user_id"],
            "roles": current_user["roles"],
            "input": message,
            "intent": None,
            "tool_result": None,
            "response": None,
            "memory": {},
            "retrieved_docs": None,
        }

        final_state = graph.invoke(state)
        
        # Log response
        logger.info(f"Chat response sent to user {current_user['user_id']}")
        
        return {"reply": final_state["response"]}
    
    except Exception as e:
        logger.error(f"Chat error for user {current_user['user_id']}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred processing your request")