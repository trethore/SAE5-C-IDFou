from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from config import load_config
from data_loader import load_track_by_id
from db import get_connection, get_sqlalchemy_engine
from model import ListenRegressor
from preprocessing import meta_from_dict, transform_tracks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prédit les listens pour un track_id donné.")
    parser.add_argument("track_id", type=str, help="UUID of the track to predict.")
    parser.add_argument("--env", type=str, default=None, help="Path to .env (default: repo root .env)")
    parser.add_argument("--config", type=str, default=None, help="Path to config.json (default: package config.json)")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model.pt (default: artifacts/model.pt)")
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = load_config(args.config)
    artifacts_dir = Path(cfg["paths"]["artifacts_dir"]).resolve()
    ckpt_path = Path(args.checkpoint) if args.checkpoint else artifacts_dir / "model.pt"

    checkpoint = torch.load(ckpt_path, map_location="cpu")
    meta = meta_from_dict(checkpoint["meta"])
    hidden_dims = cfg["training"]["hidden_dims"]
    dropout = cfg["training"]["dropout"]

    engine = get_sqlalchemy_engine(args.env)
    df = load_track_by_id(args.track_id, engine)
    if df.empty:
        raise ValueError(f"No track found for id={args.track_id}")

    X, ids = transform_tracks(df, meta)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ListenRegressor(
        input_dim=X.shape[1],
        hidden_dims=hidden_dims,
        dropout=dropout,
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    with torch.no_grad():
        tensor = torch.from_numpy(X).to(device)
        pred_log = model(tensor).cpu().numpy()
    pred_listens = float(np.expm1(pred_log[0]))
    output = {
        "track_id": ids[0],
        "predicted_listens": pred_listens,
    }
    # Si la valeur réelle est disponible on l'affiche aussi pour contrôle
    if "track_listens" in df.columns and not df["track_listens"].isna().all():
        output["actual_listens"] = int(df["track_listens"].iloc[0])
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
