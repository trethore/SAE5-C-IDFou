from typing import Tuple, Dict, List
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import StandardScaler
from scipy.sparse import csr_matrix


def prepare_features(tracks_df: pd.DataFrame) -> Tuple[Dict[str, object], List[str], Dict]:
    
    if tracks_df.empty:
        return {}, [], {}

    df = tracks_df.copy()

    if 'track_id' not in df.columns:
        raise ValueError('tracks_df must contain track_id')

    df = df.set_index('track_id')

    feature_matrices = {}
    preprocessors = {}

    # Text fields
    def fit_vector(col):
        if col not in df.columns:
            return None
        texts = df[col].fillna('').astype(str).str.lower().str.strip()
        vec = CountVectorizer(binary=True)
        mat = vec.fit_transform(texts)
        return vec, mat

    print('  Vectorizing genres...')
    preprocessors['vec_genres'], feature_matrices['genres'] = fit_vector('genres')

    print('  Vectorizing tags...')
    preprocessors['vec_tags'], feature_matrices['tags'] = fit_vector('tags')

    print('  Vectorizing artists...')
    preprocessors['vec_artists'], feature_matrices['artists'] = fit_vector('artists')

    if 'album_title' in df.columns:
        print('  Vectorizing albums...')
        preprocessors['vec_albums'], feature_matrices['albums'] = fit_vector('album_title')
    else:
        preprocessors['vec_albums'] = None
        feature_matrices['albums'] = None

    if 'track_title' in df.columns:
        print('  Vectorizing titles...')
        preprocessors['vec_titles'], feature_matrices['titles'] = fit_vector('track_title')
    else:
        preprocessors['vec_titles'] = None
        feature_matrices['titles'] = None

    # Audio numeric fields
    audio_cols = [c for c in ['acousticness','danceability','energy','instrumentalness','liveness','speechiness','tempo','valence'] if c in df.columns]
    preprocessors['numeric_cols'] = audio_cols

    if audio_cols:
        numeric = df[audio_cols].fillna(0).astype(float)
        print(f'  Scaling {len(audio_cols)} audio features...')
        scaler = StandardScaler()
        scaled = scaler.fit_transform(numeric)
        feature_matrices['audio'] = csr_matrix(scaled)
        preprocessors['audio_scaler'] = scaler
    else:
        preprocessors['audio_scaler'] = None
        feature_matrices['audio'] = csr_matrix((len(df), 0))

    return feature_matrices, list(df.index), preprocessors


def transform_single_track(payload: dict, preprocessors: Dict):
   
    comps = {}

    def _transform_text(vec_key, payload_key):
        vec = preprocessors.get(vec_key)
        if vec is None:
            return None
        text = str(payload.get(payload_key, '')).lower().strip()
        return vec.transform([text])

    comps['genres'] = _transform_text('vec_genres', 'genres')
    comps['tags'] = _transform_text('vec_tags', 'tags')
    comps['artists'] = _transform_text('vec_artists', 'artists')
    comps['albums'] = _transform_text('vec_albums', 'album_title')
    comps['titles'] = _transform_text('vec_titles', 'track_title')

    numeric_cols = preprocessors.get('numeric_cols', [])
    if numeric_cols and preprocessors.get('audio_scaler') is not None:
        values = [payload.get(c, 0.0) for c in numeric_cols]
        arr = np.array(values).reshape(1, -1)
        scaled = preprocessors['audio_scaler'].transform(arr)
        comps['audio'] = csr_matrix(scaled)
    else:
        comps['audio'] = csr_matrix((1, 0))

    return comps
