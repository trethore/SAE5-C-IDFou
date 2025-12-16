from __future__ import annotations

import pandas as pd
from psycopg2.extensions import connection

from db import get_sqlalchemy_engine


def load_tracks(engine=None) -> pd.DataFrame:
    """Charge les colonnes necessaires depuis la table track."""
    query = """
        WITH latest_rank AS (
            SELECT
                track_id,
                rank_song_hotttnesss,
                rank_song_currency,
                ROW_NUMBER() OVER (PARTITION BY track_id ORDER BY ranks_date DESC) AS rn
            FROM rank_track
        )
        SELECT
            t.track_id,
            t.track_duration,
            t.track_number,
            t.track_disc_number,
            t.track_favorites,
            t.track_interest,
            t.track_comments,
            t.track_date_created,
            t.track_listens,
            lr.rank_song_hotttnesss,
            lr.rank_song_currency
        FROM track t
        LEFT JOIN latest_rank lr ON lr.track_id = t.track_id AND lr.rn = 1;
    """
    engine = engine or get_sqlalchemy_engine()
    return pd.read_sql_query(query, engine)


def load_track_by_id(track_id: str, engine=None) -> pd.DataFrame:
    """Charge une seule piste par track_id."""
    query = """
        SELECT
            track_id,
            track_duration,
            track_number,
            track_disc_number,
            track_favorites,
            track_interest,
            track_comments,
            track_date_created,
            track_listens
        FROM track
        WHERE track_id = %(track_id)s;
    """
    engine = engine or get_sqlalchemy_engine()
    return pd.read_sql_query(query, engine, params={"track_id": track_id})
