-- ====================================================================================
-- VIEWS
-- ====================================================================================

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
LEFT JOIN LATERAL (
    SELECT rank_song_currency, rank_song_hotttnesss
    FROM rank_track
    WHERE track_id = t.track_id
    ORDER BY ranks_date DESC
    LIMIT 1
) rt ON true;

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
LEFT JOIN LATERAL (
    SELECT rank_artist_discovery, rank_artist_familiarity, rank_artist_hotttnesss
    FROM rank_artist
    WHERE artist_id = ar.artist_id
    ORDER BY ranks_date DESC
    LIMIT 1
) ra ON true;

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
    (SELECT json_agg(g.title) 
     FROM genre_preference gp 
     JOIN genre g ON g.genre_id = gp.genre_id 
     WHERE gp.account_id = u.account_id) AS track_genres
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
LEFT JOIN LATERAL (
    SELECT rank_song_hotttnesss
    FROM rank_track
    WHERE track_id = t.track_id
    ORDER BY ranks_date DESC
    LIMIT 1
) rt ON true;

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
