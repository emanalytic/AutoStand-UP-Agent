from twilio.rest import Client
from config import Config
import os

config = Config()

class WhatsAppPoster:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = config.get('settings', 'whatsapp_from')
        
        # Support both single recipient and multiple recipients (including groups)
        whatsapp_to_raw = config.get('settings', 'whatsapp_to')
        self.whatsapp_recipients = [recipient.strip() for recipient in whatsapp_to_raw.split(',')]
        
        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio credentials not found. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")
        
        self.client = Client(self.account_sid, self.auth_token)

    def post_message(self, text: str):
        """
        Send message to all configured recipients (individuals or groups).
        Supports both individual phone numbers (+1234567890) and group IDs (group:12345).
        """
        results = []
        
        for recipient in self.whatsapp_recipients:
            try:
                # Format recipient for Twilio API
                if recipient.startswith('group:'):
                    # WhatsApp group ID format
                    to_address = f'whatsapp:{recipient}'
                else:
                    # Individual phone number format
                    to_address = f'whatsapp:{recipient}'
                
                message = self.client.messages.create(
                    from_=f'whatsapp:{self.whatsapp_from}',
                    body=text,
                    to=to_address
                )
                results.append({"status": "success", "sid": message.sid, "recipient": recipient})
                
            except Exception as e:
                results.append({"status": "error", "error": str(e), "recipient": recipient})
        
        # Check if any message was sent successfully
        successful_sends = [r for r in results if r["status"] == "success"]
        if not successful_sends:
            # If all failed, raise an exception with details
            errors = [r["error"] for r in results if r["status"] == "error"]
            raise Exception(f"WhatsApp API Error: Failed to send to all recipients. Errors: {'; '.join(errors)}")
        
        return {
            "status": "success", 
            "total_recipients": len(self.whatsapp_recipients),
            "successful_sends": len(successful_sends),
            "results": results
        }