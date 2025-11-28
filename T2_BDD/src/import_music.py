"""
Modular Music Data Import Script
Imports music data from CSV files into PostgreSQL database with UUID primary keys.
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import uuid

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = os.getenv("PGDB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sae5idfou")
DB_USER = os.getenv("DB_USER", "idfou")
DB_PASSWORD = os.getenv("DB_ROOT_PASSWORD")

DATA_DIR = "../../T1_analyse_de_donnees/cleaned_data/"

# Global cache for UUID mapping: {table_name: {old_id: new_uuid}}
ID_MAPPING = {}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_id(old_id):
    """Normalize an ID to consistent string format (handles int/float variations)."""
    if pd.isna(old_id) or old_id == "":
        return None
    try:
        return str(int(float(old_id)))
    except (ValueError, TypeError):
        return str(old_id)

def get_uuid(old_id, table_name):
    """Generate or retrieve UUID for an old_id."""
    old_id_str = normalize_id(old_id)
    if not old_id_str:
        return None
    
    if table_name not in ID_MAPPING:
        ID_MAPPING[table_name] = {}
    
    if old_id_str not in ID_MAPPING[table_name]:
        ID_MAPPING[table_name][old_id_str] = str(uuid.uuid4())
    
    return ID_MAPPING[table_name][old_id_str]

def get_existing_uuid(old_id, table_name):
    """Get existing UUID from cache (for FK lookups)."""
    # Special case for tags: use string directly
    if table_name == "tag":
        tag_name_str = str(old_id) if old_id else None
        if tag_name_str and "tag" in ID_MAPPING and tag_name_str in ID_MAPPING["tag"]:
            return ID_MAPPING["tag"][tag_name_str]
        return None
    
    # Regular ID lookup
    old_id_str = normalize_id(old_id)
    if not old_id_str:
        return None
    
    if table_name in ID_MAPPING and old_id_str in ID_MAPPING[table_name]:
        return ID_MAPPING[table_name][old_id_str]
    return None

def safe_int(val):
    """Convert to int, handling NaN."""
    if pd.isna(val):
        return None
    try:
        return int(float(val))
    except:
        return None

def safe_str(val, max_len=255):
    """Convert to string, truncate if needed."""
    if pd.isna(val):
        return None
    s = str(val)
    return s[:max_len] if len(s) > max_len else s

def safe_bool(val):
    """Convert to boolean, handling string values intelligently."""
    if pd.isna(val) or val == "" or val is None:
        return None
    # If already boolean
    if isinstance(val, bool):
        return val
    # Convert string to boolean: non-empty string = True
    if isinstance(val, str):
        val_lower = val.lower().strip()
        # Empty or explicit false values
        if val_lower in ["", "false", "non", "no", "0"]:
            return False
        # Non-empty string = True (consent text, "yes", etc.)
        return True
    # For numbers: 0 = False, non-zero = True
    try:
        return bool(int(val))
    except:
        return None

def get_db_connection():
    """Create database connection."""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# =============================================================================
# TABLE CONFIGURATION
# Based on database.sql - tables in dependency order
# =============================================================================

# Helper for parsing list strings
import ast

def parse_list(s):
    """Parse string representation of list."""
    if pd.isna(s) or s == "" or s == "[]":
        return []
    try:
        # Handle escaped quotes format: '["\"rock\"", "\"pop\""]' -> ["rock", "pop"]
        if '""' in str(s):
            s = str(s).replace('""', '"')
        
        val = ast.literal_eval(s)
        if isinstance(val, list):
            # Strip whitespace from string items
            return [item.strip() if isinstance(item, str) else item for item in val]
        return []
    except:
        return []

TABLE_CONFIG = [
    # ========== MUSIC DOMAIN ==========
    
    {
        "table": "genre",
        "csv": "clean_genres.csv",
        "pk": "genre_id",
        "columns": {
            "genre_id": "genre_id",
            "title": "title",
            "top_level": "top_level"
        },
        "fk": {},
        "recursive_fk": {"parent_id": "parent"},  # Special: self-referencing
    },
    {
        "table": "album",
        "csv": "clean_raw_albums.csv",
        "pk": "album_id",
        "columns": {
            "album_id": "album_id",
            "album_title": "album_title",
            "album_type": "album_type",
            "album_tracks_count": "album_tracks",
            "album_date_released": "album_date_released",
            "album_listens": "album_listens",
            "album_favorites": "album_favorites",
            "album_comments": "album_comments",
            "album_producer": "album_producer"
        },
        "fk": {},
    },
    {
        "table": "artist",
        "csv": "clean_raw_artists.csv",
        "pk": "artist_id",
        "columns": {
            "artist_id": "artist_id",
            "artist_bio": "artist_bio",
            "artist_location": "artist_location",
            "artist_latitude": "artist_latitude",
            "artist_longitude": "artist_longitude",
            "artist_active_year_begin": "artist_active_year_begin",
            "artist_active_year_end": "artist_active_year_end",
            "artist_favorites": "artist_favorites",
            "artist_comments": "artist_comments"
        },
        "fk": {},
        "create_account": True,  # Special: must create account entry first
        "csv_name_col": "artist_name",  # For account.name
    },
    {
        "table": "tag",
        "csv": None,  # Will be generated from artist and track tags
        "pk": "tag_id",
        "generated": True,  # Special: extract from other CSVs
    },
    {
        "table": "track",
        "csv": "clean_tracks.csv",
        "pk": "track_id",
        "columns": {
            "track_id": "track_id",
            "album_id": "album_id",
            "track_title": "track_title",
            "track_duration": "track_duration",
            "track_number": "track_number",
            "track_disc_number": "track_disc_number",
            "track_explicit": "track_explicit",
            "track_instrumental": "track_instrumental",
            "track_listens": "track_listens",
            "track_favorites": "track_favorites",
            "track_interest": "track_interest",
            "track_comments": "track_comments",
            "track_date_created": "track_date_created",
            "track_composer": "track_composer",
            "track_lyricist": "track_lyricist",
            "track_publisher": "track_publisher"
        },
        "fk": {
            "album_id": "album"
        },
    },
    {
        "table": "audio_feature",
        "csv": "clean_echonest.csv",
        "pk": "track_id",
        "columns": {
            "track_id": "track_id",
            "acousticness": "acousticness",
            "danceability": "danceability",
            "energy": "energy",
            "instrumentalness": "instrumentalness",
            "liveness": "liveness",
            "speechiness": "speechiness",
            "tempo": "tempo",
            "valence": "valence"
        },
        "fk": {
            "track_id": "track"
        },
    },
    {
        "table": "temporal_feature",
        "csv": "clean_features.csv",
        "pk": "track_id",
        "columns": None,  # Will be generated dynamically
        "fk": {
            "track_id": "track"
        },
        "dynamic_columns": True,  # Special: many columns with dots
    },
    
    # ========== JUNCTION TABLES ==========
    
    {
        "table": "track_genre",
        "csv": "clean_tracks.csv",
        "junction": {
            "pk1": ("track_id", "track_id", "track"),
            "pk2": ("genre_id", "track_genres", "genre"),  # CSV has list
            "is_list": True,  # CSV column contains list
        }
    },
    {
        "table": "track_artist_main",
        "csv": "clean_tracks.csv",
        "junction": {
            "pk1": ("track_id", "track_id", "track"),
            "pk2": ("artist_id", "artist_id", "artist"),
            "is_list": False,
        }
    },
    # album_artist: Generated from track + track_artist_main (no direct CSV column)
    {
        "table": "track_tag",
        "csv": "clean_tracks.csv",
        "junction": {
            "pk1": ("track_id", "track_id", "track"),
            "pk2": ("tag_id", "track_tags", "tag"),  # CSV column is track_tags
            "is_list": True,
        }
    },
    {
        "table": "artist_tag",
        "csv": "clean_raw_artists.csv",
        "junction": {
            "pk1": ("artist_id", "artist_id", "artist"),
            "pk2": ("tag_id", "tags", "tag"),  # CSV column is tags
            "is_list": True,
        }
    },
    
    # ========== USER DOMAIN ==========
    
    {
        "table": "user",
        "csv": "../../T1_alternants/src/clean/out/clean_answers.csv",
        "pk": "account_id",
        "columns": {
            "account_id": None,  # Generated
            "pseudo": None,  # Generated
        },
        "fk": {},
        "user_import": True,  # Special: creates account + user + preference
    },
]

# =============================================================================
# IMPORT FUNCTION
# =============================================================================

def import_table(conn, config):
    """
    Generic import function - routes to appropriate handler based on config.
    """
    table = config["table"]
    
    # Route to appropriate handler
    if config.get("generated"):
        import_tags(conn)
    elif config.get("junction"):
        import_junction_table(conn, config)
    elif config.get("user_import"):
        import_users(conn, config)
    elif config.get("recursive_fk"):
        import_recursive_table(conn, config)
    else:
        import_regular_table(conn, config)

# =============================================================================
# SPECIAL HANDLERS
# =============================================================================

def import_tags(conn):
    """Generate and import tag table from artist and track CSVs."""
    print(f"\n{'='*60}")
    print(f"Generating tags from artist and track data...")
    print(f"{'='*60}")
    
    # Collect all unique tags
    all_tags = set()
    
    # From artists
    artist_csv = os.path.join(DATA_DIR, "clean_raw_artists.csv")
    if os.path.exists(artist_csv):
        df_artist = pd.read_csv(artist_csv)
        for tags_str in df_artist["tags"]:
            tags = parse_list(tags_str)
            all_tags.update(tags)
    
    # From tracks
    track_csv = os.path.join(DATA_DIR, "clean_tracks.csv")
    if os.path.exists(track_csv):
        df_track = pd.read_csv(track_csv)
        if "tags" in df_track.columns:
            for tags_str in df_track["tags"]:
                tags = parse_list(tags_str)
                all_tags.update(tags)
    
    # Prepare batch insert data
    cursor = conn.cursor()
    inserted_count = 0
    error_count = 0
    batch_data = []
    
    # Initialize ID mapping
    if "tag" not in ID_MAPPING:
        ID_MAPPING["tag"] = {}
    
    for tag_name in all_tags:
        if tag_name and tag_name != "":
            # For tags, use the name directly as the key (don't normalize as number)
            tag_name_str = str(tag_name)
            
            # Generate UUID for this tag
            if tag_name_str not in ID_MAPPING["tag"]:
                ID_MAPPING["tag"][tag_name_str] = str(uuid.uuid4())
            
            tag_uuid = ID_MAPPING["tag"][tag_name_str]
            batch_data.append((tag_uuid, safe_str(tag_name)))
    
    # Batch insert all tags
    try:
        print(f"📤 Inserting {len(batch_data)} tags in batch...")
        execute_values(
            cursor,
            "INSERT INTO tag (tag_id, tag_name) VALUES %s ON CONFLICT (tag_id) DO NOTHING",
            batch_data,
            page_size=1000
        )
        conn.commit()
        
        # Count how many were actually inserted
        cursor.execute("SELECT COUNT(*) FROM tag")
        inserted_count = cursor.fetchone()[0]
        print(f"✅ Database now contains {inserted_count} tags")
        
    except Exception as e:
        print(f"❌ Error during batch insert: {e}")
        conn.rollback()
        
        # Fallback to individual inserts for debugging
        print("🔄 Falling back to individual inserts...")
        inserted_count = 0
        for tag_uuid, tag_name in batch_data:
            try:
                cursor.execute(
                    "INSERT INTO tag (tag_id, tag_name) VALUES (%s, %s) ON CONFLICT (tag_id) DO NOTHING",
                    (tag_uuid, tag_name)
                )
                conn.commit()
                inserted_count += 1
            except Exception as e2:
                print(f"❌ Error inserting tag '{tag_name}': {e2}")
                conn.rollback()
                error_count += 1
    
    cursor.close()
    
    print(f"\n📈 Import Summary for tag:")
    print(f"   Total unique tags: {len(all_tags)}")
    print(f"   ✅ Successfully inserted: {inserted_count}")
    if error_count > 0:
        print(f"   ❌ Errors: {error_count}")
    print(f"   🗂️  ID mapping cache size: {len(ID_MAPPING.get('tag', {}))}")

def import_junction_table(conn, config):
    """Import junction table (many-to-many relationships)."""
    table = config["table"]
    csv_file = config["csv"]
    junction = config["junction"]
    
    pk1_sql, pk1_csv, pk1_table = junction["pk1"]
    pk2_sql, pk2_csv, pk2_table = junction["pk2"]
    is_list = junction.get("is_list", False)
    
    print(f"\n{'='*60}")
    print(f"Importing junction table {table}...")
    print(f"{'='*60}")
    
    # Debug: Show mapping status
    pk1_count = len(ID_MAPPING.get(pk1_table, {}))
    pk2_count = len(ID_MAPPING.get(pk2_table, {}))
    print(f"🔗 Junction: {pk1_table} ({pk1_count} IDs) ↔ {pk2_table} ({pk2_count} IDs)")
    
    # Load CSV
    csv_path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"📊 Total rows in CSV: {total_rows}")
    
    cursor = conn.cursor()
    inserted_count = 0
    skipped_count = 0
    pk1_missing = 0
    pk2_missing = 0
    
    for idx, row in df.iterrows():
        # Get PK1 UUID
        old_pk1 = row.get(pk1_csv)
        pk1_uuid = get_existing_uuid(old_pk1, pk1_table)
        
        if not pk1_uuid:
            if pk1_missing == 0:  # Show first error only
                print(f"⚠️  Row {idx}: Cannot find {pk1_table} UUID for {pk1_csv}={old_pk1} (normalized: {normalize_id(old_pk1)})")
            skipped_count += 1
            pk1_missing += 1
            continue
        
        # Get PK2 UUID(s)
        pk2_values = []
        if is_list:
            # CSV column contains list
            pk2_list = parse_list(row.get(pk2_csv, "[]"))
            for item in pk2_list:
                pk2_uuid = get_existing_uuid(item, pk2_table)
                if pk2_uuid:
                    pk2_values.append(pk2_uuid)
                else:
                    pk2_missing += 1
        else:
            # CSV column contains single value
            old_pk2 = row.get(pk2_csv)
            pk2_uuid = get_existing_uuid(old_pk2, pk2_table)
            if pk2_uuid:
                pk2_values.append(pk2_uuid)
            else:
                if pk2_missing == 0:  # Show first error only
                    print(f"⚠️  Row {idx}: Cannot find {pk2_table} UUID for {pk2_csv}={old_pk2} (normalized: {normalize_id(old_pk2)})")
                pk2_missing += 1
        
        # Insert all combinations
        for pk2_uuid in pk2_values:
            try:
                cursor.execute(
                    f"INSERT INTO {table} ({pk1_sql}, {pk2_sql}) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    ( pk1_uuid, pk2_uuid)
                )
                conn.commit()
                inserted_count += 1
            except Exception as e:
                if inserted_count == 0:  # Show first error only
                    print(f"❌ Insert error: {e}")
                conn.rollback()
    
    cursor.close()
    
    print(f"\n📈 Import Summary for {table}:")
    print(f"   Total source rows: {total_rows}")
    print(f"   ✅ Successfully inserted: {inserted_count}")
    print(f"   ⚠️  Skipped: {skipped_count}")
    if pk1_missing > 0:
        print(f"   🔍 Missing {pk1_table} references: {pk1_missing}")
    if pk2_missing > 0:
        print(f"   🔍 Missing {pk2_table} references: {pk2_missing}")

def generate_album_artist(conn):
    """Generate album_artist from track + track_artist_main relationships."""
    print(f"\n{'='*60}")
    print(f"Generating album_artist from track + track_artist_main...")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # Get all track->album->artist relationships from database
    cursor.execute("""
        SELECT DISTINCT t.album_id, tam.artist_id
        FROM track t
        JOIN track_artist_main tam ON t.track_id = tam.track_id
        WHERE t.album_id IS NOT NULL
    """)
    
    relationships = cursor.fetchall()
    total_relationships = len(relationships)
    print(f"📊 Found {total_relationships} unique album-artist relationships")
    
    inserted_count = 0
    for album_id, artist_id in relationships:
        try:
            cursor.execute(
                "INSERT INTO album_artist (album_id, artist_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (album_id, artist_id)
            )
            conn.commit()
            inserted_count += 1
        except Exception as e:
            if inserted_count == 0:  # Show first error only
                print(f"❌ Insert error: {e}")
            conn.rollback()
    
    cursor.close()
    
    print(f"\n📈 Import Summary for album_artist:")
    print(f"   Total relationships: {total_relationships}")
    print(f"   ✅ Successfully inserted: {inserted_count}")


def import_users(conn, config):
    """Import user, account, and preference data from clean_answers.csv."""
    table = config["table"]
    csv_file = config["csv"]
    
    print(f"\n{'='*60}")
    print(f"Importing users, accounts, and preferences...")
    print(f"{'='*60}")
    
    # Load CSV
    csv_path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"📊 Total rows in CSV: {total_rows}")
    
    cursor = conn.cursor()
    inserted_count = 0
    
    for idx, row in df.iterrows():
        # Generate UUID for this user
        account_uuid = str(uuid.uuid4())
        
        try:
            # 1. Insert account (with test credentials)
            cursor.execute(
                """INSERT INTO account (account_id, login, password, name, email, created_at) 
                   VALUES (%s, %s, %s, %s, %s, NOW()) ON CONFLICT (account_id) DO NOTHING""",
                (account_uuid, f"user{idx+1}", "test123", f"User {idx+1}", f"user{idx+1}@test.com")
            )
            
            # 2. Insert user
            cursor.execute(
                """INSERT INTO \"user\" (account_id, pseudo) 
                   VALUES (%s, %s) ON CONFLICT (account_id) DO NOTHING""",
                (account_uuid, f"User{idx+1}")
            )
            
            # 3. Insert preference
            cursor.execute(
                """INSERT INTO preference (account_id, age_range, gender, position, has_consented, is_listening, 
                                          frequency, when_listening, duration_pref, energy_pref, tempo_pref, 
                                          feeling_pref, is_live_pref, quality_pref, curiosity_pref, context, 
                                          how, platform, utility, track_genre)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (account_id) DO NOTHING""",
                (
                    account_uuid,
                    safe_str(row.get("age_range")),
                    safe_str(row.get("gender")),
                    safe_str(row.get("position")),
                    safe_bool(row.get("has_consented")),
                    safe_bool(row.get("is_listening")),
                    safe_str(row.get("frequency")),  # CSV: text like "+ d'une fois par jour"
                    float(row.get("when")) if pd.notna(row.get("when")) else None,  # CSV: "when"
                    safe_int(row.get("duration")),  # CSV: "duration"
                    safe_str(row.get("energy")),  # CSV: "energy"
                    float(row.get("tempo")) if pd.notna(row.get("tempo")) else None,  # CSV: "tempo"
                    safe_str(row.get("feeling")),  # CSV: "feeling"
                    safe_str(row.get("is_live")),  # CSV: "is_live"
                    safe_int(row.get("quality")),  # CSV: "quality"
                    safe_int(row.get("curiosity")),  # CSV: "curiosity"
                    safe_str(row.get("context")),  # CSV: list like "['seul(e)', 'entre amis']"
                    safe_str(row.get("how")),
                    safe_str(row.get("platform")),
                    safe_str(row.get("utility")),
                    safe_str(row.get("track_genre"))
                )
            )
            
            conn.commit()
            inserted_count += 1
            
        except Exception as e:
            if inserted_count < 5:  # Show first 5 errors
                print(f"❌ Row {idx} error: {e}")
            conn.rollback()
    
    cursor.close()
    
    print(f"\n📈 Import Summary for users/accounts/preferences:")
    print(f"   Total rows: {total_rows}")
    print(f"   ✅ Successfully inserted: {inserted_count}")

def import_recursive_table(conn, config):
    """Handle self-referencing tables (genre)."""
    table = config["table"]
    csv_file = config["csv"]
    pk_col = config["pk"]
    columns = config["columns"]
    recursive_fk = config["recursive_fk"]
    
    print(f"\n{'='*60}")
    print(f"Importing {table}...")
    print(f"{'='*60}")
    
    # Load CSV
    csv_path = os.path.join(DATA_DIR, csv_file)
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"📊 Total rows in CSV: {total_rows}")
    
    cursor = conn.cursor()
    inserted_count = 0
    
    # First pass: Insert with NULL parent
    for _, row in df.iterrows():
        old_pk = row[columns[pk_col]]
        new_uuid = get_uuid(old_pk, table)
        
        values = {
            pk_col: new_uuid,
            "title": safe_str(row["title"]),
            "top_level": safe_int(row["top_level"])
        }
        
        cursor.execute(
            f"INSERT INTO {table} ({pk_col}, title, top_level) VALUES (%s, %s, %s) ON CONFLICT ({pk_col}) DO NOTHING",
            (values[pk_col], values["title"], values["top_level"])
        )
        inserted_count += 1
    
    conn.commit()
    
    # Second pass: Update parent_id
    for fk_col, csv_col in recursive_fk.items():
        for _, row in df.iterrows():
            old_pk = row[columns[pk_col]]
            old_parent = row.get(csv_col)
            
            if pd.notna(old_parent) and old_parent != 0:
                child_uuid = get_existing_uuid(old_pk, table)
                parent_uuid = get_existing_uuid(old_parent, table)
                
                if child_uuid and parent_uuid:
                    cursor.execute(
                        f"UPDATE {table} SET {fk_col} = %s WHERE {pk_col} = %s",
                        (parent_uuid, child_uuid)
                    )
    
    conn.commit()
    cursor.close()
    
    print(f"\n📈 Import Summary for {table}:")
    print(f"   Total rows: {total_rows}")
    print(f"   ✅ Successfully inserted: {inserted_count}")
    print(f"   🗂️  ID mapping cache size: {len(ID_MAPPING.get(table, {}))}")

def import_regular_table(conn, config):
    """Import regular tables (artist, album, track, features)."""
    table = config["table"]
    csv_file = config["csv"]
    pk_col = config.get("pk")
    columns = config.get("columns", {})
    fk_map = config.get("fk", {})
    
    print(f"\n{'='*60}")
    print(f"Importing {table}...")
    print(f"{'='*60}")
    
    # Load CSV
    csv_path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"📊 Total rows in CSV: {total_rows}")
    
    # Debug: Show FK dependencies
    if fk_map:
        print(f"🔗 Foreign key dependencies:")
        for fk_col, ref_table in fk_map.items():
            ref_count = len(ID_MAPPING.get(ref_table, {}))
            print(f"   - {fk_col} -> {ref_table} (mapping has {ref_count} IDs)")
    
    # Handle dynamic columns (temporal_feature)
    if config.get("dynamic_columns"):
        columns = generate_temporal_columns(df, conn)
    
    cursor = conn.cursor()
    inserted_count = 0
    skipped_count = 0
    fk_missing_count = 0
    commit_every = 100
    
    # Import row by row
    for idx, row in df.iterrows():
        try:
            # Generate or retrieve UUID for PK
            old_pk = row[columns[pk_col]]
            
            # Special case: If PK is also a FK (e.g., audio_feature.track_id -> track.track_id)
            # We must reuse the existing UUID from the referenced table
            if pk_col in fk_map:
                ref_table = fk_map[pk_col]
                new_uuid = get_existing_uuid(old_pk, ref_table)
                if not new_uuid:
                    # Skip row if referenced UUID doesn't exist
                    if skipped_count == 0:  # Only show first few errors
                        print(f"⚠️  Row {idx}: Cannot find {ref_table} UUID for PK {pk_col}={old_pk} (normalized: {normalize_id(old_pk)})")
                    skipped_count += 1
                    fk_missing_count += 1
                    continue
            else:
                # Regular case: generate new UUID
                new_uuid = get_uuid(old_pk, table)
            
            # Special case: artist requires account creation
            if config.get("create_account"):
                name_col = config.get("csv_name_col", "name")
                create_account_for_artist(cursor, conn, new_uuid, row.get(name_col))
            
            # Resolve foreign keys and build values
            values = {}
            skip_row = False
            
            for sql_col, csv_col in columns.items():
                if sql_col == pk_col:
                    values[sql_col] = new_uuid
                elif sql_col in fk_map:
                    # Resolve FK
                    ref_table = fk_map[sql_col]
                    old_fk = row.get(csv_col)
                    fk_uuid = get_existing_uuid(old_fk, ref_table)
                    if not fk_uuid:
                        if fk_missing_count < 5:  # Only show first few errors
                            print(f"⚠️  Row {idx}: Cannot find {ref_table} UUID for FK {sql_col}={old_fk} (normalized: {normalize_id(old_fk)})")
                        skip_row = True
                        fk_missing_count += 1
                        break
                    values[sql_col] = fk_uuid
                else:
                    # Regular column - apply type conversions
                    val = row.get(csv_col)
                    values[sql_col] = convert_value(sql_col, val)
            
            if skip_row:
                skipped_count += 1
                continue
            
            # Build and execute INSERT
            cols = list(values.keys())
            vals = [values[c] for c in cols]
            placeholders = ", ".join(["%s"] * len(cols))
            query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders}) ON CONFLICT ({pk_col}) DO NOTHING"
            
            cursor.execute(query, vals)
            inserted_count += 1
            
            # Periodic commits for performance
            if (idx + 1) % commit_every == 0:
                conn.commit()
                print(f"  Progress: {idx + 1}/{total_rows} rows processed...")
                
        except Exception as e:
            if skipped_count < 5:  # Only show first few errors
                print(f"❌ Row {idx} error: {e}")
            conn.rollback()
            skipped_count += 1
    
    # Final commit
    conn.commit()
    cursor.close()
    
    # Summary
    print(f"\n📈 Import Summary for {table}:")
    print(f"   Total rows: {total_rows}")
    print(f"   ✅ Successfully inserted: {inserted_count}")
    print(f"   ⚠️  Skipped (FK/errors): {skipped_count}")
    if fk_missing_count > 0:
        print(f"   🔍 Missing FK references: {fk_missing_count}")
    print(f"   🗂️  ID mapping cache size: {len(ID_MAPPING.get(table, {}))}")

def create_account_for_artist(cursor, conn, artist_uuid, artist_name):
    """Create account entry for artist."""
    try:
        cursor.execute(
            "INSERT INTO account (account_id, name) VALUES (%s, %s) ON CONFLICT (account_id) DO NOTHING",
            (artist_uuid, safe_str(artist_name))
        )
        conn.commit()
    except Exception:
        conn.rollback()

def generate_temporal_columns(df, conn):
    """Generate column mapping for temporal_feature, filtering to only existing DB columns."""
    columns = {"track_id": "track_id"}
    
    # Get actual columns from database schema
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'temporal_feature'
        AND column_name != 'track_id'
        ORDER BY ordinal_position
    """)
    db_columns = set(row[0] for row in cursor.fetchall())
    cursor.close()
    
    print(f"📋 Database has {len(db_columns)} temporal_feature columns")
    
    # Map CSV columns to SQL columns, but only if they exist in DB
    skipped = 0
    for col in df.columns:
        if col != "track_id":
            # Remove dots from SQL column names
            sql_col = col.replace(".", "")
            
            # Only add if this column exists in the database
            if sql_col in db_columns:
                columns[sql_col] = col
            else:
                skipped += 1
    
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} CSV columns not in database schema")
    
    print(f"✅ Will import {len(columns)-1} matching columns")
    
    return columns

def convert_value(col_name, val):
    """Apply type conversion based on column name."""
    if pd.isna(val):
        return None
    
    # Float columns (features, lat/lon) - CHECK FIRST before boolean!
    # This includes columns like "instrumentalness", "acousticness", etc.
    if any(x in col_name for x in ["latitude", "longitude", "ness", "ability", "energy", "tempo", "valence", "interest", "when_"]) or "feature" in col_name or col_name.startswith(("chroma", "mfcc", "spectral", "tonnetz", "zcr", "rmse")):
        try:
            return float(val)
        except:
            return None
    
    # Integer columns
    if any(x in col_name for x in ["_id", "count", "year", "listens", "favorites", "comments", "duration", "number", "disc", "frequency", "quality", "curiosity", "context"]):
        return safe_int(val)
    
    # String columns (truncate to 255)
    if any(x in col_name for x in ["title", "name", "location", "bio", "type", "composer", "lyricist", "publisher", "producer", "range", "gender", "position", "pref", "how", "platform", "utility", "genre", "pseudo"]):
        return safe_str(val)
    
    # Boolean columns - only for track_explicit, track_instrumental (NOT instrumentalness!)
    if any(x in col_name for x in ["explicit", "consented", "listening"]) or col_name in ["track_instrumental"]:
        if isinstance(val, bool):
            return val
        return bool(val) if pd.notna(val) else None
    
    # Date columns
    if "date" in col_name:
        return val if pd.notna(val) else None
    
    # Default: return as-is
    return val

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main import loop."""
    print("\n" + "="*60)
    print("🎵 MUSIC DATA IMPORT")
    print("="*60)
    
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return
    
    try:
        for config in TABLE_CONFIG:
            import_table(conn, config)
        
        # Generate album_artist from track + track_artist_main relationships
        generate_album_artist(conn)
        
        print("\n" + "="*60)
        print("✅ ALL IMPORTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
