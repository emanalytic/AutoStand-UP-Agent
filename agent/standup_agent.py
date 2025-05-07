from tools.slack_poster import SlackPoster
from tools.github_fetcher import GitHubFetcher
from tools.notion_fetcher import NotionFetcher
from config import Config
from groq import Groq
import os
import time
import json

config = Config()
member_info = config.get_section("members")
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
            {
                "role": "system",
                "content": (
                    "You are an assistant that formats daily standup updates for Slack in a professional and human-friendly tone. "
                    "The goal is to provide a concise update of each team member’s key activities and tasks, while maintaining a clean and easy-to-read structure. "
                    "Use the following formatting rules:\n"
                    "- Mention team members by their Slack IDs (e.g., <@SLACK_ID>)\n"
                    "- Use *bold* for labels (e.g., *Completed Yesterday:*)\n"
                    "- Use _italics_ for dates and task statuses (e.g., _2025-04-27_ or _In Progress_)\n"
                    "- Use bullet points (•) to list key tasks or updates\n"
                    "- Focus on keeping the report simple, clear, and professional without unnecessary fluff or jargon.\n"
                    "Do not add extra introductions or LLM-style framing. Start directly with the stand-up update."
                )
            },
            {
                "role": "user",
                "content": (
                    f"member_info = {json.dumps(member_info)}\n\n"
                    f"Input JSON = {standup_report}\n"
                    "Generate a Slack message with the following structure:\n\n"
                    "*Daily Stand-up Report — _MM/DD/YYYY_*\n\n"
                    "For each team member, follow this format:\n"
                    "  *Name* <@SLACK_ID>\n"
                    "    • *What was done yesterday:* A brief summary of key accomplishments or tasks completed\n"
                    "    • *What is being worked on today:* A concise description of ongoing work\n"
                    "    • *Any blockers or challenges:* Mention any issues preventing progress, if applicable\n"
                    "    • *Due dates or goals:* Any important deadlines or milestones\n\n"
                    "Focus on professional, concise language while maintaining a tone of collaboration and progress."
                )
            }
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

if __name__ == "__main__":
    agent = AutoStandupAgent()
    print(agent.run())