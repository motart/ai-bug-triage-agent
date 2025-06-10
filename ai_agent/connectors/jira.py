import os
import requests


class JiraConnector:
    def __init__(self, base_url: str, username: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, token)

    def get_open_bugs(self, project_key: str):
        """Fetch open bug issues from Jira."""
        jql = f"project={project_key} AND issuetype=Bug AND status!=Done"
        url = f"{self.base_url}/rest/api/2/search"
        response = requests.get(url, params={"jql": jql}, auth=self.auth)
        response.raise_for_status()
        data = response.json()
        return data.get("issues", [])
