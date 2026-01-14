from langchain_openai import ChatOpenAI
from app.llm.state import AgentState
from pathlib import Path
import os
from dotenv import load_dotenv
 
# Load env file (same logic as seed_data.py)
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env.example"
load_dotenv(env_path)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

INTENT_PROMPT = """
Classify the user intent into ONE of the following:
- PRODUCTION_QUERY
- DOWNTIME_QUERY
- CREATE_TICKET
- UNKNOWN

User message:
{input}

Return ONLY the intent label.
"""


def classify_intent(state: AgentState) -> AgentState:
    context_hint = ""
    if state.get("memory"):
        context_hint = f"""
Previous context:
{state["memory"]}
"""

    prompt = INTENT_PROMPT.format(input=state["input"]) + context_hint
    intent = llm.invoke(prompt).content.strip()
    state["intent"] = intent
    return state



from app.services.production_service import get_daily_production_summary
from app.services.downtime_service import get_downtime_summary
from app.services.ticket_service import create_ticket
from app.services.memory_service import load_user_memory, save_user_memory
from app.rag.retriever import retrieve_docs



def handle_production(state: AgentState) -> AgentState:
    # NOTE: In real system, extract date/line via NLP or defaults
    result = get_daily_production_summary("LINE-1", "2026-01-10")
    state["tool_result"] = result
    return state


def handle_downtime(state: AgentState) -> AgentState:
    result = get_downtime_summary("LINE-1", "2026-01-10")
    state["tool_result"] = result
    return state


def handle_ticket(state: AgentState) -> AgentState:
    if "SUPERVISOR" not in state["roles"]:
        state["response"] = "You are not authorized to create tickets."
        return state

    ticket = create_ticket(
        line_code="LINE-1",
        issue_summary=state["input"],
        severity="High",
        created_by_user_id=state["user_id"],
    )
    state["tool_result"] = ticket
    return state


def format_response(state: AgentState) -> AgentState:
    if state.get("response"):
        return state

    if state.get("retrieved_docs"):
        content = "\n\n".join([d.page_content for d in state["retrieved_docs"]])
        state["response"] = f"Based on SOPs:\n\n{content}"
        return state

    if state.get("tool_result"):
        state["response"] = str(state["tool_result"])
        return state

    state["response"] = "I could not find relevant information."
    return state




def load_memory(state: AgentState) -> AgentState:
    memory = load_user_memory(state["user_id"])
    state["memory"] = memory
    return state


def persist_memory(state: AgentState) -> AgentState:
    memory = state.get("memory", {})

    # Update memory intelligently
    memory.update(
        {
            "last_intent": state.get("intent"),
            "last_issue": state.get("input"),
        }
    )

    save_user_memory(state["user_id"], memory)
    return state

def retrieve_knowledge(state: AgentState) -> AgentState:
    docs = retrieve_docs(state["input"])
    state["retrieved_docs"] = docs
    return state