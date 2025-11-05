"""Produit une heatmap des corrélations entre les caractéristiques des morceaux et la moyenne de leur album.

Utilisation :
    python3 src/graphs/heatmap_tracks_vs_albums/heatMap.py
(exécuter depuis la racine du projet avec le fichier 'cleaned_data/merged_tracks.csv' disponible)
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os


def generate_correlation_heatmap(csv_path="../../../../data/merged_tracks.csv", 
                                  output_filename="heatmap_track_vs_album_correlation.png"):
    
    # Colonnes compréhensibles pour l'analyse
    analysis_columns = [
        "energy",              # Intensité énergétique
        "danceability",        # Potentiel dansant
        "valence",             # Valence émotionnelle
        "tempo",               # Tempo
        "acousticness",        # Caractère acoustique
        "instrumentalness",    # Contenu instrumental
        "speechiness",         # Contenu vocal
        "liveness"             # Ambiance live
    ]
    
    # Charger le CSV
    print("Loading CSV data...")
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Vérifier que album_id existe
    if 'album_id' not in df.columns:
        print("ERROR: 'album_id' column not found in CSV!")
        raise SystemExit(1)
    
    # Colonnes nécessaires
    required_columns = ['album_id'] + analysis_columns
    
    # Vérifier que toutes les colonnes existent
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"ERROR: Missing columns in CSV: {', '.join(missing_columns)}")
        raise SystemExit(1)
    
    # Filtrer le dataframe
    df_filtered = df[required_columns].copy()
    
    # Supprimer les lignes avec des valeurs manquantes
    df_filtered = df_filtered.dropna()
    
    print(f"Data loaded: {len(df_filtered)} tracks")
    
    # Filtrer pour garder uniquement les albums avec au moins 2 tracks
    album_counts = df_filtered['album_id'].value_counts()
    valid_albums = album_counts[album_counts >= 2].index
    df_filtered = df_filtered[df_filtered['album_id'].isin(valid_albums)]
    
    print(f"Albums with ≥2 tracks: {len(valid_albums)} albums, {len(df_filtered)} tracks")
    
    # Calculer la moyenne de l'album pour chaque track (sans la track elle-même)
    print("Calculating album means for each track (excluding the track itself)...")
    
    # Calculer la somme et l'effectif pour chaque album
    album_sum = df_filtered.groupby('album_id')[analysis_columns].sum()
    album_count = df_filtered.groupby('album_id')[analysis_columns].count()
    
    # Pour chaque track, calculer la moyenne des autres tracks de son album
    album_means_list = []
    
    for idx, row in df_filtered.iterrows():
        album_id = row['album_id']
        # Moyenne de l'album sans cette track
        # (somme_album - valeur_track) / (album_count - 1)
        album_mean_without_track = (album_sum.loc[album_id] - row[analysis_columns]) / (album_count.loc[album_id] - 1)
        album_means_list.append(album_mean_without_track)
    
    # Créer un DataFrame avec les moyennes d'album
    df_album_means = pd.DataFrame(album_means_list, index=df_filtered.index)
    df_album_means.columns = [f"{col}_album_mean" for col in analysis_columns]
    
    print("Album means calculated. Computing correlation matrix...")
    
    # Combiner les valeurs de track et les moyennes d'album
    df_combined = pd.concat([
        df_filtered[analysis_columns].reset_index(drop=True),
        df_album_means.reset_index(drop=True)
    ], axis=1)
    
    # Calculer la matrice de corrélation entre track features et album mean features
    correlation_matrix = df_combined.corr()
    
    # Extraire uniquement la sous-matrice qui nous intéresse :
    # Lignes = track features, Colonnes = album mean features
    track_vs_album_corr = correlation_matrix.loc[
        analysis_columns,
        [f"{col}_album_mean" for col in analysis_columns]
    ]
    
    # Renommer les colonnes pour plus de clarté
    track_vs_album_corr.columns = [col.replace('_album_mean', ' (Album Avg)') for col in track_vs_album_corr.columns]
    track_vs_album_corr.index = [f"{col} (Track)" for col in track_vs_album_corr.index]
    
    print(f"Correlation matrix calculated!")
    print(f"Diagonal values (track vs its album mean):")
    for i, col in enumerate(analysis_columns):
        print(f"  {col}: {track_vs_album_corr.iloc[i, i]:.3f}")
    
    # Créer la heatmap
    plt.figure(figsize=(14, 12))
    sns.heatmap(track_vs_album_corr, annot=True, cmap='RdYlGn', center=0, 
                fmt='.2f', square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                annot_kws={"size": 9}, vmin=-1, vmax=1)
    
    plt.title('Track vs Album-Average Correlation Heatmap\n(Shows how individual tracks correlate with their album\'s average)', 
              fontsize=16, pad=20, fontweight='bold')
    plt.xlabel('Album Average Features', fontsize=12, fontweight='bold')
    plt.ylabel('Individual Track Features', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    
    # Sauvegarder la heatmap
    output_path = os.path.join('./', output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Track vs Album correlation heatmap saved successfully at: {output_path}")
    return output_path


# Point d'entrée principal
if __name__ == "__main__":
    generate_correlation_heatmap()
