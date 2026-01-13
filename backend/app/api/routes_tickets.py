from fastapi import APIRouter
from app.services.ticket_service import create_ticket, get_ticket_by_number
from fastapi import Depends, HTTPException
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/")
def create_ticket_api(
    line_code: str,
    issue: str,
    severity: str,
    current_user=Depends(get_current_user),
):
    if "SUPERVISOR" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return create_ticket(
        line_code=line_code,
        issue_summary=issue,
        severity=severity,
        created_by_user_id=current_user["user_id"],
    )



@router.get("/{ticket_no}")
def get_ticket(ticket_no: str):
    return get_ticket_by_number(ticket_no)
