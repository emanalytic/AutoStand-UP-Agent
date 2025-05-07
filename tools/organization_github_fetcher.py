import os
from typing import List, Dict
from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv

load_dotenv()

class GitHubFetcher:
    def __init__(self):
        self.token = os.getenv("G_TOKEN")
        self.organization = config.get('settings', 'organization')
        self.hours = int(config.get('settings', 'hours'))
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_activity(self) -> Dict[str, Dict[str, str]]:
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=self.hours)

        all_repos = self._fetch_org_repositories()
        activities_by_user = {}
        activities_by_repo = {}

        for repo in all_repos:
            repo_name = repo['name']
            commits = self._fetch_commits(self.organization, repo_name, since, now)
            prs = self._fetch_pull_requests(self.organization, repo_name, since)
            repo_activities = self._group_activities(commits, prs)

            if repo_name not in activities_by_repo:
                activities_by_repo[repo_name] = {}

            for user, acts in repo_activities.items():
                if user not in activities_by_user:
                    activities_by_user[user] = {"commits": [], "prs": []}
                activities_by_user[user]["commits"].extend(acts["commits"])
                activities_by_user[user]["prs"].extend(acts["prs"])

            for user, acts in repo_activities.items():
                if user not in activities_by_repo[repo_name]:
                    activities_by_repo[repo_name][user] = {"commits": [], "prs": []}
                activities_by_repo[repo_name][user]["commits"].extend(acts["commits"])
                activities_by_repo[repo_name][user]["prs"].extend(acts["prs"])

        collective_act = {}

        for user, activities in activities_by_user.items():
            collective_act[user] = {
                "organization": self.organization,
                "repository": repo_name,
                "commits": "\n".join(activities["commits"]) if activities["commits"] else "No commits.",
                "commits_count": len(activities["commits"]),
                "prs": "\n".join(activities["prs"]) if activities["prs"] else "No PRs."
            }

        return collective_act
        #return [activities_by_repo, activities_by_user, collective_act]

    def _fetch_org_repositories(self) -> List[Dict]:
        url = f"https://api.github.com/orgs/{self.organization}/repos"
        params = {"per_page": 100, "type": "all"}
        try:
            response = requests.get(url, headers=self.headers, params=params)
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

# fetcher = GitHubFetcher()
# print(fetcher.fetch_activity())
#example output
# {
#     'organization': '9c56ff3b94',  # Anonymized repository name
#     'repository': '9c56ff3b94',    # Anonymized repository name
#     'user': '4e9a16a9cf',          # Anonymized user name
#     'commits': 'fix\nUpdate PaymentController.cs\nUpdate PaymentController.cs\nreturn also products\nUpdate PaymentController.cs\ndecimal -> int\nSolid principle for payments\nPayment Api',
#     'commits_count': 8,
#     'prs': 'No PRs.'
# },
# {
#     'organization': '320c7bcdcd',  # Anonymized repository name
#     'repository': '320c7bcdcd',    # Anonymized repository name
#     'user': 'd2458ff9a1',          # Anonymized user name
#     'commits': 'small fixes\nfix\nAureyo fix\ndeducting points + fixes\nfix\nquantity of points\nfix\nfix\nfix\nfix\nfix\nSave user subscription\nprice is number\naureyoPoints',
#     'commits_count': 13,
#     'prs': 'No PRs.'
# },
# {
#     'organization': 'cf15e1f88d',  # Anonymized repository name
#     'repository': 'cf15e1f88d',    # Anonymized repository name
#     'user': '2b416e3405',          # Anonymized user name
#     'commits': 'fix\nUpdate PaymentController.cs\nUpdate PaymentController.cs\nreturn also products\nUpdate PaymentController.cs\ndecimal -> int\nSolid principle for payments\nPayment Api\nsmall fixes\nfix\nAureyo fix\ndeducting points + fixes\nfix\nquantity of points\nfix\nfix\nfix\nfix\nfix\nSave user subscription\nprice is number\naureyoPoints',
#     'commits_count': 22,
#     'prs': 'No PRs.'
# }
