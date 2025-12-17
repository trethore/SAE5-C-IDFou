import os
import psycopg2

from dotenv import load_dotenv


ID: str = "6df16dd4-9a1e-497d-a999-e9049d3bc1f0"
MAX: int = 5

GET_CLOSEST_USERS_QUERY: str = """
SELECT 
    account_id, 
    -- Calcule la distance (plus c'est proche de 0, plus c'est similaire)
    embedding <=> (SELECT embedding FROM preference_vector WHERE account_id = %s) AS distance
FROM preference_vector
WHERE account_id != %s -- On ne veut pas se recommander soi-même
ORDER BY distance ASC
LIMIT %s;
"""

GET_LISTENED_TRACKS_QUERY: str = """
SELECT track.track_id, track.track_title
FROM track
INNER JOIN track_user_listen
    ON track.track_id = track_user_listen.track_id
WHERE track_user_listen.account_id = %s;
"""


def main() -> None:
    load_dotenv()

    connection = psycopg2.connect(
        host="localhost",
        port=os.environ["PGDB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_ROOT_PASSWORD"],
    )
    cursor = connection.cursor()

    cursor.execute(GET_CLOSEST_USERS_QUERY, (ID, ID, MAX))
    closest_users_id_and_distance = cursor.fetchall()
    
    recommended_music: list = []

    for user_id_and_dist in closest_users_id_and_distance:
        cursor.execute(GET_LISTENED_TRACKS_QUERY, (user_id_and_dist[0],))
        listened_tracks = cursor.fetchall()
        recommended_music += listened_tracks
    
    print(recommended_music)


if __name__ == "__main__":
    main()
