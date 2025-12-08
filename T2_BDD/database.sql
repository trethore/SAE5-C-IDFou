-- ====================================================================================
-- SCHEMA + VUES + FONCTIONS/TRIGGERS
-- ====================================================================================

-- extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------
-- DROP
-- ------------------------------------------------
DROP TABLE IF EXISTS account, artist, album, genre, track, audio_feature, temporal_feature, tag, playlist, rank_track, rank_artist, license, track_genre, track_tag, artist_tag, album_artist, track_artist_main, track_artist_feat, track_license, playlist_track, "user", preference, playlist_user, track_user_like, track_user_listen, track_comment CASCADE;

-- ====================================================================================
-- TABLES
-- ====================================================================================

CREATE TABLE account (
    account_id UUID DEFAULT uuid_generate_v4(),
    login VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP,
    PRIMARY KEY (account_id)
);

CREATE TABLE artist (
    artist_id UUID DEFAULT uuid_generate_v4(),
    artist_bio TEXT,
    artist_location TEXT,
    artist_latitude DOUBLE PRECISION,
    artist_longitude DOUBLE PRECISION,
    artist_active_year_begin INTEGER,
    artist_active_year_end INTEGER,
    artist_favorites BIGINT,
    artist_comments BIGINT,
    PRIMARY KEY (artist_id),
    FOREIGN KEY (artist_id) REFERENCES account(account_id)
);

CREATE TABLE album (
    album_id UUID DEFAULT uuid_generate_v4(),
    album_title TEXT,
    album_type VARCHAR(255),
    album_tracks_count INTEGER,
    album_date_released DATE,
    album_listens BIGINT,
    album_favorites BIGINT,
    album_comments BIGINT,
    album_producer VARCHAR(255),
    PRIMARY KEY (album_id)
);

CREATE TABLE genre (
    genre_id UUID DEFAULT uuid_generate_v4(),
    parent_id UUID,
    title VARCHAR(255),
    top_level INTEGER,
    PRIMARY KEY (genre_id),
    FOREIGN KEY (parent_id) REFERENCES genre(genre_id)
);

CREATE TABLE track (
    track_id UUID DEFAULT uuid_generate_v4(),
    album_id UUID,
    track_title VARCHAR(255),
    track_duration BIGINT,
    track_number INTEGER,
    track_disc_number INTEGER,
    track_explicit BOOLEAN,
    track_instrumental BOOLEAN,
    track_listens BIGINT,
    track_favorites BIGINT,
    track_interest DOUBLE PRECISION,
    track_comments BIGINT,
    track_date_created DATE,
    track_composer VARCHAR(255),
    track_lyricist VARCHAR(255),
    track_publisher VARCHAR(255),
    PRIMARY KEY (track_id),
    FOREIGN KEY (album_id) REFERENCES album(album_id)
);

CREATE TABLE audio_feature (
    track_id UUID,
    acousticness DOUBLE PRECISION,
    danceability DOUBLE PRECISION,
    energy DOUBLE PRECISION,
    instrumentalness DOUBLE PRECISION,
    liveness DOUBLE PRECISION,
    speechiness DOUBLE PRECISION,
    tempo DOUBLE PRECISION,
    valence DOUBLE PRECISION,
    PRIMARY KEY (track_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id)
);

CREATE TABLE temporal_feature (
    track_id UUID,
    chroma_stft_skew1 DOUBLE PRECISION,
    chroma_stft_skew2 DOUBLE PRECISION,
    chroma_stft_skew3 DOUBLE PRECISION,
    chroma_stft_skew4 DOUBLE PRECISION,
    chroma_stft_skew5 DOUBLE PRECISION,
    chroma_stft_skew6 DOUBLE PRECISION,
    chroma_stft_skew7 DOUBLE PRECISION,
    chroma_stft_skew8 DOUBLE PRECISION,
    chroma_stft_skew9 DOUBLE PRECISION,
    chroma_stft_skew10 DOUBLE PRECISION,
    chroma_stft_skew11 DOUBLE PRECISION,
    chroma_stft_std DOUBLE PRECISION,
    chroma_stft_std1 DOUBLE PRECISION,
    chroma_stft_std2 DOUBLE PRECISION,
    chroma_stft_std3 DOUBLE PRECISION,
    chroma_stft_std4 DOUBLE PRECISION,
    chroma_stft_std5 DOUBLE PRECISION,
    chroma_stft_std6 DOUBLE PRECISION,
    chroma_stft_std7 DOUBLE PRECISION,
    chroma_stft_std8 DOUBLE PRECISION,
    chroma_stft_std9 DOUBLE PRECISION,
    chroma_stft_std10 DOUBLE PRECISION,
    chroma_stft_std11 DOUBLE PRECISION,
    mfcc_kurtosis DOUBLE PRECISION,
    mfcc_kurtosis1 DOUBLE PRECISION,
    mfcc_kurtosis2 DOUBLE PRECISION,
    mfcc_kurtosis3 DOUBLE PRECISION,
    mfcc_kurtosis4 DOUBLE PRECISION,
    mfcc_kurtosis5 DOUBLE PRECISION,
    mfcc_kurtosis6 DOUBLE PRECISION,
    mfcc_kurtosis7 DOUBLE PRECISION,
    mfcc_kurtosis8 DOUBLE PRECISION,
    mfcc_kurtosis9 DOUBLE PRECISION,
    mfcc_kurtosis10 DOUBLE PRECISION,
    mfcc_kurtosis11 DOUBLE PRECISION,
    mfcc_kurtosis12 DOUBLE PRECISION,
    mfcc_kurtosis13 DOUBLE PRECISION,
    mfcc_kurtosis14 DOUBLE PRECISION,
    mfcc_kurtosis15 DOUBLE PRECISION,
    mfcc_kurtosis16 DOUBLE PRECISION,
    mfcc_kurtosis17 DOUBLE PRECISION,
    mfcc_kurtosis18 DOUBLE PRECISION,
    mfcc_kurtosis19 DOUBLE PRECISION,
    mfcc_max DOUBLE PRECISION,
    mfcc_max1 DOUBLE PRECISION,
    mfcc_max2 DOUBLE PRECISION,
    mfcc_max3 DOUBLE PRECISION,
    mfcc_max4 DOUBLE PRECISION,
    mfcc_max5 DOUBLE PRECISION,
    mfcc_max6 DOUBLE PRECISION,
    mfcc_max7 DOUBLE PRECISION,
    mfcc_max8 DOUBLE PRECISION,
    mfcc_max9 DOUBLE PRECISION,
    mfcc_max10 DOUBLE PRECISION,
    mfcc_max11 DOUBLE PRECISION,
    mfcc_max12 DOUBLE PRECISION,
    mfcc_max13 DOUBLE PRECISION,
    mfcc_max14 DOUBLE PRECISION,
    mfcc_max15 DOUBLE PRECISION,
    mfcc_max16 DOUBLE PRECISION,
    mfcc_max17 DOUBLE PRECISION,
    mfcc_max18 DOUBLE PRECISION,
    mfcc_max19 DOUBLE PRECISION,
    mfcc_mean DOUBLE PRECISION,
    mfcc_mean1 DOUBLE PRECISION,
    mfcc_mean2 DOUBLE PRECISION,
    mfcc_mean3 DOUBLE PRECISION,
    mfcc_mean4 DOUBLE PRECISION,
    mfcc_mean5 DOUBLE PRECISION,
    mfcc_mean6 DOUBLE PRECISION,
    mfcc_mean7 DOUBLE PRECISION,
    mfcc_mean8 DOUBLE PRECISION,
    mfcc_mean9 DOUBLE PRECISION,
    mfcc_mean10 DOUBLE PRECISION,
    mfcc_mean11 DOUBLE PRECISION,
    mfcc_mean12 DOUBLE PRECISION,
    mfcc_mean13 DOUBLE PRECISION,
    mfcc_mean14 DOUBLE PRECISION,
    mfcc_mean15 DOUBLE PRECISION,
    mfcc_mean16 DOUBLE PRECISION,
    mfcc_mean17 DOUBLE PRECISION,
    mfcc_mean18 DOUBLE PRECISION,
    mfcc_mean19 DOUBLE PRECISION,
    mfcc_median DOUBLE PRECISION,
    mfcc_median1 DOUBLE PRECISION,
    mfcc_median2 DOUBLE PRECISION,
    mfcc_median3 DOUBLE PRECISION,
    mfcc_median4 DOUBLE PRECISION,
    mfcc_median5 DOUBLE PRECISION,
    mfcc_median6 DOUBLE PRECISION,
    mfcc_median7 DOUBLE PRECISION,
    mfcc_median8 DOUBLE PRECISION,
    mfcc_median9 DOUBLE PRECISION,
    mfcc_median10 DOUBLE PRECISION,
    mfcc_median11 DOUBLE PRECISION,
    mfcc_median12 DOUBLE PRECISION,
    mfcc_median13 DOUBLE PRECISION,
    mfcc_median14 DOUBLE PRECISION,
    mfcc_median15 DOUBLE PRECISION,
    mfcc_median16 DOUBLE PRECISION,
    mfcc_median17 DOUBLE PRECISION,
    mfcc_median18 DOUBLE PRECISION,
    mfcc_median19 DOUBLE PRECISION,
    mfcc_min DOUBLE PRECISION,
    mfcc_min1 DOUBLE PRECISION,
    mfcc_min2 DOUBLE PRECISION,
    mfcc_min3 DOUBLE PRECISION,
    mfcc_min4 DOUBLE PRECISION,
    mfcc_min5 DOUBLE PRECISION,
    mfcc_min6 DOUBLE PRECISION,
    mfcc_min7 DOUBLE PRECISION,
    mfcc_min8 DOUBLE PRECISION,
    mfcc_min9 DOUBLE PRECISION,
    mfcc_min10 DOUBLE PRECISION,
    mfcc_min11 DOUBLE PRECISION,
    mfcc_min12 DOUBLE PRECISION,
    mfcc_min13 DOUBLE PRECISION,
    mfcc_min14 DOUBLE PRECISION,
    mfcc_min15 DOUBLE PRECISION,
    mfcc_min16 DOUBLE PRECISION,
    mfcc_min17 DOUBLE PRECISION,
    mfcc_min18 DOUBLE PRECISION,
    mfcc_min19 DOUBLE PRECISION,
    mfcc_skew DOUBLE PRECISION,
    mfcc_skew1 DOUBLE PRECISION,
    mfcc_skew2 DOUBLE PRECISION,
    mfcc_skew3 DOUBLE PRECISION,
    mfcc_skew4 DOUBLE PRECISION,
    mfcc_skew5 DOUBLE PRECISION,
    mfcc_skew6 DOUBLE PRECISION,
    mfcc_skew7 DOUBLE PRECISION,
    mfcc_skew8 DOUBLE PRECISION,
    mfcc_skew9 DOUBLE PRECISION,
    mfcc_skew10 DOUBLE PRECISION,
    mfcc_skew11 DOUBLE PRECISION,
    mfcc_skew12 DOUBLE PRECISION,
    mfcc_skew13 DOUBLE PRECISION,
    mfcc_skew14 DOUBLE PRECISION,
    mfcc_skew15 DOUBLE PRECISION,
    mfcc_skew16 DOUBLE PRECISION,
    mfcc_skew17 DOUBLE PRECISION,
    mfcc_skew18 DOUBLE PRECISION,
    mfcc_skew19 DOUBLE PRECISION,
    mfcc_std DOUBLE PRECISION,
    mfcc_std1 DOUBLE PRECISION,
    mfcc_std2 DOUBLE PRECISION,
    mfcc_std3 DOUBLE PRECISION,
    mfcc_std4 DOUBLE PRECISION,
    mfcc_std5 DOUBLE PRECISION,
    mfcc_std6 DOUBLE PRECISION,
    mfcc_std7 DOUBLE PRECISION,
    mfcc_std8 DOUBLE PRECISION,
    mfcc_std9 DOUBLE PRECISION,
    mfcc_std10 DOUBLE PRECISION,
    mfcc_std11 DOUBLE PRECISION,
    mfcc_std12 DOUBLE PRECISION,
    mfcc_std13 DOUBLE PRECISION,
    mfcc_std14 DOUBLE PRECISION,
    mfcc_std15 DOUBLE PRECISION,
    mfcc_std16 DOUBLE PRECISION,
    mfcc_std17 DOUBLE PRECISION,
    mfcc_std18 DOUBLE PRECISION,
    mfcc_std19 DOUBLE PRECISION,
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
    spectral_contrast_kurtosis1 DOUBLE PRECISION,
    spectral_contrast_kurtosis2 DOUBLE PRECISION,
    spectral_contrast_kurtosis3 DOUBLE PRECISION,
    spectral_contrast_kurtosis4 DOUBLE PRECISION,
    spectral_contrast_kurtosis5 DOUBLE PRECISION,
    spectral_contrast_kurtosis6 DOUBLE PRECISION,
    spectral_contrast_max DOUBLE PRECISION,
    spectral_contrast_max1 DOUBLE PRECISION,
    spectral_contrast_max2 DOUBLE PRECISION,
    spectral_contrast_max3 DOUBLE PRECISION,
    spectral_contrast_max4 DOUBLE PRECISION,
    spectral_contrast_max5 DOUBLE PRECISION,
    spectral_contrast_max6 DOUBLE PRECISION,
    spectral_contrast_mean DOUBLE PRECISION,
    spectral_contrast_mean1 DOUBLE PRECISION,
    spectral_contrast_mean2 DOUBLE PRECISION,
    spectral_contrast_mean3 DOUBLE PRECISION,
    spectral_contrast_mean4 DOUBLE PRECISION,
    spectral_contrast_mean5 DOUBLE PRECISION,
    spectral_contrast_mean6 DOUBLE PRECISION,
    spectral_contrast_median DOUBLE PRECISION,
    spectral_contrast_median1 DOUBLE PRECISION,
    spectral_contrast_median2 DOUBLE PRECISION,
    spectral_contrast_median3 DOUBLE PRECISION,
    spectral_contrast_median4 DOUBLE PRECISION,
    spectral_contrast_median5 DOUBLE PRECISION,
    spectral_contrast_median6 DOUBLE PRECISION,
    spectral_contrast_min DOUBLE PRECISION,
    spectral_contrast_min1 DOUBLE PRECISION,
    spectral_contrast_min2 DOUBLE PRECISION,
    spectral_contrast_min3 DOUBLE PRECISION,
    spectral_contrast_min4 DOUBLE PRECISION,
    spectral_contrast_min5 DOUBLE PRECISION,
    spectral_contrast_min6 DOUBLE PRECISION,
    spectral_contrast_skew DOUBLE PRECISION,
    spectral_contrast_skew1 DOUBLE PRECISION,
    spectral_contrast_skew2 DOUBLE PRECISION,
    spectral_contrast_skew3 DOUBLE PRECISION,
    spectral_contrast_skew4 DOUBLE PRECISION,
    spectral_contrast_skew5 DOUBLE PRECISION,
    spectral_contrast_skew6 DOUBLE PRECISION,
    spectral_contrast_std DOUBLE PRECISION,
    spectral_contrast_std1 DOUBLE PRECISION,
    spectral_contrast_std2 DOUBLE PRECISION,
    spectral_contrast_std3 DOUBLE PRECISION,
    spectral_contrast_std4 DOUBLE PRECISION,
    spectral_contrast_std5 DOUBLE PRECISION,
    spectral_contrast_std6 DOUBLE PRECISION,
    spectral_rolloff_kurtosis DOUBLE PRECISION,
    spectral_rolloff_max DOUBLE PRECISION,
    spectral_rolloff_mean DOUBLE PRECISION,
    spectral_rolloff_median DOUBLE PRECISION,
    spectral_rolloff_min DOUBLE PRECISION,
    spectral_rolloff_skew DOUBLE PRECISION,
    spectral_rolloff_std DOUBLE PRECISION,
    tonnetz_kurtosis DOUBLE PRECISION,
    tonnetz_kurtosis1 DOUBLE PRECISION,
    tonnetz_kurtosis2 DOUBLE PRECISION,
    tonnetz_kurtosis3 DOUBLE PRECISION,
    tonnetz_kurtosis4 DOUBLE PRECISION,
    tonnetz_kurtosis5 DOUBLE PRECISION,
    tonnetz_max DOUBLE PRECISION,
    tonnetz_max1 DOUBLE PRECISION,
    tonnetz_max2 DOUBLE PRECISION,
    tonnetz_max3 DOUBLE PRECISION,
    tonnetz_max4 DOUBLE PRECISION,
    tonnetz_max5 DOUBLE PRECISION,
    tonnetz_mean DOUBLE PRECISION,
    tonnetz_mean1 DOUBLE PRECISION,
    tonnetz_mean2 DOUBLE PRECISION,
    tonnetz_mean3 DOUBLE PRECISION,
    tonnetz_mean4 DOUBLE PRECISION,
    tonnetz_mean5 DOUBLE PRECISION,
    tonnetz_median DOUBLE PRECISION,
    tonnetz_median1 DOUBLE PRECISION,
    tonnetz_median2 DOUBLE PRECISION,
    tonnetz_median3 DOUBLE PRECISION,
    tonnetz_median4 DOUBLE PRECISION,
    tonnetz_median5 DOUBLE PRECISION,
    tonnetz_min DOUBLE PRECISION,
    tonnetz_min1 DOUBLE PRECISION,
    tonnetz_min2 DOUBLE PRECISION,
    tonnetz_min3 DOUBLE PRECISION,
    tonnetz_min4 DOUBLE PRECISION,
    tonnetz_min5 DOUBLE PRECISION,
    tonnetz_skew DOUBLE PRECISION,
    tonnetz_skew1 DOUBLE PRECISION,
    tonnetz_skew2 DOUBLE PRECISION,
    tonnetz_skew3 DOUBLE PRECISION,
    tonnetz_skew4 DOUBLE PRECISION,
    tonnetz_skew5 DOUBLE PRECISION,
    tonnetz_std DOUBLE PRECISION,
    tonnetz_std1 DOUBLE PRECISION,
    tonnetz_std2 DOUBLE PRECISION,
    tonnetz_std3 DOUBLE PRECISION,
    tonnetz_std4 DOUBLE PRECISION,
    tonnetz_std5 DOUBLE PRECISION,
    zcr_kurtosis DOUBLE PRECISION,
    zcr_max DOUBLE PRECISION,
    zcr_mean DOUBLE PRECISION,
    zcr_median DOUBLE PRECISION,
    zcr_min DOUBLE PRECISION,
    zcr_skew DOUBLE PRECISION,
    zcr_std DOUBLE PRECISION,
    PRIMARY KEY (track_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id)
);

CREATE TABLE tag (
    tag_id UUID DEFAULT uuid_generate_v4(),
    tag_name VARCHAR(255),
    PRIMARY KEY (tag_id)
);

CREATE TABLE playlist (
    playlist_id UUID DEFAULT uuid_generate_v4(),
    playlist_name VARCHAR(255),
    PRIMARY KEY (playlist_id)
);

CREATE TABLE rank_track (
    track_id UUID,
    rank_song_currency BIGINT,
    rank_song_hotttnesss BIGINT,
    PRIMARY KEY (track_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id)
);

CREATE TABLE rank_artist (
    artist_id UUID,
    rank_artist_discovery BIGINT,
    rank_artist_familiarity BIGINT,
    rank_artist_hotttnesss BIGINT,
    PRIMARY KEY (artist_id),
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id)
);

CREATE TABLE license (
    license_id UUID DEFAULT uuid_generate_v4(),
    license_title VARCHAR(255),
    license_url VARCHAR(255),
    PRIMARY KEY (license_id)
);

CREATE TABLE track_genre (
    track_id UUID,
    genre_id UUID,
    PRIMARY KEY (track_id, genre_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);

CREATE TABLE track_tag (
    track_id UUID,
    tag_id UUID,
    PRIMARY KEY (track_id, tag_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (tag_id) REFERENCES tag(tag_id)
);

CREATE TABLE artist_tag (
    artist_id UUID,
    tag_id UUID,
    PRIMARY KEY (artist_id, tag_id),
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id),
    FOREIGN KEY (tag_id) REFERENCES tag(tag_id)
);

CREATE TABLE album_artist (
    album_id UUID,
    artist_id UUID,
    PRIMARY KEY (album_id, artist_id),
    FOREIGN KEY (album_id) REFERENCES album(album_id),
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id)
);

CREATE TABLE track_artist_main (
    track_id UUID,
    artist_id UUID,
    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id)
);

CREATE TABLE track_artist_feat (
    track_id UUID,
    artist_id UUID,
    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id)
);

CREATE TABLE track_license (
    track_id UUID,
    license_id UUID,
    PRIMARY KEY (track_id, license_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (license_id) REFERENCES license(license_id)
);

CREATE TABLE playlist_track (
    playlist_id UUID,
    track_id UUID,
    PRIMARY KEY (playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES playlist(playlist_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id)
);

CREATE TABLE "user" (
    account_id UUID,
    pseudo VARCHAR(255),
    PRIMARY KEY (account_id),
    FOREIGN KEY (account_id) REFERENCES account(account_id)
);

CREATE TABLE preference (
    account_id UUID,
    age_range VARCHAR(255),
    gender VARCHAR(255),
    position VARCHAR(255),
    has_consented BOOLEAN,
    is_listening BOOLEAN,
    frequency INTEGER,
    when_listening DOUBLE PRECISION,
    duration_pref INTEGER,
    energy_pref VARCHAR(255),
    tempo_pref DOUBLE PRECISION,
    feeling_pref VARCHAR(255),
    is_live_pref VARCHAR(255),
    quality_pref INTEGER,
    curiosity_pref INTEGER,
    context INTEGER,
    how VARCHAR(255),
    platform VARCHAR(255),
    utility VARCHAR(255),
    track_genre VARCHAR(255),
    PRIMARY KEY (account_id),
    FOREIGN KEY (account_id) REFERENCES "user"(account_id)
);

CREATE TABLE playlist_user (
    playlist_id UUID,
    account_id UUID,
    PRIMARY KEY (playlist_id, account_id),
    FOREIGN KEY (playlist_id) REFERENCES playlist(playlist_id),
    FOREIGN KEY (account_id) REFERENCES "user"(account_id)
);

CREATE TABLE track_user_like (
    track_id UUID,
    account_id UUID,
    PRIMARY KEY (track_id, account_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (account_id) REFERENCES "user"(account_id)
);

CREATE TABLE track_user_listen (
    track_id UUID,
    account_id UUID,
    PRIMARY KEY (track_id, account_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (account_id) REFERENCES "user"(account_id)
);


CREATE TABLE track_comment (
    comment_id UUID DEFAULT uuid_generate_v4(),
    track_id UUID NOT NULL,
    account_id UUID,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (comment_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (account_id) REFERENCES "user"(account_id)
);

CREATE OR REPLACE VIEW v_track_full AS
SELECT
    t.track_id,
    t.album_id,
    t.track_title,
    t.track_duration,
    t.track_number,
    t.track_disc_number,
    t.track_explicit,
    t.track_instrumental,
    t.track_listens,
    t.track_favorites,
    t.track_interest,
    t.track_comments,
    t.track_date_created,
    t.track_composer,
    t.track_lyricist,
    t.track_publisher,
    a.album_title,
    a.album_date_released,
    a.album_tracks_count,
    (SELECT json_agg(json_build_object('artist_id', tam.artist_id))
       FROM track_artist_main tam WHERE tam.track_id = t.track_id) AS main_artists,
    (SELECT json_agg(json_build_object('artist_id', taf.artist_id))
       FROM track_artist_feat taf WHERE taf.track_id = t.track_id) AS feat_artists,
    (SELECT json_agg(g.title)
       FROM track_genre tg JOIN genre g ON g.genre_id = tg.genre_id
       WHERE tg.track_id = t.track_id) AS genres,
    (SELECT json_agg(tag_name)
       FROM track_tag tt JOIN tag tg ON tg.tag_id = tt.tag_id
       WHERE tt.track_id = t.track_id) AS tags,
    af.acousticness,
    af.danceability,
    af.energy,
    af.instrumentalness,
    af.liveness,
    af.speechiness,
    af.tempo,
    af.valence,
    to_jsonb(tf) - 'track_id' AS temporal_features
FROM track t
LEFT JOIN album a ON t.album_id = a.album_id
LEFT JOIN audio_feature af ON af.track_id = t.track_id
LEFT JOIN temporal_feature tf ON tf.track_id = t.track_id;

CREATE OR REPLACE VIEW v_album_full AS
SELECT
    al.album_id,
    al.album_title,
    al.album_type,
    al.album_tracks_count,
    al.album_date_released,
    (SELECT json_agg(json_build_object('artist_id', aa.artist_id)) 
       FROM album_artist aa WHERE aa.album_id = al.album_id) AS artists,
    (SELECT json_agg(json_build_object('track_id', t.track_id, 'track_title', t.track_title, 'track_number', t.track_number)) 
       FROM track t WHERE t.album_id = al.album_id) AS tracks
FROM album al;

CREATE OR REPLACE VIEW v_artist_full AS
SELECT
    ar.artist_id,
    ar.artist_bio,
    ar.artist_location,
    ar.artist_latitude,
    ar.artist_longitude,
    ar.artist_active_year_begin,
    ar.artist_active_year_end,
    ar.artist_favorites,
    ar.artist_comments,
    (SELECT json_agg(tag_id) FROM artist_tag at WHERE at.artist_id = ar.artist_id) AS tags,
    (SELECT json_agg(album_id) FROM album_artist aa WHERE aa.artist_id = ar.artist_id) AS albums,
    (SELECT json_agg(track_id) FROM track_artist_main tam WHERE tam.artist_id = ar.artist_id) AS main_tracks,
    (SELECT json_agg(track_id) FROM track_artist_feat taf WHERE taf.artist_id = ar.artist_id) AS feat_tracks
FROM artist ar;

CREATE OR REPLACE VIEW v_tracks_list AS
SELECT
    track_id,
    track_title,
    track_duration,
    track_listens,
    track_favorites,
    track_comments
FROM track;

CREATE OR REPLACE VIEW v_albums_list AS
SELECT
    album_id,
    album_title,
    album_tracks_count,
    album_listens,
    album_favorites,
    album_comments
FROM album;

CREATE OR REPLACE VIEW v_artists_list AS
SELECT
    artist_id,
    artist_bio,
    artist_location,
    artist_favorites,
    artist_comments
FROM artist;

CREATE OR REPLACE VIEW v_track_popularity AS
SELECT
    t.track_id,
    t.track_title,
    t.track_listens,
    t.track_favorites,
    t.track_comments,
    rt.rank_song_currency,
    rt.rank_song_hotttnesss
FROM track t
LEFT JOIN rank_track rt ON rt.track_id = t.track_id;

CREATE OR REPLACE VIEW v_artist_popularity AS
SELECT
    ar.artist_id,
    ar.artist_bio,
    ar.artist_favorites,
    ar.artist_comments,
    ra.rank_artist_discovery,
    ra.rank_artist_familiarity,
    ra.rank_artist_hotttnesss
FROM artist ar
LEFT JOIN rank_artist ra ON ra.artist_id = ar.artist_id;

CREATE OR REPLACE VIEW v_user_playlists AS
SELECT
    u.account_id,
    u.pseudo,
    pu.playlist_id,
    p.playlist_name,
    (SELECT json_agg(pt.track_id ORDER BY pt.track_id) 
       FROM playlist_track pt WHERE pt.playlist_id = p.playlist_id) AS track_ids
FROM "user" u
LEFT JOIN playlist_user pu ON pu.account_id = u.account_id
LEFT JOIN playlist p ON p.playlist_id = pu.playlist_id;

CREATE OR REPLACE VIEW v_track_comments AS
SELECT
    tc.track_id,
    json_agg(json_build_object('comment_id', tc.comment_id, 'account_id', tc.account_id, 'content', tc.content, 'created_at', tc.created_at) ORDER BY tc.created_at) AS comments
FROM track_comment tc
GROUP BY tc.track_id;

CREATE OR REPLACE VIEW v_user_listen_history AS
SELECT
    tul.account_id,
    json_agg(tul.track_id) AS listened_track_ids
FROM track_user_listen tul
GROUP BY tul.account_id;

CREATE OR REPLACE VIEW v_user_summary AS
SELECT
    u.account_id,
    u.pseudo,
    a.login,
    a.email,
    a.name,
    a.created_at AS account_created_at,
    p.age_range,
    p.gender,
    p.position,
    p.has_consented,
    p.is_listening,
    p.frequency,
    p.when_listening,
    p.duration_pref,
    p.energy_pref,
    p.tempo_pref,
    p.feeling_pref,
    p.is_live_pref,
    p.quality_pref,
    p.curiosity_pref,
    p.context,
    p.how,
    p.platform,
    p.utility,
    p.track_genre
FROM "user" u
LEFT JOIN account a ON a.account_id = u.account_id
LEFT JOIN preference p ON p.account_id = u.account_id;

CREATE OR REPLACE VIEW v_tracks_recommended AS
SELECT
    t.track_id,
    t.track_title,
    af.energy,
    af.tempo,
    af.valence,
    rt.rank_song_hotttnesss,
    t.track_listens,
    t.track_favorites
FROM track t
LEFT JOIN audio_feature af ON af.track_id = t.track_id
LEFT JOIN rank_track rt ON rt.track_id = t.track_id;

CREATE OR REPLACE VIEW v_entity_tags AS
SELECT 'track' AS entity_type, tt.track_id AS entity_id, tg.tag_id, tg.tag_name 
FROM track_tag tt 
JOIN tag tg ON tg.tag_id = tt.tag_id
UNION ALL
SELECT 'artist' AS entity_type, at.artist_id AS entity_id, tg.tag_id, tg.tag_name 
FROM artist_tag at 
JOIN tag tg ON tg.tag_id = at.tag_id;

CREATE OR REPLACE VIEW v_track_audio AS
SELECT
    t.track_id,
    af.acousticness,
    af.danceability,
    af.energy,
    af.instrumentalness,
    af.liveness,
    af.speechiness,
    af.tempo,
    af.valence,
    to_jsonb(tf) - 'track_id' AS temporal_features
FROM track t
LEFT JOIN audio_feature af ON af.track_id = t.track_id
LEFT JOIN temporal_feature tf ON tf.track_id = t.track_id;

-- ====================================================================================
-- FONCTIONS & TRIGGERS
-- ====================================================================================

/*
  Helper: fonction pour incrémenter album_tracks_count (utilisée par triggers insert/delete)
*/
CREATE OR REPLACE FUNCTION f_inc_album_tracks_count(p_album_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE album
  SET album_tracks_count = COALESCE(album_tracks_count,0) + 1
  WHERE album_id = p_album_id;
END;
$$ LANGUAGE plpgsql;

/*
  Helper: fonction pour décrémenter album_tracks_count
*/
CREATE OR REPLACE FUNCTION f_dec_album_tracks_count(p_album_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE album
  SET album_tracks_count = GREATEST(COALESCE(album_tracks_count,0) - 1, 0)
  WHERE album_id = p_album_id;
END;
$$ LANGUAGE plpgsql;

/*
  Trigger: après INSERT track -> si album_id NULL créer un album (single) et set NEW.album_id
           et ensuite incrémenter album_tracks_count.
  On implémente la création d'album dans un trigger BEFORE INSERT pour pouvoir modifier NEW.album_id.
*/
CREATE OR REPLACE FUNCTION f_track_before_insert_create_album_if_null()
RETURNS trigger AS $$
DECLARE created_album_id UUID;
BEGIN
  IF NEW.album_id IS NULL THEN
    INSERT INTO album(album_title, album_type, album_tracks_count, album_date_released)
    VALUES (COALESCE(NEW.track_title, 'Untitled') || ' - Single', 'single', 1, COALESCE(NEW.track_date_created, CURRENT_DATE))
    RETURNING album_id INTO created_album_id;

    NEW.album_id := created_album_id;
    -- set counters on track (initial)
    NEW.track_listens := COALESCE(NEW.track_listens, 0);
    NEW.track_favorites := COALESCE(NEW.track_favorites, 0);
    NEW.track_comments := COALESCE(NEW.track_comments, 0);
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_track_before_insert_create_album_if_null
BEFORE INSERT ON track
FOR EACH ROW
EXECUTE FUNCTION f_track_before_insert_create_album_if_null();

/*
  Trigger: après INSERT sur track -> incrémente album_tracks_count (si album existant)
  et crée en base rank_track, audio_feature, temporal_feature automatiquement.
*/
CREATE OR REPLACE FUNCTION f_track_after_insert_postcreate()
RETURNS trigger AS $$
BEGIN
  IF NEW.album_id IS NOT NULL THEN
    PERFORM f_inc_album_tracks_count(NEW.album_id);
  END IF;

  -- créer rank_track si absent
  INSERT INTO rank_track(track_id, rank_song_currency, rank_song_hotttnesss)
  VALUES (NEW.track_id, 0, 0)
  ON CONFLICT (track_id) DO NOTHING;

  -- créer audio_feature si absent
  INSERT INTO audio_feature(track_id) VALUES (NEW.track_id)
  ON CONFLICT (track_id) DO NOTHING;

  -- créer temporal_feature si absent
  INSERT INTO temporal_feature(track_id) VALUES (NEW.track_id)
  ON CONFLICT (track_id) DO NOTHING;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_track_after_insert_postcreate
AFTER INSERT ON track
FOR EACH ROW
EXECUTE FUNCTION f_track_after_insert_postcreate();

CREATE OR REPLACE FUNCTION f_track_before_delete_cleanup()
RETURNS trigger AS $$
BEGIN
    -- Supprimer toutes les dépendances
    DELETE FROM track_artist_main WHERE track_id = OLD.track_id;
    DELETE FROM track_artist_feat WHERE track_id = OLD.track_id;
    DELETE FROM track_license WHERE track_id = OLD.track_id;
    DELETE FROM track_genre WHERE track_id = OLD.track_id;
    DELETE FROM track_tag WHERE track_id = OLD.track_id;
    DELETE FROM playlist_track WHERE track_id = OLD.track_id;
    DELETE FROM track_user_like WHERE track_id = OLD.track_id;
    DELETE FROM track_user_listen WHERE track_id = OLD.track_id;
    DELETE FROM track_comment WHERE track_id = OLD.track_id;
    DELETE FROM rank_track WHERE track_id = OLD.track_id;
    DELETE FROM audio_feature WHERE track_id = OLD.track_id;
    DELETE FROM temporal_feature WHERE track_id = OLD.track_id;

    -- Décrémenter album_tracks_count
    IF OLD.album_id IS NOT NULL THEN
        PERFORM f_dec_album_tracks_count(OLD.album_id);
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;



-- Créer le trigger BEFORE DELETE
CREATE TRIGGER tr_track_before_delete_cleanup
BEFORE DELETE ON track
FOR EACH ROW
EXECUTE FUNCTION f_track_before_delete_cleanup();


/*
  Trigger: empêcher suppression d'un album s'il contient des tracks
*/
CREATE OR REPLACE FUNCTION f_prevent_album_delete_if_tracks()
RETURNS trigger AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM track WHERE album_id = OLD.album_id) THEN
    RAISE EXCEPTION 'Impossible de supprimer l''album % : il contient des tracks.', OLD.album_id;
  END IF;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_prevent_album_delete
BEFORE DELETE ON album
FOR EACH ROW
EXECUTE FUNCTION f_prevent_album_delete_if_tracks();

CREATE OR REPLACE FUNCTION f_track_assign_anonymous_if_no_main_artist_and_album_artists()
RETURNS trigger AS $$
DECLARE
    anon_artist_id UUID;
    has_artist BOOLEAN;
BEGIN
    -- Créer artiste anonyme s'il n'existe pas
    SELECT account_id INTO anon_artist_id
    FROM account
    WHERE login = 'anonymous_artist';

    IF anon_artist_id IS NULL THEN
        INSERT INTO account(account_id, login, email, name)
        VALUES (uuid_generate_v4(), 'anonymous_artist', 'anon@example.com', 'Anonymous Artist')
        RETURNING account_id INTO anon_artist_id;
    END IF;

    -- Vérifier s'il existe un main artist pour le track
    SELECT EXISTS(
        SELECT 1 FROM track_artist_main tam
        WHERE tam.track_id = NEW.track_id
    ) INTO has_artist;

    -- Vérifier si l'album a des artistes
    IF NOT has_artist AND NOT EXISTS (
        SELECT 1 FROM album_artist aa
        WHERE aa.album_id = NEW.album_id
    ) THEN
        -- On peut maintenant ajouter le lien
        INSERT INTO track_artist_main(track_id, artist_id)
        VALUES (NEW.track_id, anon_artist_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_track_assign_anonymous_if_no_main_artist_and_album_artists
AFTER INSERT ON track
FOR EACH ROW
EXECUTE FUNCTION f_track_assign_anonymous_if_no_main_artist_and_album_artists();


/*
  Triggers pour likes : lorsque track_user_like est inséré/supprimé, on met à jour track.track_favorites
*/
CREATE OR REPLACE FUNCTION f_inc_track_favorites_on_like()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_favorites = COALESCE(track_favorites,0) + 1 WHERE track_id = NEW.track_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_dec_track_favorites_on_unlike()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_favorites = GREATEST(COALESCE(track_favorites,0) - 1, 0) WHERE track_id = OLD.track_id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_inc_track_favorites
AFTER INSERT ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_inc_track_favorites_on_like();

CREATE TRIGGER tr_dec_track_favorites
AFTER DELETE ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_dec_track_favorites_on_unlike();

/*
  Triggers pour listens : incrémente track.track_listens quand on insère un écoute
*/
CREATE OR REPLACE FUNCTION f_inc_track_listens_on_listen()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_listens = COALESCE(track_listens,0) + 1 WHERE track_id = NEW.track_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_inc_track_listens
AFTER INSERT ON track_user_listen
FOR EACH ROW
EXECUTE FUNCTION f_inc_track_listens_on_listen();

/*
  Triggers pour commentaires : insert/delete dans track_comment met à jour track.track_comments
*/
CREATE OR REPLACE FUNCTION f_inc_track_comments_on_comment()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_comments = COALESCE(track_comments,0) + 1 WHERE track_id = NEW.track_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_dec_track_comments_on_comment_delete()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_comments = GREATEST(COALESCE(track_comments,0) - 1,0) WHERE track_id = OLD.track_id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_inc_track_comments
AFTER INSERT ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_inc_track_comments_on_comment();

CREATE TRIGGER tr_dec_track_comments
AFTER DELETE ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_dec_track_comments_on_comment_delete();

/*
  Trigger : créer automatiquement une playlist pour un user s'il n'en a aucune
  On suppose que création se déclenche lorsqu'un like est ajouté (ex: user like first track).
*/
CREATE OR REPLACE FUNCTION f_create_playlist_if_none_for_user()
RETURNS trigger AS $$
DECLARE p_id UUID;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM playlist_user WHERE account_id = NEW.account_id) THEN
    INSERT INTO playlist(playlist_name) VALUES ('My First Playlist') RETURNING playlist_id INTO p_id;
    INSERT INTO playlist_user(playlist_id, account_id) VALUES (p_id, NEW.account_id);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_create_playlist_if_none
AFTER INSERT ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_create_playlist_if_none_for_user();

/*
  Trigger: création automatique de rank_artist quand un artist est ajouté
*/
CREATE OR REPLACE FUNCTION f_auto_create_rank_artist()
RETURNS trigger AS $$
BEGIN
  INSERT INTO rank_artist(artist_id, rank_artist_discovery, rank_artist_familiarity, rank_artist_hotttnesss)
  VALUES (NEW.artist_id, 0, 0, 0)
  ON CONFLICT (artist_id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_auto_create_rank_artist
AFTER INSERT ON artist
FOR EACH ROW
EXECUTE FUNCTION f_auto_create_rank_artist();

/*
  Trigger: update album_tracks_count when track is deleted (we have earlier function but safeguard)
  (Already handled by f_track_after_delete_cleanup -> calls f_dec_album_tracks_count)
*/

/*
  Trigger: mettre à jour les compteurs dérivés d’un artiste (favorites, comments…)
  - artist_favorites = somme des track_favorites pour les tracks où il est main (ou feat selon choix)
  - artist_comments = somme des track_comments pour les tracks où il est main (ou feat selon choix)
*/
CREATE OR REPLACE FUNCTION f_recompute_artist_counters(p_artist_id UUID)
RETURNS void AS $$
DECLARE fav_sum BIGINT;
DECLARE com_sum BIGINT;
BEGIN
  -- somme des favorites des tracks où artist est main OR feat (on inclut les deux)
  SELECT COALESCE(SUM(t.track_favorites),0) INTO fav_sum
  FROM track t
  WHERE EXISTS (SELECT 1 FROM track_artist_main tam WHERE tam.track_id = t.track_id AND tam.artist_id = p_artist_id)
     OR EXISTS (SELECT 1 FROM track_artist_feat taf WHERE taf.track_id = t.track_id AND taf.artist_id = p_artist_id);

  SELECT COALESCE(SUM(t.track_comments),0) INTO com_sum
  FROM track t
  WHERE EXISTS (SELECT 1 FROM track_artist_main tam WHERE tam.track_id = t.track_id AND tam.artist_id = p_artist_id)
     OR EXISTS (SELECT 1 FROM track_artist_feat taf WHERE taf.track_id = t.track_id AND taf.artist_id = p_artist_id);

  UPDATE artist
  SET artist_favorites = fav_sum,
      artist_comments = com_sum
  WHERE artist_id = p_artist_id;
END;
$$ LANGUAGE plpgsql;

/*
  Appels triggers: lorsqu'une relation track_artist_main / track_artist_feat change,
  ou lorsqu'un like/comment est inséré/supprimé sur un track, on recalculera l'artiste concerné.
*/
CREATE OR REPLACE FUNCTION f_after_track_artist_main_change()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(NEW.artist_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_after_insert_track_artist_main
AFTER INSERT ON track_artist_main
FOR EACH ROW
EXECUTE FUNCTION f_after_track_artist_main_change();

CREATE OR REPLACE FUNCTION f_after_delete_track_artist_main()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(OLD.artist_id);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_after_delete_track_artist_main
AFTER DELETE ON track_artist_main
FOR EACH ROW
EXECUTE FUNCTION f_after_delete_track_artist_main();

-- même pour featured artists
CREATE OR REPLACE FUNCTION f_after_track_artist_feat_change()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(NEW.artist_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_after_insert_track_artist_feat
AFTER INSERT ON track_artist_feat
FOR EACH ROW
EXECUTE FUNCTION f_after_track_artist_feat_change();

CREATE OR REPLACE FUNCTION f_after_delete_track_artist_feat()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(OLD.artist_id);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_after_delete_track_artist_feat
AFTER DELETE ON track_artist_feat
FOR EACH ROW
EXECUTE FUNCTION f_after_delete_track_artist_feat();

-- lorsque les likes/comments changent, recalculer compteurs artiste(s) liés au track
CREATE OR REPLACE FUNCTION f_after_like_change_recompute_artists()
RETURNS trigger AS $$
DECLARE v_track UUID := NEW.track_id;
BEGIN
  -- trouver artistes main et feat pour ce track et refresh
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_main WHERE track_id = v_track;
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_feat WHERE track_id = v_track;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_after_like_insert_recompute_artists
AFTER INSERT ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_after_like_change_recompute_artists();

CREATE TRIGGER tr_after_like_delete_recompute_artists
AFTER DELETE ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_after_like_change_recompute_artists();

-- pour les commentaires
CREATE OR REPLACE FUNCTION f_after_comment_change_recompute_artists()
RETURNS trigger AS $$
DECLARE v_track UUID := NEW.track_id;
BEGIN
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_main WHERE track_id = v_track;
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_feat WHERE track_id = v_track;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_after_comment_insert_recompute_artists
AFTER INSERT ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_after_comment_change_recompute_artists();

CREATE TRIGGER tr_after_comment_delete_recompute_artists
AFTER DELETE ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_after_comment_change_recompute_artists();


-- Fonction trigger
CREATE OR REPLACE FUNCTION ensure_artist_account()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifie si l'artist_id existe déjà dans account
    IF NOT EXISTS (SELECT 1 FROM account WHERE account_id = NEW.artist_id) THEN
        INSERT INTO account(account_id, login, email, name, created_at)
        VALUES (
            NEW.artist_id,
            'artist_' || NEW.artist_id::text,
            'artist_' || NEW.artist_id::text || '@example.com',  
            'Artist_' || NEW.artist_id::text, 
            CURRENT_TIMESTAMP
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger sur artist
CREATE TRIGGER trg_ensure_artist_account
BEFORE INSERT ON artist
FOR EACH ROW
EXECUTE FUNCTION ensure_artist_account();
