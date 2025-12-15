import sys
import os
import argparse
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path to allow importing from utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # item_based_song_user
sys.path.append(parent_dir)

from utils.data_loader import get_user_listen_history, get_all_tracks_data
from utils.feature_processing import prepare_features
from utils.env_loader import load_env_file

def recommend_tracks(user_id, n_recommendations=10):
    load_env_file()
    print(f"Starting recommendation (Mk4 - Individual Feature Similarity) for User: {user_id}")
    
    # 1. Load Data
    print("Loading user history...")
    user_history = get_user_listen_history(user_id)
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
    
    # Mk4: Text Components + Individual Audio Features
    text_components = ['genres', 'tags', 'artists', 'albums', 'titles']
    
    # List to store all similarity arrays (1 per text component, 1 per audio feature)
    all_similarities = []
    valid_component_names = []
    
    # Identify user indices and weights
    user_indices = []
    weights = []
    for tid, count in user_history.items():
        if tid in id_to_idx:
            user_indices.append(id_to_idx[tid])
            weights.append(count)
            
    if not user_indices:
        print("None of the user's listened tracks are in the features database.")
        return []
        
    weights = np.array(weights)
    weights = weights / weights.sum()
    
    # A. Process Text Components
    print("  Processing Text Components...")
    for comp in text_components:
        matrix = feature_matrices.get(comp)
        if matrix is None:
            continue
            
        # Get user vectors for this component
        user_track_vectors = matrix[user_indices]
        
        try:
            # Weighted Profile
            if hasattr(user_track_vectors, 'toarray') or hasattr(user_track_vectors, 'dot'):
                 user_profile = user_track_vectors.T.dot(weights)
            else:
                 user_profile = np.average(user_track_vectors, axis=0, weights=weights)
                 
            user_profile = user_profile.reshape(1, -1)
            
            # Similarity
            sim = cosine_similarity(user_profile, matrix).flatten()
            all_similarities.append(sim)
            valid_component_names.append(comp)
            
        except Exception as e:
            print(f"    Error processing {comp}: {e}")
            continue

    # B. Process Individual Audio Features
    print("  Processing Individual Audio Features...")
    if 'audio' in feature_matrices:
        audio_matrix = feature_matrices['audio']
        
        # Convert to dense for easier column iteration (assumption: metrics fit in memory)
        # 100k rows * 300 cols * 8 bytes ~ 240MB. Should be fine.
        if hasattr(audio_matrix, 'toarray'):
            audio_dense = audio_matrix.toarray()
        else:
            audio_dense = audio_matrix
            
        n_features = audio_dense.shape[1]
        print(f"    Iterating over {n_features} audio dimensions...")
        
        for i in range(n_features):
            # Extract column i: shape (N,)
            col_data = audio_dense[:, i]
            
            # User profile for this specific feature (Weighted Average)
            user_vals = col_data[user_indices]
            # user_profile_val is a scalar
            user_profile_val = np.average(user_vals, weights=weights)
            if user_profile_val == 0:
                sim = np.zeros(len(col_data))
            else:
                # Reshape for sklearn: (1, 1) and (N, 1)
                u_vec = np.array([[user_profile_val]])
                c_vecs = col_data.reshape(-1, 1)
                
                sim = cosine_similarity(u_vec, c_vecs).flatten()
                
            all_similarities.append(sim)
            valid_component_names.append(f"audio_{i}")

    if not all_similarities:
        print("No valid feature components found.")
        return []
        
    print(f"Averaging scores from {len(all_similarities)} components...")
    
    # 4. Average Similarity
    # Stack arrays: (n_components, n_tracks)
    stacked_sims = np.vstack(all_similarities)
    final_similarity = np.mean(stacked_sims, axis=0) # Average across components
    
    # Mk3 Logic: Add Random Noise
    print("Adding random variation (Mk3 style)...")
    noise = np.random.uniform(low=0.0, high=0.05, size=final_similarity.shape)
    final_similarity = final_similarity + noise
    
    # 5. Rank and Filter
    sorted_indices = final_similarity.argsort()[::-1]
    
    recommendations = []
    count = 0
    
    for idx in sorted_indices:
        track_id = tracks_index_list[idx]
        
        if track_id in listened_track_ids:
            continue
            
        score = final_similarity[idx]
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
    parser = argparse.ArgumentParser(description="Item-Based Music Recommendation Mk4 (Individual Audio Features)")
    parser.add_argument("user_id", type=str, help="UUID of the user")
    parser.add_argument("--n", type=int, default=10, help="Number of recommendations")
    
    args = parser.parse_args()
    
    try:
        recs = recommend_tracks(args.user_id, args.n)
        
        print("\n" + "="*50)
        print(f"Top {len(recs)} Recommendations (Mk4) for User {args.user_id}")
        print("="*50)
        
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec['title']} (by {rec['artist']}) - Score: {rec['score']:.4f}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
