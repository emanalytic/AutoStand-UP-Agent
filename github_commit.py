from datetime import datetime, timedelta, timezone
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_recent_commits(owner, repo, hours=24, debug=False):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")

    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)

    # Commit URL
    commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "since": since.isoformat(),
        "until": now.isoformat(),
        "per_page": 100
    }

    # Fetch commits
    commits = []
    try:
        response = requests.get(commit_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"[Error] GitHub API returned {response.status_code}: {response.text}")
            return []

        raw_commits = response.json()
        if not raw_commits:
            print("[Info] No commits found in the given time range.")
        
        for commit in raw_commits:
            commit_data = commit.get("commit", {})
            author_info = commit.get("author", {})
            commit_author = commit_data.get("author", {})

            commits.append({
                "user": author_info.get("login") or commit_author.get("name", "unknown"),
                "message": commit_data.get("message", "").strip(),
                "timestamp": commit_author.get("date"),
                "url": commit.get("html_url"),
                "repo": repo
            })

        if debug:
            for c in commits:
                print(f"[{c['user']}] {c['timestamp']} → {c['message']}")

    except Exception as e:
        print(f"[Exception] Failed to fetch commits: {e}")

    # PR URL
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    pr_params = {
        "state": "all",  # You can also use 'open', 'closed', or 'merged' if you want to filter
        "since": since.isoformat(),
        "until": now.isoformat(),
        "per_page": 100
    }

    # Fetch PRs
    prs = []
    try:
        response = requests.get(pr_url, headers=headers, params=pr_params)
        if response.status_code != 200:
            print(f"[Error] GitHub API returned {response.status_code}: {response.text}")
            return []

        raw_prs = response.json()
        if not raw_prs:
            print("[Info] No PRs found in the given time range.")

        for pr in raw_prs:
            pr_data = pr.get("pull_request", {})
            pr_user = pr.get("user", {})
            pr_state = pr_data.get("state", "unknown")
            pr_timestamp = pr_data.get("created_at", "unknown")

            prs.append({
                "user": pr_user.get("login", "unknown"),
                "title": pr_data.get("title", "").strip(),
                "state": pr_state,
                "timestamp": pr_timestamp,
                "url": pr_data.get("html_url"),
                "repo": repo
            })

        if debug:
            for pr in prs:
                print(f"[{pr['user']}] {pr['state'].capitalize()} PR: {pr['title']} at {pr['timestamp']}")

    except Exception as e:
        print(f"[Exception] Failed to fetch PRs: {e}")

    return {"commits": commits, "prs": prs}



owner = "emanalytic"
repo = "AutoStand-UP-Agent"

# Fetch commits and PRs in the last 24 hours
result = get_recent_commits(owner, repo, hours=84, debug=True)

# Now `result` contains two lists: commits and prs
commits = result['commits']
prs = result['prs']

# Example: Print the results
print("\nCommits:")
for c in commits:
    print(f"[{c['user']}] {c['timestamp']} → {c['message']}")

print("\nPRs:")
for pr in prs:
    print(f"[{pr['user']}] {pr['state'].capitalize()} PR: {pr['title']} at {pr['timestamp']}")
