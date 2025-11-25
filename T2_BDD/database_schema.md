# Database Schema Proposal (T2_BDD)

Based on the analysis of `T1_analyse_de_donnees` (Music) and `T1_alternants` (Users), here is the proposed normalized PostgreSQL schema.

## 1. Music Domain

### Tables

#### `Artists`
- `artist_id` (INT, PK)
- `artist_name` (VARCHAR)
- `artist_bio` (TEXT)
- `artist_location` (VARCHAR)
- `artist_latitude` (FLOAT)
- `artist_longitude` (FLOAT)
- `artist_active_year_begin` (INT)
- `artist_active_year_end` (INT)
- `artist_favorites` (INT)
- `artist_comments` (INT)

#### `Albums`
- `album_id` (INT, PK)
- `album_title` (VARCHAR)
- `album_type` (VARCHAR)
- `album_tracks_count` (INT)
- `album_date_released` (DATE)
- `album_listens` (INT)
- `album_favorites` (INT)
- `album_comments` (INT)
- `album_producer` (VARCHAR)

#### `Genres`
- `genre_id` (INT, PK)
- `parent_id` (INT, FK -> Genres.genre_id)
- `title` (VARCHAR)
- `top_level` (INT)

#### `Tracks`
- `track_id` (INT, PK)
- `album_id` (INT, FK -> Albums.album_id)
- `artist_id` (INT, FK -> Artists.artist_id)
- `track_title` (VARCHAR)
- `track_duration` (INT)
- `track_number` (INT)
- `track_disc_number` (INT)
- `track_explicit` (BOOLEAN)
- `track_instrumental` (BOOLEAN)
- `track_listens` (INT)
- `track_favorites` (INT)
- `track_interest` (FLOAT)
- `track_comments` (INT)
- `track_date_created` (DATE)
- `track_composer` (VARCHAR)
- `track_lyricist` (VARCHAR)
- `track_publisher` (VARCHAR)

#### `AudioFeatures`
- `track_id` (INT, PK, FK -> Tracks.track_id)
- `acousticness` (FLOAT)
- `danceability` (FLOAT)
- `energy` (FLOAT)
- `instrumentalness` (FLOAT)
- `liveness` (FLOAT)
- `speechiness` (FLOAT)
- `tempo` (FLOAT)
- `valence` (FLOAT)

### Junction Tables (Normalization)

#### `TrackGenres`
- `track_id` (INT, FK -> Tracks.track_id)
- `genre_id` (INT, FK -> Genres.genre_id)
- PK: (`track_id`, `genre_id`)

#### `TrackTags`
- `track_id` (INT, FK -> Tracks.track_id)
- `tag` (VARCHAR)
- PK: (`track_id`, `tag`)

#### `ArtistTags`
- `artist_id` (INT, FK -> Artists.artist_id)
- `tag` (VARCHAR)
- PK: (`artist_id`, `tag`)

#### `ArtistAssociatedLabels`
- `artist_id` (INT, FK -> Artists.artist_id)
- `label` (VARCHAR)
- PK: (`artist_id`, `label`)

#### `ArtistMembers`
- `artist_id` (INT, FK -> Artists.artist_id)
- `member_name` (VARCHAR)
- PK: (`artist_id`, `member_name`)

---

## 2. User Domain (Alternants)

### Tables

#### `Users`
- `user_id` (SERIAL, PK)
- `created_at` (TIMESTAMP)
- `age_range` (VARCHAR)
- `gender` (VARCHAR)
- `position` (VARCHAR)
- `has_consented` (BOOLEAN)
- `is_listening` (BOOLEAN)
- `frequency` (VARCHAR)
- `when_listening` (FLOAT) -- Normalized quantitative value
- `duration_pref` (FLOAT) -- Normalized quantitative value
- `energy_pref` (VARCHAR)
- `tempo_pref` (FLOAT) -- Normalized quantitative value
- `feeling_pref` (VARCHAR)
- `is_live_pref` (VARCHAR)
- `quality_pref` (FLOAT) -- Normalized quantitative value
- `curiosity_pref` (FLOAT) -- Normalized quantitative value

### Junction Tables (Normalization)

#### `UserContexts`
- `user_id` (INT, FK -> Users.user_id)
- `context` (VARCHAR)
- PK: (`user_id`, `context`)

#### `UserListeningMethods`
- `user_id` (INT, FK -> Users.user_id)
- `method` (VARCHAR) -- from 'how' column
- PK: (`user_id`, `method`)

#### `UserPlatforms`
- `user_id` (INT, FK -> Users.user_id)
- `platform` (VARCHAR)
- PK: (`user_id`, `platform`)

#### `UserUtilities`
- `user_id` (INT, FK -> Users.user_id)
- `utility` (VARCHAR)
- PK: (`user_id`, `utility`)

#### `UserGenrePrefs`
- `user_id` (INT, FK -> Users.user_id)
- `genre_name` (VARCHAR) -- Note: This is text from the survey, might not match `Genres.title` exactly, but we can try to link if needed. For now, keeping as VARCHAR.
- PK: (`user_id`, `genre_name`)
