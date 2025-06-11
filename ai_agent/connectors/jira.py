import os
import requests


class JiraConnector:
    def __init__(self, base_url: str | None, username: str | None, token: str | None):
        """Simple wrapper around the Jira REST API."""
        if not base_url:
            raise ValueError("JIRA_URL environment variable is required")
        if not username or not token:
            raise ValueError("JIRA_USER and JIRA_TOKEN must be set")


        self.base_url = base_url.rstrip("/")
        self.auth = (username, token)

    def get_open_bugs(self, project_key: str):
        """Fetch open bug issues from Jira.

        Parameters
        ----------
        project_key: str
            Key of the Jira project. Jira keys are typically uppercase, but
            any leading/trailing whitespace will be stripped and the key will
            be converted to uppercase automatically.
        """

        project_key = project_key.strip().upper()
        jql = f"project={project_key} AND issuetype=Bug AND status!=Done"
        url = f"{self.base_url}/rest/api/2/search"
        response = requests.get(url, params={"jql": jql}, auth=self.auth)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            msg = response.text.strip()
            raise requests.HTTPError(
                f"Failed to query Jira: {msg or response.reason}",
                response=response,
            ) from exc
        data = response.json()
        return data.get("issues", [])
