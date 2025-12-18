"""
Recommendeur simple basé sur les préférences utilisateurs.
Entrées depuis la base (scripts T2_BDD).
Usage :
    python T3_Recommandation/src/user_based/user_based.py <account_id> [limit]
"""

import os
import sys
import psycopg2
from typing import List, Tuple, Optional


def load_env_file() -> None:
    """Charge les variables d'environnement depuis le .env à la racine du projet."""
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../user_based
    src_dir = os.path.dirname(current_dir)  # .../src
    t3_dir = os.path.dirname(src_dir)  # .../T3_Recommandation
    project_root = os.path.dirname(t3_dir)  # .../SAE5-C-IDFou
    env_path = os.path.join(project_root, ".env")

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip("'").strip('"')


def get_db_connection():
    """Connexion PostgreSQL via variables d'env (avec valeurs par défaut)."""
    DB_HOST = os.getenv("PGDB_HOST", "localhost")
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
            password=DB_PASSWORD,
        )
    except Exception as e:
        print(f"Erreur de connexion à la base : {e}")
        return None


def fetch_target_profile(conn, account_id: str) -> Optional[dict]:
    """Récupère profil (démographie) + genres préférés de l'utilisateur."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT age_range, gender
            FROM preference
            WHERE account_id = %s
            """,
            (account_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        age_range, gender = row

        cur.execute(
            """
            SELECT g.genre_id, g.title
            FROM genre_preference gp
            JOIN genre g ON g.genre_id = gp.genre_id
            WHERE gp.account_id = %s
            """,
            (account_id,),
        )
        genres = cur.fetchall() or []
        return {
            "age_range": age_range,
            "gender": gender,
            "genres": genres,  # (genre_id, title)
        }


def recommend_for_user(account_id: str, limit: int = 10) -> List[Tuple[str, str, int]]:
    """
    Reco basée sur :
    - utilisateurs similaires (score sur préférences)
    - recos filtrées par genres si existants
    Exclut les titres déjà écoutés.
    """
    load_env_file()
    conn = get_db_connection()
    if not conn:
        return []

    try:
        profile = fetch_target_profile(conn, account_id)
        if not profile:
            print(f"Aucun profil trouvé pour account_id={account_id}")
            return []

        has_genres = bool(profile["genres"])
        genre_ids = [g[0] for g in profile["genres"]]

        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS tmp_similar_users")
            cur.execute(
                """
                CREATE TEMP TABLE tmp_similar_users AS
                WITH target AS (
                    SELECT
                        age_range,
                        gender,
                        frequency,
                        context,
                        when_listening,
                        duration_pref,
                        energy_pref,
                        tempo_pref,
                        feeling_pref,
                        is_live_pref,
                        quality_pref,
                        curiosity_pref,
                        platform,
                        how,
                        utility
                    FROM preference
                    WHERE account_id = %s
                )
                SELECT
                    p.account_id,
                    (
                        (CASE WHEN p.age_range IS NOT NULL AND p.age_range = t.age_range THEN 3 ELSE 0 END) +
                        (CASE WHEN p.gender IS NOT NULL AND p.gender = t.gender THEN 2 ELSE 0 END) +
                        (CASE WHEN p.platform IS NOT NULL AND p.platform = t.platform THEN 2 ELSE 0 END) +
                        (CASE WHEN p.how IS NOT NULL AND p.how = t.how THEN 2 ELSE 0 END) +
                        (CASE WHEN p.context IS NOT NULL AND p.context = t.context THEN 1 ELSE 0 END) +
                        (CASE WHEN p.frequency IS NOT NULL AND p.frequency = t.frequency THEN 1 ELSE 0 END) +
                        (CASE WHEN p.when_listening IS NOT NULL AND p.when_listening = t.when_listening THEN 1 ELSE 0 END) +
                        (CASE WHEN p.feeling_pref IS NOT NULL AND p.feeling_pref = t.feeling_pref THEN 1 ELSE 0 END) +
                        (CASE WHEN p.energy_pref IS NOT NULL AND p.energy_pref = t.energy_pref THEN 1 ELSE 0 END) +
                        (CASE WHEN p.is_live_pref IS NOT NULL AND p.is_live_pref = t.is_live_pref THEN 1 ELSE 0 END) +
                        (CASE WHEN p.utility IS NOT NULL AND p.utility = t.utility THEN 1 ELSE 0 END) +
                        (CASE WHEN p.duration_pref IS NOT NULL AND t.duration_pref IS NOT NULL AND ABS(p.duration_pref - t.duration_pref) <= 5 THEN 1 ELSE 0 END) +
                        (CASE WHEN p.quality_pref IS NOT NULL AND t.quality_pref IS NOT NULL AND ABS(p.quality_pref - t.quality_pref) <= 2 THEN 1 ELSE 0 END) +
                        (CASE WHEN p.curiosity_pref IS NOT NULL AND t.curiosity_pref IS NOT NULL AND ABS(p.curiosity_pref - t.curiosity_pref) <= 2 THEN 1 ELSE 0 END) +
                        (CASE WHEN p.tempo_pref IS NOT NULL AND t.tempo_pref IS NOT NULL AND ABS(p.tempo_pref - t.tempo_pref) <= 10 THEN 1 ELSE 0 END)
                    ) AS score
                FROM preference p
                CROSS JOIN target t
                WHERE p.account_id <> %s;
                """,
                (account_id, account_id),
            )

            genre_filter = ""
            params: Tuple
            if has_genres:
                genre_filter = "AND tg.genre_id = ANY(%s::uuid[])"
                params = (account_id, genre_ids, limit)
            else:
                params = (account_id, limit)

            cur.execute(
                f"""
                SELECT
                    tr.track_id,
                    tr.track_title,
                    SUM(l.count * GREATEST(sim.score, 1)) AS total_score
                FROM track_user_listen l
                JOIN tmp_similar_users sim ON sim.account_id = l.account_id
                JOIN track tr ON tr.track_id = l.track_id
                LEFT JOIN track_genre tg ON tg.track_id = tr.track_id
                WHERE tr.track_id NOT IN (
                    SELECT track_id FROM track_user_listen WHERE account_id = %s
                )
                {genre_filter}
                GROUP BY tr.track_id, tr.track_title
                HAVING SUM(l.count * GREATEST(sim.score, 1)) > 0
                ORDER BY total_score DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()

            if not rows:
                print("Pas de recos via utilisateurs similaires, fallback popularité globale.")
                genre_filter_global = ""
                params_global: Tuple = ()
                if has_genres:
                    genre_filter_global = "WHERE tg.genre_id = ANY(%s::uuid[])"
                    params_global = (genre_ids,)

                cur.execute(
                    f"""
                    SELECT
                        tr.track_id,
                        tr.track_title,
                        SUM(l.count) AS total_listens
                    FROM track_user_listen l
                    JOIN track tr ON tr.track_id = l.track_id
                    LEFT JOIN track_genre tg ON tg.track_id = tr.track_id
                    {genre_filter_global}
                    GROUP BY tr.track_id, tr.track_title
                    ORDER BY total_listens DESC
                    LIMIT %s
                    """,
                    params_global + (limit,),
                )
                rows = cur.fetchall()

            if not rows:
                if has_genres:
                    cur.execute(
                        """
                        WITH pref_counts AS (
                            SELECT genre_id, count(*) AS genre_pref_count
                            FROM genre_preference
                            GROUP BY genre_id
                        ),
                        candidate AS (
                            SELECT tr.track_id, tr.track_title, COALESCE(pc.genre_pref_count, 0) AS score
                            FROM track tr
                            JOIN track_genre tg ON tg.track_id = tr.track_id
                            LEFT JOIN pref_counts pc ON pc.genre_id = tg.genre_id
                            WHERE tg.genre_id = ANY(%s::uuid[])
                        )
                        SELECT track_id, track_title, MAX(score) AS score
                        FROM candidate
                        GROUP BY track_id, track_title
                        ORDER BY score DESC, random()
                        LIMIT %s
                        """,
                        (genre_ids, limit),
                    )
                else:
                    cur.execute(
                        """
                        WITH pref_counts AS (
                            SELECT genre_id, count(*) AS genre_pref_count
                            FROM genre_preference
                            GROUP BY genre_id
                        ),
                        candidate AS (
                            SELECT tr.track_id, tr.track_title, COALESCE(pc.genre_pref_count, 0) AS score
                            FROM track tr
                            LEFT JOIN track_genre tg ON tg.track_id = tr.track_id
                            LEFT JOIN pref_counts pc ON pc.genre_id = tg.genre_id
                        )
                        SELECT track_id, track_title, MAX(score) AS score
                        FROM candidate
                        GROUP BY track_id, track_title
                        ORDER BY score DESC, random()
                        LIMIT %s
                        """,
                        (limit,),
                    )
                rows = cur.fetchall()

            return [(r[0], r[1], int(r[2])) for r in rows]
    finally:
        conn.close()


def _format_recs(rows: List[Tuple[str, str, int]]) -> str:
    if not rows:
        return "Aucune recommandation trouvée."
    lines = []
    for idx, (tid, title, score) in enumerate(rows, 1):
        lines.append(f"{idx:02d}. {title} (track_id={tid}, score={score})")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python T3_Recommandation/src/user_based/user_based.py <account_id> [limit]")
        sys.exit(1)

    account_id = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    recs = recommend_for_user(account_id, limit=limit)
    print(_format_recs(recs))
