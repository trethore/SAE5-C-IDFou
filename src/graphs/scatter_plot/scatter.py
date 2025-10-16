"""Trace la moyenne des écoutes par position des morceaux au sein de chaque album.

Utilisation :
    python3 src/graphs/scatter_plot/scatter.py
(exécuter depuis la racine du projet pour lire 'cleaned_data/merged_tracks.csv' et sauvegarder 'scatter.png')
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import os


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)
    required_cols = {'album_id', 'track_number', 'track_listens'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {', '.join(missing)}")
    # Sélection des colonnes nécessaires pour comprendre la position et l'audience de chaque morceau.
    return df[['album_id', 'track_number', 'track_listens']].dropna()


def keep_first_n_tracks_per_album(df: pd.DataFrame, n: int = 50) -> pd.DataFrame:
    df_sorted = df.sort_values(['album_id', 'track_number'])
    # On limite la taille de l'ensemble en gardant uniquement les n premières pistes de chaque album.
    filtered_df = df_sorted.groupby('album_id').head(n)
    print(f"Les {n} premiers morceaux de chaque album sont conservés.")
    return filtered_df


def compute_average_listens(df: pd.DataFrame) -> pd.Series:
    # Calcul de l'audience moyenne pour chaque position dans l'album.
    return df.groupby('track_number')['track_listens'].mean()


def plot_average_listens(avg_listens: pd.Series, output_path: str, max_track: int = 50):
    avg_listens = avg_listens[avg_listens.index <= max_track]
    plt.figure(figsize=(10, 6))
    # La courbe met en évidence comment les écoutes évoluent selon la position du morceau dans l'album.
    avg_listens.plot(kind='line', marker='o', color='purple', label='Average Listens')
    plt.title(f"Average Track Listens by Track Position (tracks 1 to {max_track})")
    plt.xlabel("Track Number in Album")
    plt.ylabel("Average Listens")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Graph saved : {output_path}")


def main() -> int:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    csv_path = os.path.join(project_root, "cleaned_data", "merged_tracks.csv")
    output_path = os.path.join(os.path.dirname(__file__), "scatter.png")

    df = load_data(csv_path)
    df = keep_first_n_tracks_per_album(df, n=50)
    avg_listens = compute_average_listens(df)
    plot_average_listens(avg_listens, output_path, max_track=50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
