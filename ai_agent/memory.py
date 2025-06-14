import json
import os
from pathlib import Path
from typing import List, Dict, Any

import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np


class SimpleMemory:
    """Store bug reports and solutions as vector embeddings."""

    def __init__(self, model_name: str | None = None, path: str | Path = "memory.json") -> None:
        self.model_name = model_name or os.environ.get("MEMORY_MODEL", "distilbert-base-uncased")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.path = Path(path)
        self.entries: List[Dict[str, Any]] = []
        if self.path.is_file():
            try:
                self.entries = json.loads(self.path.read_text())
            except json.JSONDecodeError:
                self.entries = []

    def _embed(self, text: str) -> List[float]:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs).last_hidden_state.mean(dim=1)
        return outputs.squeeze().tolist()

    def save(self) -> None:
        self.path.write_text(json.dumps(self.entries))

    def add(self, text: str, solution: Dict[str, str]) -> None:
        vec = self._embed(text)
        self.entries.append({"text": text, "solution": solution, "embedding": vec})
        self.save()

    def search(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.entries:
            return []
        query = np.array(self._embed(text))

        def similarity(v: List[float]) -> float:
            v = np.array(v)
            denom = np.linalg.norm(query) * np.linalg.norm(v)
            if denom == 0:
                return 0.0
            return float(np.dot(query, v) / denom)

        scored = [(similarity(e["embedding"]), e) for e in self.entries]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_k]]
