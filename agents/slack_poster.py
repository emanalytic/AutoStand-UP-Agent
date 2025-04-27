import os
import logging
from typing import Dict
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from groq import Groq
import time
from dotenv import load_dotenv
from agents.notion_fetcher import NotionFetcher
from agents.github_fetcher import GitHubFetcher


load_dotenv()


class SlackPoster:
    def __init__(self, slack_token: str = None, slack_channel: str = None, groq_api_key: str = None,
                 llm_model: str = None):
        self.slack_token = slack_token or os.getenv("SLACK_BOT_TOKEN")
        self.slack_channel = slack_channel or os.getenv("SLACK_CHANNEL")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "llama3-70b-8192")

        if not all([self.slack_token, self.slack_channel, self.groq_api_key]):
            raise ValueError("Missing necessary environment variables.")

        self.slack_client = WebClient(token=self.slack_token)
        self.groq_client = Groq(api_key=self.groq_api_key)

        self.github_fetcher = GitHubFetcher()
        self.notion_fetcher = NotionFetcher()

    def fetch_and_generate_report(self, owner: str, repo: str, hours: int = 24) -> Dict:

        github_activities = self.github_fetcher.fetch_activity(owner, repo, hours)

        notion_activities = self.notion_fetcher.fetch_tasks()

        standup_report = {
            "github": github_activities,
            "notion": notion_activities
        }

        return standup_report

    def format_standup(self, standup_report: Dict) -> str:
      member_info = {
      "Eman":    {"github": "emanalytic",    "slack_id": "U08PZ74CXQT"},
      "Maryam":  {"github": "Maryam-Sikander",  "slack_id": "U08PGDU7KGS"},
      "John" : {"github": "justbuilding",  "slack_id": "U08PZJPGX8B"}
      
  }
      messages = [
    {
        "role": "system",
        "content": (
            "You are an assistant that formats daily standup updates for Slack."
            "Keep it clean, concise, and easy to read. Provide a summary of each person’s activity, and avoid excessive repetition."
            "Focus on tasks and key contributions."
            "Use only Slack markdown: bold with *asterisks*, italics with _underscores_, "
            "bullet points (•), and section headers. "
            "When referring to a member, look up their slack_id in member_info and mention them as <@SLACK_ID>. "
            "If you person name exist on Notion or GitHub but not found slack id then just mention their name with updates. "
            "Do not add any extra introduction or LLM-style preamble—start immediately with the report."
        )
    },
    {
        "role": "user",
        "content": (
            f"member_info = {json.dumps(member_info)}\n\n"
            f"Input JSON = {standup_report}\n"
            "Generate a single Slack message with this exact structure:\n\n"
            "*Daily Stand-up Report*\n"
            "For each member in the order given:\n"
            "  * <@SLACK_ID>\n"
            "Return a Slack markdown in a simple, friendly, and clean format without too many headings or bullet points."
            "Focus on the activity of each person. Make it conversational and concise."
            "Ensure:\n"
            "- You replace each name with its `<@SLACK_ID>` mention.\n"
            "- You use exactly one section header.\n"
            "- You use bold for labels (e.g. *Done Yesterday:*), italics for dates/status.\n"
            "- No extra lines, no “Here is” or “Below” or any LLM framing—only the report itself."
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
                logging.error(f"[SlackPoster] Groq API error on attempt {attempt + 1}: {str(e)}")
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise Exception(f"Failed to format standup after {retry_attempts} attempts.")

    def post_to_slack(self, text: str) -> Dict:
        try:
            response = self.slack_client.chat_postMessage(channel=self.slack_channel, text=text)
            return response.data
        except SlackApiError as e:
            logging.error(f"[SlackPoster] Slack API error: {e.response['error']}")
            raise Exception(f"Failed to send message to Slack: {e.response['error']}")

    def send_standup(self, owner: str, repo: str, hours: int = 24) -> Dict:
        """Full flow: Fetch activity → Format → Post to Slack."""
        standup_report = self.fetch_and_generate_report(owner, repo, hours)
        slack_text = self.format_standup(standup_report)
        result = self.post_to_slack(slack_text)
        return result

