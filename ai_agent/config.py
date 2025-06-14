import json
import os
from pathlib import Path
from typing import Any, Dict


def load_config(path: str | None = None) -> Dict[str, Any]:
    """Load configuration from *path* if it exists.

    The file is expected to contain JSON with keys matching the lowercase
    environment variable names used by the application. If the file cannot be
    read or parsed, an empty dictionary is returned.
    """
    file_path = Path(path or "config.json")
    if not file_path.is_file():
        return {}
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fail silently and just use environment variables
        return {}
