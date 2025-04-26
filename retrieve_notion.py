from dotenv import load_dotenv
import os
import datetime
import json
import os
from notion_client import Client

# Load .env file
load_dotenv()

# Access environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")


# Initialize Notion client
client = Client(auth=NOTION_TOKEN)

def fetch_recent_tasks(database_id, hours_ago=1):

    time_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=hours_ago)).isoformat()
    response = client.databases.query(
        database_id=database_id,
        filter={
            "timestamp": "last_edited_time",
            "last_edited_time": {
                "after": time_ago
            }
        }
    )
    return response.get("results", [])

def parse_tasks(data):
    tasks = []
    for page in data:
        properties = page["properties"]

        name_property = properties.get("First Name", {})
        first_name = name_property.get("title", [{}])[0].get("text", {}).get("content", "No Name")

        status_property = properties.get("Status", {})
        status = status_property.get("status", {}).get("name", "No Status")

        due_date_property = properties.get("Due date", {})
        due_date = due_date_property.get("date", {}).get("start", "No Due Date")

        task = {
            "First Name": first_name,
            "Status": status,
            "Due Date": due_date
        }
        tasks.append(task)
    return tasks

def save_tasks_to_json(tasks, filename='db.json'):
   
    with open(filename, 'w') as f:
        json.dump(tasks, f, indent=4)

def main():
    data = fetch_recent_tasks(DATABASE_ID, hours_ago=1)  
    tasks = parse_tasks(data)
    save_tasks_to_json(tasks)

if __name__ == "__main__":
    main()
