import os
from dotenv import load_dotenv
from .connectors.jira import JiraConnector
from .connectors.perforce import PerforceConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer
from .agent import BugTriageAgent
from .terraform_infra import TerraformInfrastructure
from .connectors.jira_ws import JiraWebSocketClient



def main():
    load_dotenv()
    jira_url = os.environ.get("JIRA_URL")
    jira_user = os.environ.get("JIRA_USER")
    jira_token = os.environ.get("JIRA_TOKEN")
    project_key = os.environ.get("JIRA_PROJECT")

    if not all([jira_url, jira_user, jira_token, project_key]):
        raise SystemExit("JIRA_URL, JIRA_USER, JIRA_TOKEN and JIRA_PROJECT must be set")

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

    agent = BugTriageAgent(jira, vcs, analyzer, review_platform)

    tf_dir = os.environ.get("TERRAFORM_DIR")
    if tf_dir:
        infra = TerraformInfrastructure(tf_dir)
        infra.apply()

    ws_url = os.environ.get("JIRA_WS_URL")
    if ws_url:
        ws = JiraWebSocketClient(ws_url)
        ws.listen(agent.process_bug)
    else:
        agent.triage(project_key)


if __name__ == "__main__":
    main()
