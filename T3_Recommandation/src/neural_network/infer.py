from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict

import numpy as np
import torch
import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from db import get_connection  # noqa: E402
from data_loader import load_all  # noqa: E402
from model import PopularityRegressor  # noqa: E402
from preprocessing import PreprocessMeta, meta_from_dict, transform_features  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate top-N track recommendations.")
    parser.add_argument("--env", type=str, default=None, help="Path to .env file (defaults to root .env).")
    parser.add_argument("--model-path", type=Path, default=Path("T3_Recommandation/src/neural_network/artifacts/model.pt"))
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("T3_Recommandation/src/neural_network/artifacts/summary.txt"))
    return parser.parse_args()


def load_model(model_path: Path) -> Dict:
    state = torch.load(model_path, map_location="cpu", weights_only=False)
    meta: PreprocessMeta = meta_from_dict(state["meta"])
    config = state.get("config", {})
    return state, meta, config


def main():
    args = parse_args()
    state, meta, config = load_model(args.model_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with get_connection(args.env) as conn:
        tables = load_all(conn)

    X, item_ids = transform_features(tables, meta)
    x_tensor = torch.from_numpy(X).to(device)

    model = PopularityRegressor(
        input_dim=X.shape[1],
        hidden_dim=config.get("hidden_dim", 256),
        dropout=config.get("dropout", 0.1),
    ).to(device)
    model.load_state_dict(state["model_state_dict"])
    model.eval()

    with torch.no_grad():
        scores, _ = model(x_tensor)

    scores_np = scores.cpu().numpy()
    tracks_df = tables["tracks"][["track_id", "track_title", "track_listens"]].copy()
    tracks_df["score"] = scores_np

    top_df = (
        tracks_df.sort_values("score", ascending=False)
        .head(args.top_k)
        .reset_index(drop=True)
    )

    # Save to output file
    lines = [f"Top {args.top_k} recommended tracks (score desc):"]
    for idx, row in top_df.iterrows():
        title = row.get("track_title") or "Unknown title"
        listens = row.get("track_listens")
        lines.append(
            f"{idx+1:02d}. {title} | score={row['score']:.4f} | listens={listens}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
