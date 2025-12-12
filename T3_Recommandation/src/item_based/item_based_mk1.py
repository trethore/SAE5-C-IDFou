import sys
import os
import argparse
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path to allow importing from utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.data_loader import get_user_listen_history, get_all_tracks_data
from utils.feature_processing import prepare_features
from utils.env_loader import load_env_file

def recommend_tracks(user_id, n_recommendations=10):
    load_env_file()
    print(f"Starting recommendation for User: {user_id}")
    
    # 1. Load Data
    print("Loading user history...")
    user_history = get_user_listen_history(user_id) # returns dict {track_id: count}
    listened_track_ids = set(user_history.keys())
    print(f"User has listened to {len(listened_track_ids)} tracks.")
    
    if not listened_track_ids:
        print("User has no listening history. Cannot compute item-based recommendations.")
        return []

    print("Loading all tracks data...")
    tracks_df = get_all_tracks_data()
    print(f"Loaded {len(tracks_df)} tracks from database.")
    
    if tracks_df.empty:
        print("No tracks found in database.")
        return []
        
    # 2. Prepare Features
    print("Vectorizing features...")
    feature_matrix, track_index = prepare_features(tracks_df)
    
    if feature_matrix is None:
        print("Failed to prepare features.")
        return []

    # Now set_index for lookups
    if 'track_id' in tracks_df.columns:
        tracks_df = tracks_df.set_index('track_id')

    # Map track_id to matrix index
    # track_index is the index of tracks_df (which we set to track_id in prepare_features)
    # create a map from track_id -> integer index in matrix
    id_to_idx = {tid: i for i, tid in enumerate(track_index)}
    tracks_index_list = list(track_index) # track_ids in order of the matrix rows
    
    # 3. Create User Profile
    print("Creating user profile...")
    user_indices = []
    weights = []
    
    for tid, count in user_history.items():
        if tid in id_to_idx:
            idx = id_to_idx[tid]
            user_indices.append(idx)
            weights.append(count)
            
    if not user_indices:
        print("None of the user's listened tracks are in the features database (inconsistant data?).")
        return []
    
    # Extract vectors for user tracks
    user_track_vectors = feature_matrix[user_indices]
    
    # Compute Weighted Average Vector
    # (n_samples, n_features) -> (1, n_features)
    # Average weighted by listen counts
    if weights:
        # Normalize weights to sum to 1
        weights = np.array(weights)
        weights = weights / weights.sum()
        # Reshape for broadcasting usually needed, but average takes weights
        user_profile = np.average(user_track_vectors.toarray(), axis=0, weights=weights)
    else:
        user_profile = np.mean(user_track_vectors.toarray(), axis=0)
        
    user_profile = user_profile.reshape(1, -1)
    
    # 4. Compute Similarity
    print("Computing similarities...")
    # metrics.pairwise.cosine_similarity(X, Y)
    # X = User Profile (1, F), Y = All Tracks (N, F)
    # Result = (1, N)
    similarities = cosine_similarity(user_profile, feature_matrix)
    similarities = similarities.flatten() # (N,) array of scores
    
    # 5. Rank and Filter
    # Get indices of top sorted elements
    # We want descending order
    sorted_indices = similarities.argsort()[::-1]
    
    recommendations = []
    count = 0
    
    for idx in sorted_indices:
        track_id = tracks_index_list[idx]
        
        # Filter: Exclude tracks already listened to
        if track_id in listened_track_ids:
            continue
            
        score = similarities[idx]
        # Retrieve metadata
        # tracks_df index is track_id
        track_info = tracks_df.loc[track_id]
        
        rec = {
            'track_id': track_id,
            'title': track_info['track_title'],
            'artist': track_info['artists'],
            'score': float(score)
        }
        recommendations.append(rec)
        count += 1
        
        if count >= n_recommendations:
            break
            
    return recommendations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Item-Based Music Recommendation Mk1")
    parser.add_argument("user_id", type=str, help="UUID of the user")
    parser.add_argument("--n", type=int, default=10, help="Number of recommendations")
    
    args = parser.parse_args()
    
    try:
        recs = recommend_tracks(args.user_id, args.n)
        
        print("\n" + "="*50)
        print(f"Top {len(recs)} Recommendations for User {args.user_id}")
        print("="*50)
        
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec['title']} (by {rec['artist']}) - Score: {rec['score']:.4f}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
