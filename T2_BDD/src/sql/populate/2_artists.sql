-- ====================================================================================
-- ARTISTE
-- ====================================================================================
CREATE TEMP TABLE stg_artist (
    artist_id TEXT,
    artist_active_year_begin INT,
    artist_active_year_end INT,
    artist_associated_labels TEXT,
    artist_bio TEXT,
    artist_comments INT,
    artist_favorites INT,
    artist_latitude DOUBLE PRECISION,
    artist_location TEXT,
    artist_longitude DOUBLE PRECISION,
    artist_members TEXT,
    artist_name TEXT,
    artist_related_projects TEXT,
    tags TEXT
);

\copy stg_artist FROM 'T1_analyse_de_donnees/cleaned_data/clean_raw_artists.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

ALTER TABLE stg_artist ADD COLUMN new_uuid UUID DEFAULT uuid_generate_v4();

-- Creer des comptes pour les artistes
INSERT INTO account (account_id, login, name, email, created_at)
SELECT 
    new_uuid, 
    'artist_' || artist_id, 
    artist_name, 
    'artist_' || artist_id || '@example.com', 
    NOW()
FROM stg_artist;

-- Inserer les artistes
INSERT INTO artist (
    artist_id, artist_bio, artist_location, artist_latitude, artist_longitude, 
    artist_active_year_begin, artist_active_year_end, artist_favorites, artist_comments
)
SELECT 
    new_uuid, artist_bio, artist_location, artist_latitude, artist_longitude,
    artist_active_year_begin, artist_active_year_end, artist_favorites, artist_comments
FROM stg_artist;

INSERT INTO _legacy_id_map (table_name, old_id, new_uuid)
SELECT 'artist', artist_id, new_uuid FROM stg_artist;
