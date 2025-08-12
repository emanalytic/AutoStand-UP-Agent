from tools.slack_poster import SlackPoster
from tools.teams_poster import TeamsPoster
from tools.whatsapp_poster import WhatsAppPoster
from tools.github_fetcher import GitHubFetcher
from tools.notion_fetcher import NotionFetcher
from tools.github_projects_fetcher import GitHubProjectsFetcher
from config import Config
from llm_providers.factory import create_llm_provider
import os
import time
import json
from datetime import datetime

config = Config()
member_info = config.get_section("members")

class AutoStandupAgent:
    def __init__(self):
        self.github_fetcher = GitHubFetcher()
        
        # Determine data source for tasks - either Notion or GitHub Projects
        self.data_source = config.get('settings', 'data_source', fallback='notion').lower()
        
        try:
            if self.data_source == 'notion':
                self.task_fetcher = NotionFetcher()
            elif self.data_source == 'github_projects':
                self.task_fetcher = GitHubProjectsFetcher()
            else:
                print(f"Warning: Unknown data source '{self.data_source}'. Defaulting to Notion.")
                self.task_fetcher = NotionFetcher()
        except Exception as e:
            print(f"Warning: Could not initialize {self.data_source} fetcher: {e}")
            print("Falling back to GitHub Projects fetcher.")
            try:
                self.task_fetcher = GitHubProjectsFetcher()
                self.data_source = 'github_projects'
            except Exception as e2:
                print(f"Warning: Could not initialize GitHub Projects fetcher either: {e2}")
                raise ValueError("Could not initialize any task data source. Please check your configuration and credentials.")
            
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
        
        # Fetch task data from configured source
        if self.data_source == 'github_projects':
            task_data = self.task_fetcher.fetch_issues()
        else:  # notion or fallback
            task_data = self.task_fetcher.fetch_tasks()

        standup_report = {
            "github": github_data,
            "tasks": task_data,
            "data_source": self.data_source
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
        data_source = standup_report.get("data_source", "notion")
        task_label = "GitHub Projects Issues" if data_source == "github_projects" else "Notion Tasks"

        today_date = datetime.now().strftime("%d/%m/%Y")
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a stand-up update assistant specialized in formatting daily reports for Slack. "
                    "Your output should be professional, concise, and easy to read, focusing on each team member’s key tasks and progress. "
                    "Follow these formatting guidelines:\n"
                    "- Mention team members using their Slack IDs (e.g., <@SLACK_ID>)\n"
                    "- Use *bold* for section labels (e.g., *Completed Yesterday:*)\n"
                    "- Use _italics_ for all dates, deadlines, and task statuses (e.g., _2025-04-27_, _In Progress_)\n"
                    "- Use bullet points (•) for listing tasks or updates\n"
                    "- Dates should be consistently formatted as _MM/DD/YYYY_ or _YYYY-MM-DD_, depending on the input, and always italicized\n"
                    "- Avoid unnecessary jargon or filler—keep it clear and straightforward\n"
                    "- Do not add greetings, introductions, or concluding remarks—start immediately with the stand-up content"
                )
            },
            {
                "role": "user",
                "content": (
                    f"member_info = {json.dumps(member_info)}\n\n"
                    f"Input JSON = {json.dumps(standup_report)}\n\n"
                    f"Data source for tasks: {task_label}\n\n"
                    f"Create a Slack-formatted daily stand-up message structured as follows:\n\n"
                    f"*Daily Stand-up Report — _{today_date}_*\n\n"
                    "For each team member, format their update like this:\n"
                    "  *Name* <@SLACK_ID>\n"
                    "    • *Completed Yesterday:* Brief key accomplishments or finished tasks, including any dates in _MM/DD/YYYY_ or _YYYY-MM-DD_ format\n"
                    "    • *Working Today:* Current tasks or focus areas, include any relevant dates italicized\n"
                    "    • *Blockers or Challenges:* Any impediments affecting progress (omit if none)\n"
                    "    • *Due Dates or Goals:* List any deadlines or milestones, always italicizing dates\n\n"
                    "Maintain a consistent date format and italicize all dates to enhance readability."
                )
            }
        ]
        
        return self.llm_provider.chat_completion(messages, temperature=0.7, max_tokens=500)

if __name__ == "__main__":
    agent = AutoStandupAgent()
    print(agent.run())
