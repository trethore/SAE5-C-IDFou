"""Génère un diagramme circulaire de la répartition des écoutes par genre principal.

Utilisation :
    python3 src/graphs/pie/main.py
(déclencher depuis la racine du projet pour lire 'cleaned_data/merged_tracks.csv' et sauvegarder dans 'src/graphs/output/')
"""

from pathlib import Path
from typing import List, Sequence, Tuple, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Wedge
from matplotlib.text import Text


def resolve_paths() -> Tuple[Path, Path]:
    """Retourne le chemin du jeu de données et du dossier de sortie."""
    # Garantir que le script fonctionne quel que soit le répertoire courant
    src_dir = Path(__file__).resolve().parents[3]
    project_root = src_dir.parent
    data_path = project_root / "cleaned_data" / "merged_tracks.csv"
    output_dir = src_dir / "graphs" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return data_path, output_dir


def load_genre_streams(data_path: Path) -> Tuple[pd.Series, int]:
    """Charge les données et agrège les écoutes par genre principal."""
    df = pd.read_csv(data_path)
    # Nettoyer les données : supprimer les valeurs nulles
    df_clean = df.dropna(subset=["track_genre_top", "track_listens"]).copy()
    # Grouper par genre principal et sommer les streams
    genre_streams = (
        df_clean.groupby("track_genre_top")["track_listens"]
        .sum()
        .sort_values(ascending=False)
    )
    return genre_streams, len(df_clean)


def prepare_plot_data(genre_streams: pd.Series, top_n: int = 10) -> pd.Series:
    """Prépare les données pour le graphique avec une catégorie 'Others'."""
    # Garder le top N et regrouper le reste
    if len(genre_streams) > top_n:
        top_genres = genre_streams.head(top_n)
        others_sum = genre_streams.iloc[top_n:].sum()
        # Créer une nouvelle série avec "Others"
        plot_data = pd.concat([top_genres, pd.Series({"Others": others_sum})])
    else:
        plot_data = genre_streams
    return plot_data


def generate_pie_chart(plot_data: pd.Series, output_dir: Path) -> Path:
    """Crée le diagramme circulaire et retourne le chemin de sauvegarde."""
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(14, 10))

    # Couleurs personnalisées
    color_map = plt.get_cmap("Set3")
    colors = [tuple(color) for color in color_map(np.linspace(0, 1, len(plot_data)))]

    # Créer le pie chart
    pie_result = ax.pie(
        plot_data,
        labels=list(plot_data.index.astype(str)),
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 11, "weight": "bold"},
        pctdistance=0.85,
    )
    wedges = list(cast(Sequence[Wedge], pie_result[0]))
    texts = list(cast(Sequence[Text], pie_result[1]))
    autotexts: List[Text] = (
        list(cast(Sequence[Text], pie_result[2])) if len(pie_result) > 2 else []
    )

    # Améliorer la lisibilité des pourcentages
    for autotext in autotexts:
        autotext.set_color("black")
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")

    # Améliorer la lisibilité des labels
    for text in texts:
        text.set_fontsize(11)

    # Titre
    plt.title(
        "Stream Distribution by Genre\n(Using track_genre_top)",
        fontsize=18,
        weight="bold",
        pad=20,
    )

    # Assurer que le pie chart est circulaire
    ax.axis("equal")

    # Ajouter une légende pour les genres
    legend_labels = [
        f"{genre}: {streams:,.0f}"
        for genre, streams in plot_data.items()
    ]
    ax.legend(
        wedges,
        legend_labels,
        title="Genres",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=12,
        title_fontsize=14,
    )

    plt.tight_layout()
    output_path = output_dir / "pie_chart_genres.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def display_summary(genre_streams: pd.Series, track_count: int) -> None:
    """Affiche un résumé lisible dans la console."""
    total_streams = genre_streams.sum()
    print(f"Total tracks analyzed: {track_count}")
    print(f"Total streams: {total_streams:,.0f}")
    print(f"Number of top genres: {len(genre_streams)}")
    print()
    print("Top 10 genres by streams (from track_genre_top):")
    for i, (genre, streams) in enumerate(genre_streams.head(10).items(), 1):
        percentage = (streams / total_streams) * 100 if total_streams else 0.0
        print(f"{i}. {genre}: {streams:,.0f} streams ({percentage:.2f}%)")


def main() -> None:
    """Génère un diagramme circulaire des streams par genre."""
    data_path, output_dir = resolve_paths()
    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. Ensure preprocessing is complete."
        )

    genre_streams, track_count = load_genre_streams(data_path)
    if genre_streams.empty or genre_streams.sum() == 0:
        # Informer l'utilisateur si les données sont insuffisantes
        raise ValueError(
            "No genre streams available after cleaning. Check data preparation steps."
        )

    display_summary(genre_streams, track_count)
    plot_data = prepare_plot_data(genre_streams)
    output_path = generate_pie_chart(plot_data, output_dir)
    print(f"\nChart saved in '{output_path}'")


if __name__ == "__main__":
    main()
