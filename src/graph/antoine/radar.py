import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# Charger les données
df = pd.read_csv('cleaned_data/merged_tracks.csv')

# Sélectionner les colonnes audio features
audio_cols = ['acousticness', 'danceability', 'energy', 'speechiness', 'instrumentalness']

# Créer un score composite basé sur les caractéristiques audio
df_clean = df.dropna(subset=audio_cols).copy()

# Calculer un score composite (moyenne des caractéristiques normalisées)
# Toutes les valeurs sont déjà entre 0 et 1
df_clean['composite_score'] = (
    df_clean['acousticness'] + 
    df_clean['danceability'] + 
    df_clean['energy'] + 
    df_clean['speechiness'] + 
    df_clean['instrumentalness']
) / 5

# Trouver la meilleure et la pire musique
best_track = df_clean.loc[df_clean['composite_score'].idxmax()]
worst_track = df_clean.loc[df_clean['composite_score'].idxmin()]

# Calculer la moyenne de tous les morceaux
average_track = {
    'track_title': 'MOYENNE',
    'artist_name': 'Tous les morceaux',
    'composite_score': df_clean['composite_score'].mean(),
    'acousticness': df_clean['acousticness'].mean(),
    'danceability': df_clean['danceability'].mean(),
    'energy': df_clean['energy'].mean(),
    'speechiness': df_clean['speechiness'].mean(),
    'instrumentalness': df_clean['instrumentalness'].mean()
}

print(f"Meilleure musique: {best_track['track_title']} - {best_track['artist_name']}")
print(f"Score composite: {best_track['composite_score']:.3f}")
print(f"  - Acousticness: {best_track['acousticness']:.3f}")
print(f"  - Danceability: {best_track['danceability']:.3f}")
print(f"  - Energy: {best_track['energy']:.3f}")
print(f"  - Speechiness: {best_track['speechiness']:.3f}")
print(f"  - Instrumentalness: {best_track['instrumentalness']:.3f}")
print()
print(f"Pire musique: {worst_track['track_title']} - {worst_track['artist_name']}")
print(f"Score composite: {worst_track['composite_score']:.3f}")
print(f"  - Acousticness: {worst_track['acousticness']:.3f}")
print(f"  - Danceability: {worst_track['danceability']:.3f}")
print(f"  - Energy: {worst_track['energy']:.3f}")
print(f"  - Speechiness: {worst_track['speechiness']:.3f}")
print(f"  - Instrumentalness: {worst_track['instrumentalness']:.3f}")
print()
print(f"Moyenne (tous les morceaux):")
print(f"Score composite: {average_track['composite_score']:.3f}")
print(f"  - Acousticness: {average_track['acousticness']:.3f}")
print(f"  - Danceability: {average_track['danceability']:.3f}")
print(f"  - Energy: {average_track['energy']:.3f}")
print(f"  - Speechiness: {average_track['speechiness']:.3f}")
print(f"  - Instrumentalness: {average_track['instrumentalness']:.3f}")
print()

# Préparer les données pour le radar chart
categories = ['Acousticness', 'Danceability', 'Energy', 'Speechiness', 'Instrumentalness']

# Normaliser les valeurs entre 0 et 1 pour le graphique
def normalize_values(track_data):
    values = []
    
    # Acousticness (déjà normalisé entre 0 et 1)
    values.append(track_data['acousticness'])
    
    # Danceability (déjà normalisé entre 0 et 1)
    values.append(track_data['danceability'])
    
    # Energy (déjà normalisé entre 0 et 1)
    values.append(track_data['energy'])
    
    # Speechiness (déjà normalisé entre 0 et 1)
    values.append(track_data['speechiness'])
    
    # Instrumentalness (déjà normalisé entre 0 et 1)
    values.append(track_data['instrumentalness'])
    
    return values

best_values = normalize_values(best_track)
worst_values = normalize_values(worst_track)
average_values = normalize_values(average_track)

# Créer le radar chart
angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
best_values += best_values[:1]  # Compléter le cercle
worst_values += worst_values[:1]
average_values += average_values[:1]
angles += angles[:1]

# Initialiser le graphique
fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

# Tracer les données
best_label = f'{best_track["track_title"][:25]} - {best_track["artist_name"][:20]}'
worst_label = f'{worst_track["track_title"][:25]} - {worst_track["artist_name"][:20]}'

ax.plot(angles, best_values, 'o-', linewidth=2.5, label=f'Best: {best_label}', color='#00b894')
ax.fill(angles, best_values, alpha=0.25, color='#00b894')

ax.plot(angles, worst_values, 'o-', linewidth=2.5, label=f'Worst: {worst_label}', color='#d63031')
ax.fill(angles, worst_values, alpha=0.25, color='#d63031')

ax.plot(angles, average_values, 'o--', linewidth=3, label='Average (all tracks)', color='#fdcb6e')
ax.fill(angles, average_values, alpha=0.15, color='#fdcb6e')

# Configurer les étiquettes
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=13, weight='bold')
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=10)
ax.grid(True, linewidth=0.5, alpha=0.7)

# Titre et légende
plt.title('Radar Chart: Best vs Worst vs Average\n(Audio Features)', 
          size=18, pad=20, weight='bold')
plt.legend(loc='upper right', bbox_to_anchor=(1.4, 1.1), fontsize=10)

plt.tight_layout()
plt.savefig('src/graph/antoine/radar_comparison.png', dpi=300, bbox_inches='tight')
print("\nGraphique sauvegardé dans 'src/graph/antoine/radar_comparison.png'")
