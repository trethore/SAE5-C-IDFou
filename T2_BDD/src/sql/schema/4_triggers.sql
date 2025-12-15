-- ====================================================================================
-- TRIGGERS
-- ====================================================================================

CREATE TRIGGER tr_track_before_insert_create_album_if_null
BEFORE INSERT ON track
FOR EACH ROW
EXECUTE FUNCTION f_track_before_insert_create_album_if_null();

CREATE TRIGGER tr_track_after_insert_postcreate
AFTER INSERT ON track
FOR EACH ROW
EXECUTE FUNCTION f_track_after_insert_postcreate();

CREATE TRIGGER tr_track_before_delete_cleanup
BEFORE DELETE ON track
FOR EACH ROW
EXECUTE FUNCTION f_track_before_delete_cleanup();

CREATE TRIGGER tr_prevent_album_delete
BEFORE DELETE ON album
FOR EACH ROW
EXECUTE FUNCTION f_prevent_album_delete_if_tracks();

CREATE TRIGGER tr_inc_track_favorites
AFTER INSERT ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_inc_track_favorites_on_like();

CREATE TRIGGER tr_dec_track_favorites
AFTER DELETE ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_dec_track_favorites_on_unlike();

CREATE TRIGGER tr_inc_track_listens
AFTER INSERT ON track_user_listen
FOR EACH ROW
EXECUTE FUNCTION f_inc_track_listens_on_listen();

CREATE TRIGGER tr_inc_track_comments
AFTER INSERT ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_inc_track_comments_on_comment();

CREATE TRIGGER tr_dec_track_comments
AFTER DELETE ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_dec_track_comments_on_comment_delete();

CREATE TRIGGER tr_create_playlist_if_none
AFTER INSERT ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_create_playlist_if_none_for_user();

CREATE TRIGGER tr_auto_create_rank_artist
AFTER INSERT ON artist
FOR EACH ROW
EXECUTE FUNCTION f_auto_create_rank_artist();

CREATE TRIGGER tr_after_insert_track_artist_main
AFTER INSERT ON track_artist_main
FOR EACH ROW
EXECUTE FUNCTION f_after_track_artist_main_change();

CREATE TRIGGER tr_after_delete_track_artist_main
AFTER DELETE ON track_artist_main
FOR EACH ROW
EXECUTE FUNCTION f_after_delete_track_artist_main();

CREATE TRIGGER tr_after_insert_track_artist_feat
AFTER INSERT ON track_artist_feat
FOR EACH ROW
EXECUTE FUNCTION f_after_track_artist_feat_change();

CREATE TRIGGER tr_after_delete_track_artist_feat
AFTER DELETE ON track_artist_feat
FOR EACH ROW
EXECUTE FUNCTION f_after_delete_track_artist_feat();

CREATE TRIGGER tr_after_like_insert_recompute_artists
AFTER INSERT ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_after_like_change_recompute_artists();

CREATE TRIGGER tr_after_like_delete_recompute_artists
AFTER DELETE ON track_user_like
FOR EACH ROW
EXECUTE FUNCTION f_after_like_change_recompute_artists();

CREATE TRIGGER tr_after_comment_insert_recompute_artists
AFTER INSERT ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_after_comment_change_recompute_artists();

CREATE TRIGGER tr_after_comment_delete_recompute_artists
AFTER DELETE ON track_comment
FOR EACH ROW
EXECUTE FUNCTION f_after_comment_change_recompute_artists();

CREATE TRIGGER trg_ensure_artist_account
BEFORE INSERT ON artist
FOR EACH ROW
EXECUTE FUNCTION ensure_artist_account();
