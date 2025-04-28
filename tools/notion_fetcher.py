import logging
from notion_client import Client
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class NotionFetcher:
    def __init__(self):
        self.token =  os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("DATABASE_ID")
        if not self.token:
            raise ValueError("NOTION_TOKEN not found in environment variables")

        self.client = Client(auth=self.token)

    def fetch_tasks(self) -> List[Dict]:
        tasks = []
        has_more = True
        start_cursor = None

        while has_more:
            try:
                response = self.client.databases.query(
                    database_id=self.database_id, start_cursor=start_cursor)
                tasks.extend(self._process_tasks(response))
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor", None)
            except Exception as e:
                logging.error(f"[NotionFetcher] Error fetching data from Notion: {e}")
                break

        return tasks

    def _process_tasks(self, response) -> List[Dict]:
        tasks = []
        for page in response.get("results", []):
            properties = page["properties"]

            task_name = (properties.get("Task Name", {}).get("rich_text") or [{}])[0].get("text", {}).get("content",
                                                                                                          "Unnamed Task")
            assignee = (properties.get("Assignee", {}).get("title") or [{}])[0].get("text", {}).get("content",
                                                                                                    "Unassigned")
            status = (properties.get("Status", {}).get("status") or {}).get("name", "No Status")
            due_date = (properties.get("Due date", {}).get("date") or {}).get("start", "No Due Date")

            task = {
                "Task Name": task_name,
                "Assignee": assignee,
                "Status": status,
                "Due Date": due_date,
            }
            tasks.append(task)

        return tasks


