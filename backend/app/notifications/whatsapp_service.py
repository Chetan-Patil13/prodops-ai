import os
from twilio.rest import Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def send_whatsapp(message: str, phone_number: str):
    """
    Send WhatsApp message via Twilio
    """
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")  # e.g., whatsapp:+14155238886

        if not all([account_sid, auth_token, twilio_whatsapp_number]):
            logger.error("Twilio configuration incomplete.")
            raise ValueError("Twilio configuration incomplete")

        # Format phone number (must include country code)
        if not phone_number.startswith("whatsapp:"):
            phone_number = f"whatsapp:{phone_number}"

        client = Client(account_sid, auth_token)
        
        whatsapp_message = client.messages.create(
            body=message,
            from_=twilio_whatsapp_number,
            to=phone_number
        )

        logger.info(f"WhatsApp sent successfully to {phone_number} (SID: {whatsapp_message.sid})")
        
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {phone_number}: {str(e)}")
        raise