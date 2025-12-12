import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

def prepare_features(tracks_df):
    """
    Processes the raw tracks DataFrame into a feature matrix suitable for similarity calculation.
    
    Args:
        tracks_df (pd.DataFrame): DataFrame containing track data. 
                                  Must have 'track_id', 'genres', 'tags', 'artists' columns 
                                  and numeric temporal features.
    
    Returns:
        tuple: (feature_matrix (sparse matrix), track_ids (list/index))
    """
    if tracks_df.empty:
        return None, []

    # Ensure track_id is identifying the rows
    df = tracks_df.set_index('track_id')
    
    # 1. Textual Features
    # Combine genres, tags, artists into a single text document per track
    # We strip and lower case to ensure consistency
    text_data = (
        df['genres'].fillna('') + " " + 
        df['tags'].fillna('') + " " + 
        df['artists'].fillna('')
    ).str.lower().str.strip()

    tfidf = TfidfVectorizer(stop_words='english', min_df=2)
    text_features = tfidf.fit_transform(text_data)
    
    # 2. Numeric Features (Temporal Features)
    # Exclude metadata columns
    metadata_cols = ['track_title', 'genres', 'tags', 'artists']
    # Also exclude track_id if it's still a column (though we set_index)
    numeric_df = df.drop(columns=[c for c in metadata_cols if c in df.columns])
    
    # Identify numeric columns (should be all remaining, but safety check)
    numeric_cols = numeric_df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        # Try to infer objects if they are numbers
        numeric_df = numeric_df.apply(pd.to_numeric, errors='coerce')
        numeric_cols = numeric_df.select_dtypes(include=[np.number]).columns
        
    numeric_data = numeric_df[numeric_cols]
    
    # Handle NaN values - simple imputation with 0 or mean. 
    # For audio features, 0 might be wrong (e.g. tempo 0), but for coefficients, mean or 0 is standard.
    # Let's use 0 for simplicity as missing usually implies silence or error in extraction.
    numeric_data = numeric_data.fillna(0)
    
    
    if len(numeric_cols) > 0:
        scaler = StandardScaler()
        numeric_features = scaler.fit_transform(numeric_data)
    else:
        print("WARNING: No numeric features found. using empty matrix.")
        from scipy.sparse import csr_matrix
        numeric_features = csr_matrix((len(df), 0))

    # 3. Combine Features
    
    # 3. Combine Features
    
    final_features = hstack([text_features, numeric_features])
    
    return final_features.tocsr(), df.index
