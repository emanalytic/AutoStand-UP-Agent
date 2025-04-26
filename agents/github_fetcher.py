from datetime import datetime, timedelta, timezone
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_github_activity(owner, repo, hours=84, debug=False):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")

    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Fetch Commits
    commits = []
    try:
        commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"since": since.isoformat(), "until": now.isoformat(), "per_page": 100}
        response = requests.get(commit_url, headers=headers, params=params)
        response.raise_for_status()
        raw_commits = response.json()

        for commit in raw_commits:
            commit_data = commit.get("commit", {})
            author_info = commit.get("author", {}) or {}
            commit_author = commit_data.get("author", {}) or {}

            commits.append({
                "user": author_info.get("login") or commit_author.get("name", "unknown"),
                "message": commit_data.get("message", "").strip(),
                "timestamp": commit_author.get("date"),
                "url": commit.get("html_url"),
                "repo": repo
            })

    except Exception as e:
        print(f"[Exception] Failed to fetch commits: {e}")

    # Fetch PRs
    prs = []
    try:
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        pr_params = {"since": since.isoformat(), "state": "all", "per_page": 100}
        response = requests.get(pr_url, headers=headers, params=pr_params)
        response.raise_for_status()
        raw_items = response.json()

        for item in raw_items:
            if "pull_request" in item:
                prs.append({
                    "user": item.get("user", {}).get("login", "unknown"),
                    "title": item.get("title", "").strip(),
                    "state": item.get("state", "unknown"),
                    "timestamp": item.get("created_at", "unknown"),
                    "url": item.get("html_url"),
                    "repo": repo
                })

    except Exception as e:
        print(f"[Exception] Failed to fetch PRs: {e}")

    # 🧠 Group By User
    activities_by_user = {}

    for commit in commits:
        user = commit["user"]
        activities_by_user.setdefault(user, {"commits": [], "prs": []})
        activities_by_user[user]["commits"].append(commit)

    for pr in prs:
        user = pr["user"]
        activities_by_user.setdefault(user, {"commits": [], "prs": []})
        activities_by_user[user]["prs"].append(pr)

    if debug:
        for user, activities in activities_by_user.items():
            print(f"\n👤 User: {user}")
            for c in activities["commits"]:
                print(f"  - [Commit] {c['message']} ({c['timestamp']})")
            for p in activities["prs"]:
                print(f"  - [PR-{p['state'].capitalize()}] {p['title']} ({p['timestamp']})")

    return activities_by_user

def github_fetcher_node(state):
    owner = state["owner"]
    repo = state["repo"]
    hours = state.get("hours", 24)

    activities_by_user = fetch_github_activity(owner, repo, hours)

    return {"github_activity": activities_by_user}


