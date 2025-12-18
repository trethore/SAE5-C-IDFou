"""Item-based recommender (v2) - MK1 (original implementation).

Scoring: compute cosine similarity for each textual component vs. user profile
and audio similarity; final score = 0.5*audio + 0.5*mean(text components).
"""
from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .utils.data_loader import get_all_tracks_data
from .utils.feature_processing import prepare_features, transform_single_track


def recommend_for_track(payload_or_track_id: object, n: int = 10) -> List[Dict]:
    """Given a payload dict describing a single track or a track_id present in DB, return recs."""
    df = get_all_tracks_data()
    if df.empty:
        return []

    matrices, track_index, preprocessors = prepare_features(df)
    df_indexed = df.set_index('track_id')

    # if given a track id string and it exists in df
    single = None
    input_id = None
    if isinstance(payload_or_track_id, str):
        if payload_or_track_id in df_indexed.index:
            row = df_indexed.loc[payload_or_track_id]
            payload = {
                'genres': row.get('genres', ''), 'tags': row.get('tags', ''), 'artists': row.get('artists', ''),
                'album_title': row.get('album_title', ''), 'track_title': row.get('track_title', '')
            }
            # include audio numeric values
            for c in preprocessors.get('numeric_cols', []):
                payload[c] = row.get(c, 0.0)
            input_id = payload_or_track_id
            single = transform_single_track(payload, preprocessors)
        else:
            # treat it as JSON path or external id — user should pass payload dict instead
            raise ValueError('Track id not found in data. Provide dict payload to recommend for a custom track.')
    elif isinstance(payload_or_track_id, dict):
        single = transform_single_track(payload_or_track_id, preprocessors)
    else:
        raise TypeError('payload_or_track_id must be track_id string or dict payload')

    # Compute per-component similarities of single -> all tracks
    comps = ['genres', 'tags', 'artists', 'albums', 'titles']
    text_sims = []
    for comp in comps:
        vec = single.get(comp)
        mat = matrices.get(comp)
        if vec is None or mat is None:
            continue
        sim = cosine_similarity(vec, mat).flatten()
        text_sims.append(sim)

    if not text_sims:
        mean_text = np.zeros(len(track_index))
    else:
        mean_text = np.mean(np.vstack(text_sims), axis=0)

    # audio
    audio_vec = single.get('audio')
    audio_mat = matrices.get('audio')
    if audio_mat is None or audio_mat.shape[1] == 0 or audio_vec.shape[1] == 0:
        audio_sim = np.zeros(len(track_index))
    else:
        a_dense = audio_mat.toarray() if hasattr(audio_mat, 'toarray') else audio_mat
        v_dense = audio_vec.toarray() if hasattr(audio_vec, 'toarray') else audio_vec
        audio_sim = cosine_similarity(v_dense, a_dense).flatten()

    final = 0.5 * audio_sim + 0.5 * mean_text

    # If recommending for existing track id, exclude itself
    sorted_idx = np.argsort(final)[::-1]
    recs = []
    count = 0

    for idx in sorted_idx:
        tid = track_index[idx]
        if input_id and tid == input_id:
            continue
        row = df_indexed.loc[tid]
        recs.append({'track_id': tid, 'title': row.get('track_title', ''), 'artists': row.get('artists', ''), 'score': float(final[idx])})
        count += 1
        if count >= n:
            break

    return recs
