from typing import List

from .connectors.jira import JiraConnector
from .connectors.perforce import PerforceConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer


class BugTriageAgent:
    def __init__(
        self, jira: JiraConnector, vcs, analyzer: CodeAnalyzer, review_platform: str
    ):
        self.jira = jira
        self.vcs = vcs
        self.analyzer = analyzer
        self.review_platform = review_platform

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
        review_url = self.create_review(key, summary, fix)
        print(f"Created review for {key}: {review_url}")

    def find_related_files(self, bug) -> List[str]:
        # Placeholder: use bug data to locate affected files
        return []

    def create_review(self, bug_key: str, summary: str, fix: dict):
        if self.review_platform == "github_pr" and isinstance(
            self.vcs, GitHubConnector
        ):
            branch = f"bugfix-{bug_key}".lower().replace(" ", "-")
            self.vcs.ensure_branch(branch, "main")
            github_pr = self.vcs.create_pull_request(
                title=f"Fix: {summary}",
                head=branch,
                base="main",
                body="Automated fix",
            )
            return github_pr.get("html_url")
        elif self.review_platform == "swarm" and isinstance(
            self.vcs, PerforceConnector
        ):
            review = self.vcs.create_swarm_review(summary, list(fix.keys()))
            return review.get("review_url")
        else:
            raise ValueError("Unsupported review platform for the configured VCS")
