from fastapi import APIRouter
from app.services.ticket_service import create_ticket, get_ticket_by_number

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/")
def create_ticket_api(
    line_code: str,
    issue: str,
    severity: str,
    created_by_user_id: int,
):
    return create_ticket(
        line_code=line_code,
        issue_summary=issue,
        severity=severity,
        created_by_user_id=created_by_user_id,
    )


@router.get("/{ticket_no}")
def get_ticket(ticket_no: str):
    return get_ticket_by_number(ticket_no)
