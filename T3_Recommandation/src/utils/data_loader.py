import pandas as pd
import psycopg2
from .db_connexion import get_db_connection

def get_user_listen_history(account_id):
    """
    Fetches the list of tracks listened to by the user.
    Returns a list of track_ids.
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        query = """
            SELECT track_id, count
            FROM track_user_listen
            WHERE account_id = %s;
        """
        cur.execute(query, (account_id,))
        rows = cur.fetchall()
        # Return dict of track_id -> count, or just list if counts not used yet
        history = {row[0]: row[1] for row in rows}
        cur.close()
        return history
    except Exception as e:
        print(f"Error fetching user history: {e}")
        return {}
    finally:
        conn.close()

def get_all_tracks_data():
    """
    Fetches feature-rich data for all tracks:
    - Metadata: Track ID, Title
    - Temporal Features: All columns from temporal_feature table
    - Textual Data: Genres, Tags, Artist Names
    
    Returns a pandas DataFrame.
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:

        
        # Optimization: Use CTEs to pre-aggregate tags/genres/artists because the GROUP BY above is insane.
        optimized_query = """
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
            -- Temporal Features (ALL columns)
            tf.*,
            -- Textual
            COALESCE(tg.genres, '') as genres,
            COALESCE(tt.tags, '') as tags,
            COALESCE(ta.artists, '') as artists
        FROM track t
        JOIN temporal_feature tf ON tf.track_id = t.track_id
        LEFT JOIN track_genres tg ON tg.track_id = t.track_id
        LEFT JOIN track_tags tt ON tt.track_id = t.track_id
        LEFT JOIN track_artists ta ON ta.track_id = t.track_id;
        """
        
        df = pd.read_sql_query(optimized_query, conn)
        # Drop duplicate track_id columns if any (tf has track_id too)
        df = df.loc[:, ~df.columns.duplicated()]
        return df
        
    except Exception as e:
        print(f"Error fetching track data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
