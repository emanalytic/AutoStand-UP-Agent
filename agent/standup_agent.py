from tools.slack_poster import SlackPoster
from tools.teams_poster import TeamsPoster
from tools.whatsapp_poster import WhatsAppPoster
from tools.github_fetcher import GitHubFetcher
from tools.notion_fetcher import NotionFetcher
from config import Config
from llm_providers.factory import create_llm_provider
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
        # Get LLM provider settings from config
        self.llm_provider_type = config.get('settings', 'llm_provider', fallback='groq')
        
        # Initialize posters based on configuration
        self.posters = []
        
        # Get enabled posting methods from config
        enabled_methods = config.get('settings', 'posting_methods', fallback='slack').split(',')
        enabled_methods = [method.strip().lower() for method in enabled_methods]
        
        for method in enabled_methods:
            if method == 'slack':
                try:
                    self.posters.append(('Slack', SlackPoster()))
                except Exception as e:
                    print(f"Warning: Could not initialize Slack poster: {e}")
            elif method == 'teams':
                try:
                    self.posters.append(('Teams', TeamsPoster()))
                except Exception as e:
                    print(f"Warning: Could not initialize Teams poster: {e}")
            elif method == 'whatsapp':
                try:
                    self.posters.append(('WhatsApp', WhatsAppPoster()))
                except Exception as e:
                    print(f"Warning: Could not initialize WhatsApp poster: {e}")
        
        if not self.posters:
            print("Warning: No valid posters configured. Defaulting to Slack.")
            self.posters.append(('Slack', SlackPoster()))
        
        self.llm_model = config.get('settings', 'model')
       
        # Create the appropriate LLM provider
        self.llm_provider = create_llm_provider(self.llm_provider_type, self.llm_model)

    def run(self):
        github_data = self.github_fetcher.fetch_activity()
        notion_data = self.notion_fetcher.fetch_tasks()

        standup_report = {
            "github": github_data,
            "notion": notion_data
        }

        formatted_standup = self._format_standup(standup_report)
        
        # Post to all configured platforms
        success_count = 0
        for platform_name, poster in self.posters:
            try:
                result = poster.post_message(formatted_standup)
                print(f"Successfully posted to {platform_name}")
                success_count += 1
            except Exception as e:
                print(f"Failed to post to {platform_name}: {e}")
        
        if success_count == 0:
            raise Exception("Failed to post standup to any platform")
        
        return formatted_standup

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
        
        return self.llm_provider.chat_completion(messages, temperature=0.7, max_tokens=500)

if __name__ == "__main__":
    agent = AutoStandupAgent()
    print(agent.run())