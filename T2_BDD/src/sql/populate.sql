
SET synchronous_commit = off;
-- ====================================================================================
-- POPULATE SCRIPT
-- ====================================================================================

-- 1. Helper Functions
CREATE OR REPLACE FUNCTION parse_python_list(p_text TEXT) RETURNS TEXT[] AS $$
DECLARE
    clean_text TEXT;
BEGIN
    IF p_text IS NULL OR p_text = '' OR p_text = '[]' THEN
        RETURN ARRAY[]::TEXT[];
    END IF;
    
    clean_text := p_text;
    
    -- Handle double-escaped quotes often found in CSV dumps of python lists: ["\"val\""]
    IF position('""' IN clean_text) > 0 THEN
        clean_text := replace(clean_text, '""', '"');
    END IF;

    -- Replace Python-style single quotes with double quotes for JSON parsing
    -- Only if it starts with [ and '
    IF left(clean_text, 2) = '[''' THEN
         clean_text := replace(clean_text, '''', '"');
    END IF;
    
    -- Fallback for simple ' -> " replacement if not covered above but still looks like list
    IF left(clean_text, 1) = '[' AND position('''' IN clean_text) > 0 AND position('"' IN clean_text) = 0 THEN
         clean_text := replace(clean_text, '''', '"');
    END IF;

    -- If it looks like JSON now, try to parse
    BEGIN
        RETURN ARRAY(SELECT jsonb_array_elements_text(clean_text::jsonb));
    EXCEPTION WHEN OTHERS THEN
        -- Fallback: basic string splitting if JSON fails. 
        -- Removes brackets and quotes for simple CSV-like parsing
        RETURN string_to_array(replace(replace(replace(trim(both '[]' from p_text), '''', ''), '"', ''), ', ', ','), ',');
    END;
END;
$$ LANGUAGE plpgsql;

-- 2. Mapping Table for Legacy IDs
CREATE TEMP TABLE _legacy_id_map (
    table_name TEXT,
    old_id TEXT,
    new_uuid UUID
);
CREATE INDEX idx_legacy_map ON _legacy_id_map(table_name, old_id);

-- ====================================================================================
-- GENRE
-- ====================================================================================
CREATE TEMP TABLE stg_genre (
    genre_id TEXT,
    tracks_count INT,
    parent_id TEXT,
    title TEXT,
    top_level INT
);

\copy stg_genre FROM 'T1_analyse_de_donnees/cleaned_data/clean_genres.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Insert and Map
WITH inserted AS (
    INSERT INTO genre (title, top_level)
    SELECT title, top_level FROM stg_genre
    RETURNING genre_id, title
)
INSERT INTO _legacy_id_map (table_name, old_id, new_uuid)
SELECT 'genre', s.genre_id, i.genre_id
FROM stg_genre s
JOIN inserted i ON i.title = s.title; -- assuming title uniqueness for mapping or row order? 
-- Title might not be unique. Better approach: Use a DO block or function if title not unique. 
-- But strictly, we can't link back easily without a temporary key.
-- Since we are in a transaction, we can add a temp column to 'genre' or rely on order? No rely on order is risky.
-- Alternative: Generate UUIDs in staging first.

TRUNCATE TABLE _legacy_id_map; -- Start over with better approach

ALTER TABLE stg_genre ADD COLUMN new_uuid UUID DEFAULT uuid_generate_v4();

INSERT INTO genre (genre_id, title, top_level)
SELECT new_uuid, title, top_level FROM stg_genre;

INSERT INTO _legacy_id_map (table_name, old_id, new_uuid)
SELECT 'genre', genre_id, new_uuid FROM stg_genre;

-- Update Parent IDs
UPDATE genre g
SET parent_id = m_parent.new_uuid
FROM stg_genre s
JOIN _legacy_id_map m_self ON m_self.old_id = s.genre_id AND m_self.table_name = 'genre'
JOIN _legacy_id_map m_parent ON m_parent.old_id = s.parent_id AND m_parent.table_name = 'genre'
WHERE g.genre_id = m_self.new_uuid AND s.parent_id != '0' AND s.parent_id IS NOT NULL;


-- ====================================================================================
-- ARTIST
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

-- Create Accounts for Artists
INSERT INTO account (account_id, login, name, email, created_at)
SELECT 
    new_uuid, 
    'artist_' || artist_id, 
    artist_name, 
    'artist_' || artist_id || '@example.com', 
    NOW()
FROM stg_artist;

-- Insert Artists
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

-- Link Track -> Genres (List parsing)
-- track_genres is like '[21, 3]'
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


-- ====================================================================================
-- TAGS (from Artists and Tracks)
-- ====================================================================================
CREATE TEMP TABLE stg_tags (
    tag_name TEXT
);

-- Extract from Artists
INSERT INTO stg_tags (tag_name)
SELECT DISTINCT trim(elem)
FROM stg_artist, unnest(parse_python_list(tags)) as elem;

-- Extract from Tracks
INSERT INTO stg_tags (tag_name)
SELECT DISTINCT trim(elem)
FROM stg_track, unnest(parse_python_list(track_tags)) as elem;

-- Insert Tags
INSERT INTO tag (tag_name)
SELECT DISTINCT tag_name FROM stg_tags WHERE tag_name IS NOT NULL AND tag_name != ''
ON CONFLICT DO NOTHING;

-- Link Artist Tags
INSERT INTO artist_tag (artist_id, tag_id)
SELECT DISTINCT a.new_uuid, tg.tag_id
FROM stg_artist a, unnest(parse_python_list(a.tags)) as tname
JOIN tag tg ON tg.tag_name = trim(tname)
ON CONFLICT DO NOTHING;

-- Link Track Tags
INSERT INTO track_tag (track_id, tag_id)
SELECT DISTINCT t.new_uuid, tg.tag_id
FROM stg_track t
CROSS JOIN LATERAL unnest(parse_python_list(t.track_tags)) as tname
JOIN tag tg ON tg.tag_name = trim(tname) 
JOIN track tr ON tr.track_id = t.new_uuid
ON CONFLICT DO NOTHING;


-- ====================================================================================
-- AUDIO FEATURES & RANKS (clean_echonest.csv)
-- ====================================================================================
CREATE TEMP TABLE stg_echonest (
    track_id TEXT,
    acousticness DOUBLE PRECISION,
    danceability DOUBLE PRECISION,
    energy DOUBLE PRECISION,
    instrumentalness DOUBLE PRECISION,
    liveness DOUBLE PRECISION,
    speechiness DOUBLE PRECISION,
    tempo DOUBLE PRECISION,
    valence DOUBLE PRECISION,
    artist_discovery_rank DOUBLE PRECISION,
    artist_familiarity_rank DOUBLE PRECISION,
    artist_hotttnesss_rank DOUBLE PRECISION,
    song_currency_rank DOUBLE PRECISION,
    song_hotttnesss_rank DOUBLE PRECISION,
    artist_discovery DOUBLE PRECISION,
    artist_familiarity DOUBLE PRECISION,
    artist_hotttnesss DOUBLE PRECISION,
    song_currency DOUBLE PRECISION,
    song_hotttnesss DOUBLE PRECISION
);

\copy stg_echonest FROM 'T1_analyse_de_donnees/cleaned_data/clean_echonest.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Insert Audio Features
INSERT INTO audio_feature (
    track_id, acousticness, danceability, energy, instrumentalness, 
    liveness, speechiness, tempo, valence
)
SELECT 
    m.new_uuid, s.acousticness, s.danceability, s.energy, s.instrumentalness,
    s.liveness, s.speechiness, s.tempo, s.valence
FROM stg_echonest s
JOIN _legacy_id_map m ON m.old_id = s.track_id AND m.table_name = 'track'
ON CONFLICT (track_id) DO UPDATE SET 
    acousticness = EXCLUDED.acousticness,
    danceability = EXCLUDED.danceability,
    energy = EXCLUDED.energy;

-- Update Ranks (using the ranks logic)
-- rank_track
INSERT INTO rank_track (track_id, rank_song_currency, rank_song_hotttnesss)
SELECT 
    m.new_uuid, 
    CAST(s.song_currency_rank AS BIGINT), 
    CAST(s.song_hotttnesss_rank AS BIGINT)
FROM stg_echonest s
JOIN _legacy_id_map m ON m.old_id = s.track_id AND m.table_name = 'track'
ON CONFLICT DO NOTHING; -- or update if exists, logic allows multiple dates now

-- rank_artist (derived from echonest, associated with track's artist)
-- Need to find artist for the track
INSERT INTO rank_artist (artist_id, rank_artist_discovery, rank_artist_familiarity, rank_artist_hotttnesss)
SELECT DISTINCT
    ta.artist_id,
    CAST(s.artist_discovery_rank AS BIGINT),
    CAST(s.artist_familiarity_rank AS BIGINT),
    CAST(s.artist_hotttnesss_rank AS BIGINT)
FROM stg_echonest s
JOIN _legacy_id_map m ON m.old_id = s.track_id AND m.table_name = 'track'
JOIN track_artist_main ta ON ta.track_id = m.new_uuid
WHERE s.artist_discovery_rank IS NOT NULL
ON CONFLICT DO NOTHING;


-- ====================================================================================
-- TEMPORAL FEATURES (clean_features.csv)
-- ====================================================================================
CREATE TEMP TABLE stg_features (
    track_id TEXT,
    chroma_cens_kurtosis DOUBLE PRECISION,
    "chroma_cens_kurtosis.1" DOUBLE PRECISION,
    "chroma_cens_kurtosis.2" DOUBLE PRECISION,
    "chroma_cens_kurtosis.3" DOUBLE PRECISION,
    "chroma_cens_kurtosis.4" DOUBLE PRECISION,
    "chroma_cens_kurtosis.5" DOUBLE PRECISION,
    "chroma_cens_kurtosis.6" DOUBLE PRECISION,
    "chroma_cens_kurtosis.7" DOUBLE PRECISION,
    "chroma_cens_kurtosis.8" DOUBLE PRECISION,
    "chroma_cens_kurtosis.9" DOUBLE PRECISION,
    "chroma_cens_kurtosis.10" DOUBLE PRECISION,
    "chroma_cens_kurtosis.11" DOUBLE PRECISION,
    chroma_cens_max DOUBLE PRECISION,
    "chroma_cens_max.1" DOUBLE PRECISION,
    "chroma_cens_max.2" DOUBLE PRECISION,
    "chroma_cens_max.3" DOUBLE PRECISION,
    "chroma_cens_max.4" DOUBLE PRECISION,
    "chroma_cens_max.5" DOUBLE PRECISION,
    "chroma_cens_max.6" DOUBLE PRECISION,
    "chroma_cens_max.7" DOUBLE PRECISION,
    "chroma_cens_max.8" DOUBLE PRECISION,
    "chroma_cens_max.9" DOUBLE PRECISION,
    "chroma_cens_max.10" DOUBLE PRECISION,
    "chroma_cens_max.11" DOUBLE PRECISION,
    chroma_cens_mean DOUBLE PRECISION,
    "chroma_cens_mean.1" DOUBLE PRECISION,
    "chroma_cens_mean.2" DOUBLE PRECISION,
    "chroma_cens_mean.3" DOUBLE PRECISION,
    "chroma_cens_mean.4" DOUBLE PRECISION,
    "chroma_cens_mean.5" DOUBLE PRECISION,
    "chroma_cens_mean.6" DOUBLE PRECISION,
    "chroma_cens_mean.7" DOUBLE PRECISION,
    "chroma_cens_mean.8" DOUBLE PRECISION,
    "chroma_cens_mean.9" DOUBLE PRECISION,
    "chroma_cens_mean.10" DOUBLE PRECISION,
    "chroma_cens_mean.11" DOUBLE PRECISION,
    chroma_cens_median DOUBLE PRECISION,
    "chroma_cens_median.1" DOUBLE PRECISION,
    "chroma_cens_median.2" DOUBLE PRECISION,
    "chroma_cens_median.3" DOUBLE PRECISION,
    "chroma_cens_median.4" DOUBLE PRECISION,
    "chroma_cens_median.5" DOUBLE PRECISION,
    "chroma_cens_median.6" DOUBLE PRECISION,
    "chroma_cens_median.7" DOUBLE PRECISION,
    "chroma_cens_median.8" DOUBLE PRECISION,
    "chroma_cens_median.9" DOUBLE PRECISION,
    "chroma_cens_median.10" DOUBLE PRECISION,
    "chroma_cens_median.11" DOUBLE PRECISION,
    chroma_cens_min DOUBLE PRECISION,
    "chroma_cens_min.1" DOUBLE PRECISION,
    "chroma_cens_min.2" DOUBLE PRECISION,
    "chroma_cens_min.3" DOUBLE PRECISION,
    "chroma_cens_min.4" DOUBLE PRECISION,
    "chroma_cens_min.5" DOUBLE PRECISION,
    "chroma_cens_min.6" DOUBLE PRECISION,
    "chroma_cens_min.7" DOUBLE PRECISION,
    "chroma_cens_min.8" DOUBLE PRECISION,
    "chroma_cens_min.9" DOUBLE PRECISION,
    "chroma_cens_min.10" DOUBLE PRECISION,
    "chroma_cens_min.11" DOUBLE PRECISION,
    chroma_cens_skew DOUBLE PRECISION,
    "chroma_cens_skew.1" DOUBLE PRECISION,
    "chroma_cens_skew.2" DOUBLE PRECISION,
    "chroma_cens_skew.3" DOUBLE PRECISION,
    "chroma_cens_skew.4" DOUBLE PRECISION,
    "chroma_cens_skew.5" DOUBLE PRECISION,
    "chroma_cens_skew.6" DOUBLE PRECISION,
    "chroma_cens_skew.7" DOUBLE PRECISION,
    "chroma_cens_skew.8" DOUBLE PRECISION,
    "chroma_cens_skew.9" DOUBLE PRECISION,
    "chroma_cens_skew.10" DOUBLE PRECISION,
    "chroma_cens_skew.11" DOUBLE PRECISION,
    chroma_cens_std DOUBLE PRECISION,
    "chroma_cens_std.1" DOUBLE PRECISION,
    "chroma_cens_std.2" DOUBLE PRECISION,
    "chroma_cens_std.3" DOUBLE PRECISION,
    "chroma_cens_std.4" DOUBLE PRECISION,
    "chroma_cens_std.5" DOUBLE PRECISION,
    "chroma_cens_std.6" DOUBLE PRECISION,
    "chroma_cens_std.7" DOUBLE PRECISION,
    "chroma_cens_std.8" DOUBLE PRECISION,
    "chroma_cens_std.9" DOUBLE PRECISION,
    "chroma_cens_std.10" DOUBLE PRECISION,
    "chroma_cens_std.11" DOUBLE PRECISION,
    chroma_cqt_kurtosis DOUBLE PRECISION,
    "chroma_cqt_kurtosis.1" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.2" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.3" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.4" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.5" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.6" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.7" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.8" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.9" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.10" DOUBLE PRECISION,
    "chroma_cqt_kurtosis.11" DOUBLE PRECISION,
    chroma_cqt_max DOUBLE PRECISION,
    "chroma_cqt_max.1" DOUBLE PRECISION,
    "chroma_cqt_max.2" DOUBLE PRECISION,
    "chroma_cqt_max.3" DOUBLE PRECISION,
    "chroma_cqt_max.4" DOUBLE PRECISION,
    "chroma_cqt_max.5" DOUBLE PRECISION,
    "chroma_cqt_max.6" DOUBLE PRECISION,
    "chroma_cqt_max.7" DOUBLE PRECISION,
    "chroma_cqt_max.8" DOUBLE PRECISION,
    "chroma_cqt_max.9" DOUBLE PRECISION,
    "chroma_cqt_max.10" DOUBLE PRECISION,
    "chroma_cqt_max.11" DOUBLE PRECISION,
    chroma_cqt_mean DOUBLE PRECISION,
    "chroma_cqt_mean.1" DOUBLE PRECISION,
    "chroma_cqt_mean.2" DOUBLE PRECISION,
    "chroma_cqt_mean.3" DOUBLE PRECISION,
    "chroma_cqt_mean.4" DOUBLE PRECISION,
    "chroma_cqt_mean.5" DOUBLE PRECISION,
    "chroma_cqt_mean.6" DOUBLE PRECISION,
    "chroma_cqt_mean.7" DOUBLE PRECISION,
    "chroma_cqt_mean.8" DOUBLE PRECISION,
    "chroma_cqt_mean.9" DOUBLE PRECISION,
    "chroma_cqt_mean.10" DOUBLE PRECISION,
    "chroma_cqt_mean.11" DOUBLE PRECISION,
    chroma_cqt_median DOUBLE PRECISION,
    "chroma_cqt_median.1" DOUBLE PRECISION,
    "chroma_cqt_median.2" DOUBLE PRECISION,
    "chroma_cqt_median.3" DOUBLE PRECISION,
    "chroma_cqt_median.4" DOUBLE PRECISION,
    "chroma_cqt_median.5" DOUBLE PRECISION,
    "chroma_cqt_median.6" DOUBLE PRECISION,
    "chroma_cqt_median.7" DOUBLE PRECISION,
    "chroma_cqt_median.8" DOUBLE PRECISION,
    "chroma_cqt_median.9" DOUBLE PRECISION,
    "chroma_cqt_median.10" DOUBLE PRECISION,
    "chroma_cqt_median.11" DOUBLE PRECISION,
    chroma_cqt_min DOUBLE PRECISION,
    "chroma_cqt_min.1" DOUBLE PRECISION,
    "chroma_cqt_min.2" DOUBLE PRECISION,
    "chroma_cqt_min.3" DOUBLE PRECISION,
    "chroma_cqt_min.4" DOUBLE PRECISION,
    "chroma_cqt_min.5" DOUBLE PRECISION,
    "chroma_cqt_min.6" DOUBLE PRECISION,
    "chroma_cqt_min.7" DOUBLE PRECISION,
    "chroma_cqt_min.8" DOUBLE PRECISION,
    "chroma_cqt_min.9" DOUBLE PRECISION,
    "chroma_cqt_min.10" DOUBLE PRECISION,
    "chroma_cqt_min.11" DOUBLE PRECISION,
    chroma_cqt_skew DOUBLE PRECISION,
    "chroma_cqt_skew.1" DOUBLE PRECISION,
    "chroma_cqt_skew.2" DOUBLE PRECISION,
    "chroma_cqt_skew.3" DOUBLE PRECISION,
    "chroma_cqt_skew.4" DOUBLE PRECISION,
    "chroma_cqt_skew.5" DOUBLE PRECISION,
    "chroma_cqt_skew.6" DOUBLE PRECISION,
    "chroma_cqt_skew.7" DOUBLE PRECISION,
    "chroma_cqt_skew.8" DOUBLE PRECISION,
    "chroma_cqt_skew.9" DOUBLE PRECISION,
    "chroma_cqt_skew.10" DOUBLE PRECISION,
    "chroma_cqt_skew.11" DOUBLE PRECISION,
    chroma_cqt_std DOUBLE PRECISION,
    "chroma_cqt_std.1" DOUBLE PRECISION,
    "chroma_cqt_std.2" DOUBLE PRECISION,
    "chroma_cqt_std.3" DOUBLE PRECISION,
    "chroma_cqt_std.4" DOUBLE PRECISION,
    "chroma_cqt_std.5" DOUBLE PRECISION,
    "chroma_cqt_std.6" DOUBLE PRECISION,
    "chroma_cqt_std.7" DOUBLE PRECISION,
    "chroma_cqt_std.8" DOUBLE PRECISION,
    "chroma_cqt_std.9" DOUBLE PRECISION,
    "chroma_cqt_std.10" DOUBLE PRECISION,
    "chroma_cqt_std.11" DOUBLE PRECISION,
    chroma_stft_kurtosis DOUBLE PRECISION,
    "chroma_stft_kurtosis.1" DOUBLE PRECISION,
    "chroma_stft_kurtosis.2" DOUBLE PRECISION,
    "chroma_stft_kurtosis.3" DOUBLE PRECISION,
    "chroma_stft_kurtosis.4" DOUBLE PRECISION,
    "chroma_stft_kurtosis.5" DOUBLE PRECISION,
    "chroma_stft_kurtosis.6" DOUBLE PRECISION,
    "chroma_stft_kurtosis.7" DOUBLE PRECISION,
    "chroma_stft_kurtosis.8" DOUBLE PRECISION,
    "chroma_stft_kurtosis.9" DOUBLE PRECISION,
    "chroma_stft_kurtosis.10" DOUBLE PRECISION,
    "chroma_stft_kurtosis.11" DOUBLE PRECISION,
    chroma_stft_max DOUBLE PRECISION,
    "chroma_stft_max.1" DOUBLE PRECISION,
    "chroma_stft_max.2" DOUBLE PRECISION,
    "chroma_stft_max.3" DOUBLE PRECISION,
    "chroma_stft_max.4" DOUBLE PRECISION,
    "chroma_stft_max.5" DOUBLE PRECISION,
    "chroma_stft_max.6" DOUBLE PRECISION,
    "chroma_stft_max.7" DOUBLE PRECISION,
    "chroma_stft_max.8" DOUBLE PRECISION,
    "chroma_stft_max.9" DOUBLE PRECISION,
    "chroma_stft_max.10" DOUBLE PRECISION,
    "chroma_stft_max.11" DOUBLE PRECISION,
    chroma_stft_mean DOUBLE PRECISION,
    "chroma_stft_mean.1" DOUBLE PRECISION,
    "chroma_stft_mean.2" DOUBLE PRECISION,
    "chroma_stft_mean.3" DOUBLE PRECISION,
    "chroma_stft_mean.4" DOUBLE PRECISION,
    "chroma_stft_mean.5" DOUBLE PRECISION,
    "chroma_stft_mean.6" DOUBLE PRECISION,
    "chroma_stft_mean.7" DOUBLE PRECISION,
    "chroma_stft_mean.8" DOUBLE PRECISION,
    "chroma_stft_mean.9" DOUBLE PRECISION,
    "chroma_stft_mean.10" DOUBLE PRECISION,
    "chroma_stft_mean.11" DOUBLE PRECISION,
    chroma_stft_median DOUBLE PRECISION,
    "chroma_stft_median.1" DOUBLE PRECISION,
    "chroma_stft_median.2" DOUBLE PRECISION,
    "chroma_stft_median.3" DOUBLE PRECISION,
    "chroma_stft_median.4" DOUBLE PRECISION,
    "chroma_stft_median.5" DOUBLE PRECISION,
    "chroma_stft_median.6" DOUBLE PRECISION,
    "chroma_stft_median.7" DOUBLE PRECISION,
    "chroma_stft_median.8" DOUBLE PRECISION,
    "chroma_stft_median.9" DOUBLE PRECISION,
    "chroma_stft_median.10" DOUBLE PRECISION,
    "chroma_stft_median.11" DOUBLE PRECISION,
    chroma_stft_min DOUBLE PRECISION,
    "chroma_stft_min.1" DOUBLE PRECISION,
    "chroma_stft_min.2" DOUBLE PRECISION,
    "chroma_stft_min.3" DOUBLE PRECISION,
    "chroma_stft_min.4" DOUBLE PRECISION,
    "chroma_stft_min.5" DOUBLE PRECISION,
    "chroma_stft_min.6" DOUBLE PRECISION,
    "chroma_stft_min.7" DOUBLE PRECISION,
    "chroma_stft_min.8" DOUBLE PRECISION,
    "chroma_stft_min.9" DOUBLE PRECISION,
    "chroma_stft_min.10" DOUBLE PRECISION,
    "chroma_stft_min.11" DOUBLE PRECISION,
    chroma_stft_skew DOUBLE PRECISION,
    "chroma_stft_skew.1" DOUBLE PRECISION,
    "chroma_stft_skew.2" DOUBLE PRECISION,
    "chroma_stft_skew.3" DOUBLE PRECISION,
    "chroma_stft_skew.4" DOUBLE PRECISION,
    "chroma_stft_skew.5" DOUBLE PRECISION,
    "chroma_stft_skew.6" DOUBLE PRECISION,
    "chroma_stft_skew.7" DOUBLE PRECISION,
    "chroma_stft_skew.8" DOUBLE PRECISION,
    "chroma_stft_skew.9" DOUBLE PRECISION,
    "chroma_stft_skew.10" DOUBLE PRECISION,
    "chroma_stft_skew.11" DOUBLE PRECISION,
    chroma_stft_std DOUBLE PRECISION,
    "chroma_stft_std.1" DOUBLE PRECISION,
    "chroma_stft_std.2" DOUBLE PRECISION,
    "chroma_stft_std.3" DOUBLE PRECISION,
    "chroma_stft_std.4" DOUBLE PRECISION,
    "chroma_stft_std.5" DOUBLE PRECISION,
    "chroma_stft_std.6" DOUBLE PRECISION,
    "chroma_stft_std.7" DOUBLE PRECISION,
    "chroma_stft_std.8" DOUBLE PRECISION,
    "chroma_stft_std.9" DOUBLE PRECISION,
    "chroma_stft_std.10" DOUBLE PRECISION,
    "chroma_stft_std.11" DOUBLE PRECISION,
    mfcc_kurtosis DOUBLE PRECISION,
    "mfcc_kurtosis.1" DOUBLE PRECISION,
    "mfcc_kurtosis.2" DOUBLE PRECISION,
    "mfcc_kurtosis.3" DOUBLE PRECISION,
    "mfcc_kurtosis.4" DOUBLE PRECISION,
    "mfcc_kurtosis.5" DOUBLE PRECISION,
    "mfcc_kurtosis.6" DOUBLE PRECISION,
    "mfcc_kurtosis.7" DOUBLE PRECISION,
    "mfcc_kurtosis.8" DOUBLE PRECISION,
    "mfcc_kurtosis.9" DOUBLE PRECISION,
    "mfcc_kurtosis.10" DOUBLE PRECISION,
    "mfcc_kurtosis.11" DOUBLE PRECISION,
    "mfcc_kurtosis.12" DOUBLE PRECISION,
    "mfcc_kurtosis.13" DOUBLE PRECISION,
    "mfcc_kurtosis.14" DOUBLE PRECISION,
    "mfcc_kurtosis.15" DOUBLE PRECISION,
    "mfcc_kurtosis.16" DOUBLE PRECISION,
    "mfcc_kurtosis.17" DOUBLE PRECISION,
    "mfcc_kurtosis.18" DOUBLE PRECISION,
    "mfcc_kurtosis.19" DOUBLE PRECISION,
    mfcc_max DOUBLE PRECISION,
    "mfcc_max.1" DOUBLE PRECISION,
    "mfcc_max.2" DOUBLE PRECISION,
    "mfcc_max.3" DOUBLE PRECISION,
    "mfcc_max.4" DOUBLE PRECISION,
    "mfcc_max.5" DOUBLE PRECISION,
    "mfcc_max.6" DOUBLE PRECISION,
    "mfcc_max.7" DOUBLE PRECISION,
    "mfcc_max.8" DOUBLE PRECISION,
    "mfcc_max.9" DOUBLE PRECISION,
    "mfcc_max.10" DOUBLE PRECISION,
    "mfcc_max.11" DOUBLE PRECISION,
    "mfcc_max.12" DOUBLE PRECISION,
    "mfcc_max.13" DOUBLE PRECISION,
    "mfcc_max.14" DOUBLE PRECISION,
    "mfcc_max.15" DOUBLE PRECISION,
    "mfcc_max.16" DOUBLE PRECISION,
    "mfcc_max.17" DOUBLE PRECISION,
    "mfcc_max.18" DOUBLE PRECISION,
    "mfcc_max.19" DOUBLE PRECISION,
    mfcc_mean DOUBLE PRECISION,
    "mfcc_mean.1" DOUBLE PRECISION,
    "mfcc_mean.2" DOUBLE PRECISION,
    "mfcc_mean.3" DOUBLE PRECISION,
    "mfcc_mean.4" DOUBLE PRECISION,
    "mfcc_mean.5" DOUBLE PRECISION,
    "mfcc_mean.6" DOUBLE PRECISION,
    "mfcc_mean.7" DOUBLE PRECISION,
    "mfcc_mean.8" DOUBLE PRECISION,
    "mfcc_mean.9" DOUBLE PRECISION,
    "mfcc_mean.10" DOUBLE PRECISION,
    "mfcc_mean.11" DOUBLE PRECISION,
    "mfcc_mean.12" DOUBLE PRECISION,
    "mfcc_mean.13" DOUBLE PRECISION,
    "mfcc_mean.14" DOUBLE PRECISION,
    "mfcc_mean.15" DOUBLE PRECISION,
    "mfcc_mean.16" DOUBLE PRECISION,
    "mfcc_mean.17" DOUBLE PRECISION,
    "mfcc_mean.18" DOUBLE PRECISION,
    "mfcc_mean.19" DOUBLE PRECISION,
    mfcc_median DOUBLE PRECISION,
    "mfcc_median.1" DOUBLE PRECISION,
    "mfcc_median.2" DOUBLE PRECISION,
    "mfcc_median.3" DOUBLE PRECISION,
    "mfcc_median.4" DOUBLE PRECISION,
    "mfcc_median.5" DOUBLE PRECISION,
    "mfcc_median.6" DOUBLE PRECISION,
    "mfcc_median.7" DOUBLE PRECISION,
    "mfcc_median.8" DOUBLE PRECISION,
    "mfcc_median.9" DOUBLE PRECISION,
    "mfcc_median.10" DOUBLE PRECISION,
    "mfcc_median.11" DOUBLE PRECISION,
    "mfcc_median.12" DOUBLE PRECISION,
    "mfcc_median.13" DOUBLE PRECISION,
    "mfcc_median.14" DOUBLE PRECISION,
    "mfcc_median.15" DOUBLE PRECISION,
    "mfcc_median.16" DOUBLE PRECISION,
    "mfcc_median.17" DOUBLE PRECISION,
    "mfcc_median.18" DOUBLE PRECISION,
    "mfcc_median.19" DOUBLE PRECISION,
    mfcc_min DOUBLE PRECISION,
    "mfcc_min.1" DOUBLE PRECISION,
    "mfcc_min.2" DOUBLE PRECISION,
    "mfcc_min.3" DOUBLE PRECISION,
    "mfcc_min.4" DOUBLE PRECISION,
    "mfcc_min.5" DOUBLE PRECISION,
    "mfcc_min.6" DOUBLE PRECISION,
    "mfcc_min.7" DOUBLE PRECISION,
    "mfcc_min.8" DOUBLE PRECISION,
    "mfcc_min.9" DOUBLE PRECISION,
    "mfcc_min.10" DOUBLE PRECISION,
    "mfcc_min.11" DOUBLE PRECISION,
    "mfcc_min.12" DOUBLE PRECISION,
    "mfcc_min.13" DOUBLE PRECISION,
    "mfcc_min.14" DOUBLE PRECISION,
    "mfcc_min.15" DOUBLE PRECISION,
    "mfcc_min.16" DOUBLE PRECISION,
    "mfcc_min.17" DOUBLE PRECISION,
    "mfcc_min.18" DOUBLE PRECISION,
    "mfcc_min.19" DOUBLE PRECISION,
    mfcc_skew DOUBLE PRECISION,
    "mfcc_skew.1" DOUBLE PRECISION,
    "mfcc_skew.2" DOUBLE PRECISION,
    "mfcc_skew.3" DOUBLE PRECISION,
    "mfcc_skew.4" DOUBLE PRECISION,
    "mfcc_skew.5" DOUBLE PRECISION,
    "mfcc_skew.6" DOUBLE PRECISION,
    "mfcc_skew.7" DOUBLE PRECISION,
    "mfcc_skew.8" DOUBLE PRECISION,
    "mfcc_skew.9" DOUBLE PRECISION,
    "mfcc_skew.10" DOUBLE PRECISION,
    "mfcc_skew.11" DOUBLE PRECISION,
    "mfcc_skew.12" DOUBLE PRECISION,
    "mfcc_skew.13" DOUBLE PRECISION,
    "mfcc_skew.14" DOUBLE PRECISION,
    "mfcc_skew.15" DOUBLE PRECISION,
    "mfcc_skew.16" DOUBLE PRECISION,
    "mfcc_skew.17" DOUBLE PRECISION,
    "mfcc_skew.18" DOUBLE PRECISION,
    "mfcc_skew.19" DOUBLE PRECISION,
    mfcc_std DOUBLE PRECISION,
    "mfcc_std.1" DOUBLE PRECISION,
    "mfcc_std.2" DOUBLE PRECISION,
    "mfcc_std.3" DOUBLE PRECISION,
    "mfcc_std.4" DOUBLE PRECISION,
    "mfcc_std.5" DOUBLE PRECISION,
    "mfcc_std.6" DOUBLE PRECISION,
    "mfcc_std.7" DOUBLE PRECISION,
    "mfcc_std.8" DOUBLE PRECISION,
    "mfcc_std.9" DOUBLE PRECISION,
    "mfcc_std.10" DOUBLE PRECISION,
    "mfcc_std.11" DOUBLE PRECISION,
    "mfcc_std.12" DOUBLE PRECISION,
    "mfcc_std.13" DOUBLE PRECISION,
    "mfcc_std.14" DOUBLE PRECISION,
    "mfcc_std.15" DOUBLE PRECISION,
    "mfcc_std.16" DOUBLE PRECISION,
    "mfcc_std.17" DOUBLE PRECISION,
    "mfcc_std.18" DOUBLE PRECISION,
    "mfcc_std.19" DOUBLE PRECISION,
    rmse_kurtosis DOUBLE PRECISION,
    rmse_max DOUBLE PRECISION,
    rmse_mean DOUBLE PRECISION,
    rmse_median DOUBLE PRECISION,
    rmse_min DOUBLE PRECISION,
    rmse_skew DOUBLE PRECISION,
    rmse_std DOUBLE PRECISION,
    spectral_bandwidth_kurtosis DOUBLE PRECISION,
    spectral_bandwidth_max DOUBLE PRECISION,
    spectral_bandwidth_mean DOUBLE PRECISION,
    spectral_bandwidth_median DOUBLE PRECISION,
    spectral_bandwidth_min DOUBLE PRECISION,
    spectral_bandwidth_skew DOUBLE PRECISION,
    spectral_bandwidth_std DOUBLE PRECISION,
    spectral_centroid_kurtosis DOUBLE PRECISION,
    spectral_centroid_max DOUBLE PRECISION,
    spectral_centroid_mean DOUBLE PRECISION,
    spectral_centroid_median DOUBLE PRECISION,
    spectral_centroid_min DOUBLE PRECISION,
    spectral_centroid_skew DOUBLE PRECISION,
    spectral_centroid_std DOUBLE PRECISION,
    spectral_contrast_kurtosis DOUBLE PRECISION,
    "spectral_contrast_kurtosis.1" DOUBLE PRECISION,
    "spectral_contrast_kurtosis.2" DOUBLE PRECISION,
    "spectral_contrast_kurtosis.3" DOUBLE PRECISION,
    "spectral_contrast_kurtosis.4" DOUBLE PRECISION,
    "spectral_contrast_kurtosis.5" DOUBLE PRECISION,
    "spectral_contrast_kurtosis.6" DOUBLE PRECISION,
    spectral_contrast_max DOUBLE PRECISION,
    "spectral_contrast_max.1" DOUBLE PRECISION,
    "spectral_contrast_max.2" DOUBLE PRECISION,
    "spectral_contrast_max.3" DOUBLE PRECISION,
    "spectral_contrast_max.4" DOUBLE PRECISION,
    "spectral_contrast_max.5" DOUBLE PRECISION,
    "spectral_contrast_max.6" DOUBLE PRECISION,
    spectral_contrast_mean DOUBLE PRECISION,
    "spectral_contrast_mean.1" DOUBLE PRECISION,
    "spectral_contrast_mean.2" DOUBLE PRECISION,
    "spectral_contrast_mean.3" DOUBLE PRECISION,
    "spectral_contrast_mean.4" DOUBLE PRECISION,
    "spectral_contrast_mean.5" DOUBLE PRECISION,
    "spectral_contrast_mean.6" DOUBLE PRECISION,
    spectral_contrast_median DOUBLE PRECISION,
    "spectral_contrast_median.1" DOUBLE PRECISION,
    "spectral_contrast_median.2" DOUBLE PRECISION,
    "spectral_contrast_median.3" DOUBLE PRECISION,
    "spectral_contrast_median.4" DOUBLE PRECISION,
    "spectral_contrast_median.5" DOUBLE PRECISION,
    "spectral_contrast_median.6" DOUBLE PRECISION,
    spectral_contrast_min DOUBLE PRECISION,
    "spectral_contrast_min.1" DOUBLE PRECISION,
    "spectral_contrast_min.2" DOUBLE PRECISION,
    "spectral_contrast_min.3" DOUBLE PRECISION,
    "spectral_contrast_min.4" DOUBLE PRECISION,
    "spectral_contrast_min.5" DOUBLE PRECISION,
    "spectral_contrast_min.6" DOUBLE PRECISION,
    spectral_contrast_skew DOUBLE PRECISION,
    "spectral_contrast_skew.1" DOUBLE PRECISION,
    "spectral_contrast_skew.2" DOUBLE PRECISION,
    "spectral_contrast_skew.3" DOUBLE PRECISION,
    "spectral_contrast_skew.4" DOUBLE PRECISION,
    "spectral_contrast_skew.5" DOUBLE PRECISION,
    "spectral_contrast_skew.6" DOUBLE PRECISION,
    spectral_contrast_std DOUBLE PRECISION,
    "spectral_contrast_std.1" DOUBLE PRECISION,
    "spectral_contrast_std.2" DOUBLE PRECISION,
    "spectral_contrast_std.3" DOUBLE PRECISION,
    "spectral_contrast_std.4" DOUBLE PRECISION,
    "spectral_contrast_std.5" DOUBLE PRECISION,
    "spectral_contrast_std.6" DOUBLE PRECISION,
    spectral_rolloff_kurtosis DOUBLE PRECISION,
    spectral_rolloff_max DOUBLE PRECISION,
    spectral_rolloff_mean DOUBLE PRECISION,
    spectral_rolloff_median DOUBLE PRECISION,
    spectral_rolloff_min DOUBLE PRECISION,
    spectral_rolloff_skew DOUBLE PRECISION,
    spectral_rolloff_std DOUBLE PRECISION,
    tonnetz_kurtosis DOUBLE PRECISION,
    "tonnetz_kurtosis.1" DOUBLE PRECISION,
    "tonnetz_kurtosis.2" DOUBLE PRECISION,
    "tonnetz_kurtosis.3" DOUBLE PRECISION,
    "tonnetz_kurtosis.4" DOUBLE PRECISION,
    "tonnetz_kurtosis.5" DOUBLE PRECISION,
    tonnetz_max DOUBLE PRECISION,
    "tonnetz_max.1" DOUBLE PRECISION,
    "tonnetz_max.2" DOUBLE PRECISION,
    "tonnetz_max.3" DOUBLE PRECISION,
    "tonnetz_max.4" DOUBLE PRECISION,
    "tonnetz_max.5" DOUBLE PRECISION,
    tonnetz_mean DOUBLE PRECISION,
    "tonnetz_mean.1" DOUBLE PRECISION,
    "tonnetz_mean.2" DOUBLE PRECISION,
    "tonnetz_mean.3" DOUBLE PRECISION,
    "tonnetz_mean.4" DOUBLE PRECISION,
    "tonnetz_mean.5" DOUBLE PRECISION,
    tonnetz_median DOUBLE PRECISION,
    "tonnetz_median.1" DOUBLE PRECISION,
    "tonnetz_median.2" DOUBLE PRECISION,
    "tonnetz_median.3" DOUBLE PRECISION,
    "tonnetz_median.4" DOUBLE PRECISION,
    "tonnetz_median.5" DOUBLE PRECISION,
    tonnetz_min DOUBLE PRECISION,
    "tonnetz_min.1" DOUBLE PRECISION,
    "tonnetz_min.2" DOUBLE PRECISION,
    "tonnetz_min.3" DOUBLE PRECISION,
    "tonnetz_min.4" DOUBLE PRECISION,
    "tonnetz_min.5" DOUBLE PRECISION,
    tonnetz_skew DOUBLE PRECISION,
    "tonnetz_skew.1" DOUBLE PRECISION,
    "tonnetz_skew.2" DOUBLE PRECISION,
    "tonnetz_skew.3" DOUBLE PRECISION,
    "tonnetz_skew.4" DOUBLE PRECISION,
    "tonnetz_skew.5" DOUBLE PRECISION,
    tonnetz_std DOUBLE PRECISION,
    "tonnetz_std.1" DOUBLE PRECISION,
    "tonnetz_std.2" DOUBLE PRECISION,
    "tonnetz_std.3" DOUBLE PRECISION,
    "tonnetz_std.4" DOUBLE PRECISION,
    "tonnetz_std.5" DOUBLE PRECISION,
    zcr_kurtosis DOUBLE PRECISION,
    zcr_max DOUBLE PRECISION,
    zcr_mean DOUBLE PRECISION,
    zcr_median DOUBLE PRECISION,
    zcr_min DOUBLE PRECISION,
    zcr_skew DOUBLE PRECISION,
    zcr_std DOUBLE PRECISION
);

\copy stg_features FROM 'T1_analyse_de_donnees/cleaned_data/clean_features.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');


-- Add missing destination columns dynamically (strip dots)
DO $$
DECLARE
  rec record;
BEGIN
  FOR rec IN
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'stg_features'
      AND column_name <> 'track_id'
      AND table_schema LIKE 'pg_temp%'
    ORDER BY ordinal_position
  LOOP
    EXECUTE format(
      'ALTER TABLE temporal_feature ADD COLUMN IF NOT EXISTS %I double precision',
      translate(rec.column_name, '.', '')
    );
  END LOOP;
END$$;

-- Build and execute the upsert dynamically to keep the script short
DO $$
DECLARE
  col_list text;
  sel_list text;
  upd_list text;
BEGIN
  SELECT string_agg(quote_ident(translate(column_name, '.', '')), ', ' ORDER BY ordinal_position)
    INTO col_list
    FROM information_schema.columns
    WHERE table_name = 'stg_features'
      AND column_name <> 'track_id'
      AND table_schema LIKE 'pg_temp%';

  SELECT string_agg(
           format('%s AS %s', quote_ident(column_name), quote_ident(translate(column_name, '.', ''))),
           ', ' ORDER BY ordinal_position)
    INTO sel_list
    FROM information_schema.columns
    WHERE table_name = 'stg_features'
      AND column_name <> 'track_id'
      AND table_schema LIKE 'pg_temp%';

  SELECT string_agg(
           format('%1$s = EXCLUDED.%1$s', quote_ident(translate(column_name, '.', ''))),
           ', ' ORDER BY ordinal_position)
    INTO upd_list
    FROM information_schema.columns
    WHERE table_name = 'stg_features'
      AND column_name <> 'track_id'
      AND table_schema LIKE 'pg_temp%';

  EXECUTE format(
    'INSERT INTO temporal_feature (track_id, %s) ' ||
    'SELECT m.new_uuid, %s FROM stg_features s ' ||
    'JOIN _legacy_id_map m ON m.old_id = s.track_id AND m.table_name = ''track'' ' ||
    'ON CONFLICT (track_id) DO UPDATE SET %s',
    col_list,
    sel_list,
    upd_list
  );
END$$;

DROP TABLE stg_features;


-- ====================================================================================
-- USERS (clean_answers.csv)
-- ====================================================================================
CREATE TEMP TABLE stg_user (
    created_at TIMESTAMP,
    has_consented TEXT,
    is_listening TEXT,
    frequency TEXT,
    context TEXT,
    "when" DOUBLE PRECISION,
    how TEXT,
    platform TEXT,
    utility TEXT,
    track_genre TEXT,
    duration DOUBLE PRECISION,
    energy TEXT,
    tempo DOUBLE PRECISION,
    feeling TEXT,
    is_live TEXT,
    quality DOUBLE PRECISION,
    curiosity DOUBLE PRECISION,
    age_range TEXT,
    gender TEXT,
    position TEXT,
    account_uuid UUID DEFAULT uuid_generate_v4()
);

\copy stg_user (created_at, has_consented, is_listening, frequency, context, "when", how, platform, utility, track_genre, duration, energy, tempo, feeling, is_live, quality, curiosity, age_range, gender, position) FROM 'T1_alternants/src/clean/out/clean_answers.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Insert Accounts
INSERT INTO account (account_id, login, name, email, created_at)
SELECT 
    account_uuid,
    'user_' || substr(account_uuid::text, 1, 8),
    'User ' || substr(account_uuid::text, 1, 8),
    'user_' || substr(account_uuid::text, 1, 8) || '@test.com',
    created_at
FROM stg_user;

-- Insert Users
INSERT INTO "user" (account_id, pseudo)
SELECT 
    account_uuid,
    'User_' || substr(account_uuid::text, 1, 8)
FROM stg_user;

-- Insert Preferences
INSERT INTO preference (
    account_id, age_range, gender, position, has_consented, is_listening,
    frequency, when_listening, duration_pref, energy_pref, tempo_pref,
    feeling_pref, is_live_pref, quality_pref, curiosity_pref, context,
    how, platform, utility
)
SELECT
    account_uuid, age_range, gender, position, 
    (has_consented IS NOT NULL)::boolean, 
    (is_listening = 'True')::boolean,
    frequency, "when", CAST(duration AS INT), energy, tempo,
    feeling, is_live, CAST(quality AS INT), CAST(curiosity AS INT), context,
    how, platform, utility
FROM stg_user;

-- Genre Preference
-- CSV: track_genre = "['pop', 'rap']"
WITH user_genres AS (
    SELECT 
        account_uuid,
        trim(genre_name) as genre_name
    FROM stg_user, unnest(parse_python_list(track_genre)) as genre_name
)
INSERT INTO genre_preference (account_id, genre_id)
SELECT 
    ug.account_uuid,
    g.genre_id
FROM user_genres ug
JOIN genre g ON lower(g.title) = lower(ug.genre_name)
ON CONFLICT DO NOTHING;

-- Cleanup
DROP TABLE stg_genre;
DROP TABLE stg_artist;
DROP TABLE stg_album;
DROP TABLE stg_track;
DROP TABLE stg_tags;
DROP TABLE stg_echonest;
DROP TABLE stg_user;
DROP TABLE _legacy_id_map;

-- End
