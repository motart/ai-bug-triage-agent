import os
from pathlib import Path
from typing import List, Dict

from transformers import AutoModelForCausalLM, AutoTokenizer


class CodeAnalyzer:
    """Analyze bug reports with an open source language model."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or os.environ.get("HF_MODEL", "gpt2")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

    def analyze_bug(self, title: str, description: str, files: List[str]) -> Dict[str, str]:
        """Use an LLM to suggest code fixes for the given files."""

        bug_text = f"Bug Title: {title}\nDescription: {description}\n".strip()
        fixes: Dict[str, str] = {}
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
        return fixes
