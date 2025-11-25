-- Database Creation Script for SAE5 T2_BDD
-- Based on the validated schema in database_schema.md

-- =============================================================================
-- 1. Music Domain
-- =============================================================================

-- Artists Table
CREATE TABLE Artists (
    artist_id INT PRIMARY KEY,
    artist_name TEXT NOT NULL,
    artist_bio TEXT,
    artist_location TEXT,
    artist_latitude FLOAT,
    artist_longitude FLOAT,
    artist_active_year_begin INT,
    artist_active_year_end INT,
    artist_favorites INT DEFAULT 0,
    artist_comments INT DEFAULT 0
);

-- Albums Table
CREATE TABLE Albums (
    album_id INT PRIMARY KEY,
    album_title TEXT NOT NULL,
    album_type VARCHAR(50),
    album_tracks_count INT,
    album_date_released DATE,
    album_listens INT DEFAULT 0,
    album_favorites INT DEFAULT 0,
    album_comments INT DEFAULT 0,
    album_producer TEXT
);

-- Genres Table
CREATE TABLE Genres (
    genre_id INT PRIMARY KEY,
    parent_id INT,
    title TEXT NOT NULL,
    top_level INT,
    CONSTRAINT fk_genre_parent FOREIGN KEY (parent_id) REFERENCES Genres(genre_id)
);

-- Tracks Table
CREATE TABLE Tracks (
    track_id INT PRIMARY KEY,
    album_id INT,
    artist_id INT,
    track_title TEXT NOT NULL,
    track_duration INT, -- Duration in seconds or milliseconds (as per data)
    track_number INT,
    track_disc_number INT,
    track_explicit BOOLEAN DEFAULT FALSE,
    track_instrumental BOOLEAN DEFAULT FALSE,
    track_listens INT DEFAULT 0,
    track_favorites INT DEFAULT 0,
    track_interest FLOAT,
    track_comments INT DEFAULT 0,
    track_date_created DATE,
    track_composer TEXT,
    track_lyricist TEXT,
    track_publisher TEXT,
    CONSTRAINT fk_track_album FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    CONSTRAINT fk_track_artist FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);

-- AudioFeatures Table
CREATE TABLE AudioFeatures (
    track_id INT PRIMARY KEY,
    acousticness FLOAT,
    danceability FLOAT,
    energy FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    speechiness FLOAT,
    tempo FLOAT,
    valence FLOAT,
    CONSTRAINT fk_audio_track FOREIGN KEY (track_id) REFERENCES Tracks(track_id)
);

-- Junction Tables for Music Domain

-- TrackGenres
CREATE TABLE TrackGenres (
    track_id INT,
    genre_id INT,
    PRIMARY KEY (track_id, genre_id),
    CONSTRAINT fk_tg_track FOREIGN KEY (track_id) REFERENCES Tracks(track_id),
    CONSTRAINT fk_tg_genre FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

-- TrackTags
CREATE TABLE TrackTags (
    track_id INT,
    tag TEXT,
    PRIMARY KEY (track_id, tag),
    CONSTRAINT fk_tt_track FOREIGN KEY (track_id) REFERENCES Tracks(track_id)
);

-- ArtistTags
CREATE TABLE ArtistTags (
    artist_id INT,
    tag TEXT,
    PRIMARY KEY (artist_id, tag),
    CONSTRAINT fk_at_artist FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);

-- ArtistAssociatedLabels
CREATE TABLE ArtistAssociatedLabels (
    artist_id INT,
    label TEXT,
    PRIMARY KEY (artist_id, label),
    CONSTRAINT fk_aal_artist FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);

-- ArtistMembers
CREATE TABLE ArtistMembers (
    artist_id INT,
    member_name TEXT,
    PRIMARY KEY (artist_id, member_name),
    CONSTRAINT fk_am_artist FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);

-- =============================================================================
-- 2. User Domain (Alternants)
-- =============================================================================

-- Users Table
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    age_range VARCHAR(50),
    gender VARCHAR(50),
    position VARCHAR(100),
    has_consented BOOLEAN NOT NULL,
    is_listening BOOLEAN,
    frequency VARCHAR(100),
    when_listening FLOAT, -- Normalized quantitative value
    duration_pref FLOAT, -- Normalized quantitative value
    energy_pref VARCHAR(100),
    tempo_pref FLOAT, -- Normalized quantitative value
    feeling_pref VARCHAR(100),
    is_live_pref VARCHAR(100),
    quality_pref FLOAT, -- Normalized quantitative value
    curiosity_pref FLOAT -- Normalized quantitative value
);

-- Junction Tables for User Domain

-- UserContexts
CREATE TABLE UserContexts (
    user_id INT,
    context TEXT,
    PRIMARY KEY (user_id, context),
    CONSTRAINT fk_uc_user FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- UserListeningMethods
CREATE TABLE UserListeningMethods (
    user_id INT,
    method TEXT,
    PRIMARY KEY (user_id, method),
    CONSTRAINT fk_ulm_user FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- UserPlatforms
CREATE TABLE UserPlatforms (
    user_id INT,
    platform TEXT,
    PRIMARY KEY (user_id, platform),
    CONSTRAINT fk_up_user FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- UserUtilities
CREATE TABLE UserUtilities (
    user_id INT,
    utility TEXT,
    PRIMARY KEY (user_id, utility),
    CONSTRAINT fk_uu_user FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- UserGenrePrefs
CREATE TABLE UserGenrePrefs (
    user_id INT,
    genre_name TEXT,
    PRIMARY KEY (user_id, genre_name),
    CONSTRAINT fk_ugp_user FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
