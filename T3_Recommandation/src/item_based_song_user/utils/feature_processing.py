import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix

def prepare_features(tracks_df):
    """
    Processes the raw tracks DataFrame into a dictionary of feature matrices.
    
    Args:
        tracks_df (pd.DataFrame): DataFrame containing track data. 
                                  Must have 'track_id', 'track_title', 'genres', 'tags', 'artists', 'album_title' columns 
                                  and numeric temporal features.
    
    Returns:
        tuple: (feature_matrices (dict), track_ids (list/index))
               feature_matrices dict keys: 'genres', 'tags', 'artists', 'albums', 'titles', 'audio'
    """
    if tracks_df.empty:
        return {}, []

    # Ensure track_id is identifying the rows
    df = tracks_df.set_index('track_id')
    
    feature_matrices = {}
    
    # Helper to vectorize text
    def vectorize_text(column_name, data):
        # FillNa and basic cleanup
        text_data = data.fillna('').astype(str).str.lower().str.strip()
        # Use simple TF-IDF
        tfidf = TfidfVectorizer(stop_words='english', min_df=1) # min_df=1 because some attributes might be rare but exact matches matter (e.g. unique album)
        return tfidf.fit_transform(text_data)

    # 1. Textual Features (Independent)
    print("  Vectorizing Genres...")
    feature_matrices['genres'] = vectorize_text('genres', df['genres'])
    
    print("  Vectorizing Tags...")
    feature_matrices['tags'] = vectorize_text('tags', df['tags'])
    
    print("  Vectorizing Artists...")
    feature_matrices['artists'] = vectorize_text('artists', df['artists'])
    
    # Check if album_title and track_title exist (support partial data if needed, but they should be there)
    if 'album_title' in df.columns:
        print("  Vectorizing Albums...")
        feature_matrices['albums'] = vectorize_text('album_title', df['album_title'])
    else:
        feature_matrices['albums'] = None
        
    if 'track_title' in df.columns:
        print("  Vectorizing Titles...")
        feature_matrices['titles'] = vectorize_text('track_title', df['track_title'])
    else:
        feature_matrices['titles'] = None
    
    # 2. Numeric Features (Audio)
    # Exclude metadata columns to isolate numeric
    metadata_cols = ['track_title', 'genres', 'tags', 'artists', 'album_title']
    numeric_df = df.drop(columns=[c for c in metadata_cols if c in df.columns])
    
    # Identify numeric columns
    numeric_cols = numeric_df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        # Try to infer objects if they are numbers
        numeric_df = numeric_df.apply(pd.to_numeric, errors='coerce')
        numeric_cols = numeric_df.select_dtypes(include=[np.number]).columns
        
    numeric_data = numeric_df[numeric_cols].fillna(0)
    
    if len(numeric_cols) > 0:
        print(f"  Scaling {len(numeric_cols)} Audio Features...")
        scaler = StandardScaler()
        # Create sparse matrix from audio features for consistency
        feature_matrices['audio'] = csr_matrix(scaler.fit_transform(numeric_data))
    else:
        print("  WARNING: No numeric features found. using empty matrix for audio.")
        feature_matrices['audio'] = csr_matrix((len(df), 0))

    return feature_matrices, df.index
