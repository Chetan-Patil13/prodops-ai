from langchain_openai import ChatOpenAI
from app.llm.state import AgentState

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
    prompt = INTENT_PROMPT.format(input=state["input"])
    intent = llm.invoke(prompt).content.strip()
    state["intent"] = intent
    return state


from app.services.production_service import get_daily_production_summary
from app.services.downtime_service import get_downtime_summary
from app.services.ticket_service import create_ticket


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

    if not state.get("tool_result"):
        state["response"] = "I could not process your request."
        return state

    state["response"] = str(state["tool_result"])
    return state
