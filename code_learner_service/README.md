# Code Learner Service

This microservice stores small snippets of source code for later reference. It exposes two HTTP endpoints using Flask:

- `POST /learn` – submit a JSON payload with `file` and `content` keys to store code content.
- `GET /memory` – returns all stored code snippets as JSON.

Run the service directly with `python service.py`. It listens on port `5001` by default.
