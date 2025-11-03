"""Visualise la répartition du nombre de morceaux par artiste en fonction du tempo via un area chart empilé.

Utilisation :
    python3 src/graphs/area_chart/area_chart.py
(à lancer depuis la racine du projet pour accéder à 'cleaned_data/merged_tracks.csv' et produire 'area_chart_artists.png')
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


def generate_area_chart(csv_path: str = "../../../cleaned_data/merged_tracks.csv",
                        output_filename: str = "area_chart_artists.png",
                        top_n: int = 9):

    # Charger le CSV
    df = pd.read_csv(csv_path)

    # Colonnes nécessaires
    required = ["artist_id", "track_id", "tempo", "artist_favorites"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"ERROR: Missing columns in CSV: {', '.join(missing)}")
        raise SystemExit(1)

    # Nettoyage de base
    df["artist_id"] = pd.to_numeric(df["artist_id"], errors="coerce")
    df["track_id"] = pd.to_numeric(df["track_id"], errors="coerce")
    df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce")
    df["artist_favorites"] = pd.to_numeric(df["artist_favorites"], errors="coerce").fillna(0)

    # Libellés artistes
    if "artist_name" in df.columns:
        name_map = (
            df[["artist_id", "artist_name"]]
            .dropna()
            .drop_duplicates()
            .set_index("artist_id")["artist_name"]
        )
    else:
        name_map = pd.Series(dtype=str)

    # Top N artistes par favoris (max par artiste) parmi ceux avec tempo defini
    valid = df.dropna(subset=["tempo"]).copy()
    artist_rank = (
        valid.groupby("artist_id", dropna=True)["artist_favorites"]
        .max()
        .sort_values(ascending=False)
    )
    top_artists = artist_rank.head(int(top_n)).index.tolist()

    # Restreindre au top et supprimer tempo manquant
    work = df[df["artist_id"].isin(top_artists)].dropna(subset=["tempo"]).copy()

    # Dé-dupliquer paires (artist, track, tempo) si données explosées
    work = work.drop_duplicates(subset=["artist_id", "track_id", "tempo"])

    # Découper le tempo en 12 bins
    bins = 12
    work["bin"] = pd.cut(work["tempo"], bins=bins)

    # Compter le nombre de morceaux par artiste / bin
    g = work.groupby(["artist_id", "bin"]).size().rename("count").reset_index()

    # S'assurer que tous les bins existent pour chaque artiste
    all_bins = g["bin"].cat.categories
    artists = g["artist_id"].unique()
    full_index = pd.MultiIndex.from_product([artists, all_bins], names=["artist_id", "bin"])
    g = g.set_index(["artist_id", "bin"]).reindex(full_index, fill_value=0).reset_index()

    # Centres des intervalles (x)
    g["x"] = g["bin"].apply(lambda iv: (iv.left + iv.right) / 2)

    # Noms pour la légende
    def _name(aid):
        try:
            return str(name_map.loc[aid])
        except Exception:
            return f"Artist {int(aid) if pd.notna(aid) else 'Unknown'}"
    g["artist_name"] = g["artist_id"].apply(_name)

    # Tableau croisé pour tracer
    pivot = (
        g.pivot_table(index="x", columns="artist_name", values="count", aggfunc="sum")
        .sort_index()
        .fillna(0)
    )
    x = pivot.index.values
    ystack = pivot.values.T

    # Tracé: aires empilées
    plt.figure(figsize=(14, 8))
    plt.stackplot(x, ystack, labels=pivot.columns)
    shown = len(pivot.columns)
    plt.title(f"Top {shown} Artists by Favorites - Track Count across Tempo (stacked)")
    plt.xlabel("Tempo (BPM)")
    plt.ylabel("Track Count")
    plt.legend(loc="upper right", ncol=2, fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()

    # Sauvegarde
    output_path = os.path.join('./', output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Area chart saved successfully at: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_area_chart()
