from app.notifications.email_service import send_email
from app.notifications.whatsapp_service import send_whatsapp
from app.db.connection import engine
from sqlalchemy import text


def notify_ticket_created(ticket: dict):
    subject = f"New Ticket Created: {ticket['ticket_no']}"
    body = f"""
Ticket Number: {ticket['ticket_no']}
Severity: {ticket['severity']}
Status: {ticket['status']}
"""

    # Example recipients (later from DB)
    email_recipients = ["chetan.patil1397@gmail.com"]
    whatsapp_recipients = ["+918855068424"]

    for email in email_recipients:
        send_email(subject, body, email)

    for phone in whatsapp_recipients:
        send_whatsapp(body, phone)

    # Audit log
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO notification_logs
                (ticket_id, channel, recipient, status)
                VALUES (:tid, :ch, :rec, 'SENT')
            """),
            {
                "tid": ticket["id"],
                "ch": "MULTI",
                "rec": "EMAIL+WHATSAPP",
            },
        )
