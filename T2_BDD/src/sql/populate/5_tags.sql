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
