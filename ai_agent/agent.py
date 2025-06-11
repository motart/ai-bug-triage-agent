from typing import List

from .connectors.jira import JiraConnector
from .connectors.perforce import PerforceConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer


class BugTriageAgent:
    def __init__(self, jira: JiraConnector, vcs, analyzer: CodeAnalyzer):
        self.jira = jira
        self.vcs = vcs
        self.analyzer = analyzer

    def triage(self, project_key: str):
        bugs = self.jira.get_open_bugs(project_key)
        for bug in bugs:
            self.process_bug(bug)

    def process_bug(self, bug) -> None:
        """Run analysis and create a review for a single bug."""
        key = bug["key"]
        summary = bug["fields"]["summary"]
        files = self.find_related_files(bug)
        fix = self.analyzer.analyze_bug(summary, files)
        review_url = self.create_review(summary, fix)
        print(f"Created review for {key}: {review_url}")

    def find_related_files(self, bug) -> List[str]:
        # Placeholder: use bug data to locate affected files
        return []

    def create_review(self, summary: str, fix: dict):
        if isinstance(self.vcs, GitHubConnector):
            pr = self.vcs.create_pull_request(
                title=f"Fix: {summary}",
                head="bugfix",  # placeholder branch
                base="main",
                body="Automated fix",
            )
            return pr.get("html_url")
        elif isinstance(self.vcs, PerforceConnector):
            review = self.vcs.create_swarm_review(summary, list(fix.keys()))
            return review.get("review_url")
        else:
            raise ValueError("Unsupported VCS")
