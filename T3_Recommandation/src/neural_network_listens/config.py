import json
from pathlib import Path
from typing import Any, Dict


def load_config(path: str | Path | None = None) -> Dict[str, Any]:
    """Load JSON config with sane defaults."""
    default_path = Path(__file__).resolve().parent / "config.json"
    cfg_path = Path(path) if path else default_path
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found at {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)
