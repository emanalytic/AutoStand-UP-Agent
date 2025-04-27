from tools.slack_poster import SlackPoster
from tools.github_fetcher import GitHubFetcher
from tools.notion_fetcher import NotionFetcher
from config import Config
from groq import Groq
import os
import time

config = Config()

class AutoStandupAgent:
    def __init__(self):
        self.github_fetcher = GitHubFetcher()
        self.notion_fetcher = NotionFetcher()
        self.slack_poster = SlackPoster()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.llm_model = config.get('settings', 'model')

    def run(self):
        github_data = self.github_fetcher.fetch_activity()
        notion_data = self.notion_fetcher.fetch_tasks()

        standup_report = {
            "github": github_data,
            "notion": notion_data
        }

        formatted_standup = self._format_standup(standup_report)
        self.slack_poster.post_message(formatted_standup)

    def _format_standup(self, standup_report):
        messages = [
            {"role": "system", "content": "You format daily standups..."},
            {"role": "user", "content": f"Input JSON: {standup_report}\nFormat for Slack..."}
        ]

        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                completion = self.groq_client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise Exception("Failed to format standup.")
