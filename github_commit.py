from datetime import datetime, timedelta, timezone
import requests

now = datetime.now(timezone.utc)
since = now - timedelta(hours=24)



owner = "emanalytic"
repo = "AutoStand-UP-Agent"
token = "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"

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

