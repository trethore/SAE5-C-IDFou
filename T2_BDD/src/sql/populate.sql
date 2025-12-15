-- Entrypoint populate script; executes staged imports
\i T2_BDD/src/sql/populate/0_settings_helpers.sql
\i T2_BDD/src/sql/populate/1_genres.sql
\i T2_BDD/src/sql/populate/2_artists.sql
\i T2_BDD/src/sql/populate/3_albums.sql
\i T2_BDD/src/sql/populate/4_tracks.sql
\i T2_BDD/src/sql/populate/5_tags.sql
\i T2_BDD/src/sql/populate/6_audio_features.sql
\i T2_BDD/src/sql/populate/7_temporal_features.sql
\i T2_BDD/src/sql/populate/8_users.sql
\i T2_BDD/src/sql/populate/9_cleanup.sql
