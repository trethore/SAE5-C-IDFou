-- ====================================================================================
-- TRACK
-- ====================================================================================
CREATE TEMP TABLE stg_track (
    track_id TEXT,
    album_id TEXT,
    artist_id TEXT,
    track_comments INT,
    track_composer TEXT,
    track_date_created DATE,
    track_duration INT,
    track_favorites INT,
    track_genre_top TEXT,
    track_genres TEXT,
    track_interest DOUBLE PRECISION,
    track_listens INT,
    track_lyricist TEXT,
    track_publisher TEXT,
    track_tags TEXT,
    track_title TEXT
);

\copy stg_track FROM 'T1_analyse_de_donnees/cleaned_data/clean_tracks.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

ALTER TABLE stg_track ADD COLUMN new_uuid UUID DEFAULT uuid_generate_v4();

INSERT INTO track (
    track_id, album_id, track_title, track_duration, track_listens, 
    track_favorites, track_interest, track_comments, track_date_created, 
    track_composer, track_lyricist, track_publisher
)
SELECT 
    t.new_uuid, 
    m_alb.new_uuid, 
    t.track_title, 
    t.track_duration, 
    t.track_listens, 
    t.track_favorites, 
    t.track_interest, 
    t.track_comments, 
    t.track_date_created, 
    t.track_composer, 
    t.track_lyricist, 
    t.track_publisher
FROM stg_track t
LEFT JOIN _legacy_id_map m_alb ON m_alb.old_id = t.album_id AND m_alb.table_name = 'album'
JOIN _legacy_id_map m_art ON m_art.old_id = t.artist_id AND m_art.table_name = 'artist';

INSERT INTO _legacy_id_map (table_name, old_id, new_uuid)
SELECT 'track', t.track_id, t.new_uuid 
FROM stg_track t
JOIN _legacy_id_map m_art ON m_art.old_id = t.artist_id AND m_art.table_name = 'artist';

-- Link Track -> Artist (Main)
INSERT INTO track_artist_main (track_id, artist_id)
SELECT 
    t.new_uuid, 
    m_art.new_uuid
FROM stg_track t
JOIN _legacy_id_map m_art ON m_art.old_id = t.artist_id AND m_art.table_name = 'artist';

-- Link Album -> Artist (Derived from Tracks)
INSERT INTO album_artist (album_id, artist_id)
SELECT DISTINCT 
    m_alb.new_uuid, 
    m_art.new_uuid
FROM stg_track t
JOIN _legacy_id_map m_alb ON m_alb.old_id = t.album_id AND m_alb.table_name = 'album'
JOIN _legacy_id_map m_art ON m_art.old_id = t.artist_id AND m_art.table_name = 'artist'
ON CONFLICT DO NOTHING;

-- Track -> Genres
WITH exploded AS (
    SELECT 
        new_uuid as track_uuid, 
        trim(genre_old_id) as genre_old_id
    FROM stg_track, unnest(parse_python_list(track_genres)) as genre_old_id
    WHERE track_genres IS NOT NULL AND track_genres != '[]'
),
cleaned_ids AS (
    SELECT track_uuid, genre_old_id
    FROM exploded
)
INSERT INTO track_genre (track_id, genre_id)
SELECT 
    c.track_uuid, 
    m.new_uuid
FROM cleaned_ids c
JOIN _legacy_id_map m ON m.old_id = c.genre_old_id AND m.table_name = 'genre' JOIN track t ON t.track_id = c.track_uuid
ON CONFLICT DO NOTHING;
