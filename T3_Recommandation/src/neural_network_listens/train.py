from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

from config import load_config
from data_loader import load_tracks
from db import get_connection, get_sqlalchemy_engine
from model import ListenRegressor
from preprocessing import PreprocessResult, meta_to_dict, prepare_features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entraine un regresseur sur la table track seule.")
    parser.add_argument("--env", type=str, default=None, help="Path to .env (default: repo root .env)")
    parser.add_argument("--config", type=str, default=None, help="Path to config.json (default: package config.json)")
    return parser.parse_args()


def to_dataloader(X: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    ds = TensorDataset(torch.from_numpy(X), torch.from_numpy(y))
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)


def split_indices(n_rows: int, test_size: float, random_state: int):
    """Retourne les index train/test pour garder le split reproductible."""
    indices = np.arange(n_rows)
    train_idx, test_idx = train_test_split(
        indices,
        test_size=test_size,
        random_state=random_state,
        shuffle=True,
    )
    return train_idx, test_idx


def compute_loss(model, loader, criterion, device) -> float:
    model.eval()
    total = 0.0
    n = 0
    with torch.no_grad():
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            preds = model(xb)
            loss = criterion(preds, yb)
            total += loss.item() * xb.size(0)
            n += xb.size(0)
    return total / max(n, 1)


def train_loop(
    model: ListenRegressor,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int,
    device,
    lr: float,
    weight_decay: float = 0.0,
    lr_factor: float = 0.5,
    lr_patience: int = 3,
):
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=lr_factor,
        patience=lr_patience,
        verbose=False,
    )
    best_state = None
    best_val = float("inf")
    history: List[Dict] = []

    for epoch in range(1, epochs + 1):
        model.train()
        total = 0.0
        n = 0
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
            total += loss.item() * xb.size(0)
            n += xb.size(0)
        train_loss = total / max(n, 1)

        val_loss = compute_loss(model, val_loader, criterion, device) if len(val_loader.dataset) else float("nan")
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})
        print(f"Epoch {epoch:02d} | perte_train={train_loss:.4f} | perte_val={val_loss:.4f}")

        if not np.isnan(val_loss):
            scheduler.step(val_loss)

        if not np.isnan(val_loss) and val_loss < best_val:
            best_val = val_loss
            best_state = model.state_dict()

    if best_state is None:
        best_state = model.state_dict()
        best_val = history[-1]["val_loss"]

    return best_state, best_val, history


def save_artifacts(
    artifacts_dir: Path,
    model_state,
    meta_dict: Dict,
    config: Dict,
    input_dim: int,
    best_val: float,
    history: List[Dict],
):
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model_state,
            "meta": meta_dict,
            "config": config,
            "input_dim": input_dim,
            "best_val": best_val,
        },
        artifacts_dir / "model.pt",
    )
    summary = {
        "best_val_loss": best_val,
        "epochs": len(history),
        "history": history,
        "input_dim": input_dim,
    }
    with open(artifacts_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


def main():
    args = parse_args()
    cfg = load_config(args.config)
    train_cfg = cfg["training"]
    artifacts_dir = Path(cfg["paths"]["artifacts_dir"]).resolve()

    np.random.seed(train_cfg["random_state"])
    torch.manual_seed(train_cfg["random_state"])

    engine = get_sqlalchemy_engine(args.env)
    tracks = load_tracks(engine)

    tracks = tracks.sort_values("track_id").reset_index(drop=True)
    train_idx, test_idx = split_indices(
        n_rows=len(tracks),
        test_size=train_cfg["test_size"],
        random_state=train_cfg["random_state"],
    )
    tracks_train = tracks.iloc[train_idx].reset_index(drop=True)
    tracks_test = tracks.iloc[test_idx].reset_index(drop=True)

    prep_train = prepare_features(tracks_train)
    X_train_full, y_train_full = prep_train.X, prep_train.y

    # Securite : remplacement des valeurs non finies restantes
    X_train_full = np.nan_to_num(X_train_full, nan=0.0, posinf=0.0, neginf=0.0)
    y_train_full = np.nan_to_num(y_train_full, nan=0.0, posinf=0.0, neginf=0.0)

    if train_cfg["val_ratio"] > 0:
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_full,
            y_train_full,
            test_size=train_cfg["val_ratio"],
            random_state=train_cfg["random_state"],
            shuffle=True,
        )
    else:
        X_train, y_train = X_train_full, y_train_full
        X_val = np.empty((0, X_train.shape[1]), dtype=np.float32)
        y_val = np.empty((0,), dtype=np.float32)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ListenRegressor(
        input_dim=X_train.shape[1],
        hidden_dims=train_cfg["hidden_dims"],
        dropout=train_cfg["dropout"],
    ).to(device)

    train_loader = to_dataloader(X_train, y_train, batch_size=train_cfg["batch_size"], shuffle=True)
    val_loader = to_dataloader(X_val, y_val, batch_size=train_cfg["batch_size"], shuffle=False)

    best_state, best_val, history = train_loop(
        model,
        train_loader,
        val_loader,
        epochs=train_cfg["epochs"],
        device=device,
        lr=train_cfg["learning_rate"],
        weight_decay=train_cfg.get("weight_decay", 0.0),
        lr_factor=train_cfg.get("lr_factor", 0.5),
        lr_patience=train_cfg.get("lr_patience", 3),
    )

    save_artifacts(
        artifacts_dir=artifacts_dir,
        model_state=best_state,
        meta_dict=meta_to_dict(prep_train.meta),
        config=train_cfg,
        input_dim=X_train.shape[1],
        best_val=best_val,
        history=history,
    )

    print(f"Modele enregistre dans {artifacts_dir / 'model.pt'}")
    print(f"Resume enregistre dans {artifacts_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
