import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


def generate_correlation_heatmap(csv_path="../../../../data/merged_tracks.csv", 
                                  output_filename="heatmap_correlation.png"):
    """
    Generate a correlation heatmap from musical features and technical audio statistics.
    
    Args:
        csv_path (str): Path to the CSV file containing the data
        output_filename (str): Name of the output PNG file to save
    
    Returns:
        str: Path to the saved image file
    """
    
    # Liste des colonnes qui nous intéressent
    # Colonnes liées à la popularité et l'engagement + statistiques techniques audio
    colonnes_interessantes = [
        # Perceptual musical characteristics
        "energy",                  # Energy
        "acousticness",            # Acoustic character
        
        # Technical audio statistics (means)
        "mfcc_mean",               # MFCC (vocal/instrumental timbre)
        "spectral_centroid_mean",  # Spectral centroid (sound brightness)
        "spectral_bandwidth_mean", # Spectral bandwidth (harmonic richness)
        "spectral_rolloff_mean",   # Spectral rolloff (frequency distribution)
        "rmse_mean",               # RMS Energy (volume/power)
        "zcr_mean",                # Zero-crossing rate (percussive content)
        "chroma_stft_mean"         # Chroma STFT (tonal/harmonic content)
    ]
    
    # Charger le CSV
    df = pd.read_csv(csv_path)
    
    # Filtrer uniquement les colonnes qui nous intéressent
    df_filtered = df[colonnes_interessantes]
    
    # Vérifier que toutes les colonnes sont numériques
    colonnes_non_numeriques = []
    for col in colonnes_interessantes:
        if col not in df_filtered.columns:
            print(f"ERROR: Column '{col}' does not exist in the CSV!")
            exit(1)
        
        if not pd.api.types.is_numeric_dtype(df_filtered[col]):
            colonnes_non_numeriques.append(col)
    
    if colonnes_non_numeriques:
        print(f"ERROR: The following columns are not numeric (int or float):")
        for col in colonnes_non_numeriques:
            print(f"   - '{col}' (type: {df_filtered[col].dtype})")
        print("\n Correlation heatmap requires only numeric columns.")
        print("   Please modify the 'colonnes_interessantes' list to exclude these columns.")
        exit(1)
    
    print(f"All columns are numeric. Generating heatmap...")
    
    # Créer la matrice de corrélation
    correlation_matrix = df_filtered.corr()
    
    # Créer la heatmap
    plt.figure(figsize=(16, 14))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                fmt='.2f', square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                annot_kws={"size": 8})
    
    plt.title('Correlation Heatmap: Musical Features and Technical Audio Statistics', 
              fontsize=16, pad=20, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    
    # Sauvegarder la heatmap
    output_path = os.path.join('./', output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # Fermer la figure pour libérer la mémoire
    
    print(f"Heatmap saved successfully at: {output_path}")
    return output_path


# Point d'entrée principal
if __name__ == "__main__":
    generate_correlation_heatmap()

