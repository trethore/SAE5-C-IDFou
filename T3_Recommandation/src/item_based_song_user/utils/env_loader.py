import os

def load_env_file():
    """
    Loads environment variables from .env file located in the project root.
    Project root is assumed to be 3 levels up from this file (src/utils/env_loader.py).
    """
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) # utils
    item_based_dir = os.path.dirname(current_dir) # item_based_song_user
    src_dir = os.path.dirname(item_based_dir) # src
    t3_dir = os.path.dirname(src_dir) # T3_Recommandation
    project_root = os.path.dirname(t3_dir) # SAE5-C-IDFou (Root)
    
    env_path = os.path.join(project_root, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip().strip("'").strip('"')
                    os.environ[key.strip()] = value
