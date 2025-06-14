"""Bug analyzer and learning microservice."""

from flask import Flask, request, jsonify

from ai_agent.analysis import CodeAnalyzer
from ai_agent.memory import SimpleMemory

app = Flask(__name__)
memory = SimpleMemory(path="memory.json")
analyzer = CodeAnalyzer(memory=memory)


@app.route("/analyze", methods=["POST"])
def analyze_bug():
    """Return suggested code fixes for a bug report."""
    payload = request.get_json(force=True)
    title = payload.get("title", "")
    description = payload.get("description", "")
    files = payload.get("files", [])
    fixes = analyzer.analyze_bug(title, description, files)
    return jsonify(fixes)


@app.route("/remember", methods=["POST"])
def remember_fix():
    """Remember a bug fix for future reuse."""
    payload = request.get_json(force=True)
    title = payload.get("title", "")
    description = payload.get("description", "")
    fix = payload.get("fix", {})
    analyzer.remember(title, description, fix)
    return jsonify({"status": "stored"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
