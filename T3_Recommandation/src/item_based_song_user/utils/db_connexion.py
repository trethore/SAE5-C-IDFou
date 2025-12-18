import psycopg2
import os
from dotenv import load_dotenv

def get_db_connection():
    """Create database connection."""
    # DB_HOST = "localhost"
    # DB_PORT = os.getenv("PGDB_PORT", "5432")
    # DB_NAME = os.getenv("DB_NAME", "sae5idfou")
    # DB_USER = os.getenv("DB_USER", "idfou")
    # DB_PASSWORD = os.getenv("DB_ROOT_PASSWORD")
    load_dotenv()

    try:
        return psycopg2.connect(
            host="localhost",
            port=os.environ["PGDB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_ROOT_PASSWORD"],
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
