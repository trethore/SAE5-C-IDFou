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
