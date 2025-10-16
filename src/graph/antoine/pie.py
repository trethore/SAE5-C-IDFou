import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Charger les données
df = pd.read_csv('cleaned_data/merged_tracks.csv')

# Nettoyer les données : supprimer les valeurs nulles
df_clean = df.dropna(subset=['track_genre_top', 'track_listens']).copy()

# Grouper par genre principal (track_genre_top) et sommer les streams
genre_streams = df_clean.groupby('track_genre_top')['track_listens'].sum().sort_values(ascending=False)

print(f"Total tracks analyzed: {len(df_clean)}")
print(f"Total streams: {genre_streams.sum():,.0f}")
print(f"Number of top genres: {len(genre_streams)}")
print()
print("Top 10 genres by streams (from track_genre_top):")
for i, (genre, streams) in enumerate(genre_streams.head(10).items(), 1):
    percentage = (streams / genre_streams.sum()) * 100
    print(f"{i}. {genre}: {streams:,.0f} streams ({percentage:.2f}%)")

# Créer le pie chart
# Garder le top 10 et regrouper les autres dans "Others"
top_n = 10
if len(genre_streams) > top_n:
    top_genres = genre_streams.head(top_n)
    others_sum = genre_streams.iloc[top_n:].sum()
    
    # Créer une nouvelle série avec "Others"
    plot_data = pd.concat([top_genres, pd.Series({'Others': others_sum})])
else:
    plot_data = genre_streams

# Créer le graphique
fig, ax = plt.subplots(figsize=(14, 10))

# Couleurs personnalisées
colors = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))

# Créer le pie chart
wedges, texts, autotexts = ax.pie(
    plot_data,
    labels=plot_data.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'fontsize': 11, 'weight': 'bold'},
    pctdistance=0.85
)

# Améliorer la lisibilité des pourcentages
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontsize(10)
    autotext.set_weight('bold')

# Améliorer la lisibilité des labels
for text in texts:
    text.set_fontsize(11)

# Titre
plt.title('Stream Distribution by Genre\n(Using track_genre_top)', 
          fontsize=18, weight='bold', pad=20)

# Assurer que le pie chart est circulaire
ax.axis('equal')

# Ajouter une légende pour les genres
ax.legend(
    wedges,
    [f'{genre}: {streams:,.0f}' for genre, streams in plot_data.items()],
    title="Genres",
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1),
    fontsize=12,
    title_fontsize=14
)

plt.tight_layout()
plt.savefig('src/graph/antoine/pie_chart_genres.png', dpi=300, bbox_inches='tight')
print("\nChart saved in 'src/graph/antoine/pie_chart_genres.png'")
