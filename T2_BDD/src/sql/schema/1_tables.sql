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
    ranks_date TIMESTAMP DEFAULT NOW(),
    rank_song_currency BIGINT,
    rank_song_hotttnesss BIGINT,
    PRIMARY KEY (track_id, ranks_date),
    FOREIGN KEY (track_id) REFERENCES track(track_id)
);

CREATE TABLE rank_artist (
    artist_id UUID,
    ranks_date TIMESTAMP DEFAULT NOW(),
    rank_artist_discovery BIGINT,
    rank_artist_familiarity BIGINT,
    rank_artist_hotttnesss BIGINT,
    PRIMARY KEY (artist_id, ranks_date),
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
    frequency VARCHAR(255),
    when_listening DOUBLE PRECISION,
    duration_pref INTEGER,
    energy_pref VARCHAR(255),
    tempo_pref DOUBLE PRECISION,
    feeling_pref VARCHAR(255),
    is_live_pref VARCHAR(255),
    quality_pref INTEGER,
    curiosity_pref INTEGER,
    context VARCHAR(255),
    how VARCHAR(255),
    platform VARCHAR(255),
    utility VARCHAR(255),
    PRIMARY KEY (account_id),
    FOREIGN KEY (account_id) REFERENCES "user"(account_id)
);

CREATE TABLE genre_preference (
    account_id UUID,
    genre_id UUID,
    PRIMARY KEY (account_id, genre_id),
    FOREIGN KEY (account_id) REFERENCES preference(account_id),
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
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
    count INTEGER DEFAULT 1,
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
