import os
from pathlib import Path
from typing import List, Dict

from transformers import AutoModelForCausalLM, AutoTokenizer
from .memory import SimpleMemory


class CodeAnalyzer:
    """Analyze bug reports with an open source language model and optional memory."""

    def __init__(self, model_name: str | None = None, memory: SimpleMemory | None = None) -> None:
        self.model_name = model_name or os.environ.get("HF_MODEL", "gpt2")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.memory = memory

    def analyze_bug(self, title: str, description: str, files: List[str]) -> Dict[str, str]:
        """Use an LLM to suggest code fixes for the given files."""

        bug_text = f"Bug Title: {title}\nDescription: {description}\n".strip()
        fixes: Dict[str, str] = {}
        if self.memory:
            # Attempt to reuse existing solutions
            past = self.memory.search(bug_text, top_k=1)
            if past:
                return past[0]["solution"]
        for file in files:
            try:
                code = Path(file).read_text()
            except OSError:
                code = ""
            prompt = (
                bug_text
                + f"\nFile: {file}\nCode:\n{code}\n# Suggested patch:\n"
            )
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
            output_ids = self.model.generate(
                input_ids, max_new_tokens=120, do_sample=True, top_p=0.95
            )
            text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            patch = text.split("# Suggested patch:")[-1].strip()
            fixes[file] = patch
        if self.memory:
            self.memory.add(bug_text, fixes)
        return fixes

    def remember(self, title: str, description: str, fix: Dict[str, str]) -> None:
        """Persist the bug description and resulting fix."""
        if self.memory:
            bug_text = f"Bug Title: {title}\nDescription: {description}\n".strip()
            self.memory.add(bug_text, fix)

