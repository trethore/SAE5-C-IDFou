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
    # Now returns a dict of matrices and the index
    feature_matrices, track_index = prepare_features(tracks_df)
    
    if not feature_matrices:
        print("Failed to prepare features.")
        return []

    # Map track_id to matrix index
    id_to_idx = {tid: i for i, tid in enumerate(track_index)}
    tracks_index_list = list(track_index)
    
    if 'track_id' in tracks_df.columns:
        tracks_df = tracks_df.set_index('track_id')
        
    # 3. Create User Profile & Compute Similarity per Component
    print("Computing similarities per component...")
    
    # Define components to use for Mk1 (Text/Metadata only)
    components = ['genres', 'tags', 'artists', 'albums', 'titles']
    valid_components = []
    
    # Store similarities for each component
    component_similarities = []
    
    # Identify user indices and weights once
    user_indices = []
    weights = []
    for tid, count in user_history.items():
        if tid in id_to_idx:
            user_indices.append(id_to_idx[tid])
            weights.append(count)
            
    if not user_indices:
        print("None of the user's listened tracks are in the features database.")
        return []
        
    # Normalize weights
    weights = np.array(weights)
    weights = weights / weights.sum()
    
    for comp in components:
        matrix = feature_matrices.get(comp)
        if matrix is None:
            continue
            
        print(f"  Processing {comp}...")
        
        # Get user vectors for this component
        user_track_vectors = matrix[user_indices]
        
        # Weighted Average Profile
        # sparse matrix * weights requires conversion or dot product
        # user_track_vectors is (n_samples, n_features)
        # weights is (n_samples,)
        # We want (1, n_features)
        
        # Safe dot product for sparse
        user_profile = user_track_vectors.T.dot(weights) # result is (n_features,)
        user_profile = user_profile.reshape(1, -1)
        
        # Compute Cosine Similarity
        # (1, F) vs (N, F) -> (1, N)
        sim = cosine_similarity(user_profile, matrix).flatten()
        component_similarities.append(sim)
        valid_components.append(comp)

    if not component_similarities:
        print("No valid feature components found.")
        return []
        
    # 4. Average Similarity
    print(f"Averaging scores from: {', '.join(valid_components)}")
    final_similarity = np.mean(component_similarities, axis=0) # Average across components
    
    # 5. Rank and Filter
    sorted_indices = final_similarity.argsort()[::-1]
    
    recommendations = []
    count = 0
    
    for idx in sorted_indices:
        track_id = tracks_index_list[idx]
        
        # Filter: Exclude tracks already listened to
        if track_id in listened_track_ids:
            continue
            
        score = final_similarity[idx]
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
