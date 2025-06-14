import base64
import requests


class GitHubConnector:
    def __init__(self, repo: str, token: str):
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    def ensure_branch(self, branch: str, base: str = "main") -> None:
        """Create the branch if it does not exist."""
        ref_url = f"{self.base_url}/git/ref/heads/{branch}"
        resp = requests.get(ref_url, headers=self.headers)
        if resp.status_code == 404:
            base_ref_url = f"{self.base_url}/git/ref/heads/{base}"
            base_resp = requests.get(base_ref_url, headers=self.headers)
            base_resp.raise_for_status()
            sha = base_resp.json().get("object", {}).get("sha")
            create_url = f"{self.base_url}/git/refs"
            payload = {"ref": f"refs/heads/{branch}", "sha": sha}
            create_resp = requests.post(create_url, json=payload, headers=self.headers)
            create_resp.raise_for_status()

    def commit_files(self, branch: str, files: dict[str, str], message: str) -> None:
        """Create or update files on the given branch."""

        for path, content in files.items():
            url = f"{self.base_url}/contents/{path}"
            get_resp = requests.get(url, params={"ref": branch}, headers=self.headers)
            data = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch,
            }
            if get_resp.status_code == 200:
                sha = get_resp.json().get("sha")
                if sha:
                    data["sha"] = sha
            put_resp = requests.put(url, json=data, headers=self.headers)
            put_resp.raise_for_status()

    def create_pull_request(self, title: str, head: str, base: str, body: str):
        url = f"{self.base_url}/pulls"
        payload = {"title": title, "head": head, "base": base, "body": body}
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def search_code(self, keywords: list[str], max_results: int = 5) -> list[str]:
        """Search the repository for files containing the given keywords."""

        results: list[str] = []
        for word in keywords:
            query = f"{word} repo:{self.repo}"
            url = "https://api.github.com/search/code"
            resp = requests.get(url, params={"q": query}, headers=self.headers)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for item in data.get("items", [])[:max_results]:
                path = item.get("path")
                if path and path not in results:
                    results.append(path)
        return results
