# Code Learner Service

This microservice stores small snippets of source code and builds a vector index
using **LlamaIndex** with a **FAISS** backend. It can also generate code using
a local StarCoder model. The service exposes several HTTP endpoints:

- `POST /learn` – store a snippet with `file` and `content` keys.
- `GET /memory` – return all stored snippets.
- `POST /query` – search the FAISS index with `query` and return matching files.
- `POST /generate` – provide a `prompt` to get a StarCoder completion.

Run the service directly with `python service.py`. It listens on port `5001` by
default.
