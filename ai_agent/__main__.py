import os
from .connectors.jira import JiraConnector
from .connectors.perforce import PerforceConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer
from .agent import BugTriageAgent
from .terraform_infra import TerraformInfrastructure


def main():
    jira_url = os.environ.get("JIRA_URL")
    jira_user = os.environ.get("JIRA_USER")
    jira_token = os.environ.get("JIRA_TOKEN")
    project_key = os.environ.get("JIRA_PROJECT")
    vcs_type = os.environ.get("VCS_TYPE", "git")

    jira = JiraConnector(jira_url, jira_user, jira_token)
    analyzer = CodeAnalyzer()

    if vcs_type == "git":
        repo = os.environ.get("GITHUB_REPO")
        gh_token = os.environ.get("GITHUB_TOKEN")
        vcs = GitHubConnector(repo, gh_token)
    else:
        p4port = os.environ.get("P4PORT")
        p4user = os.environ.get("P4USER")
        p4ticket = os.environ.get("P4TICKET")
        vcs = PerforceConnector(p4port, p4user, p4ticket)

    tf_dir = os.environ.get("TERRAFORM_DIR")
    if tf_dir:
        infra = TerraformInfrastructure(tf_dir)
        infra.apply()

    agent = BugTriageAgent(jira, vcs, analyzer)
    agent.triage(project_key)


if __name__ == "__main__":
    main()
