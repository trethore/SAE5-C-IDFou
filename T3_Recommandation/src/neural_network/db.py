import os
from typing import Optional

import psycopg2
from dotenv import load_dotenv


def load_env(env_path: Optional[str] = None) -> None:
    load_dotenv(dotenv_path=env_path, override=False)


def get_connection(env_path: Optional[str] = None):
    """
    Create a psycopg2 connection using .env values.
    Falls back to sane defaults matching docker-compose.
    """
    load_env(env_path)
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT") or os.getenv("PGDB_PORT") or 5432)
    dbname = os.getenv("DB_NAME", "sae5idfou")
    user = os.getenv("DB_USER", "idfou")
    password = os.getenv("DB_ROOT_PASSWORD") or os.getenv("DB_PASSWORD") or ""

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
