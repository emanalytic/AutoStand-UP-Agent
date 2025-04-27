from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

class SlackPoster:
    def __init__(self, slack_token=None, slack_channel=None):
        self.slack_token = slack_token or os.getenv("SLACK_BOT_TOKEN")
        self.slack_channel = slack_channel or os.getenv("SLACK_CHANNEL")
        self.slack_client = WebClient(token=self.slack_token)

    def post_message(self, text: str):
        try:
            response = self.slack_client.chat_postMessage(channel=self.slack_channel, text=text)
            return response.data
        except SlackApiError as e:
            raise Exception(f"Slack API Error: {e.response['error']}")
