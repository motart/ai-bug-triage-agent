"""Microservice for learning and querying code snippets."""

import os
from typing import Any

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

from .vector_index import CodeVectorIndex


app = Flask(__name__)
code_memory: dict[str, str] = {}
vector_index = CodeVectorIndex()

MODEL_NAME = os.getenv("CODE_MODEL", "bigcode/starcoderbase-1b")
tokenizer: AutoTokenizer | None = None
model: AutoModelForCausalLM | None = None


def _load_model() -> None:
    global tokenizer, model
    if tokenizer is None or model is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)


def generate_code(prompt: str, max_new_tokens: int = 64) -> str:
    """Generate code completion using StarCoder (or compatible) model."""
    _load_model()
    assert tokenizer is not None and model is not None
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


@app.route("/learn", methods=["POST"])
def learn_code():
    """Store code content keyed by file name."""
    payload = request.get_json(force=True)
    filename = payload.get("file")
    content = payload.get("content", "")
    if not filename:
        return jsonify({"error": "file required"}), 400
    code_memory[filename] = content
    vector_index.add_code(filename, content)
    return jsonify({"status": "stored", "file": filename}), 200


@app.route("/memory", methods=["GET"])
def get_memory():
    """Return known code snippets."""
    return jsonify(code_memory)


@app.route("/query", methods=["POST"])
def query_code() -> Any:
    """Search indexed code snippets for a text query."""
    payload = request.get_json(force=True)
    query = payload.get("query", "")
    files = vector_index.query(query)
    return jsonify({"files": files})


@app.route("/generate", methods=["POST"])
def generate() -> Any:
    """Generate code with the selected model."""
    payload = request.get_json(force=True)
    prompt = payload.get("prompt", "")
    result = generate_code(prompt)
    return jsonify({"completion": result})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
