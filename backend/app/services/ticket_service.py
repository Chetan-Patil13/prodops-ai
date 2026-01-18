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
            u.full_name AS created_by,
            pl.line_code
        FROM tickets t
        JOIN users u ON t.created_by = u.id
        JOIN production_lines pl ON t.line_id = pl.id
        WHERE t.ticket_no = :ticket_no;
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql, {"ticket_no": ticket_no}
        ).mappings().first()

    return result


def get_all_tickets(limit: int = 50, status: str = None):
    """Get all tickets with optional status filter"""
    if status:
        sql = text("""
            SELECT
                t.id,
                t.ticket_no,
                t.issue_summary,
                t.severity,
                t.status,
                t.created_at,
                t.updated_at,
                u.full_name AS created_by,
                pl.line_code
            FROM tickets t
            JOIN users u ON t.created_by = u.id
            JOIN production_lines pl ON t.line_id = pl.id
            WHERE t.status = :status
            ORDER BY t.created_at DESC
            LIMIT :limit;
        """)
        params = {"status": status, "limit": limit}
    else:
        sql = text("""
            SELECT
                t.id,
                t.ticket_no,
                t.issue_summary,
                t.severity,
                t.status,
                t.created_at,
                t.updated_at,
                u.full_name AS created_by,
                pl.line_code
            FROM tickets t
            JOIN users u ON t.created_by = u.id
            JOIN production_lines pl ON t.line_id = pl.id
            ORDER BY t.created_at DESC
            LIMIT :limit;
        """)
        params = {"limit": limit}

    with engine.connect() as conn:
        results = conn.execute(sql, params).mappings().all()

    return results


def get_ticket_stats():
    """Get ticket statistics"""
    sql = text("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'OPEN') AS open_count,
            COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') AS in_progress_count,
            COUNT(*) FILTER (WHERE status = 'CLOSED') AS closed_count,
            COUNT(*) AS total_count
        FROM tickets;
    """)

    with engine.connect() as conn:
        result = conn.execute(sql).mappings().first()

    return result


def update_ticket_status(ticket_no: str, new_status: str, updated_by_user_id: int):
    """Update ticket status"""
    sql = text("""
        UPDATE tickets
        SET status = :new_status,
            updated_at = CURRENT_TIMESTAMP
        WHERE ticket_no = :ticket_no
        RETURNING id, ticket_no, status, updated_at;
    """)

    with engine.begin() as conn:
        result = conn.execute(
            sql,
            {
                "ticket_no": ticket_no,
                "new_status": new_status,
            }
        ).mappings().first()

    return result


def get_open_tickets_count():
    """Get count of open tickets"""
    sql = text("""
        SELECT COUNT(*) as count
        FROM tickets
        WHERE status = 'OPEN';
    """)

    with engine.connect() as conn:
        result = conn.execute(sql).mappings().first()

    return result['count'] if result else 0