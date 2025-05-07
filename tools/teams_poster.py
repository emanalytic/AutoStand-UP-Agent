import requests
from config import Config

config = Config()

class TeamsPoster:
    def __init__(self):
        self.webhook_url = config.get('settings', 'teams_webhook_url')

    def post_message(self, text: str):
        payload = {
            "text": text
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(self.webhook_url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Teams Webhook Error: {response.status_code} - {response.text}")
        
        return {"status": "success", "code": response.status_code}