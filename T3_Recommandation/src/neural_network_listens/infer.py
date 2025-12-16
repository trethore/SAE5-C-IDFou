from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import torch

from config import load_config
from data_loader import load_track_by_id
from db import get_sqlalchemy_engine
from model import ListenRegressor
from preprocessing import meta_from_dict, transform_tracks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Predire les listens pour un track_id (BD) ou un CSV (stdin ou fichier).",
    )
    src_group = parser.add_mutually_exclusive_group(required=False)
    src_group.add_argument("--track-id", type=str, help="UUID du track a predire (lecture BD).")
    src_group.add_argument(
        "--csv",
        type=str,
        help="Chemin vers un CSV ou '-' pour stdin. Si non fourni et stdin non interactif, stdin est utilise.",
    )
    parser.add_argument("--env", type=str, default=None, help="chemin vers .env")
    parser.add_argument("--config", type=str, default=None, help="chemin vers config.json")
    parser.add_argument("--checkpoint", type=str, default=None, help="chemin vers le model")
    return parser.parse_args()


def _load_csv(path: Optional[str]) -> pd.DataFrame:
    if path is None or path == "-":
        data = sys.stdin.read()
        if not data.strip():
            raise ValueError("Aucune donnee lue sur stdin pour le CSV.")
        return pd.read_csv(io.StringIO(data))
    return pd.read_csv(path)


def main():
    args = parse_args()
    cfg = load_config(args.config)
    artifacts_dir = Path(cfg["paths"]["artifacts_dir"]).resolve()
    ckpt_path = Path(args.checkpoint) if args.checkpoint else artifacts_dir / "model.pt"

    checkpoint = torch.load(ckpt_path, map_location="cpu")
    meta = meta_from_dict(checkpoint["meta"])
    target_log_min = float(checkpoint.get("target_log_min", 0.0))
    target_log_max = float(checkpoint.get("target_log_max", np.inf))
    hidden_dims = cfg["training"]["hidden_dims"]
    dropout = cfg["training"]["dropout"]

    # Source BD ou CSV
    df: Optional[pd.DataFrame] = None
    if args.track_id:
        engine = get_sqlalchemy_engine(args.env)
        df = load_track_by_id(args.track_id, engine)
        if df.empty:
            raise ValueError(f"Pas de track pour id ={args.track_id}")
    else:
        csv_path = args.csv
        if csv_path is None and not sys.stdin.isatty():
            csv_path = "-"
        if csv_path is None:
            raise ValueError("Fournir --track-id ou un CSV (fichier ou stdin)." )
        df = _load_csv(csv_path)
        if "track_date_created" not in df.columns:
            raise ValueError("Le CSV doit contenir la colonne track_date_created (ISO date).")
        # s'assurer qu'un identifiant existe pour l'affichage
        if "track_id" not in df.columns:
            df["track_id"] = [f"csv_row_{i}" for i in range(len(df))]

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
        pred_log = model(tensor).cpu().numpy().reshape(-1)
        pred_log = np.clip(pred_log, target_log_min, target_log_max)

    pred_listens = np.expm1(pred_log)
    outputs = []
    for idx, pred in zip(ids, pred_listens):
        item = {
            "track_id": idx,
            "predicted_listens": float(pred),
        }
        actual_val = -1.0
        if "track_listens" in df.columns:
            actual = df.loc[df["track_id"] == idx, "track_listens"].iloc[0]
            if pd.notna(actual):
                actual_val = float(actual)
        item["actual_listens"] = actual_val
        outputs.append(item)

    print(json.dumps(outputs if len(outputs) > 1 else outputs[0], indent=2))


if __name__ == "__main__":
    main()
