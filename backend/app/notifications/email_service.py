import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def send_email(subject: str, body: str, to_email: str):
    try:
        # Validate environment variables
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("ALERT_EMAIL_FROM")

        if not all([smtp_host, smtp_port, smtp_user, smtp_password, from_email]):
            logger.error("SMTP configuration incomplete. Missing environment variables.")
            raise ValueError("SMTP configuration incomplete")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(body)

        # Use SMTP with STARTTLS instead of SMTP_SSL
        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=10) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise