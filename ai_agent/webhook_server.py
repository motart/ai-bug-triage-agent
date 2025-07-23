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
from .analysis import CodeAnalyzer
from .memory import SimpleMemory
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

    jira = JiraConnector(jira_url, jira_user, jira_token)

    memory_file = os.environ.get("MEMORY_FILE", "memory.json")
    memory = SimpleMemory(path=memory_file)
    analyzer = CodeAnalyzer(memory=memory)

    repo = os.environ.get("GITHUB_REPO")
    gh_token = os.environ.get("GITHUB_TOKEN")
    if not repo or not gh_token:
        raise SystemExit("GITHUB_REPO and GITHUB_TOKEN must be set")

    github = GitHubConnector(repo, gh_token)

    return BugTriageAgent(jira, github, analyzer)


@app.route("/webhook", methods=["POST", "GET"])
def webhook() -> tuple:
    """Handle Jira webhook calls for newly created bug issues."""
    if request.method == "GET":
        if "payload" in request.args:
            try:
                payload = json.loads(request.args["payload"])
            except json.JSONDecodeError:
                payload = {}
        else:
            payload = request.args.to_dict()
    else:
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
            # Show the raw issue for debugging purposes when a ticket is created
            print(f"Received new issue via webhook: {json.dumps(issue)}")
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

