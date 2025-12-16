from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

from config import load_config
from data_loader import load_tracks
from db import get_connection, get_sqlalchemy_engine
from model import ListenRegressor
from preprocessing import meta_from_dict, transform_tracks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Évalue le modèle sur le jeu de test (20%).")
    parser.add_argument("--env", type=str, default=None, help="Path to .env (default: repo root .env)")
    parser.add_argument("--config", type=str, default=None, help="Path to config.json (default: package config.json)")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model.pt (default: artifacts/model.pt)")
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = load_config(args.config)
    train_cfg = cfg["training"]
    artifacts_dir = Path(cfg["paths"]["artifacts_dir"]).resolve()
    ckpt_path = Path(args.checkpoint) if args.checkpoint else artifacts_dir / "model.pt"

    checkpoint = torch.load(ckpt_path, map_location="cpu")
    meta = meta_from_dict(checkpoint["meta"])
    hidden_dims = train_cfg["hidden_dims"]
    dropout = train_cfg["dropout"]

    engine = get_sqlalchemy_engine(args.env)
    tracks = load_tracks(engine)
    tracks = tracks.sort_values("track_id").reset_index(drop=True)
    X_all, ids = transform_tracks(tracks, meta)
    y_all = np.log1p(tracks["track_listens"].astype(np.float32)).to_numpy(dtype=np.float32)

    X_train, X_test, y_train, y_test = train_test_split(
        X_all,
        y_all,
        test_size=train_cfg["test_size"],
        random_state=train_cfg["random_state"],
        shuffle=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ListenRegressor(
        input_dim=X_all.shape[1],
        hidden_dims=hidden_dims,
        dropout=dropout,
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    test_loader = DataLoader(TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test)), batch_size=512)

    preds_log = []
    targets_log = []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            pred = model(xb).cpu().numpy()
            preds_log.append(pred)
            targets_log.append(yb.numpy())

    y_pred_log = np.concatenate(preds_log)
    y_true_log = np.concatenate(targets_log)

    # Retour à l'échelle d'origine
    y_pred = np.expm1(y_pred_log)
    y_true = np.expm1(y_true_log)

    # Nettoyage NaN/inf éventuels
    y_pred = np.nan_to_num(y_pred, nan=0.0, posinf=0.0, neginf=0.0)
    y_true = np.nan_to_num(y_true, nan=0.0, posinf=0.0, neginf=0.0)

    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(json.dumps({"rmse": rmse, "mae": mae, "r2": r2}, indent=2))


if __name__ == "__main__":
    main()
