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

def fetch_database_items(database_id):
    response = client.databases.query(database_id=database_id)
    return response["results"]

data = fetch_database_items(DATABASE_ID)
tasks = []

for page in data:
    properties = page["properties"]

    task_property = properties["Task Name"]
    task_name = task_property["rich_text"][0]["text"]["content"] if task_property["rich_text"] else "No Task"


    name_property = properties["Assignee"]
    assignee = name_property["title"][0]["text"]["content"] if name_property["title"] else "No Assignee"

    status_property = properties["Status"]
    status = status_property["status"]["name"] if status_property["status"] else "No Status"

    due_date_property = properties["Due date"]
    due_date = due_date_property["date"]["start"] if due_date_property["date"] else "No Due Date"

    last_edited = page.get("last_edited_time", "No Last Edit")


    task = {
        "Task Name": task_name,
        "Assignee": assignee,
        "Status": status,
        "Due Date": due_date,
        "Last edited" : last_edited
    }
    tasks.append(task)

print(json.dumps(tasks, indent=4))

def save_tasks_to_json(tasks, filename='db.json'):
   
    with open(filename, 'w') as f:
        json.dump(tasks, f, indent=4)

def main():
    
    save_tasks_to_json(tasks)

if __name__ == "__main__":
    main()
