from app.notifications.email_service import send_email
from app.notifications.whatsapp_service import send_whatsapp
from app.db.connection import engine
from sqlalchemy import text
import logging
import time

logger = logging.getLogger(__name__)


def format_ticket_notification(ticket: dict) -> tuple[str, str]:
    """Format ticket information for notifications"""
    
    # Email format (HTML-like with better structure)
    email_subject = f"🎫 New Ticket Created: {ticket['ticket_no']}"
    
    email_body = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   NEW MAINTENANCE TICKET CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticket Number: {ticket['ticket_no']}
Severity: {ticket['severity']} ⚠️
Status: {ticket['status']}
Created: {ticket['created_at']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ ACTION REQUIRED

Please review and take appropriate action on this ticket.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated message from ProdOps AI.
Please do not reply to this email.
"""
    
    # WhatsApp format (shorter, more mobile-friendly)
    whatsapp_body = f"""
🎫 *NEW TICKET ALERT*

*Ticket:* {ticket['ticket_no']}
*Severity:* {ticket['severity']}
*Status:* {ticket['status']}
*Time:* {ticket['created_at']}

⚡ Action required - Please review immediately.

— ProdOps AI
"""
    
    return email_subject, email_body, whatsapp_body


def notify_ticket_created(ticket: dict):
    """Send notifications when ticket is created"""
    
    email_subject, email_body, whatsapp_body = format_ticket_notification(ticket)
    
    # Recipients (later fetch from database based on severity/line)
    email_recipients = ["chetan.patil1397@gmail.com"]
    whatsapp_recipients = ["+918855068424"]

    notification_status = "SENT"
    
    # Send emails with retry
    for email in email_recipients:
        success = False
        for attempt in range(3):
            try:
                send_email(email_subject, email_body, email)
                logger.info(f"Email sent successfully to {email}")
                success = True
                break
            except Exception as e:
                logger.error(f"Email attempt {attempt + 1} failed for {email}: {str(e)}")
                if attempt < 2:
                    time.sleep(2)
        
        if not success:
            notification_status = "PARTIAL"

    # Send WhatsApp notifications
    for phone in whatsapp_recipients:
        try:
            send_whatsapp(whatsapp_body, phone)
            logger.info(f"WhatsApp sent successfully to {phone}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {phone}: {str(e)}")
            notification_status = "PARTIAL"

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
                    "ch": "EMAIL+WHATSAPP",
                    "rec": f"{len(email_recipients)} emails, {len(whatsapp_recipients)} WhatsApp",
                    "status": notification_status,
                },
            )
    except Exception as e:
        logger.error(f"Failed to log notification: {str(e)}")


def notify_ticket_status_changed(ticket_no: str, old_status: str, new_status: str):
    """Send notification when ticket status changes"""
    
    subject = f"🔔 Ticket Status Updated: {ticket_no}"
    body = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TICKET STATUS UPDATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticket: {ticket_no}
Previous Status: {old_status}
New Status: {new_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

— ProdOps AI
"""
    
    # Send to relevant stakeholders
    email_recipients = ["chetan.patil1397@gmail.com"]
    
    for email in email_recipients:
        try:
            send_email(subject, body, email)
            logger.info(f"Status change notification sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send status notification: {str(e)}")