# Bug Analyzer + Learner Service

This service wraps the existing `CodeAnalyzer` from the main project and exposes simple HTTP endpoints:

- `POST /analyze` – accepts `title`, `description`, and optional `files` to return suggested fixes.
- `POST /remember` – store a provided fix so that future analysis can reuse it.

Start the server with `python service.py`. It listens on port `5002`.
