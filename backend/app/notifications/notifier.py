from app.notifications.email_service import send_email
from app.notifications.whatsapp_service import send_whatsapp
from app.db.connection import engine
from sqlalchemy import text
import logging
import time

logger = logging.getLogger(__name__)


def notify_ticket_created(ticket: dict):
    subject = f"New Ticket Created: {ticket['ticket_no']}"
    body = f"""
Ticket Number: {ticket['ticket_no']}
Severity: {ticket['severity']}
Status: {ticket['status']}
Created At: {ticket['created_at']}
"""

    # Example recipients (later from DB)
    email_recipients = ["chetan.patil1397@gmail.com"]
    whatsapp_recipients = ["whatsapp:+918855068424"]

    notification_status = "SENT"
    
    # Send emails with retry
    for email in email_recipients:
        success = False
        for attempt in range(3):  # 3 retry attempts
            try:
                send_email(subject, body, email)
                logger.info(f"Email sent successfully to {email}")
                success = True
                break
            except Exception as e:
                logger.error(f"Email attempt {attempt + 1} failed for {email}: {str(e)}")
                if attempt < 2:  # Don't sleep on last attempt
                    time.sleep(2)  # Wait 2 seconds before retry
        
        if not success:
            notification_status = "FAILED"

    # Send WhatsApp notifications
    for phone in whatsapp_recipients:
        try:
            send_whatsapp(body, phone)
            logger.info(f"WhatsApp sent successfully to {phone}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {phone}: {str(e)}")

    # Audit log
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO notification_logs
                    (ticket_id, channel, recipient, status)
                    VALUES (:tid, :ch, :rec, :status)
                """),
                {
                    "tid": ticket["id"],
                    "ch": "MULTI",
                    "rec": "EMAIL+WHATSAPP",
                    "status": notification_status,
                },
            )
    except Exception as e:
        logger.error(f"Failed to log notification: {str(e)}")