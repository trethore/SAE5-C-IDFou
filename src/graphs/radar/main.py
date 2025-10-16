from math import pi
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd


def resolve_paths() -> Tuple[Path, Path]:
    """Retourne le chemin du jeu de données et le dossier de sortie."""
    # Garantir que le script fonctionne quel que soit le répertoire courant
    src_dir = Path(__file__).resolve().parents[3]
    project_root = src_dir.parent
    data_path = project_root / "cleaned_data" / "merged_tracks.csv"
    output_dir = src_dir / "graphs" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return data_path, output_dir


def load_audio_features(
    data_path: Path,
    selected_genres: List[str],
    audio_cols: List[str],
) -> Tuple[pd.DataFrame, int]:
    """Charge les données audio et filtre les genres souhaités."""
    df = pd.read_csv(data_path)
    # Nettoyer les données pour conserver les colonnes indispensables
    df_clean = df.dropna(subset=["track_genre_top", *audio_cols]).copy()
    df_filtered = df_clean[df_clean["track_genre_top"].isin(selected_genres)]
    return df_filtered, len(df_filtered)


def compute_genre_averages(
    df_filtered: pd.DataFrame,
    selected_genres: List[str],
    audio_cols: List[str],
) -> Dict[str, Dict[str, float]]:
    """Calcule les moyennes des attributs audio par genre."""
    genre_averages: Dict[str, Dict[str, float]] = {}
    for genre in selected_genres:
        genre_data = df_filtered[df_filtered["track_genre_top"] == genre]
        if genre_data.empty:
            continue
        averages = {
            feature: float(genre_data[feature].mean())
            for feature in audio_cols
        }
        averages["count"] = int(len(genre_data))
        genre_averages[genre] = averages
    return genre_averages


def display_summary(
    genre_averages: Dict[str, Dict[str, float]],
    audio_cols: List[str],
) -> None:
    """Affiche un résumé lisible des moyennes calculées."""
    print(f"Total genres plotted: {len(genre_averages)}")
    print()
    for genre, stats in genre_averages.items():
        print(f"{genre} ({int(stats['count'])} tracks):")
        for feature in audio_cols:
            print(f"  - {feature.capitalize()}: {stats[feature]:.3f}")
        print()


def build_radar_chart(
    genre_averages: Dict[str, Dict[str, float]],
    audio_cols: List[str],
    selected_genres: List[str],
    output_dir: Path,
) -> Path:
    """Crée un radar chart comparant les moyennes des genres."""
    categories = [col.capitalize() for col in audio_cols]
    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection="polar"))

    # Couleurs avec bon contraste
    colors = {
        "Rock": "#E63946",
        "Instrumental": "#2A9D8F",
        "Hip-Hop": "#F77F00",
    }

    # Tracer les données pour chaque genre
    plotted = False
    for genre in selected_genres:
        if genre not in genre_averages:
            continue
        values = [genre_averages[genre][feature] for feature in audio_cols]
        values += values[:1]
        ax.plot(
            angles,
            values,
            "o-",
            linewidth=2.5,
            label=f"{genre} (n={int(genre_averages[genre]['count'])})",
            color=colors.get(genre, "#264653"),
        )
        ax.fill(angles, values, alpha=0.15, color=colors.get(genre, "#264653"))
        plotted = True

    if not plotted:
        raise ValueError(
            "No data available for the selected genres. Adjust the genre list."
        )

    # Configurer les étiquettes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=13, weight="bold")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], size=10)
    ax.grid(True, linewidth=0.5, alpha=0.7)

    # Titre et légende
    plt.title(
        "Genre Comparison: Average Audio Features\n(Rock, Instrumental, Hip-Hop)",
        size=16,
        pad=20,
        weight="bold",
    )
    plt.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=14)

    plt.tight_layout()
    output_path = output_dir / "radar_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    """Génère un radar chart comparant les genres sélectionnés."""
    data_path, output_dir = resolve_paths()
    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. Ensure preprocessing is complete."
        )

    audio_cols = [
        "acousticness",
        "danceability",
        "energy",
        "speechiness",
        "instrumentalness",
    ]
    selected_genres = ["Rock", "Instrumental", "Hip-Hop"]

    df_filtered, filtered_count = load_audio_features(
        data_path, selected_genres, audio_cols
    )
    if filtered_count == 0:
        raise ValueError(
            "Filtered dataset is empty. Verify the selected genres and data quality."
        )

    genre_averages = compute_genre_averages(df_filtered, selected_genres, audio_cols)
    if not genre_averages:
        raise ValueError(
            "No averages computed for the selected genres. Review preprocessing steps."
        )

    display_summary(genre_averages, audio_cols)
    output_path = build_radar_chart(
        genre_averages, audio_cols, selected_genres, output_dir
    )
    print(f"\nGraphique sauvegardé dans '{output_path}'")


if __name__ == "__main__":
    main()
