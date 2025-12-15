from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
from psycopg2.extensions import connection


def _read_sql(conn: connection, query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, conn)


def load_tracks(conn: connection) -> pd.DataFrame:
    """
    Load core track metadata and simple popularity signals.
    """
    query = """
        SELECT
            t.track_id,
            t.album_id,
            t.track_title,
            t.track_duration,
            t.track_explicit::int AS track_explicit,
            t.track_instrumental::int AS track_instrumental,
            t.track_listens,
            t.track_favorites,
            t.track_interest,
            t.track_comments,
            t.track_date_created
        FROM track t;
    """
    return _read_sql(conn, query)


def load_audio_features(conn: connection) -> pd.DataFrame:
    """
    Load numeric acoustic features; many rows are sparse.
    """
    query = """
        SELECT
            track_id,
            acousticness,
            danceability,
            energy,
            instrumentalness,
            liveness,
            speechiness,
            tempo,
            valence
        FROM audio_feature;
    """
    return _read_sql(conn, query)


def load_rank_labels(conn: connection) -> pd.DataFrame:
    """
    Use the most recent rank per track as a training target proxy.
    """
    query = """
        WITH latest AS (
            SELECT
                track_id,
                rank_song_hotttnesss,
                rank_song_currency,
                ranks_date,
                ROW_NUMBER() OVER (PARTITION BY track_id ORDER BY ranks_date DESC) AS rn
            FROM rank_track
        )
        SELECT track_id, rank_song_hotttnesss, rank_song_currency, ranks_date
        FROM latest
        WHERE rn = 1;
    """
    return _read_sql(conn, query)


def load_genres(conn: connection) -> pd.DataFrame:
    """
    Aggregate genres per track.
    """
    query = """
        SELECT
            tg.track_id,
            ARRAY_AGG(g.title) AS genres
        FROM track_genre tg
        JOIN genre g ON g.genre_id = tg.genre_id
        GROUP BY tg.track_id;
    """
    return _read_sql(conn, query)


def load_tags(conn: connection) -> pd.DataFrame:
    """
    Aggregate tags per track.
    """
    query = """
        SELECT
            tt.track_id,
            ARRAY_AGG(t.tag_name) AS tags
        FROM track_tag tt
        JOIN tag t ON t.tag_id = tt.tag_id
        GROUP BY tt.track_id;
    """
    return _read_sql(conn, query)


def load_playlist_interactions(conn: connection) -> pd.DataFrame:
    """
    Load playlist-based user–track interactions, if any.
    Returns columns: playlist_id, track_id.
    """
    query = """
        SELECT playlist_id, track_id
        FROM playlist_track;
    """
    return _read_sql(conn, query)


def load_all(conn: connection) -> Dict[str, pd.DataFrame]:
    """
    Convenience loader for all relevant tables.
    """
    return {
        "tracks": load_tracks(conn),
        "audio": load_audio_features(conn),
        "rank": load_rank_labels(conn),
        "genres": load_genres(conn),
        "tags": load_tags(conn),
        "playlist": load_playlist_interactions(conn),
    }
