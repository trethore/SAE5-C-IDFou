from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd


# Colonnes utilisées pour X
BASE_NUMERIC_COLUMNS = [
    "track_duration",
    "track_number",
    "track_disc_number",
    "track_favorites",
    "track_interest",
    "track_comments",
    "track_age_years",
    "rank_song_hotttnesss",
    "rank_song_currency",
]


@dataclass
class PreprocessMeta:
    numeric_columns: List[str]
    means: np.ndarray
    stds: np.ndarray


def meta_to_dict(meta: PreprocessMeta) -> dict:
    return {
        "numeric_columns": meta.numeric_columns,
        "means": meta.means.tolist(),
        "stds": meta.stds.tolist(),
    }


def meta_from_dict(data: dict) -> PreprocessMeta:
    return PreprocessMeta(
        numeric_columns=list(data["numeric_columns"]),
        means=np.array(data["means"], dtype=np.float32),
        stds=np.array(data["stds"], dtype=np.float32),
    )


@dataclass
class PreprocessResult:
    X: np.ndarray
    y: np.ndarray
    track_ids: List[str]
    meta: PreprocessMeta


def _compute_age_years(series: pd.Series) -> pd.Series:
    """Convertit une date en âge en années flottantes par rapport à aujourd'hui."""
    parsed = pd.to_datetime(series, errors="coerce", utc=True)
    now = pd.Timestamp.now(tz="UTC")
    delta_days = (now - parsed).dt.total_seconds() / 86400.0
    return delta_days / 365.25


def _normalize(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    means = df[columns].mean()
    stds = df[columns].std().replace(0, 1.0)
    normalized = (df[columns] - means) / stds
    return normalized, means.to_numpy(dtype=np.float32), stds.to_numpy(dtype=np.float32)


def prepare_features(tracks_df: pd.DataFrame) -> PreprocessResult:
    """Nettoie, crée les features et renvoie X, y et meta."""
    df = tracks_df.copy()

    # Ajout de l'âge en années
    df["track_age_years"] = _compute_age_years(df["track_date_created"])

    # Conversion numérique et remplissage médian
    df[BASE_NUMERIC_COLUMNS] = df[BASE_NUMERIC_COLUMNS].apply(pd.to_numeric, errors="coerce")
    df[BASE_NUMERIC_COLUMNS] = df[BASE_NUMERIC_COLUMNS].replace([np.inf, -np.inf], np.nan)
    df[BASE_NUMERIC_COLUMNS] = df[BASE_NUMERIC_COLUMNS].fillna(df[BASE_NUMERIC_COLUMNS].median())

    # Normalisation
    X_norm, means, stds = _normalize(df, BASE_NUMERIC_COLUMNS)
    X = X_norm.to_numpy(dtype=np.float32)
    X[~np.isfinite(X)] = 0.0

    # Cible log1p
    y = np.log1p(df["track_listens"].astype(np.float32)).to_numpy(dtype=np.float32)
    y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)

    meta = PreprocessMeta(
        numeric_columns=BASE_NUMERIC_COLUMNS,
        means=means,
        stds=stds,
    )
    return PreprocessResult(
        X=X,
        y=y,
        track_ids=df["track_id"].astype(str).tolist(),
        meta=meta,
    )


def transform_tracks(tracks_df: pd.DataFrame, meta: PreprocessMeta) -> Tuple[np.ndarray, List[str]]:
    """Applique le même préprocessing (sans recalcule des stats) pour l'inférence."""
    df = tracks_df.copy()
    df["track_age_years"] = _compute_age_years(df["track_date_created"])
    for col in meta.numeric_columns:
        if col not in df.columns:
            df[col] = np.nan
    df[meta.numeric_columns] = df[meta.numeric_columns].apply(pd.to_numeric, errors="coerce")
    df[meta.numeric_columns] = df[meta.numeric_columns].fillna(df[meta.numeric_columns].median())

    norm = (df[meta.numeric_columns] - meta.means) / meta.stds
    X = norm.to_numpy(dtype=np.float32)
    ids = df["track_id"].astype(str).tolist()
    return X, ids
