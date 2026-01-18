from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import (
    get_current_user, 
    supervisor_only, 
    maintenance_or_supervisor
)
from app.services.ticket_service import (
    create_ticket,
    get_ticket_by_number,
    get_all_tickets,
    get_ticket_stats,
    update_ticket_status
)
from pydantic import BaseModel, validator
import re

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# Request models with validation
class CreateTicketRequest(BaseModel):
    line_code: str
    issue: str
    severity: str
    
    @validator('line_code')
    def validate_line_code(cls, v):
        if not re.match(r'^LINE-[A-Z0-9]+$', v):
            raise ValueError('Invalid line_code format. Must be LINE-XXX')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        valid = ['Low', 'Medium', 'High', 'Critical']
        if v not in valid:
            raise ValueError(f'Severity must be one of: {valid}')
        return v
    
    @validator('issue')
    def validate_issue(cls, v):
        if len(v) < 10:
            raise ValueError('Issue description must be at least 10 characters')
        if len(v) > 500:
            raise ValueError('Issue description must be less than 500 characters')
        return v


class UpdateTicketStatusRequest(BaseModel):
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        valid = ['OPEN', 'IN_PROGRESS', 'CLOSED']
        if v not in valid:
            raise ValueError(f'Status must be one of: {valid}')
        return v


# Create ticket (Supervisors only)
@router.post("/")
def create_ticket_api(
    payload: CreateTicketRequest,
    current_user=Depends(supervisor_only),
):
    return create_ticket(
        line_code=payload.line_code,
        issue_summary=payload.issue,
        severity=payload.severity,
        created_by_user_id=current_user["user_id"],
    )


# Get all tickets (Any authenticated user)
@router.get("/")
def list_tickets(
    limit: int = 50,
    status: str = None,
    current_user=Depends(get_current_user)
):
    # Validate limit
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    # Validate status if provided
    if status and status not in ['OPEN', 'IN_PROGRESS', 'CLOSED']:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    
    return get_all_tickets(limit=limit, status=status)


# Get ticket statistics (Any authenticated user)
@router.get("/stats")
def ticket_statistics(current_user=Depends(get_current_user)):
    return get_ticket_stats()


# Get specific ticket (Any authenticated user)
@router.get("/{ticket_no}")
def get_ticket(ticket_no: str, current_user=Depends(get_current_user)):
    # Validate ticket number format
    if not re.match(r'^TKT-[A-Z0-9]{6}$', ticket_no):
        raise HTTPException(status_code=400, detail="Invalid ticket number format")
    
    ticket = get_ticket_by_number(ticket_no)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# Update ticket status (Maintenance or Supervisor)
@router.patch("/{ticket_no}/status")
def update_status(
    ticket_no: str,
    payload: UpdateTicketStatusRequest,
    current_user=Depends(maintenance_or_supervisor)
):
    # Validate ticket number format
    if not re.match(r'^TKT-[A-Z0-9]{6}$', ticket_no):
        raise HTTPException(status_code=400, detail="Invalid ticket number format")
    
    result = update_ticket_status(
        ticket_no=ticket_no,
        new_status=payload.status,
        updated_by_user_id=current_user["user_id"]
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return result