import os
import uuid
from typing import Dict, Optional
import pandas as pd

try:
    from item_based_song_user.utils.db_connexion import get_db_connection
except Exception:
    def get_db_connection():
        return None


def get_all_tracks_data() -> pd.DataFrame:
   
    conn = get_db_connection()
    if conn:
        try:
            query = """
            WITH track_genres AS (
                SELECT tg.track_id, string_agg(DISTINCT g.title, ' ') as genres
                FROM track_genre tg
                JOIN genre g ON g.genre_id = tg.genre_id
                GROUP BY tg.track_id
            ),
            track_tags AS (
                SELECT tt.track_id, string_agg(DISTINCT tag.tag_name, ' ') as tags
                FROM track_tag tt
                JOIN tag ON tag.tag_id = tt.tag_id
                GROUP BY tt.track_id
            ),
            track_artists AS (
                SELECT tam.track_id, string_agg(DISTINCT a.name, ' ') as artists
                FROM track_artist_main tam
                JOIN artist art ON art.artist_id = tam.artist_id
                JOIN account a ON a.account_id = art.artist_id
                GROUP BY tam.track_id
            )
            SELECT
                t.track_id,
                t.track_title,
                af.acousticness,
                af.danceability,
                af.energy,
                af.instrumentalness,
                af.liveness,
                af.speechiness,
                af.tempo,
                af.valence,
                COALESCE(tg.genres, '') as genres,
                COALESCE(tt.tags, '') as tags,
                COALESCE(ta.artists, '') as artists,
                COALESCE(alb.album_title, '') as album_title
            FROM track t
            LEFT JOIN audio_feature af ON af.track_id = t.track_id
            LEFT JOIN track_genres tg ON tg.track_id = t.track_id
            LEFT JOIN track_tags tt ON tt.track_id = t.track_id
            LEFT JOIN track_artists ta ON ta.track_id = t.track_id
            LEFT JOIN album alb ON alb.album_id = t.album_id;
            """
            df = pd.read_sql_query(query, conn)
            df = df.loc[:, ~df.columns.duplicated()]
            return df
        except Exception as e:
            print(f"DB query failed: {e}")

    # Fallback to CSV: check 'data/clean_tracks.csv' then 'clean_tracks.csv' in CWD
    candidates = [
        os.path.join(os.getcwd(), 'data', 'clean_tracks.csv'),
        os.path.join(os.getcwd(), 'clean_tracks.csv')
    ]
    for fallback in candidates:
        if os.path.exists(fallback):
            try:
                df = pd.read_csv(fallback)
                # Keep only relevant columns if present
                keep = ['track_id', 'track_title', 'genres', 'tags', 'artists', 'album_title']
                # audio cols might be present under audio_feature or top-level
                audio_cols = ['acousticness','danceability','energy','instrumentalness','liveness','speechiness','tempo','valence']
                for c in audio_cols:
                    if c in df.columns and c not in keep:
                        keep.append(c)
                df = df[[c for c in keep if c in df.columns]]
                return df
            except Exception as e:
                print(f"Failed reading fallback CSV ({fallback}): {e}")

    print("No track data available (DB and CSV fallback failed)")
    return pd.DataFrame()
