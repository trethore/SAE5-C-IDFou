-- ====================================================================================
-- ALBUM
-- ====================================================================================
CREATE TEMP TABLE stg_album (
    album_id TEXT,
    album_comments INT,
    album_date_released DATE,
    album_favorites INT,
    album_listens INT,
    album_producer TEXT,
    album_title TEXT,
    album_tracks INT,
    album_type TEXT,
    tags TEXT
);

\copy stg_album FROM 'T1_analyse_de_donnees/cleaned_data/clean_raw_albums.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

ALTER TABLE stg_album ADD COLUMN new_uuid UUID DEFAULT uuid_generate_v4();

INSERT INTO album (
    album_id, album_title, album_type, album_tracks_count, album_date_released, 
    album_listens, album_favorites, album_comments, album_producer
)
SELECT 
    new_uuid, album_title, album_type, album_tracks, album_date_released,
    album_listens, album_favorites, album_comments, album_producer
FROM stg_album;

INSERT INTO _legacy_id_map (table_name, old_id, new_uuid)
SELECT 'album', album_id, new_uuid FROM stg_album;
