from __future__ import annotations

import torch
from torch import nn


class ItemEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class PopularityRegressor(nn.Module):
    """
    Simple MLP regressor: encodes item features then predicts a scalar popularity score.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 256, dropout: float = 0.1):
        super().__init__()
        self.encoder = ItemEncoder(input_dim, hidden_dim, dropout)
        self.head = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        emb = self.encoder(x)
        score = self.head(emb).squeeze(-1)
        return score, emb
