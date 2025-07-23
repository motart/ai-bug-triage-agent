from typing import List

from .connectors.jira import JiraConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer


class BugTriageAgent:
    """Handle bug triage using Jira and GitHub."""

    def __init__(self, jira: JiraConnector, github: GitHubConnector, analyzer: CodeAnalyzer):
        self.jira = jira
        self.github = github
        self.analyzer = analyzer

    def triage(self, project_key: str):
        bugs = self.jira.get_open_bugs(project_key)
        for bug in bugs:
            self.process_bug(bug)

    def process_bug(self, bug) -> None:
        """Run analysis and create a review for a single bug."""
        key = bug["key"]
        fields = bug.get("fields", {})
        summary = fields.get("summary", "")
        description = fields.get("description", "") or ""
        files = self.find_related_files(summary, description)
        fix = self.analyzer.analyze_bug(summary, description, files)
        review_url = self.create_review(key, summary, fix)
        self.analyzer.remember(summary, description, fix)
        print(f"Created review for {key}: {review_url}")

    def find_related_files(self, title: str, description: str) -> List[str]:
        """Try to locate relevant files using bug text."""

        words = {
            w.strip(".,").lower()
            for w in (title + " " + description).split()
            if len(w) > 3
        }
        return self.github.search_code(list(words))

    def create_review(self, bug_key: str, summary: str, fix: dict) -> str:
        """Create a GitHub pull request with the suggested fix."""

        branch = f"bugfix-{bug_key}".lower().replace(" ", "-")
        self.github.ensure_branch(branch, "main")
        if fix:
            self.github.commit_files(branch, fix, "Automated fix")
        github_pr = self.github.create_pull_request(
            title=f"Fix: {summary}", head=branch, base="main", body="Automated fix"
        )
        return github_pr.get("html_url")
