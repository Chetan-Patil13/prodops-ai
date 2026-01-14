from typing import TypedDict, Optional, Any, List, Dict


class AgentState(TypedDict):
    user_id: int
    roles: List[str]
    input: str
    intent: Optional[str]
    tool_result: Optional[Any]
    response: Optional[str]
    memory: Dict
    retrieved_docs: Optional[list]
