SET synchronous_commit = off;
-- ====================================================================================
-- HELPERS & MAPPINGS
-- ====================================================================================

-- 1. Helper Functions
CREATE OR REPLACE FUNCTION parse_python_list(p_text TEXT) RETURNS TEXT[] AS $$
DECLARE
    clean_text TEXT;
BEGIN
    IF p_text IS NULL OR p_text = '' OR p_text = '[]' THEN
        RETURN ARRAY[]::TEXT[];
    END IF;
    
    clean_text := p_text;
    
    -- Handle double-escaped quotes often found in CSV dumps of python lists: ["\"val\""]
    IF position('""' IN clean_text) > 0 THEN
        clean_text := replace(clean_text, '""', '"');
    END IF;

    -- Replace Python-style single quotes with double quotes for JSON parsing
    -- Only if it starts with [ and '
    IF left(clean_text, 2) = '[''' THEN
         clean_text := replace(clean_text, '''', '"');
    END IF;
    
    -- Fallback for simple ' -> " replacement if not covered above but still looks like list
    IF left(clean_text, 1) = '[' AND position('''' IN clean_text) > 0 AND position('"' IN clean_text) = 0 THEN
         clean_text := replace(clean_text, '''', '"');
    END IF;

    -- If it looks like JSON now, try to parse
    BEGIN
        RETURN ARRAY(SELECT jsonb_array_elements_text(clean_text::jsonb));
    EXCEPTION WHEN OTHERS THEN
        -- Fallback: basic string splitting if JSON fails. 
        -- Removes brackets and quotes for simple CSV-like parsing
        RETURN string_to_array(replace(replace(replace(trim(both '[]' from p_text), '''', ''), '"', ''), ', ', ','), ',');
    END;
END;
$$ LANGUAGE plpgsql;

-- 2. Mapping Table for Legacy IDs
CREATE TEMP TABLE _legacy_id_map (
    table_name TEXT,
    old_id TEXT,
    new_uuid UUID
);
CREATE INDEX idx_legacy_map ON _legacy_id_map(table_name, old_id);
