import os
from .connectors.jira import JiraConnector
from .connectors.perforce import PerforceConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer
from .agent import BugTriageAgent
from .aws_infra import AWSInfrastructure


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

    infra = None
    ami_id = os.environ.get("AMI_ID")
    if ami_id:
        infra = AWSInfrastructure()
        infra.launch_ec2_instance(
            ami_id=ami_id,
            instance_type=os.environ.get("INSTANCE_TYPE", "t3.micro"),
            key_name=os.environ.get("KEY_NAME"),
            security_group_ids=os.environ.get("SECURITY_GROUP_IDS", "").split()
            if os.environ.get("SECURITY_GROUP_IDS")
            else None,
        )

    agent = BugTriageAgent(jira, vcs, analyzer)
    agent.triage(project_key)


if __name__ == "__main__":
    main()
