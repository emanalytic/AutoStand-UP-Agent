import os
from typing import List, Dict
from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv
from config import Config

config = Config()
load_dotenv()

class GitHubFetcher:
    def __init__(self):
        self.token =  os.getenv("G_TOKEN")
        self.owner = config.get('settings', 'owner')
        self.repo = config.get('settings', 'repo')
        self.hours = int(config.get('settings', 'hours'))
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_activity(self) -> Dict[str, Dict[str, str]]:
        """Fetch commits and PRs from GitHub repository."""
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=self.hours)

        commits = self._fetch_commits(since, now)
        prs = self._fetch_pull_requests(self.owner, self.repo, since)

        activities_by_user = self._group_activities(commits, prs)

        return activities_by_user

    def _fetch_commits(self, since: datetime, until: datetime) -> List[Dict]:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits"
        params = {"since": since.isoformat(), "until": until.isoformat(), "per_page": 100}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            raw_commits = response.json()

            commits = []
            for commit in raw_commits:
                commit_data = commit.get("commit", {})
                author_info = commit.get("author", {}) or {}
                commit_author = commit_data.get("author", {}) or {}

                commits.append({
                    "user": author_info.get("login") or commit_author.get("name", "unknown"),
                    "message": commit_data.get("message", "").strip(),
                })
            return commits
        except Exception as e:
            print(f"[GitHubFetcher] Error fetching commits: {e}")
            return []

    def _fetch_pull_requests(self, owner: str, repo: str, since: datetime) -> List[Dict]:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {"since": since.isoformat(), "state": "all", "per_page": 100}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            raw_items = response.json()

            prs = []
            for item in raw_items:
                if "pull_request" in item:
                    prs.append({
                        "user": item.get("user", {}).get("login", "unknown"),
                        "title": item.get("title", "").strip(),
                        "state": item.get("state", "unknown"),
                    })
            return prs
        except Exception as e:
            print(f"[GitHubFetcher] Error fetching PRs: {e}")
            return []

    def _group_activities(self, commits: List[Dict], prs: List[Dict]) -> Dict[str, Dict[str, str]]:
        activities_by_user = {}

        for commit in commits:
            user = commit["user"]
            activities_by_user.setdefault(user, {"commits": [], "prs": []})
            activities_by_user[user]["commits"].append(commit["message"])

        for pr in prs:
            user = pr["user"]
            activities_by_user.setdefault(user, {"commits": [], "prs": []})
            activities_by_user[user]["prs"].append(pr["title"])

        collective_act = {}
        for user, activities in activities_by_user.items():
            collective_act[user] = {
                "commits": "\n".join(activities["commits"]) if activities["commits"] else "No commits in the last 24 hours.",
                "prs": "\n".join(activities["prs"]) if activities["prs"] else "No PRs in the last 24 hours."
            }

        return collective_act


d = GitHubFetcher()
print(d.fetch_activity())