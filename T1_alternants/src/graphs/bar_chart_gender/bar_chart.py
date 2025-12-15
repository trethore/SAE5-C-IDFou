"""Génère un diagramme en barres de l'énergie moyenne par genre musical.

Utilisation :
    python3 src/graphs/bar_chart/bar_chart.py
(à lancer depuis la racine du projet après préparation des données dans 'cleaned_data/merged_tracks.csv')
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

globalrules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../clean'))
sys.path.append(globalrules_path)

from globalrules import DEFAULT_OUTPUT_DIR, DEFAULT_GRAPHS_FOLDER


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)
    required_cols = {'gender'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {', '.join(missing)}")
    # On ne conserve que les colonnes utiles pour le calcul de l'énergie moyenne par genre.
    return df[['gender']].dropna()

import pandas as pd

import pandas as pd

def compute_genders(df: pd.DataFrame) -> pd.Series:
    if 'gender' not in df.columns:
        raise ValueError("Le DataFrame doit contenir la colonne 'gender'.")
    # Comptage et normalisation pour obtenir les proportions
    gender_proportions = df['gender'].value_counts(normalize=True).sort_values(ascending=False)

    return gender_proportions

def plot_genders(genders: pd.Series, output_path: str):
    plt.figure(figsize=(20, 10))
    bars = plt.bar(genders.index, genders.values)

    ax = plt.gca()
    ax.bar_label(bars, fmt='%.2f', padding=3, fontsize=18)

    plt.xticks(rotation=45, ha='right', fontsize=18)
    plt.xlabel('Gender', fontsize=18)
    plt.ylabel('Proportion', fontsize=18)
    plt.title('Proportion of each gender', fontsize=18)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Graphique sauvegardé sous : {output_path}")

def main() -> int:
    csv_path = DEFAULT_OUTPUT_DIR / "clean_answers.csv"
    output_path = DEFAULT_GRAPHS_FOLDER / "output" / "bar_chart_genders.png"

    df = load_data(csv_path)
    genders = compute_genders(df)
    plot_genders(genders, output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
