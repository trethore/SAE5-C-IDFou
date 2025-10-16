import pandas as pd
import matplotlib.pyplot as plt
import sys
import os


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)
    required_cols = {'track_genre_top', 'energy'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {', '.join(missing)}")
    return df[list(required_cols)].dropna()


def compute_energy_by_genre(df: pd.DataFrame) -> pd.Series:
    energy_by_genre = df.groupby('track_genre_top')['energy'].mean()
    return energy_by_genre.dropna().sort_values(ascending=True)


def plot_energy_by_genre(energy_by_genre: pd.Series, output_path: str):
    plt.figure(figsize=(20, 10))
    bars = plt.bar(energy_by_genre.index, energy_by_genre.values, color='orange')

    ax = plt.gca()
    ax.bar_label(bars, fmt='%.2f', padding=3, fontsize=14)

    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Music Genre', fontsize=14)
    plt.ylabel('Average Energy', fontsize=14)
    plt.title('Average Energy by Music Genre', fontsize=18)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Graphique sauvegardé sous : {output_path}")


def main() -> int:
    # même logique que ton autre script
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    csv_path = os.path.join(project_root, "cleaned_data", "merged_tracks.csv")
    output_path = os.path.join(os.path.dirname(__file__), "energy_by_genre.png")

    df = load_data(csv_path)
    energy_by_genre = compute_energy_by_genre(df)
    plot_energy_by_genre(energy_by_genre, output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
