from sqlalchemy import text
from app.db.connection import engine
from datetime import datetime
import uuid
from app.notifications.notifier import notify_ticket_created




def create_ticket(
    line_code: str,
    issue_summary: str,
    severity: str,
    created_by_user_id: int,
):
    ticket_no = f"TKT-{uuid.uuid4().hex[:6].upper()}"

    sql = text("""
        INSERT INTO tickets
        (ticket_no, ticket_type, line_id, issue_summary, severity, status, created_by)
        SELECT
            :ticket_no,
            'Maintenance',
            id,
            :issue_summary,
            :severity,
            'OPEN',
            :created_by
        FROM production_lines
        WHERE line_code = :line_code
        RETURNING id, ticket_no, severity, status, created_at;
    """)

    with engine.begin() as conn:
        result = conn.execute(
            sql,
            {
                "ticket_no": ticket_no,
                "issue_summary": issue_summary,
                "severity": severity,
                "created_by": created_by_user_id,
                "line_code": line_code,
            },
        ).mappings().first()
        
    # after ticket creation
    notify_ticket_created(result)
    return result




def get_ticket_by_number(ticket_no: str):
    sql = text("""
        SELECT
            t.ticket_no,
            t.issue_summary,
            t.severity,
            t.status,
            t.created_at,
            u.full_name AS created_by
        FROM tickets t
        JOIN users u ON t.created_by = u.id
        WHERE t.ticket_no = :ticket_no;
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql, {"ticket_no": ticket_no}
        ).mappings().first()

    return result
