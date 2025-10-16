import pandas as pd
import matplotlib.pyplot as plt
import os


def generate_bubble_chart(csv_path="../../../../data/merged_tracks.csv",
                          output_filename="bubble_chart_albums.png"):
    # Charger le CSV
    df = pd.read_csv(csv_path)
    
    # Colonnes nécessaires pour le bubble chart
    required_columns = [
        "album_id",
        "track_id",
        "energy",             # Pour l'axe des X
        "danceability",       # Pour l'axe des Y
        "track_listens",      # Pour la taille des bulles
        "valence"             # Pour la couleur (positivité)
    ]
    
    # Vérifier que toutes les colonnes existent
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"ERROR: Missing columns in CSV: {', '.join(missing_columns)}")
        raise SystemExit(1)
    
    # Filtrer le dataframe
    df_bubble = df[required_columns].copy()
    
    # Supprimer les lignes avec des valeurs manquantes
    df_bubble = df_bubble.dropna()
    
    # Regrouper par album_id et calculer les moyennes + nombre de tracks
    df_albums = df_bubble.groupby('album_id').agg({
        'energy': 'mean',             # Énergie moyenne par album
        'danceability': 'mean',       # Danseabilité moyenne par album
        'valence': 'mean',            # Valence moyenne par album
        'track_id': 'count'           # Nombre de morceaux par album (pour la taille)
    }).reset_index()
    
    # Renommer la colonne track_id en track_count
    df_albums.rename(columns={'track_id': 'track_count'}, inplace=True)
    
    print(f"Data loaded: {len(df_albums)} albums to display")
    print(f"   Columns used:")
    print(f"   - X axis: energy (average energy)")
    print(f"   - Y axis: danceability (average danceability)")
    print(f"   - Size: track_count (number of tracks per album)")
    print(f"   - Color: valence (average emotional positivity)")
    
    # Créer le bubble chart
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Normaliser la taille des bulles (track_count)
    size_factor = 50  # Facteur pour rendre les bulles visibles
    bubble_sizes = df_albums['track_count'] * size_factor
    
    # Créer le scatter plot avec couleur basée sur valence
    scatter = ax.scatter(
        df_albums['energy'],
        df_albums['danceability'],
        s=bubble_sizes,
        c=df_albums['valence'],
        cmap='coolwarm',
        alpha=0.6,
        edgecolors='black',
        linewidth=0.5
    )
    
    # Ajouter une colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Valence (Emotional Positivity, 0-1)', rotation=270, labelpad=20, fontsize=12)
    
    # Labels et titre
    ax.set_xlabel('Average Energy (0-1)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Danceability (0-1)', fontsize=14, fontweight='bold')
    ax.set_title('Bubble Chart: Albums by Energy, Danceability and Track Count\n(Size = Number of Tracks, Color = Valence)', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Grille
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Ajouter une légende pour la taille
    # Créer des bulles de référence pour la légende
    # Calculer des tailles représentatives basées sur les quantiles
    q25 = df_albums['track_count'].quantile(0.25) * size_factor
    q50 = df_albums['track_count'].quantile(0.50) * size_factor
    q75 = df_albums['track_count'].quantile(0.75) * size_factor
    
    # Arrondir pour afficher des nombres entiers de tracks
    tracks_25 = int(df_albums['track_count'].quantile(0.25))
    tracks_50 = int(df_albums['track_count'].quantile(0.50))
    tracks_75 = int(df_albums['track_count'].quantile(0.75))
    
    legend_sizes = [q25, q50, q75]
    legend_labels = [f'{tracks_25} tracks', f'{tracks_50} tracks', f'{tracks_75} tracks']
    legend_handles = []
    
    for size, label in zip(legend_sizes, legend_labels):
        legend_handles.append(plt.scatter([], [], s=size, c='gray', alpha=0.6, 
                                         edgecolors='black', linewidth=0.5, label=label))
    
    ax.legend(handles=legend_handles, loc='upper right', title='Album Size', fontsize=10)
    
    plt.tight_layout()
    
    # Sauvegarder le graphique
    output_path = os.path.join('./', output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Bubble chart saved successfully at: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_bubble_chart()
