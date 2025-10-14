# Auto Standup Agent <img src="https://github.com/user-attachments/assets/6fc6e64d-3c23-4f11-91af-5721fed9fa05" alt="AutoStand-UP-Agent Logo" width="200"/>


A lightweight agent that pulls activity from GitHub and Notion, summarizes each team member’s progress using a language model, and sends a clean Slack update. Designed for teams who want async visibility without the overhead of manual standups.

## What It Does

1. **Fetches activity** from GitHub (commits, PRs) and task data from Notion or GitHub Projects issues.
2. **Maps activity to individual contributors** using GitHub usernames and Slack IDs.
3. **Uses a local or API-based language model** to generate clear summaries (what was done, what’s in progress, blockers).
4. **Formats and sends messages to Slack** in a simple, readable format.



## How It Works

The agent runs automatically via GitHub Actions (or can be run manually). Here’s the flow:

```mermaid
flowchart TD
    A[Scheduled Trigger - GitHub Action] --> B[Auth & Setup]
    
    B --> C[GitHub API]
    C --> C1[Pull commits in last 24h]
    C --> C2[Fetch PRs created/merged]
    C --> C3[Extract metadata - author, repo, message]

    B --> D[Task Data Source]
    D --> D1{Data Source Type?}
    D1 -->|Notion| D2[Notion API - Fetch Task DB]
    D1 -->|GitHub Projects| D3[GitHub API - Fetch Issues]
    D2 --> D4[Parse Notion status - In Progress, Blocked, Done]
    D3 --> D5[Parse GitHub issues - Map labels to status]
    D4 --> D6[Match user activity with GitHub if possible]
    D5 --> D6

    C3 --> E[Activity Aggregation Engine]
    D6 --> E

    E --> F[LLM Summarizer - GROQ API]
    F --> F1[Prompt engineering - What I did / Doing / Blockers]
    F1 --> G[Per-user summaries]

    G --> H[Final Stand-Up Builder]
    H --> H1[Format per-user messages]
    H --> H2[Sort + merge team-wide summary]

    H2 --> I[Output to Slack ]
    I --> I1[Use Webhook or Bot to send to channel]

    I1 --> Z[Done! Daily stand-up delivered]
```

---

## Getting Started

### 1. Clone the repo and install dependencies

```bash
git clone https://github.com/emanalytic/auto-standup-agent.git
cd auto-standup-agent
pip install -r requirements.txt
```

---

##  Configuration Guide

### A. Set your team’s GitHub and Slack info

Open the `config.ini` file and fill in your team details under `[members]`. This is how the agent links GitHub activity to Slack updates:

```ini
[members]
Eman_github = emanalytic
Eman_slack_id = U12345678

John_github = just-building
John_slack_id = U87654321
```

Add one line per user for both GitHub and Slack. IDs must match exactly.

---

### B. Set your config

Also in `config.ini`, set the language model you’re using under `[settings]`:

```ini
[settings]
model = llama3-70b-8192
```
Update the slack channel you want to post the message
```ini
[settings]
slack_channel=#daily-standup
```
Choose the GitHub mode:

`mode = org` — fetch activity from all organization repositories\
`mode = repo` — fetch from a single specified repo

```ini
[settings]
mode = org  ; or "repo"
organization = my-org-name  ; required if mode is "org"
owner = username            ; required if mode is "repo"
repo = repo-name  
```

### C. Choose your task data source

You can now choose between two data sources for task information:

- **Notion** — fetch tasks from a Notion database (requires Notion integration setup)
- **GitHub Projects** — fetch issues from GitHub repositories/organization as tasks

```ini
[settings]
data_source = notion          ; or "github_projects"
```

**Notion setup** (traditional):
- Requires `NOTION_TOKEN` and `DATABASE_ID` environment variables
- Uses your existing Notion database structure

**GitHub Projects setup** (new option):
- Uses the same GitHub token (`G_TOKEN`) as for commit/PR fetching
- Fetches GitHub issues as tasks, mapping issue states to task statuses:
  - Open issues → "To Do"
  - Issues with "in progress" label → "In Progress"  
  - Issues with "blocked" label → "Blocked"
  - Issues with "review" label → "Under Review"
  - Closed issues → "Done"

---

## Add GitHub Secrets

You'll need these for the agent to fetch data and send messages.

Go to:  
**Repository → Settings → Secrets and variables → Actions → New repository secret**

Add the following:

| Secret Name         | Description                              | Required |
|---------------------|------------------------------------------|----------|
| `G_TOKEN`           | GitHub Personal Access Token             | Yes |
| `SLACK_BOT_TOKEN`   | Slack Bot Token                          | If using Slack |
| `NOTION_TOKEN`      | Your Notion integration token            | If using Notion data source |
| `DATABASE_ID`       | Notion database ID (where your tasks live) | If using Notion data source |
| `GROQ_API_KEY`      | API key for LLM summarization            | If using Groq |
| `OPENAI_API_KEY`    | API key for OpenAI LLM (if using OpenAI) | If using OpenAI |
| `TWILIO_ACCOUNT_SID`| Twilio Account SID (for WhatsApp)        | If using WhatsApp |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (for WhatsApp)         | If using WhatsApp |

**Notes:** 
- You only need either `GROQ_API_KEY` or `OPENAI_API_KEY` depending on which LLM provider you configure in `config.ini`.
- You only need `NOTION_TOKEN` and `DATABASE_ID` if you set `data_source = notion` in your config.
- If you set `data_source = github_projects`, only the `G_TOKEN` is needed for task data (same token used for GitHub activity).

---

### B. GitHub Actions: Auto-Run Daily

This project includes a GitHub Action that can run the agent automatically every day.

#### To **enable** the daily auto-run:

1. Open `.github/workflows/standup.yaml`.
2. **Uncomment** the `schedule:` section and keep `workflow_dispatch:` to allow both daily automatic runs and manual triggers.

```yaml
on:
  schedule:
    - cron: '42 16 * * *'  # Runs every day at 4:42 PM UTC
  workflow_dispatch:       # Allows you to run it manually
```
#### **Customizing the Trigger Time**

You can adjust the cron expression to change the time of day when the agent runs. For example, to make it run at 8 AM UTC, change it to:

You can change the schedule timing [using this guide](https://crontab.guru/).

## Microsoft Teams Integration

Require Microsoft 365 (business or enterprise) account to use the Teams integration for Webhook.

## WhatsApp Integration

The agent supports WhatsApp integration using Twilio's WhatsApp API. This allows you to receive standup reports directly in WhatsApp.

### Setup WhatsApp Integration

1. **Create a Twilio Account**
   - Sign up at [Twilio](https://www.twilio.com)
   - Get your Account SID and Auth Token from the Twilio Console

2. **Enable WhatsApp on Twilio**
   - Go to Messaging → Try it out → Send a WhatsApp message
   - Follow Twilio's WhatsApp setup guide
   - Note the Twilio WhatsApp phone number (e.g., +14155238886)

3. **Configure WhatsApp Settings**
   
   Update your `config.ini` file:
   ```ini
   [settings]
   posting_methods = slack, whatsapp
   whatsapp_from = +14155238886  # Your Twilio WhatsApp number
   
   # Send to individual WhatsApp number
   whatsapp_to = +1234567890
   
   # OR send to WhatsApp group (get group ID from Twilio)
   whatsapp_to = group:12345678901234567890
   
   # OR send to multiple recipients (groups and individuals)
   whatsapp_to = +1234567890, group:12345678901234567890, +9876543210
   ```

   **Getting WhatsApp Group ID:**
   - Create a WhatsApp group with your team members
   - Add your Twilio WhatsApp number to the group
   - Send a message from the group to your Twilio number
   - Check your Twilio console logs to find the group ID
   - Group IDs typically look like: `12345678901234567890@g.us`
   - Use format: `group:12345678901234567890@g.us` in config

4. **Add Environment Variables**
   
   Add these secrets to your GitHub repository:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token

### Using Multiple Platforms

You can configure the agent to post to multiple platforms simultaneously by updating the `posting_methods` setting:

```ini
# Post to Slack only
posting_methods = slack

# Post to WhatsApp only  
posting_methods = whatsapp

# Post to both Slack and WhatsApp
posting_methods = slack, whatsapp

# Post to all platforms
posting_methods = slack, teams, whatsapp
```

---

## Run Locally

If you want to test before pushing:

```bash
python -m agent.standup_agent
```

Make sure the required environment variables are available. You can use a `.env` file or export them in your shell.

---

## Example Slack Output

![image](https://github.com/user-attachments/assets/c792ada8-eb8e-4692-b99a-67fb66d409f8)

---

## Extending the Agent

You can plug in other tools like Jira, Linear, or custom Git sources. Just update the fetchers inside:

```
tools/
├── github_fetcher.py
├── notion_fetcher.py
├── slack_poster.py
```

And adjust the prompt logic in:

```
agent/standup_agent.py
```

---

## License

MIT License
