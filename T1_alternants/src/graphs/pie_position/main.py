"""Génère un diagramme circulaire de la répartition des écoutes par position principal.

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
import ast

import os, sys
globalrules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../clean'))
sys.path.append(globalrules_path)

from globalrules import DEFAULT_OUTPUT_DIR, DEFAULT_GRAPHS_FOLDER

def resolve_paths() -> Tuple[Path, Path]:
    """Retourne le chemin du jeu de données et du dossier de sortie."""
    # Garantir que le script fonctionne quel que soit le répertoire courant
    data_path = DEFAULT_OUTPUT_DIR / "clean_answers.csv"
    output_dir = DEFAULT_GRAPHS_FOLDER / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return data_path, output_dir


def load_position_streams(data_path: Path) -> Tuple[pd.Series, int]:
    """Charge les données et agrège les domaines de travail principaux."""

    # Load data
    df = pd.read_csv(data_path)
    df_clean = df.dropna(subset=["position"]).copy()
    position_streams = df_clean["position"].value_counts()

    return position_streams, len(df_clean)


def prepare_plot_data(position_streams: pd.Series, top_n: int = 5) -> pd.Series:
    """Prépare les données pour le graphique avec une catégorie 'Others'."""
    # Garder le top N et regrouper le reste
    if len(position_streams) > top_n:
        position = position_streams.head(top_n)
        others_sum = position_streams.iloc[top_n:].sum()
        # Créer une nouvelle série avec "Others"
        plot_data = pd.concat([position, pd.Series({"Others": others_sum})])
    else:
        plot_data = position_streams
    return plot_data


def generate_pie_chart(plot_data: pd.Series, output_dir: Path) -> Path:
    """Crée le diagramme circulaire et retourne le chemin de sauvegarde."""
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(14, 5))

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
        "Stream Distribution by Position\n(Using position)",
        fontsize=18,
        weight="bold",
        pad=20,
    )

    # Assurer que le pie chart est circulaire
    ax.axis("equal")

    # Ajouter une légende pour les domaines de travail
    legend_labels = [
        f"{position}: {streams:,.0f}"
        for position, streams in plot_data.items()
    ]
    ax.legend(
        wedges,
        legend_labels,
        title="Positions",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=12,
        title_fontsize=14,
    )

    plt.tight_layout()
    output_path = output_dir / "pie_chart_positions.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def display_summary(position_streams: pd.Series, track_count: int) -> None:
    """Affiche un résumé lisible dans la console."""
    total_streams = position_streams.sum()
    print(f"Total tracks analyzed: {track_count}")
    print(f"Total streams: {total_streams:,.0f}")
    print(f"Number of positions: {len(position_streams)}")
    print()
    print("Top 5 potisions by streams (from position):")
    for i, (positions, streams) in enumerate(position_streams.head(5).items(), 1):
        percentage = (streams / total_streams) * 100 if total_streams else 0.0
        print(f"{i}. {positions}: {streams:,.0f} streams ({percentage:.2f}%)")


def main() -> None:
    """Génère un diagramme circulaire des streams par domaine de travail."""
    data_path, output_dir = resolve_paths()
    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. Ensure preprocessing is complete."
        )

    position_streams, track_count = load_position_streams(data_path)
    if position_streams.empty or position_streams.sum() == 0:
        # Informer l'utilisateur si les données sont insuffisantes
        raise ValueError(
            "No position streams available after cleaning. Check data preparation steps."
        )

    display_summary(position_streams, track_count)
    plot_data = prepare_plot_data(position_streams)
    output_path = generate_pie_chart(plot_data, output_dir)
    print(f"\nChart saved in '{output_path}'")


if __name__ == "__main__":
    main()
