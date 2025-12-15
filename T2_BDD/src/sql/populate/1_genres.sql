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
JOIN inserted i ON i.title = s.title;

TRUNCATE TABLE _legacy_id_map;

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
