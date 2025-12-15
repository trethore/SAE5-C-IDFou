from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "cleaned_data"


def _ensure_int(series: pd.Series) -> pd.Series:
    """Cast a series to pandas' nullable Int64 dtype without crashing on bad data."""
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.astype("Int64")


def _parse_track_genres(value: object) -> list[int]:
    """Convert string encoded lists like '[21, 103]' into python lists of ints."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        raw_list = value
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = ast.literal_eval(stripped)
        except (SyntaxError, ValueError):
            # Solution de secours : separer sur la virgule pour les valeurs mal formees comme '21,34'
            raw_list = [item.strip() for item in stripped.split(",") if item.strip()]
        else:
            raw_list = parsed if isinstance(parsed, (list, tuple)) else [parsed]
    else:
        raw_list = [value]

    normalised: list[int] = []
    for item in raw_list:
        if item is None or (isinstance(item, float) and pd.isna(item)):
            continue
        try:
            normalised.append(int(item))
        except (TypeError, ValueError):
            continue
    return normalised


def _merge_with_priority(
    base: pd.DataFrame,
    other: pd.DataFrame,
    *,
    key: str,
    suffix: str,
    drop: Sequence[str] | None = None,
    rename: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Left merge two frames while keeping base columns authoritative."""
    rhs = other.copy()
    if drop:
        rhs = rhs.drop(columns=list(drop), errors="ignore")
    if rename:
        rhs = rhs.rename(columns=rename)

    overlap = [col for col in rhs.columns if col in base.columns and col != key]

    merged = base.merge(rhs, on=key, how="left", suffixes=("", f"__{suffix}"))
    for column in overlap:
        other_column = f"{column}__{suffix}"
        if other_column in merged.columns:
            needs_fill = merged[column].isna()
            if needs_fill.any():
                merged.loc[needs_fill, column] = merged.loc[needs_fill, other_column]
            merged = merged.drop(columns=other_column)

    return merged


def _load_tracks(data_dir: Path) -> pd.DataFrame:
    tracks_path = data_dir / "clean_tracks.csv"
    tracks = pd.read_csv(tracks_path)
    for identifier in ("track_id", "album_id", "artist_id"):
        if identifier in tracks.columns:
            tracks[identifier] = _ensure_int(tracks[identifier])

    tracks["track_genres_list"] = tracks["track_genres"].apply(_parse_track_genres)
    return tracks


def _merge_genres(tracks: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    genres_path = data_dir / "clean_genres.csv"
    genres = pd.read_csv(genres_path).rename(
        columns={
            "#tracks": "genre_track_count",
            "parent": "genre_parent_id",
            "title": "genre_title",
            "top_level": "genre_top_level",
        }
    )
    genres["genre_id"] = _ensure_int(genres["genre_id"])

    expanded = tracks.assign(
        genre_id_expanded=tracks["track_genres_list"].apply(
            lambda values: values if values else [pd.NA]
        )
    ).explode("genre_id_expanded", ignore_index=True)
    expanded = expanded.rename(columns={"genre_id_expanded": "genre_id"})
    expanded["genre_id"] = _ensure_int(expanded["genre_id"])

    merged = expanded.merge(genres, on="genre_id", how="left")
    return merged


def _merge_albums(df: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    albums_path = data_dir / "clean_raw_albums.csv"
    albums = pd.read_csv(albums_path).rename(columns={"tags": "album_tags"})
    albums["album_id"] = _ensure_int(albums["album_id"])
    return _merge_with_priority(df, albums, key="album_id", suffix="album")


def _merge_artists(df: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    artists_path = data_dir / "clean_raw_artists.csv"
    artists = pd.read_csv(artists_path).rename(columns={"tags": "artist_tags"})
    artists["artist_id"] = _ensure_int(artists["artist_id"])
    return _merge_with_priority(df, artists, key="artist_id", suffix="artist")


def _merge_features(df: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    features_path = data_dir / "clean_features.csv"
    features = pd.read_csv(features_path)
    features["track_id"] = _ensure_int(features["track_id"])
    return _merge_with_priority(df, features, key="track_id", suffix="features")


def _merge_echonest(df: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    echonest_path = data_dir / "clean_echonest.csv"
    echonest = pd.read_csv(echonest_path)
    echonest["track_id"] = _ensure_int(echonest["track_id"])
    return _merge_with_priority(df, echonest, key="track_id", suffix="echonest")


def _merge_raw_tracks(df: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    raw_tracks_path = data_dir / "clean_raw_tracks.csv"
    raw_tracks = pd.read_csv(raw_tracks_path).rename(columns={"tags": "track_tags_raw"})
    raw_tracks["track_id"] = _ensure_int(raw_tracks["track_id"])

    # Eviter de fusionner des informations dupliquees deja fournies ailleurs.
    drop_candidates = ("album_title", "artist_name")
    merged = _merge_with_priority(
        df,
        raw_tracks,
        key="track_id",
        suffix="raw",
        drop=drop_candidates,
    )

    if "track_tags_raw" in merged.columns:
        merged["track_tags"] = merged["track_tags"].combine_first(
            merged.pop("track_tags_raw")
        )

    return merged


def _format_track_genres_for_export(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    formatted["track_genres"] = formatted["track_genres_list"].apply(json.dumps)
    formatted = formatted.drop(columns=["track_genres_list"])
    return formatted


def build_dataset(data_dir: Path) -> pd.DataFrame:
    print(f"Loading clean_tracks.csv from {data_dir} …")
    tracks = _load_tracks(data_dir)
    print(f"  -> {len(tracks):,} tracks / {tracks.shape[1]} columns")

    merged = _merge_genres(tracks, data_dir)
    print(f"After genres merge: {len(merged):,} rows / {merged.shape[1]} columns")

    merged = _merge_albums(merged, data_dir)
    print(f"After albums merge: {len(merged):,} rows / {merged.shape[1]} columns")

    merged = _merge_artists(merged, data_dir)
    print(f"After artists merge: {len(merged):,} rows / {merged.shape[1]} columns")

    merged = _merge_features(merged, data_dir)
    print(f"After features merge: {len(merged):,} rows / {merged.shape[1]} columns")

    merged = _merge_echonest(merged, data_dir)
    print(f"After echonest merge: {len(merged):,} rows / {merged.shape[1]} columns")

    merged = _merge_raw_tracks(merged, data_dir)
    print(f"After raw tracks merge: {len(merged):,} rows / {merged.shape[1]} columns")

    merged = merged.sort_values(["track_id", "genre_id"], ignore_index=True)
    return merged


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge cleaned datasets onto tracks.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory that contains the cleaned CSV files (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Where to write the merged dataset (default: <data-dir>/merged_tracks.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform the merge without writing any file to disk.",
    )
    return parser.parse_args(argv)


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = args.data_dir.expanduser().resolve()
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        return 1

    merged = build_dataset(data_dir)
    merged_for_export = _format_track_genres_for_export(merged)

    if args.dry_run:
        print("Dry-run mode enabled; skipping file write.")
        return 0

    output_path = (
        args.output.expanduser().resolve()
        if args.output is not None
        else data_dir / "merged_tracks.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_for_export.to_csv(output_path, index=False)
    print(f"Merged dataset written to {output_path}")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    sys.exit(main())
