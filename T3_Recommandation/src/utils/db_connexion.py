import psycopg2
import os

def get_db_connection():
    """Create database connection."""
    DB_HOST = "localhost"
    DB_PORT = os.getenv("PGDB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "sae5idfou")
    DB_USER = os.getenv("DB_USER", "idfou")
    DB_PASSWORD = os.getenv("DB_ROOT_PASSWORD")
    
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