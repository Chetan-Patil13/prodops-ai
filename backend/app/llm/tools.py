from langchain.tools import tool
from app.services.production_service import get_daily_production_summary
from app.services.downtime_service import get_downtime_summary
from app.services.ticket_service import create_ticket
import json


@tool
def production_summary(line_code: str, date: str) -> str:
    """Get daily production summary for a line."""
    result = get_daily_production_summary(line_code, date)
    return json.dumps(result, default=str)


@tool
def downtime_summary(line_code: str, date: str) -> str:
    """Get downtime summary for a line."""
    result = get_downtime_summary(line_code, date)
    return json.dumps(result, default=str)


@tool
def create_maintenance_ticket(
    line_code: str,
    issue: str,
    severity: str,
    user_id: int,
) -> str:
    """Create a maintenance ticket."""
    result = create_ticket(
        line_code=line_code,
        issue_summary=issue,
        severity=severity,
        created_by_user_id=user_id,
    )
    return json.dumps(result, default=str)
