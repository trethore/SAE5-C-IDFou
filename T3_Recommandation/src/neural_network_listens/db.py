import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

import psycopg2
import sqlalchemy as sa
from dotenv import load_dotenv


def _load_env(env_path: Optional[str | Path]) -> None:
    """Charge les variables d environnement"""
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        # .env a la racine du repo si sa fail
        root_env = Path(__file__).resolve().parents[3] / ".env"
        load_dotenv(dotenv_path=root_env)


@contextmanager
def get_connection(env_path: Optional[str | Path] = None) -> Iterator[psycopg2.extensions.connection]:
    """Context manager"""
    _load_env(env_path)
    conn = psycopg2.connect(
        host="localhost",
        port=os.getenv("PGDB_PORT", "5432"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_ROOT_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
    )
    try:
        yield conn
    finally:
        conn.close()


def get_sqlalchemy_engine(env_path: Optional[str | Path] = None) -> sa.Engine:
    _load_env(env_path)
    user = os.getenv("DB_USER")
    password = os.getenv("DB_ROOT_PASSWORD")
    port = os.getenv("PGDB_PORT", "5432")
    dbname = os.getenv("DB_NAME")
    url = f"postgresql+psycopg2://{user}:{password}@localhost:{port}/{dbname}"
    return sa.create_engine(url)
