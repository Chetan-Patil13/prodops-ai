import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env.example"
load_dotenv(env_path)

def send_email(subject: str, body: str, to_email: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("ALERT_EMAIL_FROM")
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL(
        os.getenv("SMTP_HOST"),
        int(os.getenv("SMTP_PORT")),
    ) as server:
        server.login(
            os.getenv("SMTP_USER"),
            os.getenv("SMTP_PASSWORD"),
        )
        server.send_message(msg)
