import argparse
import json
from .item_based_audio_mk2 import recommend_for_track

def main():
    parser = argparse.ArgumentParser(description='Item-based recommender (v2 - MK2)')
    
    # Choix exclusif : track-id, track-id-file, track-file
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--track-id', help='Existing track id to base recommendations on')
    group.add_argument('--track-id-file', help='Text file containing a track UUID (first line)')
    group.add_argument('--track-file', help='JSON file describing a single track payload')
    
    # Paramètres généraux
    parser.add_argument('--n', type=int, default=10, help='Number of recommendations')
    parser.add_argument('--audio-weight', type=float, default=0.5, help='Weight of audio similarity (0–1)')
    parser.add_argument('--random-noise', type=float, default=0.0, help='Std dev of Gaussian noise added to scores')
    parser.add_argument('--random-seed', type=int, help='Random seed for reproducibility')
    
    args = parser.parse_args()

    # Appel correct de MK2 avec tous les paramètres
    if args.track_id:
        recs = recommend_for_track(
            args.track_id,
            args.n,
            audio_weight=args.audio_weight,
            random_noise=args.random_noise,
            random_seed=args.random_seed
        )
    elif args.track_id_file:
        with open(args.track_id_file, 'r') as fh:
            for line in fh:
                tid = line.strip()
                if tid:
                    break
            else:
                raise ValueError('No track id found in file')
        recs = recommend_for_track(
            tid,
            args.n,
            audio_weight=args.audio_weight,
            random_noise=args.random_noise,
            random_seed=args.random_seed
        )
    else:
        with open(args.track_file, 'r') as fh:
            payload = json.load(fh)
        recs = recommend_for_track(
            payload,
            args.n,
            audio_weight=args.audio_weight,
            random_noise=args.random_noise,
            random_seed=args.random_seed
        )

    print('\nTop recommendations:')
    for i, r in enumerate(recs, 1):
        print(f"{i}. {r['title']} (by {r.get('artists')}) - score: {r['score']:.4f}")


if __name__ == '__main__':
    main()
