import sys
import os
import uuid
import random

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.db_connexion import get_db_connection

def load_env_file():
    # .../src
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # .../T3_Recommandation
    t3_dir = os.path.dirname(src_dir)
    # .../SAE5-C-IDFou
    project_root = os.path.dirname(t3_dir)
    
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        print(f"Loading .env from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Handle quotes
                    value = value.strip().strip("'").strip('"')
                    os.environ[key.strip()] = value.strip()

def create_test_user():
    load_env_file()
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    cur = conn.cursor()
    
    # LIST OF SONGS TO LISTEN TO
    # Format: (Title, ListenCount)
    TARGET_TRACK_TITLES = [
        ("Valentina", 2),
        ("Waking Up (Instrumental)", 3),
        ("The Rhythmic A.I. Nomothetic", 2),
        ("Eleanor", 3),
        ("Gathering", 2),
        ("Symbiosis", 1),
        ("Prosecutor as Bully (Lessig on Aaron Swartz)", 1),
        ("Seeing The Future", 2),
        ("Playing For the Train", 1),
        ("Sabre", 2)
    ]

    try:
        # 1. Create Account/User
        new_uuid = str(uuid.uuid4())
        login = f"test_user_{new_uuid[:8]}"
        
        print(f"Creating user {login} with UUID {new_uuid}")
        
        cur.execute("""
            INSERT INTO account (account_id, login, name)
            VALUES (%s, %s, 'Test User')
        """, (new_uuid, login))
        
        cur.execute("""
            INSERT INTO "user" (account_id, pseudo)
            VALUES (%s, 'TestUserPseudo')
        """, (new_uuid,))
        
        # 2. Find tracks by title
        print("Finding tracks from target list...")
        tracks_to_listen = []
        
        for title, count in TARGET_TRACK_TITLES:
            # simple ILIKE search, take first result
            cur.execute("SELECT track_id, track_title FROM track WHERE track_title ILIKE %s LIMIT 1", (title,))
            row = cur.fetchone()
            if row:
                print(f"  Found: '{title}' -> {row[1]} ({row[0]}) - Count: {count}")
                tracks_to_listen.append((row[0], count))
            else:
                print(f"  WARNING: Could not find track with title '{title}'")
        
        if not tracks_to_listen:
            print("No tracks found from the list. Aborting.")
            conn.rollback()
            return

        # 3. Insert History
            
        for tid, count in tracks_to_listen:
            cur.execute("""
                INSERT INTO track_user_listen (track_id, account_id, count)
                VALUES (%s, %s, %s)
            """, (tid, new_uuid, count))
            
        conn.commit()
        print("Successfully created test user and history.")
        print(f"USER_ID: {new_uuid}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_test_user()
