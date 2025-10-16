from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _resolve_csv(csv_path: str) -> str:
    """Resolve the merged CSV location robustly from this script location."""
    p = Path(csv_path)
    if p.exists():
        return str(p)
    here = Path(__file__).resolve()
    # repo_root/cleaned_data/merged_tracks.csv
    alt1 = here.parents[3] / "cleaned_data" / "merged_tracks.csv"
    if alt1.exists():
        return str(alt1)
    # repo_root/src/cleaned_data/merged_tracks.csv
    alt2 = here.parents[4] / "src" / "cleaned_data" / "merged_tracks.csv"
    if alt2.exists():
        return str(alt2)
    return str(p)


def plot_genre_popularity_by_year(
    csv_path: str = "../../../cleaned_data/merged_tracks.csv",
    metric: str = "track_listens",
    agg: str = "median",
    top: int = 6,
    top_by: str = "sum_metric",  
    min_year_count: int = 200,
    smooth_window: int = 3,
    log: bool = False,
    output: str = "genre_popularity_by_year.png",
) -> str:
    """
    Line chart: popularity per genre and year.
    - metric: one of 'track_listens', 'track_favorites'
    - agg: 'median' (robust), 'mean', or 'share' (percentage of yearly total)
    - top: number of genres to plot
    - top_by: select top genres by 'sum_metric' (global sum of metric) or by '#tracks'
    - min_year_count: filter years with too few tracks to reduce noise
    - smooth_window: rolling mean window; 0/1 disables smoothing
    - log: if True, apply log1p to the metric before aggregating (useful for skewed listens)
    """

    csv_path = _resolve_csv(csv_path)
    # Read only the needed columns
    head = pd.read_csv(csv_path, nrows=0).columns
    needed = ["track_genre_top", "album_date_released", metric]
    use = [c for c in needed if c in head]
    if len(use) < 3:
        raise SystemExit(f"Required columns not found for metric '{metric}': {needed}")

    df = pd.read_csv(csv_path, usecols=use)
    df["year"] = pd.to_datetime(df["album_date_released"], errors="coerce").dt.year
    # Robust genre cleaning: drop textual nulls and empties
    bad = {"", "nan", "none", "null", "unknown", "n/a", "na"}
    s = df["track_genre_top"].astype(str).str.strip()
    df = df[s.str.lower().isin(bad) == False]
    df["track_genre_top"] = df["track_genre_top"].astype(str).str.strip()
    df[metric] = pd.to_numeric(df[metric], errors="coerce")
    df = df.dropna(subset=["year", "track_genre_top", metric])

    # Select top genres
    if top_by == "sum_metric":
        genre_order = (
            df.groupby("track_genre_top")[metric]
            .sum()
            .sort_values(ascending=False)
            .head(top)
            .index
        )
    else:
        genre_order = df["track_genre_top"].value_counts().head(top).index

    dff = df[df["track_genre_top"].isin(genre_order)].copy()

    # Optional log-transform (ignored for 'share' mode)
    metric_series = pd.to_numeric(dff[metric], errors="coerce")
    if agg != "share" and log:
        dff[metric] = np.log1p(metric_series.clip(lower=0))
        y_label = f"log1p({metric.replace('_',' ').title()})"
        title_metric = f"{metric.replace('_',' ').title()} (log1p)"
    else:
        dff[metric] = metric_series
        y_label = metric.replace('_',' ').title()
        title_metric = metric.replace('_',' ').title()

    # Aggregate per year and genre
    if agg == "share":
        # Share of yearly total metric per genre (in %)
        sums = dff.groupby(["year", "track_genre_top"], as_index=False)[metric].sum()
        pivot = sums.pivot(index="year", columns="track_genre_top", values=metric)
        totals = pivot.sum(axis=1).replace(0, np.nan)
        pivot = (pivot.div(totals, axis=0) * 100.0)
        y_label = f"% of yearly {metric.replace('_',' ').title()}"
        title_metric = f"{metric.replace('_',' ').title()} Share (%)"
        # For share mode, smoothing helps but keep bounds 0..100
    elif agg == "mean":
        pivot = dff.groupby(["year", "track_genre_top"], as_index=False)[metric].mean()
        pivot = pivot.pivot(index="year", columns="track_genre_top", values=metric)
    else:
        pivot = dff.groupby(["year", "track_genre_top"], as_index=False)[metric].median()
        pivot = pivot.pivot(index="year", columns="track_genre_top", values=metric)

    # Filter years with too few tracks to reduce volatility
    counts = dff.groupby("year").size()
    valid_years = counts[counts >= min_year_count].index
    pivot = pivot.loc[pd.Index(valid_years).intersection(pivot.index)].sort_index()

    # Smooth
    if smooth_window and smooth_window > 1:
        pivot = pivot.rolling(window=smooth_window, min_periods=1).mean()

    # Plot
    ax = pivot.plot(figsize=(12, 6), marker="o")
    ax.set_title(f"{title_metric} by Genre and Year (Top {top}, {agg})")
    ax.set_xlabel("Year")
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(title="Genre", fontsize=9)
    if agg == "share":
        ax.set_ylim(0, 100)
    plt.tight_layout()

    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] wrote {output}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Line chart: popularity by genre and year")
    parser.add_argument("--csv", default="../../../cleaned_data/merged_tracks.csv")
    parser.add_argument("--metric", choices=["track_listens", "track_favorites"], default="track_listens")
    parser.add_argument("--agg", choices=["median", "mean", "share"], default="median")
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--top-by", choices=["sum_metric", "tracks"], default="sum_metric")
    parser.add_argument("--min-year-count", type=int, default=200)
    parser.add_argument("--smooth-window", type=int, default=3)
    parser.add_argument("--log", action="store_true", help="Apply log1p to the metric before aggregating")
    parser.add_argument("--output", default="genre_popularity_by_year.png")
    args = parser.parse_args()

    plot_genre_popularity_by_year(
        csv_path=args.csv,
        metric=args.metric,
        agg=args.agg,
        top=args.top,
        top_by=args.top_by,
        min_year_count=args.min_year_count,
        smooth_window=args.smooth_window,
        log=args.log,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
