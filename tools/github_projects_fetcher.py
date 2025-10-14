import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv
from config import Config

load_dotenv()
config = Config()

class GitHubProjectsFetcher:
    """
    Fetches issues from GitHub Projects as an alternative data source to Notion.
    Supports both repository-specific and organization-wide project scanning.
    """
    
    def __init__(self):
        self.token = os.getenv("G_TOKEN")
        if not self.token:
            raise ValueError("G_TOKEN (GitHub token) not found in environment variables")

        self.mode = config.get("settings", "mode", fallback="repo").lower()
        self.organization = config.get("settings", "organization", fallback=None)
        self.owner = config.get("settings", "owner", fallback=None)
        self.repo = config.get("settings", "repo", fallback=None)
        self.hours = int(config.get("settings", "hours", fallback="24"))

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_issues(self) -> List[Dict]:
        """
        Fetches GitHub issues that can be used as task data similar to Notion.
        Returns a list of issues with relevant task information.
        """
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=self.hours)

        # if self.mode == "org":
        #     if not self.organization:
        #         raise ValueError("Organization mode selected but no organization name provided.")
        #     return self._fetch_org_issues(since)

        #if not (self.owner and self.repo):
        #    raise ValueError("Repo mode selected but owner/repo not specified.")

        repository = 'yca-ca-mvp'
        return self._fetch_repo_issues(self.organization, repository, since)

        #else:
        #    raise ValueError("Invalid mode. Choose 'org' or 'repo' in config.")

    def _fetch_org_issues(self, since: datetime) -> List[Dict]:
        """Fetch issues from all repositories in the organization."""
        repos = self._fetch_org_repositories()
        all_issues = []

        for repo in repos:
            print(repo)
            repo_name = repo["name"]
            issues = self._fetch_repo_issues(self.organization, repo_name, since)
            # Add repository context to each issue
            for issue in issues:
                issue["Repository"] = repo_name
            all_issues.extend(issues)

        return all_issues

    def _fetch_org_repositories(self) -> List[Dict]:
        """Fetch all repositories in the organization."""
        url = f"https://api.github.com/orgs/{self.organization}/repos"
        try:
            response = requests.get(url, headers=self.headers, params={"per_page": 100})
            response.raise_for_status()
            print(response.json())
            return response.json()
        except Exception as e:
            print(f"[GitHubProjectsFetcher] Error fetching repos: {e}")
            return []

    def _fetch_repo_issues(self, organization: str, repo: str, since: datetime) -> List[Dict]:
        """Fetch issues from a specific GitHub repository since a given datetime."""
        url = f"https://api.github.com/repos/{organization}/{repo}/issues"
        params = {
            "since": since.isoformat(),
            "state": "all",  # Include both open and closed issues
            "per_page": 100,
            "sort": "updated",
            "direction": "desc"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            raw_issues = response.json()
    
            issues = []
            for issue in raw_issues:
                # Skip pull requests (appear in issues endpoint but contain 'pull_request' key)
                if "pull_request" in issue:
                    continue
    
                # Extract main assignee
                assignee = issue.get("assignee")
                assignee_str = assignee.get("login") if assignee else "Unassigned"
    
                # Extract labels
                labels = issue.get("labels", [])
                label_names = [label.get("name", "") for label in labels]
    
                # Determine status based on issue state and labels (your own method)
                status = self._determine_status(issue.get("state", "open"), label_names)
    
                # Extract milestone due date if available
                milestone = issue.get("milestone")
                due_date = milestone.get("due_on") if milestone and milestone.get("due_on") else "No Due Date"
    
                # Truncate body if longer than 200 characters
                body = issue.get("body", "") or ""
                if len(body) > 200:
                    body = body[:200] + "..."
    
                issue_data = {
                    "Task Name": issue.get("title", "Untitled Issue"),
                    "Assignee": assignee_str,
                    "Status": status,
                    "Due Date": due_date,
                    "URL": issue.get("html_url", ""),
                    "Number": issue.get("number", 0),
                    "Labels": ", ".join(label_names) if label_names else "No Labels",
                    "Created": issue.get("created_at", ""),
                    "Updated": issue.get("updated_at", ""),
                    "Body": body,
                }
                issues.append(issue_data)
    
            return issues
    
        except Exception as e:
            print(f"[GitHubProjectsFetcher] Error fetching issues for {repo}: {e}")
            return []

    def _determine_status(self, state: str, labels: List[str]) -> str:
        """
        Determine task status based on GitHub issue state and labels.
        Maps GitHub issue states to Notion-like status values.
        """
        # Check for common status labels first
        label_lower = [label.lower() for label in labels]
        
        if any(label in label_lower for label in ["in progress", "in-progress", "working", "doing"]):
            return "In Progress"
        elif any(label in label_lower for label in ["blocked", "waiting", "hold", "on-hold"]):
            return "Blocked"
        elif any(label in label_lower for label in ["review", "under review", "pending review"]):
            return "Under Review"
        elif any(label in label_lower for label in ["testing", "qa", "test"]):
            return "Testing"
        elif state == "closed":
            return "Done"
        elif state == "open":
            return "To Do"
        else:
            return "Unknown"


# --- Example usage ---
if __name__ == "__main__":
    fetcher = GitHubProjectsFetcher()
    issues = fetcher.fetch_issues()
    print(f"Found {len(issues)} issues:")
    for issue in issues[:3]:  # Print first 3 for testing
        print(f"- {issue['Task Name']} ({issue['Status']}) - {issue['Assignee']}")
