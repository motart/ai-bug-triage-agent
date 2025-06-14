"""Simple microservice for learning code context."""

from flask import Flask, request, jsonify

app = Flask(__name__)
code_memory: dict[str, str] = {}


@app.route("/learn", methods=["POST"])
def learn_code():
    """Store code content keyed by file name."""
    payload = request.get_json(force=True)
    filename = payload.get("file")
    content = payload.get("content", "")
    if not filename:
        return jsonify({"error": "file required"}), 400
    code_memory[filename] = content
    return jsonify({"status": "stored", "file": filename}), 200


@app.route("/memory", methods=["GET"])
def get_memory():
    """Return known code snippets."""
    return jsonify(code_memory)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
