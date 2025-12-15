-- ====================================================================================
-- EXTENSIONS ET SUPPRESSION
-- ====================================================================================

-- extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------
-- SUPPRESSION
-- ------------------------------------------------
DROP TABLE IF EXISTS account, artist, album, genre, track, audio_feature, temporal_feature, tag, playlist, rank_track, rank_artist, license, track_genre, track_tag, artist_tag, album_artist, track_artist_main, track_artist_feat, track_license, playlist_track, "user", preference, genre_preference, playlist_user, track_user_like, track_user_listen, track_comment CASCADE;
