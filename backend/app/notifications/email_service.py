import os
import requests
import logging

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def send_email(subject: str, body: str, to_email: str):
    if not SENDGRID_API_KEY:
        raise RuntimeError("SENDGRID_API_KEY not set")

    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {"email": EMAIL_FROM},
        "content": [
            {
                "type": "text/plain",
                "value": body
            }
        ]
    }

    response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=10
    )

    if response.status_code >= 400:
        logger.error(
            f"SendGrid error {response.status_code}: {response.text}"
        )
        raise RuntimeError("Failed to send email")

    logger.info(f"Email sent successfully to {to_email}")
