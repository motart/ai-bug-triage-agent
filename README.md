# ai-bug-triage-agent

This project provides a skeleton implementation for an AI-driven bug triage agent. The agent fetches bugs from Jira, analyzes the code base, suggests fixes, and creates code reviews in GitHub or Perforce Swarm. Infrastructure is created on AWS using Terraform, and the agent can be extended to learn from reviewer feedback.


## Features
- **Jira Integration** – Retrieve open bugs from a Jira project using the REST API.
- **Code Analysis** – Analyze bug descriptions and affected files to generate a suggested fix (placeholder logic).
- **Version Control Support** – Connect to GitHub or Perforce and create pull requests or Swarm reviews.
- **Extensibility** – Placeholder hooks for incorporating AI models and learning from reviewer feedback.

## Running the Agent

Configuration is handled via environment variables.  Copy `.env.example` to
`.env` and fill in the appropriate values:

```
cp .env.example .env
# edit .env with your editor of choice
```

The variables include:

- `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN`, `JIRA_PROJECT` – Jira connection details.
- `VCS_TYPE` – `git` for GitHub (default) or `p4` for Perforce.
- For GitHub: `GITHUB_REPO`, `GITHUB_TOKEN`.
- For Perforce: `P4PORT`, `P4USER`, `P4TICKET`.
- To provision infrastructure with Terraform, set `TERRAFORM_DIR` to the
  directory containing your Terraform configuration.


Run the agent and the variables in `.env` will be loaded automatically:

```bash
python -m ai_agent
```

## Terraform Infrastructure

Infrastructure is created with Terraform using the
`TerraformInfrastructure` helper in `ai_agent/terraform_infra.py`. Set the
`TERRAFORM_DIR` environment variable to a directory containing Terraform
configuration files. The helper will run `terraform init` and `terraform apply
-auto-approve` prior to running the agent.

## Notes
This codebase provides a starting point only. Actual integration with Jira, Perforce, GitHub, and AWS requires additional configuration and authentication setup. The code analysis and learning components are simplified placeholders.
