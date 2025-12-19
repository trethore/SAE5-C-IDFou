import json
from pathlib import Path
from typing import Any, Dict


def load_config(path: str | Path | None = None) -> Dict[str, Any]:
    """Charge la config JSON"""
    default_path = Path(__file__).resolve().parent / "config.json"
    cfg_path = Path(path) if path else default_path
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config introuvable  {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_split_config(cfg: Dict[str, Any]) -> Dict[str, float]:
    """Retourne les ratios train/test/val a partir de la config."""

    training_cfg = cfg.get("training", {})
    split_cfg = cfg.get("split", {})

    def _get(keys, default=None):
        for key in keys:
            if key in split_cfg:
                return split_cfg[key]
            if key in training_cfg:
                return training_cfg[key]
        return default

    train_ratio = _get(["train_ratio", "train_size"])
    test_ratio = _get(["test_ratio", "test_size"])
    val_ratio = _get(["val_ratio"], 0.0)

    if train_ratio is None and test_ratio is None:
        train_ratio, test_ratio = 0.8, 0.2
    elif train_ratio is None:
        train_ratio = 1.0 - test_ratio
    elif test_ratio is None:
        test_ratio = 1.0 - train_ratio

    if train_ratio < 0 or test_ratio < 0 or val_ratio < 0:
        raise ValueError("Les ratios de split doivent etre positifs.")
    if train_ratio + test_ratio > 1.0 + 1e-6:
        raise ValueError("La somme train + test doit etre <= 1.")

    return {
        "train_ratio": float(train_ratio),
        "test_ratio": float(test_ratio),
        "val_ratio": float(val_ratio),
    }
