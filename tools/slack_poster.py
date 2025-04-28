from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config
import os

config = Config()
class SlackPoster:
    def __init__(self):
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_channel = config.get('settings', 'slack_channel')
        self.slack_client = WebClient(token=self.slack_token)

    def post_message(self, text: str):
        try:
            response = self.slack_client.chat_postMessage(channel=self.slack_channel, text=text)
            return response.data
        except SlackApiError as e:
            raise Exception(f"Slack API Error: {e.response['error']}")
