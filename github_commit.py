from datetime import datetime, timedelta, timezone
import requests

now = datetime.now(timezone.utc)
since = now - timedelta(hours=24)



owner = "emanalytic"
repo = "AutoStand-UP-Agent"
token = "..."

url = f"https://api.github.com/repos/{owner}/{repo}/commits"
headers = {"Authorization": f"token {token}"}
params = {
    "since": since.isoformat(),
    "until": now.isoformat(),
    "per_page": 100
}

response = requests.get(url, headers=headers, params=params)
  # Debug only — shows the raw JSON

commits = response.json()

for commit in commits:
    print(commit["commit"]["author"]["date"], commit["commit"]["message"])

