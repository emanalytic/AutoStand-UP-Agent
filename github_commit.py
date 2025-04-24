from datetime import datetime, timedelta, timezone
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_recent_commits(owner, repo, hours=84, debug=False):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")

    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "since": since.isoformat(),
        "until": now.isoformat(),
        "per_page": 100
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"[Error] GitHub API returned {response.status_code}: {response.text}")
            return []

        raw_commits = response.json()
        structured_commits = []

        for commit in raw_commits:
            commit_data = commit.get("commit", {})
            author_info = commit.get("author", {})
            commit_author = commit_data.get("author", {})

            structured_commits.append({
                "user": author_info.get("login") or commit_author.get("name", "unknown"),
                "message": commit_data.get("message", "").strip(),
                "timestamp": commit_author.get("date"),
                "url": commit.get("html_url"),
                "repo": repo
            })

        if debug:
            for c in structured_commits:
                print(f"[{c['user']}] {c['timestamp']} → {c['message']}")

        return structured_commits

    except Exception as e:
        print(f"[Exception] Failed to fetch commits: {e}")
        return []



owner = "emanalytic"
repo = "AutoStand-UP-Agent"

commits = get_recent_commits(owner, repo, debug=True)
print(commits)