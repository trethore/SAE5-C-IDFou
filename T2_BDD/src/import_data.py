import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import ast
import numpy as np
import traceback

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Database connection parameters
DB_HOST = "localhost" # Assuming running locally or port forwarded
DB_PORT = os.getenv("PGDB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sae5idfou")
DB_USER = os.getenv("DB_USER", "idfou")
DB_PASSWORD = os.getenv("DB_ROOT_PASSWORD")

DATA_DIR = "../../T1_analyse_de_donnees/cleaned_data/"

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def parse_list_string(s):
    try:
        if pd.isna(s):
            return []
        val = ast.literal_eval(s)
        if isinstance(val, list):
            return val
        return []
    except (ValueError, SyntaxError):
        return []

def safe_int(val):
    if pd.isna(val):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None

def safe_float(val):
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def get_valid_ids(conn, table, column):
    cursor = conn.cursor()
    cursor.execute(sql.SQL("SELECT {} FROM {}").format(sql.Identifier(column), sql.Identifier(table)))
    ids = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return ids

def insert_genres(conn):
    print("Inserting Genres...")
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_genres.csv"))
    
    if 0 not in df['genre_id'].values:
        df['parent'] = df['parent'].replace(0, None)
        
    cursor = conn.cursor()
    
    df = df.where(pd.notnull(df), None)
    
    insert_query = """
        INSERT INTO Genres (genre_id, parent_id, title, top_level)
        VALUES %s
        ON CONFLICT (genre_id) DO NOTHING
    """
    
    data_tuples = []
    for _, row in df.iterrows():
        data_tuples.append((
            safe_int(row['genre_id']), 
            None, 
            row['title'], 
            safe_int(row['top_level'])
        ))
        
    execute_values(cursor, insert_query, data_tuples)
    conn.commit()
    
    update_query = """
        UPDATE Genres
        SET parent_id = %s
        WHERE genre_id = %s
    """
    
    update_tuples = []
    for _, row in df.iterrows():
        pid = safe_int(row['parent'])
        gid = safe_int(row['genre_id'])
        if pid is not None and pid != 0:
             update_tuples.append((pid, gid))
             
    try:
        psycopg2.extras.execute_batch(cursor, update_query, update_tuples)
        conn.commit()
    except Exception as e:
        print(f"Warning: Could not update some parent_ids: {e}")
        conn.rollback()

    print(f"Inserted/Updated {len(df)} genres.")
    cursor.close()

def insert_artists(conn):
    print("Inserting Artists...")
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_raw_artists.csv"))
    df = df.where(pd.notnull(df), None)
    
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO Artists (
            artist_id, artist_name, artist_bio, artist_location, artist_latitude, artist_longitude,
            artist_active_year_begin, artist_active_year_end, artist_favorites, artist_comments
        )
        VALUES %s
        ON CONFLICT (artist_id) DO NOTHING
    """
    
    data_tuples = []
    for _, row in df.iterrows():
        data_tuples.append((
            safe_int(row['artist_id']), 
            row['artist_name'], 
            row['artist_bio'], 
            row['artist_location'],
            safe_float(row['artist_latitude']), 
            safe_float(row['artist_longitude']), 
            safe_int(row['artist_active_year_begin']), 
            safe_int(row['artist_active_year_end']),
            safe_int(row['artist_favorites']), 
            safe_int(row['artist_comments'])
        ))
        
    execute_values(cursor, insert_query, data_tuples)
    conn.commit()
    
    print("Processing Artist Junction Tables...")
    
    tags_data = []
    labels_data = []
    members_data = []
    
    for _, row in df.iterrows():
        aid = safe_int(row['artist_id'])
        if aid is None: continue
        
        tags = parse_list_string(row['tags'])
        for tag in tags:
            tags_data.append((aid, tag))
            
        labels = parse_list_string(row['artist_associated_labels'])
        for label in labels:
            labels_data.append((aid, label))
            
        members = parse_list_string(row['artist_members'])
        for member in members:
            members_data.append((aid, member))
            
    if tags_data:
        execute_values(cursor, "INSERT INTO ArtistTags (artist_id, tag) VALUES %s ON CONFLICT DO NOTHING", tags_data)
    
    if labels_data:
        execute_values(cursor, "INSERT INTO ArtistAssociatedLabels (artist_id, label) VALUES %s ON CONFLICT DO NOTHING", labels_data)
        
    if members_data:
        execute_values(cursor, "INSERT INTO ArtistMembers (artist_id, member_name) VALUES %s ON CONFLICT DO NOTHING", members_data)
        
    conn.commit()
    print(f"Inserted {len(df)} artists and related data.")
    cursor.close()

def insert_albums(conn):
    print("Inserting Albums...")
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_raw_albums.csv"))
    df = df.where(pd.notnull(df), None)
    
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO Albums (
            album_id, album_title, album_type, album_tracks_count, album_date_released,
            album_listens, album_favorites, album_comments, album_producer
        )
        VALUES %s
        ON CONFLICT (album_id) DO NOTHING
    """
    
    data_tuples = []
    for _, row in df.iterrows():
        data_tuples.append((
            safe_int(row['album_id']), 
            row['album_title'], 
            row['album_type'], 
            safe_int(row['album_tracks']),
            row['album_date_released'], 
            safe_int(row['album_listens']), 
            safe_int(row['album_favorites']),
            safe_int(row['album_comments']), 
            row['album_producer']
        ))
        
    execute_values(cursor, insert_query, data_tuples)
    conn.commit()
    print(f"Inserted {len(df)} albums.")
    cursor.close()

def insert_tracks(conn):
    print("Inserting Tracks...")
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_tracks.csv"))
    df = df.where(pd.notnull(df), None)
    
    # Pre-fetch valid IDs
    valid_albums = get_valid_ids(conn, 'albums', 'album_id')
    valid_artists = get_valid_ids(conn, 'artists', 'artist_id')
    valid_genres = get_valid_ids(conn, 'genres', 'genre_id')
    
    initial_count = len(df)
    
    # Filter DataFrame
    # Ensure we have valid album_id and artist_id
    # We need to handle NaNs in IDs first (safe_int handles them but for filtering we need to be careful)
    
    # Convert IDs to numeric, coerce errors to NaN
    df['album_id_num'] = pd.to_numeric(df['album_id'], errors='coerce')
    df['artist_id_num'] = pd.to_numeric(df['artist_id'], errors='coerce')
    
    # Filter
    df = df[
        df['album_id_num'].isin(valid_albums) & 
        df['artist_id_num'].isin(valid_artists)
    ]
    
    filtered_count = len(df)
    print(f"Skipped {initial_count - filtered_count} tracks due to missing Album or Artist IDs.")
    
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO Tracks (
            track_id, album_id, artist_id, track_title, track_duration, track_number,
            track_disc_number, track_explicit, track_instrumental, track_listens,
            track_favorites, track_interest, track_comments, track_date_created,
            track_composer, track_lyricist, track_publisher
        )
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING
    """
    
    data_tuples = []
    track_tags_data = []
    track_genres_data = []
    
    for _, row in df.iterrows():
        tid = safe_int(row.get('track_id'))
        
        data_tuples.append((
            tid, 
            safe_int(row.get('album_id')), 
            safe_int(row.get('artist_id')), 
            row.get('track_title'),
            safe_int(row.get('track_duration')), 
            safe_int(row.get('track_number')), 
            safe_int(row.get('track_disc_number')),
            bool(row.get('track_explicit')) if row.get('track_explicit') is not None else False,
            bool(row.get('track_instrumental')) if row.get('track_instrumental') is not None else False,
            safe_int(row.get('track_listens')), 
            safe_int(row.get('track_favorites')), 
            safe_float(row.get('track_interest')),
            safe_int(row.get('track_comments')), 
            row.get('track_date_created'),
            row.get('track_composer'), 
            row.get('track_lyricist'), 
            row.get('track_publisher')
        ))
        
        tags = parse_list_string(row.get('track_tags'))
        for tag in tags:
            track_tags_data.append((tid, tag))
            
        genres_raw = row.get('track_genres')
        try:
            genres_list = parse_list_string(genres_raw)
            for g in genres_list:
                gid = None
                if isinstance(g, dict) and 'genre_id' in g:
                    gid = int(g['genre_id'])
                elif isinstance(g, int):
                    gid = g
                
                if gid is not None and gid in valid_genres:
                    track_genres_data.append((tid, gid))
        except:
            pass

    try:
        execute_values(cursor, insert_query, data_tuples)
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation as e:
        print(f"FK Violation in Tracks: {e}")
        conn.rollback()
        return

    if track_tags_data:
        execute_values(cursor, "INSERT INTO TrackTags (track_id, tag) VALUES %s ON CONFLICT DO NOTHING", track_tags_data)
        
    if track_genres_data:
        try:
            execute_values(cursor, "INSERT INTO TrackGenres (track_id, genre_id) VALUES %s ON CONFLICT DO NOTHING", track_genres_data)
        except psycopg2.errors.ForeignKeyViolation:
            print("Warning: Some track genres referenced non-existent genres.")
            conn.rollback()
            
    conn.commit()
    print(f"Inserted {len(df)} tracks.")
    cursor.close()

def insert_audio_features(conn):
    print("Inserting Audio Features...")
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_echonest.csv"))
    df = df.where(pd.notnull(df), None)
    
    # Pre-fetch valid Track IDs
    valid_tracks = get_valid_ids(conn, 'tracks', 'track_id')
    
    initial_count = len(df)
    df['track_id_num'] = pd.to_numeric(df['track_id'], errors='coerce')
    df = df[df['track_id_num'].isin(valid_tracks)]
    
    print(f"Skipped {initial_count - len(df)} audio features due to missing Track IDs.")
    
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO AudioFeatures (
            track_id, acousticness, danceability, energy, instrumentalness,
            liveness, speechiness, tempo, valence
        )
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING
    """
    
    data_tuples = []
    for _, row in df.iterrows():
        data_tuples.append((
            safe_int(row['track_id']), 
            safe_float(row['acousticness']), 
            safe_float(row['danceability']), 
            safe_float(row['energy']),
            safe_float(row['instrumentalness']), 
            safe_float(row['liveness']), 
            safe_float(row['speechiness']),
            safe_float(row['tempo']), 
            safe_float(row['valence'])
        ))
        
    try:
        execute_values(cursor, insert_query, data_tuples)
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        print("Warning: Audio features referenced non-existent tracks.")
        conn.rollback()
        
    print(f"Inserted {len(df)} audio features.")
    cursor.close()

def main():
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        insert_genres(conn)
        insert_artists(conn)
        insert_albums(conn)
        insert_tracks(conn)
        insert_audio_features(conn)
        print("Data import completed successfully.")
    except Exception as e:
        print(f"An error occurred during import: {e}")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
