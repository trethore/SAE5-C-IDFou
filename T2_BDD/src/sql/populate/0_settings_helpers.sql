SET synchronous_commit = off;
-- ====================================================================================
-- HELPERS
-- ====================================================================================

-- 1. Fonctions utilitaires
CREATE OR REPLACE FUNCTION parse_python_list(p_text TEXT) RETURNS TEXT[] AS $$
DECLARE
    clean_text TEXT;
BEGIN
    IF p_text IS NULL OR p_text = '' OR p_text = '[]' THEN
        RETURN ARRAY[]::TEXT[];
    END IF;
    
    clean_text := p_text;
    
    -- Gerer les guillemets doubles echappes souvent vus dans les CSV de listes python
    IF position('""' IN clean_text) > 0 THEN
        clean_text := replace(clean_text, '""', '"');
    END IF;

    -- Remplacer les quotes simples facon Python par des doubles pour parser en JSON
    IF left(clean_text, 2) = '[''' THEN
         clean_text := replace(clean_text, '''', '"');
    END IF;
    
    IF left(clean_text, 1) = '[' AND position('''' IN clean_text) > 0 AND position('"' IN clean_text) = 0 THEN
         clean_text := replace(clean_text, '''', '"');
    END IF;

    -- Si cela ressemble a du JSON on le parse
    BEGIN
        RETURN ARRAY(SELECT jsonb_array_elements_text(clean_text::jsonb));
    EXCEPTION WHEN OTHERS THEN
        -- Retire crochets et guillemets
        RETURN string_to_array(replace(replace(replace(trim(both '[]' from p_text), '''', ''), '"', ''), ', ', ','), ',');
    END;
END;
$$ LANGUAGE plpgsql;

-- 2. Table de correspondance id -> uuid
CREATE TEMP TABLE _legacy_id_map (
    table_name TEXT,
    old_id TEXT,
    new_uuid UUID
);
CREATE INDEX idx_legacy_map ON _legacy_id_map(table_name, old_id);
