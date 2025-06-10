import requests


class GitHubConnector:
    def __init__(self, repo: str, token: str):
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    def create_pull_request(self, title: str, head: str, base: str, body: str):
        url = f"{self.base_url}/pulls"
        payload = {"title": title, "head": head, "base": base, "body": body}
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
