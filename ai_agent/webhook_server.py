import os
from typing import Optional

try:  # handle missing dependency gracefully
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def load_dotenv() -> None:  # type: ignore
        """Fallback when python-dotenv is not installed."""
        return

import json
from typing import Optional
from flask import Flask, request, jsonify

from .connectors.jira import JiraConnector
from .connectors.github import GitHubConnector
from .connectors.perforce import PerforceConnector
from .analysis import CodeAnalyzer
from .agent import BugTriageAgent
from .terraform_infra import TerraformInfrastructure


app = Flask(__name__)
agent: Optional[BugTriageAgent] = None


def init_agent() -> BugTriageAgent:
    """Initialize the bug triage agent from environment variables."""
    load_dotenv()
    jira_url = os.environ.get("JIRA_URL")
    jira_user = os.environ.get("JIRA_USER")
    jira_token = os.environ.get("JIRA_TOKEN")
    if not all([jira_url, jira_user, jira_token]):
        raise SystemExit("JIRA_URL, JIRA_USER and JIRA_TOKEN must be set")

    vcs_type = os.environ.get("VCS_TYPE", "git")
    review_platform = os.environ.get("REVIEW_PLATFORM")

    jira = JiraConnector(jira_url, jira_user, jira_token)
    analyzer = CodeAnalyzer()

    if vcs_type == "git":
        repo = os.environ.get("GITHUB_REPO")
        gh_token = os.environ.get("GITHUB_TOKEN")
        if not repo or not gh_token:
            raise SystemExit("GITHUB_REPO and GITHUB_TOKEN must be set for GitHub")
        vcs = GitHubConnector(repo, gh_token)
    else:
        p4port = os.environ.get("P4PORT")
        p4user = os.environ.get("P4USER")
        p4ticket = os.environ.get("P4TICKET")
        if not all([p4port, p4user, p4ticket]):
            raise SystemExit("P4PORT, P4USER and P4TICKET must be set for Perforce")
        vcs = PerforceConnector(p4port, p4user, p4ticket)

    if not review_platform:
        review_platform = "github_pr" if vcs_type == "git" else "swarm"

    return BugTriageAgent(jira, vcs, analyzer, review_platform)


@app.route("/webhook", methods=["POST"])
def webhook() -> tuple:
    """Handle Jira webhook calls for newly created bug issues."""
    payload = request.get_json(force=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid payload"}), 400

    issue = payload.get("issue")
    if not issue:
        return jsonify({"error": "no issue payload"}), 400

    event = payload.get("issue_event_type_name") or payload.get("webhookEvent")
    if event and "created" in str(event).lower():
        issuetype = (
            issue.get("fields", {})
            .get("issuetype", {})
            .get("name", "")
            .lower()
        )
        if issuetype == "bug":
            agent.process_bug(issue)
            return jsonify({"status": "processed"}), 200
        return jsonify({"status": "ignored", "reason": "not a bug"}), 200
    return jsonify({"status": "ignored", "reason": "not a creation event"}), 200


def main() -> None:
    global agent
    agent = init_agent()

    tf_dir = os.environ.get("TERRAFORM_DIR")
    if tf_dir:
        infra = TerraformInfrastructure(tf_dir)
        infra.apply()

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting webhook server on {host}:{port}")
    app.run(host=host, port=port)



if __name__ == "__main__":
    main()
