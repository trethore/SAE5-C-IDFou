from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


NUMERIC_TRACK_COLUMNS = [
    "track_duration",
    "track_explicit",
    "track_instrumental",
    "track_listens",
    "track_favorites",
    "track_interest",
    "track_comments",
]

NUMERIC_AUDIO_COLUMNS = [
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "speechiness",
    "tempo",
    "valence",
]


@dataclass
class PreprocessMeta:
    numeric_columns: List[str]
    means: np.ndarray
    stds: np.ndarray
    genre_classes: List[str]
    tag_classes: List[str]
    top_k_genres: int
    top_k_tags: int


def meta_to_dict(meta: PreprocessMeta) -> Dict:
    return {
        "numeric_columns": meta.numeric_columns,
        "means": meta.means.tolist(),
        "stds": meta.stds.tolist(),
        "genre_classes": meta.genre_classes,
        "tag_classes": meta.tag_classes,
        "top_k_genres": meta.top_k_genres,
        "top_k_tags": meta.top_k_tags,
    }


def meta_from_dict(d: Dict) -> PreprocessMeta:
    return PreprocessMeta(
        numeric_columns=list(d["numeric_columns"]),
        means=np.array(d["means"], dtype=np.float32),
        stds=np.array(d["stds"], dtype=np.float32),
        genre_classes=list(d["genre_classes"]),
        tag_classes=list(d["tag_classes"]),
        top_k_genres=int(d["top_k_genres"]),
        top_k_tags=int(d["top_k_tags"]),
    )


@dataclass
class PreprocessResult:
    X: np.ndarray
    y: np.ndarray
    item_ids: List[str]
    meta: PreprocessMeta


def _normalize_numeric(df: pd.DataFrame, columns: Sequence[str]) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    means = df[columns].mean()
    stds = df[columns].std().replace(0, 1.0)
    df_norm = (df[columns] - means) / stds
    return df_norm, means.to_numpy(), stds.to_numpy()


def _pick_top_classes(series_of_lists: pd.Series, k: int) -> List[str]:
    counts = {}
    for lst in series_of_lists.dropna():
        for val in lst:
            counts[val] = counts.get(val, 0) + 1
    sorted_pairs = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [name for name, _ in sorted_pairs[:k]]


def _fit_mlb(series_of_lists: pd.Series, top_k: int) -> MultiLabelBinarizer:
    classes = _pick_top_classes(series_of_lists, top_k)
    mlb = MultiLabelBinarizer(classes=classes)
    mlb.fit([classes])  # ensure shape even if empty input
    return mlb


def _filter_labels(values, allowed: List[str]) -> List[str]:
    if not isinstance(values, list):
        return []
    allowed_set = set(allowed)
    return [v for v in values if v in allowed_set]


def _create_label(df: pd.DataFrame) -> pd.Series:
    """
    Build a 0-1 popularity score using rank_song_hotttnesss as primary signal.
    Lower rank -> higher score. Fallback to track_listens when rank missing.
    """
    rank = df["rank_song_hotttnesss"]
    if rank.notna().any():
        max_rank = rank.max()
        score = (max_rank - rank) / max_rank
    else:
        score = pd.Series(np.nan, index=df.index)

    if score.isna().any():
        listens = df["track_listens"]
        if listens.notna().any():
            max_listens = listens.max()
            score = score.fillna(listens / max_listens)

    score = score.fillna(score.mean())
    if score.isna().all():
        score = pd.Series(0.0, index=df.index)
    return score.clip(0, 1)


def build_features(tables: Dict[str, pd.DataFrame], top_k_genres: int = 50, top_k_tags: int = 200) -> PreprocessResult:
    tracks = tables["tracks"]
    audio = tables["audio"]
    rank = tables["rank"]
    genres = tables["genres"]
    tags = tables["tags"]

    df = tracks.merge(audio, on="track_id", how="left").merge(rank, on="track_id", how="left")
    df = df.merge(genres, on="track_id", how="left").merge(tags, on="track_id", how="left")

    numeric_cols = NUMERIC_TRACK_COLUMNS + NUMERIC_AUDIO_COLUMNS
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = np.nan
    # Fill numeric missing with medians; if a column is entirely NaN its median stays NaN,
    # so we fill any remaining NaNs with 0 afterward.
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # encode genres
    mlb_genre = _fit_mlb(df["genres"], top_k_genres)
    genre_matrix = mlb_genre.transform(
        df["genres"].fillna("").apply(lambda x: _filter_labels(x, mlb_genre.classes_))
    )

    # encode tags
    mlb_tag = _fit_mlb(df["tags"], top_k_tags)
    tag_matrix = mlb_tag.transform(
        df["tags"].fillna("").apply(lambda x: _filter_labels(x, mlb_tag.classes_))
    )

    numeric_norm, means, stds = _normalize_numeric(df, numeric_cols)

    X = np.hstack([numeric_norm.to_numpy(), genre_matrix, tag_matrix]).astype(np.float32)
    y = _create_label(df).astype(np.float32).to_numpy()
    item_ids = df["track_id"].astype(str).tolist()

    meta = PreprocessMeta(
        numeric_columns=list(numeric_cols),
        means=means.astype(np.float32),
        stds=stds.astype(np.float32),
        genre_classes=list(mlb_genre.classes_),
        tag_classes=list(mlb_tag.classes_),
        top_k_genres=top_k_genres,
        top_k_tags=top_k_tags,
    )
    return PreprocessResult(X=X, y=y, item_ids=item_ids, meta=meta)


def transform_features(
    tables: Dict[str, pd.DataFrame],
    meta: PreprocessMeta,
) -> Tuple[np.ndarray, List[str]]:
    tracks = tables["tracks"]
    audio = tables["audio"]
    rank = tables.get("rank", pd.DataFrame(columns=["track_id"]))
    genres = tables["genres"]
    tags = tables["tags"]

    df = tracks.merge(audio, on="track_id", how="left").merge(rank, on="track_id", how="left")
    df = df.merge(genres, on="track_id", how="left").merge(tags, on="track_id", how="left")

    for col in meta.numeric_columns:
        if col not in df.columns:
            df[col] = np.nan
    df[meta.numeric_columns] = df[meta.numeric_columns].apply(pd.to_numeric, errors="coerce")
    df[meta.numeric_columns] = df[meta.numeric_columns].fillna(df[meta.numeric_columns].median())
    df[meta.numeric_columns] = df[meta.numeric_columns].fillna(0)

    # normalize
    df_norm = (df[meta.numeric_columns] - meta.means) / meta.stds

    # encode genres/tags with stored classes
    mlb_genre = MultiLabelBinarizer(classes=meta.genre_classes)
    mlb_genre.fit([meta.genre_classes])
    genre_matrix = mlb_genre.transform(
        df["genres"].fillna("").apply(lambda x: _filter_labels(x, mlb_genre.classes_))
    )

    mlb_tag = MultiLabelBinarizer(classes=meta.tag_classes)
    mlb_tag.fit([meta.tag_classes])
    tag_matrix = mlb_tag.transform(
        df["tags"].fillna("").apply(lambda x: _filter_labels(x, mlb_tag.classes_))
    )

    X = np.hstack([df_norm.to_numpy(), genre_matrix, tag_matrix]).astype(np.float32)
    item_ids = df["track_id"].astype(str).tolist()
    return X, item_ids
