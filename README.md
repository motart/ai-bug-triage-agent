# ai-bug-triage-agent

This project provides a skeleton implementation for an AI-driven bug triage agent. The goal of the agent is to fetch bugs from Jira, analyze the code base, suggest fixes, and create code reviews in either GitHub or Perforce Swarm. The agent is designed to run on AWS infrastructure and can be extended to learn from reviewer feedback.

## Features
- **Jira Integration** – Retrieve open bugs from a Jira project using the REST API.
- **Code Analysis** – Analyze bug descriptions and affected files to generate a suggested fix (placeholder logic).
- **Version Control Support** – Connect to GitHub or Perforce and create pull requests or Swarm reviews.
- **Extensibility** – Placeholder hooks for incorporating AI models and learning from reviewer feedback.

## Running the Agent

Set the following environment variables as needed:

- `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN`, `JIRA_PROJECT` – Jira connection details.
- `VCS_TYPE` – `git` for GitHub (default) or `p4` for Perforce.
- For GitHub: `GITHUB_REPO`, `GITHUB_TOKEN`.
- For Perforce: `P4PORT`, `P4USER`, `P4TICKET`.
- For AWS EC2 provisioning: set `AMI_ID` and optional `INSTANCE_TYPE`,
  `KEY_NAME`, `SECURITY_GROUP_IDS`.

Run the agent with:

```bash
python -m ai_agent
```

## AWS Infrastructure

The `AWSInfrastructure` helper in `ai_agent/aws_infra.py` demonstrates how the
agent could provision resources on AWS. It currently exposes a simple method for
launching an EC2 instance. Configure these environment variables when using the
helper:

- `AWS_REGION` – AWS region to operate in (default `us-east-1`).
- `AMI_ID` – AMI ID used to launch the EC2 instance.
- `INSTANCE_TYPE` – Instance size (optional, defaults to `t3.micro`).
- `KEY_NAME` and `SECURITY_GROUP_IDS` – Optional EC2 parameters.

Additional infrastructure (S3 buckets, IAM roles, etc.) can be added in a
similar manner using `boto3` as requirements evolve.

## Notes
This codebase provides a starting point only. Actual integration with Jira, Perforce, GitHub, and AWS requires additional configuration and authentication setup. The code analysis and learning components are simplified placeholders.
