-- ====================================================================================
-- FONCTIONS
-- ====================================================================================

/*
  Fonction pour incrementer album_tracks_count
*/
CREATE OR REPLACE FUNCTION f_inc_album_tracks_count(p_album_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE album
  SET album_tracks_count = COALESCE(album_tracks_count,0) + 1
  WHERE album_id = p_album_id;
END;
$$ LANGUAGE plpgsql;

/*
  Fonction pour decrementer album_tracks_count
*/
CREATE OR REPLACE FUNCTION f_dec_album_tracks_count(p_album_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE album
  SET album_tracks_count = GREATEST(COALESCE(album_tracks_count,0) - 1, 0)
  WHERE album_id = p_album_id;
END;
$$ LANGUAGE plpgsql;

/*
  Apres INSERT track -> si album_id NULL creer un album et definir NEW.album_id
                puis incrementer album_tracks_count.
*/
CREATE OR REPLACE FUNCTION f_track_before_insert_create_album_if_null()
RETURNS trigger AS $$
DECLARE created_album_id UUID;
BEGIN
  IF NEW.album_id IS NULL THEN
    INSERT INTO album(album_title, album_type, album_tracks_count, album_date_released)
    VALUES (COALESCE(NEW.track_title, 'Untitled') || ' - Single', 'single', 1, COALESCE(NEW.track_date_created, CURRENT_DATE))
    RETURNING album_id INTO created_album_id;

    NEW.album_id := created_album_id;
    -- definir les compteurs
    NEW.track_listens := COALESCE(NEW.track_listens, 0);
    NEW.track_favorites := COALESCE(NEW.track_favorites, 0);
    NEW.track_comments := COALESCE(NEW.track_comments, 0);
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_track_after_insert_postcreate()
RETURNS trigger AS $$
BEGIN
  IF NEW.album_id IS NOT NULL THEN
    PERFORM f_inc_album_tracks_count(NEW.album_id);
  END IF;

  INSERT INTO rank_track(track_id, rank_song_currency, rank_song_hotttnesss)
  VALUES (NEW.track_id, 0, 0);

  INSERT INTO audio_feature(track_id) VALUES (NEW.track_id)
  ON CONFLICT (track_id) DO NOTHING;

  INSERT INTO temporal_feature(track_id) VALUES (NEW.track_id)
  ON CONFLICT (track_id) DO NOTHING;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_track_before_delete_cleanup()
RETURNS trigger AS $$
BEGIN
    -- Supprimer toutes les dépendances
    DELETE FROM track_artist_main WHERE track_id = OLD.track_id;
    DELETE FROM track_artist_feat WHERE track_id = OLD.track_id;
    DELETE FROM track_license WHERE track_id = OLD.track_id;
    DELETE FROM track_genre WHERE track_id = OLD.track_id;
    DELETE FROM track_tag WHERE track_id = OLD.track_id;
    DELETE FROM playlist_track WHERE track_id = OLD.track_id;
    DELETE FROM track_user_like WHERE track_id = OLD.track_id;
    DELETE FROM track_user_listen WHERE track_id = OLD.track_id;
    DELETE FROM track_comment WHERE track_id = OLD.track_id;
    DELETE FROM rank_track WHERE track_id = OLD.track_id;
    DELETE FROM audio_feature WHERE track_id = OLD.track_id;
    DELETE FROM temporal_feature WHERE track_id = OLD.track_id;

    -- Décrémenter album_tracks_count
    IF OLD.album_id IS NOT NULL THEN
        PERFORM f_dec_album_tracks_count(OLD.album_id);
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

/*
  On empeche la suppression d'un album s'il contient des pistes
*/
CREATE OR REPLACE FUNCTION f_prevent_album_delete_if_tracks()
RETURNS trigger AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM track WHERE album_id = OLD.album_id) THEN
    RAISE EXCEPTION 'Impossible de supprimer l''album % : il contient des tracks.', OLD.album_id;
  END IF;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

/*
  Lorsque track_user_like est insere/supprime, on met a jour track.track_favorites
*/
CREATE OR REPLACE FUNCTION f_inc_track_favorites_on_like()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_favorites = COALESCE(track_favorites,0) + 1 WHERE track_id = NEW.track_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_dec_track_favorites_on_unlike()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_favorites = GREATEST(COALESCE(track_favorites,0) - 1, 0) WHERE track_id = OLD.track_id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

/*
  Incremente track.track_listens quand on insere une ecoute
*/
CREATE OR REPLACE FUNCTION f_inc_track_listens_on_listen()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_listens = COALESCE(track_listens,0) + 1 WHERE track_id = NEW.track_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/*
  Insert/delete dans track_comment met a jour track.track_comments
*/
CREATE OR REPLACE FUNCTION f_inc_track_comments_on_comment()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_comments = COALESCE(track_comments,0) + 1 WHERE track_id = NEW.track_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_dec_track_comments_on_comment_delete()
RETURNS trigger AS $$
BEGIN
  UPDATE track SET track_comments = GREATEST(COALESCE(track_comments,0) - 1,0) WHERE track_id = OLD.track_id;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

/*
  Creer automatiquement une playlist pour un user s'il n'en a aucune.
*/
CREATE OR REPLACE FUNCTION f_create_playlist_if_none_for_user()
RETURNS trigger AS $$
DECLARE p_id UUID;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM playlist_user WHERE account_id = NEW.account_id) THEN
    INSERT INTO playlist(playlist_name) VALUES ('My First Playlist') RETURNING playlist_id INTO p_id;
    INSERT INTO playlist_user(playlist_id, account_id) VALUES (p_id, NEW.account_id);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/*
  Creation automatique de rank_artist quand un artiste est ajoute
*/
CREATE OR REPLACE FUNCTION f_auto_create_rank_artist()
RETURNS trigger AS $$
BEGIN
  INSERT INTO rank_artist(artist_id, rank_artist_discovery, rank_artist_familiarity, rank_artist_hotttnesss)
  VALUES (NEW.artist_id, 0, 0, 0);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_recompute_artist_counters(p_artist_id UUID)
RETURNS void AS $$
DECLARE fav_sum BIGINT;
DECLARE com_sum BIGINT;
BEGIN
  -- somme des favorites des tracks où artist est main OR feat
  SELECT COALESCE(SUM(t.track_favorites),0) INTO fav_sum
  FROM track t
  WHERE EXISTS (SELECT 1 FROM track_artist_main tam WHERE tam.track_id = t.track_id AND tam.artist_id = p_artist_id)
     OR EXISTS (SELECT 1 FROM track_artist_feat taf WHERE taf.track_id = t.track_id AND taf.artist_id = p_artist_id);

  SELECT COALESCE(SUM(t.track_comments),0) INTO com_sum
  FROM track t
  WHERE EXISTS (SELECT 1 FROM track_artist_main tam WHERE tam.track_id = t.track_id AND tam.artist_id = p_artist_id)
     OR EXISTS (SELECT 1 FROM track_artist_feat taf WHERE taf.track_id = t.track_id AND taf.artist_id = p_artist_id);

  UPDATE artist
  SET artist_favorites = fav_sum,
      artist_comments = com_sum
  WHERE artist_id = p_artist_id;
END;
$$ LANGUAGE plpgsql;

/*
  Lorsqu'une relation track_artist_main / track_artist_feat change,
  ou lorsqu'un like/comment est inséré/supprimé sur un track, on recalculera l'artiste concerné.
*/
CREATE OR REPLACE FUNCTION f_after_track_artist_main_change()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(NEW.artist_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_after_delete_track_artist_main()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(OLD.artist_id);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- meme pour artistes invites
CREATE OR REPLACE FUNCTION f_after_track_artist_feat_change()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(NEW.artist_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_after_delete_track_artist_feat()
RETURNS trigger AS $$
BEGIN
  PERFORM f_recompute_artist_counters(OLD.artist_id);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- lorsque les likes/commentaires changent, recalculer les compteurs des artistes lies a la piste
CREATE OR REPLACE FUNCTION f_after_like_change_recompute_artists()
RETURNS trigger AS $$
DECLARE v_track UUID := NEW.track_id;
BEGIN
  -- trouver artistes main et feat pour ce track et refresh
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_main WHERE track_id = v_track;
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_feat WHERE track_id = v_track;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_after_comment_change_recompute_artists()
RETURNS trigger AS $$
DECLARE v_track UUID := NEW.track_id;
BEGIN
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_main WHERE track_id = v_track;
  PERFORM f_recompute_artist_counters(artist_id) FROM track_artist_feat WHERE track_id = v_track;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Fonction trigger
CREATE OR REPLACE FUNCTION ensure_artist_account()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifie si l'artist_id existe déjà dans account
    IF NOT EXISTS (SELECT 1 FROM account WHERE account_id = NEW.artist_id) THEN
        INSERT INTO account(account_id, login, email, name, created_at)
        VALUES (
            NEW.artist_id,
            'artist_' || NEW.artist_id::text,
            'artist_' || NEW.artist_id::text || '@example.com',  
            'Artist_' || NEW.artist_id::text, 
            CURRENT_TIMESTAMP
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ====================================================================================
-- Fonctions supplementaires
-- ====================================================================================

CREATE OR REPLACE FUNCTION increment_listen_count(p_account_id UUID, p_track_id UUID)
RETURNS VOID AS $$
BEGIN
    INSERT INTO track_user_listen (account_id, track_id, count)
    VALUES (p_account_id, p_track_id, 1)
    ON CONFLICT (track_id, account_id)
    DO UPDATE SET count = track_user_listen.count + 1;
END;
$$ LANGUAGE plpgsql;
