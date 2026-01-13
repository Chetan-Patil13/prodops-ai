from typing import TypedDict, Optional, Any, List


class AgentState(TypedDict):
    user_id: int
    roles: List[str]
    input: str
    intent: Optional[str]
    tool_result: Optional[Any]
    response: Optional[str]
