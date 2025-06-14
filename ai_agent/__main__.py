import os
from dotenv import load_dotenv
from .connectors.jira import JiraConnector
from .connectors.perforce import PerforceConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer
from .agent import BugTriageAgent
from .terraform_infra import TerraformInfrastructure
from .connectors.jira_ws import JiraWebSocketClient
from .config import load_config



def main():
    load_dotenv()
    config = load_config(os.environ.get("CONFIG_FILE"))
    jira_url = os.environ.get("JIRA_URL") or config.get("jira_url")
    jira_user = os.environ.get("JIRA_USER") or config.get("jira_user")
    jira_token = os.environ.get("JIRA_TOKEN") or config.get("jira_token")
    project_key = os.environ.get("JIRA_PROJECT") or config.get("jira_project")

    if not all([jira_url, jira_user, jira_token, project_key]):
        raise SystemExit(
            "JIRA_URL, JIRA_USER, JIRA_TOKEN and JIRA_PROJECT must be set"
        )

    vcs_type = os.environ.get("VCS_TYPE") or config.get("vcs_type", "git")
    review_platform = os.environ.get("REVIEW_PLATFORM") or config.get("review_platform")

    jira = JiraConnector(jira_url, jira_user, jira_token)
    analyzer = CodeAnalyzer()

    if vcs_type == "git":
        repo = os.environ.get("GITHUB_REPO") or config.get("github_repo")
        gh_token = os.environ.get("GITHUB_TOKEN") or config.get("github_token")
        if not repo or not gh_token:
            raise SystemExit(
                "GITHUB_REPO and GITHUB_TOKEN must be set for GitHub"
            )

        vcs = GitHubConnector(repo, gh_token)
    else:
        p4port = os.environ.get("P4PORT") or config.get("p4port")
        p4user = os.environ.get("P4USER") or config.get("p4user")
        p4ticket = os.environ.get("P4TICKET") or config.get("p4ticket")
        if not all([p4port, p4user, p4ticket]):
            raise SystemExit(
                "P4PORT, P4USER and P4TICKET must be set for Perforce"
            )
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
