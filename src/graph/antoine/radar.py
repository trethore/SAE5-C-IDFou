import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# Charger les données
df = pd.read_csv('cleaned_data/merged_tracks.csv')

# Sélectionner les colonnes audio features
audio_cols = ['acousticness', 'danceability', 'energy', 'speechiness', 'instrumentalness']

# Nettoyer les données
df_clean = df.dropna(subset=['track_genre_top'] + audio_cols).copy()

# Filtrer les 3 genres souhaités
selected_genres = ['Rock', 'Instrumental', 'Hip-Hop']
df_filtered = df_clean[df_clean['track_genre_top'].isin(selected_genres)]

print(f"Total tracks analyzed: {len(df_filtered)}")
print()

# Calculer la moyenne des caractéristiques audio par genre
genre_averages = {}
for genre in selected_genres:
    genre_data = df_filtered[df_filtered['track_genre_top'] == genre]
    if len(genre_data) > 0:
        genre_averages[genre] = {
            'acousticness': genre_data['acousticness'].mean(),
            'danceability': genre_data['danceability'].mean(),
            'energy': genre_data['energy'].mean(),
            'speechiness': genre_data['speechiness'].mean(),
            'instrumentalness': genre_data['instrumentalness'].mean(),
            'count': len(genre_data)
        }
        print(f"{genre} ({genre_averages[genre]['count']} tracks):")
        print(f"  - Acousticness: {genre_averages[genre]['acousticness']:.3f}")
        print(f"  - Danceability: {genre_averages[genre]['danceability']:.3f}")
        print(f"  - Energy: {genre_averages[genre]['energy']:.3f}")
        print(f"  - Speechiness: {genre_averages[genre]['speechiness']:.3f}")
        print(f"  - Instrumentalness: {genre_averages[genre]['instrumentalness']:.3f}")
        print()

# Préparer les données pour le radar chart
categories = ['Acousticness', 'Danceability', 'Energy', 'Speechiness', 'Instrumentalness']

# Fonction pour extraire les valeurs normalisées
def get_genre_values(genre_stats):
    return [
        genre_stats['acousticness'],
        genre_stats['danceability'],
        genre_stats['energy'],
        genre_stats['speechiness'],
        genre_stats['instrumentalness']
    ]

# Extraire les valeurs pour chaque genre
genre_values = {}
for genre in selected_genres:
    if genre in genre_averages:
        genre_values[genre] = get_genre_values(genre_averages[genre])

# Créer le radar chart
angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
angles += angles[:1]

# Initialiser le graphique
fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

# Couleurs avec bon contraste
colors = {
    'Rock': '#E63946',              # Rouge vif
    'Instrumental': '#2A9D8F',      # Vert turquoise
    'Hip-Hop': '#F77F00'            # Orange
}

# Tracer les données pour chaque genre
for genre in selected_genres:
    if genre in genre_values:
        values = genre_values[genre] + genre_values[genre][:1]  # Compléter le cercle
        ax.plot(angles, values, 'o-', linewidth=2.5, 
                label=f'{genre} (n={genre_averages[genre]["count"]})', 
                color=colors[genre])
        ax.fill(angles, values, alpha=0.15, color=colors[genre])

# Configurer les étiquettes
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=13, weight='bold')
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=10)
ax.grid(True, linewidth=0.5, alpha=0.7)

# Titre et légende
plt.title('Genre Comparison: Average Audio Features\n(Rock, Instrumental, Hip-Hop)', 
          size=16, pad=20, weight='bold')
plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=14)

plt.tight_layout()
plt.savefig('src/graph/antoine/radar_comparison.png', dpi=300, bbox_inches='tight')
print("\nGraphique sauvegardé dans 'src/graph/antoine/radar_comparison.png'")
