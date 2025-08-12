from twilio.rest import Client
from config import Config
import os

config = Config()

class WhatsAppPoster:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = config.get('settings', 'whatsapp_from')
        self.whatsapp_to = config.get('settings', 'whatsapp_to')
        
        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio credentials not found. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")
        
        self.client = Client(self.account_sid, self.auth_token)

    def post_message(self, text: str):
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_from}',
                body=text,
                to=f'whatsapp:{self.whatsapp_to}'
            )
            return {"status": "success", "sid": message.sid}
        except Exception as e:
            raise Exception(f"WhatsApp API Error: {str(e)}")