import os
from dotenv import load_dotenv
from .connectors.jira import JiraConnector
from .connectors.github import GitHubConnector
from .analysis import CodeAnalyzer
from .memory import SimpleMemory
from .agent import BugTriageAgent
from .connectors.jira_ws import JiraWebSocketClient



def main():
    load_dotenv()
    jira_url = os.environ.get("JIRA_URL")
    jira_user = os.environ.get("JIRA_USER")
    jira_token = os.environ.get("JIRA_TOKEN")
    project_key = os.environ.get("JIRA_PROJECT")

    if not all([jira_url, jira_user, jira_token, project_key]):
        raise SystemExit(
            "JIRA_URL, JIRA_USER, JIRA_TOKEN and JIRA_PROJECT must be set"
        )

    jira = JiraConnector(jira_url, jira_user, jira_token)

    memory_file = os.environ.get("MEMORY_FILE", "memory.json")
    memory = SimpleMemory(path=memory_file)
    analyzer = CodeAnalyzer(memory=memory)

    repo = os.environ.get("GITHUB_REPO")
    gh_token = os.environ.get("GITHUB_TOKEN")
    if not repo or not gh_token:
        raise SystemExit("GITHUB_REPO and GITHUB_TOKEN must be set")

    github = GitHubConnector(repo, gh_token)
    agent = BugTriageAgent(jira, github, analyzer)
    ws_url = os.environ.get("JIRA_WS_URL")
    if ws_url:
        ws = JiraWebSocketClient(ws_url)
        ws.listen(agent.process_bug)
    else:
        agent.triage(project_key)


if __name__ == "__main__":
    main()

