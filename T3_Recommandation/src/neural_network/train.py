from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from db import get_connection  # noqa: E402
from data_loader import load_all  # noqa: E402
from model import PopularityRegressor  # noqa: E402
from preprocessing import build_features, meta_to_dict  # noqa: E402
from config import load_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a simple neural recommender (popularity regressor).")
    parser.add_argument("--env", type=str, default=None, help="Path to .env file (defaults to root .env).")
    parser.add_argument("--config", type=str, default=None, help="Path to config.json (overrides defaults).")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--hidden-dim", type=int, default=None)
    parser.add_argument("--dropout", type=float, default=None)
    parser.add_argument("--top-k-genres", type=int, default=None)
    parser.add_argument("--top-k-tags", type=int, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("T3_Recommandation/src/neural_network/artifacts"))
    return parser.parse_args()


def to_tensor_dataset(X: np.ndarray, y: np.ndarray) -> TensorDataset:
    x_t = torch.from_numpy(X)
    y_t = torch.from_numpy(y)
    return TensorDataset(x_t, y_t)


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    for xb, yb in loader:
        xb = xb.to(device)
        yb = yb.to(device)
        optimizer.zero_grad()
        preds, _ = model(xb)
        loss = criterion(preds, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * xb.size(0)
    return total_loss / len(loader.dataset)


def eval_loss(model, loader, criterion, device):
    model.eval()
    total = 0.0
    with torch.no_grad():
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            preds, _ = model(xb)
            loss = criterion(preds, yb)
            total += loss.item() * xb.size(0)
    return total / len(loader.dataset)


def main():
    args = parse_args()
    cfg = load_config(args.config)
    train_cfg = cfg.get("training", {})

    def param(name, arg_val, default):
        return arg_val if arg_val is not None else train_cfg.get(name, default)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    os.makedirs(args.output_dir, exist_ok=True)

    with get_connection(args.env) as conn:
        tables: Dict[str, np.ndarray] = load_all(conn)

    preprocess = build_features(
        tables,
        top_k_genres=param("top_k_genres", args.top_k_genres, 50),
        top_k_tags=param("top_k_tags", args.top_k_tags, 200),
    )

    X_train, X_val, y_train, y_val = train_test_split(
        preprocess.X,
        preprocess.y,
        test_size=0.1,
        random_state=42,
        shuffle=True,
    )

    train_loader = DataLoader(
        to_tensor_dataset(X_train, y_train),
        batch_size=param("batch_size", args.batch_size, 256),
        shuffle=True,
    )
    val_loader = DataLoader(
        to_tensor_dataset(X_val, y_val),
        batch_size=param("batch_size", args.batch_size, 256),
        shuffle=False,
    )

    model = PopularityRegressor(
        input_dim=preprocess.X.shape[1],
        hidden_dim=param("hidden_dim", args.hidden_dim, 256),
        dropout=param("dropout", args.dropout, 0.1),
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=param("lr", args.lr, 1e-3))
    criterion = torch.nn.MSELoss()

    best_val = float("inf")
    best_state = None

    epochs = param("epochs", args.epochs, 5)
    for epoch in range(1, epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss = eval_loss(model, val_loader, criterion, device)
        print(f"Epoch {epoch:02d} | train_loss={train_loss:.4f} | val_loss={val_loss:.4f}")
        if val_loss < best_val:
            best_val = val_loss
            best_state = {
                "model_state_dict": model.state_dict(),
                "meta": meta_to_dict(preprocess.meta),
                "train_loss": train_loss,
                "val_loss": val_loss,
                "config": vars(args) | {"resolved_training": train_cfg},
            }

    if best_state is None:
        best_state = {
            "model_state_dict": model.state_dict(),
            "meta": meta_to_dict(preprocess.meta),
            "train_loss": train_loss,
            "val_loss": val_loss,
            "config": vars(args) | {"resolved_training": train_cfg},
        }

    out_path = args.output_dir / "model.pt"
    torch.save(best_state, out_path)

    # persist a human-readable summary
    summary = {
        "train_loss": best_state["train_loss"],
        "val_loss": best_state["val_loss"],
        "epochs": epochs,
        "device": str(device),
        "n_samples": int(preprocess.X.shape[0]),
        "n_features": int(preprocess.X.shape[1]),
    }
    with open(args.output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved model to {out_path}")
    print(f"Summary: {summary}")


if __name__ == "__main__":
    main()
