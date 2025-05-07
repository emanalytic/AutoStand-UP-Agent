import os
from typing import List, Dict
from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv
from config import Config

load_dotenv()
config = Config()

class GitHubFetcher:
    def __init__(self):
        self.token = os.getenv("G_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")

        self.mode = config.get("settings", "mode", fallback="repo").lower()
        self.organization = config.get("settings", "organization", fallback=None)
        self.owner = config.get("settings", "owner", fallback=None)
        self.repo = config.get("settings", "repo", fallback=None)
        self.hours = int(config.get("settings", "hours", fallback="24"))

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_activity(self) -> Dict[str, Dict[str, str]]:
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=self.hours)

        if self.mode == "org":
            if not self.organization:
                raise ValueError("Organization mode selected but no organization name provided.")
            return self._fetch_org_activity(since, now)

        elif self.mode == "repo":
            if not (self.owner and self.repo):
                raise ValueError("Repo mode selected but owner/repo not specified.")
            commits = self._fetch_commits(self.owner, self.repo, since, now)
            prs = self._fetch_pull_requests(self.owner, self.repo, since)
            return self._format_grouped(self._group_activities(commits, prs))

        else:
            raise ValueError("Invalid mode. Choose 'org' or 'repo' in config.")

    def _fetch_org_activity(self, since: datetime, until: datetime) -> Dict[str, Dict[str, str]]:
        repos = self._fetch_org_repositories()
        all_activities = {}

        for repo in repos:
            repo_name = repo["name"]
            commits = self._fetch_commits(self.organization, repo_name, since, until)
            prs = self._fetch_pull_requests(self.organization, repo_name, since)
            grouped = self._group_activities(commits, prs)

            for user, data in grouped.items():
                if user not in all_activities:
                    all_activities[user] = {"commits": [], "prs": []}
                all_activities[user]["commits"].extend(data["commits"])
                all_activities[user]["prs"].extend(data["prs"])

        return self._format_grouped(all_activities)

    def _fetch_org_repositories(self) -> List[Dict]:
        url = f"https://api.github.com/orgs/{self.organization}/repos"
        try:
            response = requests.get(url, headers=self.headers, params={"per_page": 100})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[GitHubFetcher] Error fetching repos: {e}")
            return []

    def _fetch_commits(self, owner: str, repo: str, since: datetime, until: datetime) -> List[Dict]:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
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
            print(f"[GitHubFetcher] Error fetching commits for {repo}: {e}")
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
            print(f"[GitHubFetcher] Error fetching PRs for {repo}: {e}")
            return []

    def _group_activities(self, commits: List[Dict], prs: List[Dict]) -> Dict[str, Dict[str, List[str]]]:
        activities_by_user = {}

        for commit in commits:
            user = commit["user"]
            activities_by_user.setdefault(user, {"commits": [], "prs": []})
            activities_by_user[user]["commits"].append(commit["message"])

        for pr in prs:
            user = pr["user"]
            activities_by_user.setdefault(user, {"commits": [], "prs": []})
            activities_by_user[user]["prs"].append(pr["title"])

        return activities_by_user

    def _format_grouped(self, grouped: Dict[str, Dict[str, List[str]]]) -> Dict[str, Dict[str, str]]:
        return {
            user: {
                "commits": "\n".join(data["commits"]) if data["commits"] else "No commits.",
                "prs": "\n".join(data["prs"]) if data["prs"] else "No PRs."
            } for user, data in grouped.items()
        }


# --- Example usage ---
if __name__ == "__main__":
    fetcher = GitHubFetcher()
    activity = fetcher.fetch_activity()
    print(activity)
