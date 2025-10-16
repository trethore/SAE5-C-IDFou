#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CSV_PATH = (ROOT / "cleaned_data/merged_tracks.csv").resolve()
OUT_DIR = (HERE / "out").resolve()
PREFERRED_PATTERNS = [
    "energy",
    "danceability",
    "valence",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "tempo",
]



def ensure_outdir() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data(path: Path) -> pd.DataFrame:
    print(f"Lecture du CSV: {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"Shape brut: {df.shape}")
    return df


def pick_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    # Variable catégorielle pour colorier les individus
    cat = df.get("track_genre_top")
    # Exclure identifiants évidents
    drop_like = {"track_id", "album_id", "artist_id"}
    cols = [c for c in df.columns if c not in drop_like]

    # Garder uniquement les colonnes numériques
    num = df[cols].select_dtypes(include=[np.number]).copy()
    preferred_available = [col for col in PREFERRED_PATTERNS if col in num.columns]
    missing = sorted(set(PREFERRED_PATTERNS) - set(preferred_available))
    if missing:
        print(f"Colonnes préférées absentes et ignorées: {missing}")

    if not preferred_available:
        raise ValueError("Aucune des colonnes préférées n'est disponible pour l'ACP.")

    num = num[preferred_available]
    print(f"Variables numériques retenues: {len(preferred_available)} / {len(PREFERRED_PATTERNS)}")
    return num, cat


def standardize_impute(X: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    # Imputation médiane pour éviter le carnage des NaN
    imputer = SimpleImputer(strategy="median")
    X_imp = imputer.fit_transform(X.values)

    scaler = StandardScaler(with_mean=True, with_std=True)
    X_std = scaler.fit_transform(X_imp)

    features = list(X.columns)
    return X_std, features


def optimize_feature_subset(X: pd.DataFrame, target_ratio: float = 0.5, min_features: int = 4) -> pd.DataFrame:
    if X.empty:
        raise ValueError("Le DataFrame de travail est vide, impossible de poursuivre l'ACP.")

    valid_columns = [col for col in X.columns if X[col].notna().any()]
    dropped = sorted(set(X.columns) - set(valid_columns))
    if dropped:
        print(f"Colonnes sans observations supprimées: {dropped}")
    remaining = valid_columns

    if len(remaining) < min_features:
        print("Trop peu de variables pour appliquer une sélection dynamique, utilisation de toutes les variables restantes.")
        return X[remaining]

    best_cols = remaining.copy()
    best_ratio = -np.inf

    # Utiliser un remplissage médian pour évaluer les corrélations sans déformer la structure
    filled = X[remaining].copy()
    medians = filled.median(numeric_only=True)
    filled = filled.fillna(medians)

    while len(remaining) >= min_features:
        X_subset = filled[remaining]
        X_std, _ = standardize_impute(X_subset)
        pca = run_pca(X_std, max_components=min(10, X_subset.shape[1]))
        ratio12 = float(np.sum(pca.explained_variance_ratio_[:2]))
        print(f"Essai avec {len(remaining)} variables (Dim1+Dim2 = {ratio12*100:.2f}%) -> {remaining}")

        if ratio12 >= target_ratio:
            print(f"Objectif atteint: {ratio12*100:.2f}% de variance cumulée sur Dim1+Dim2.")
            return X[remaining]

        if ratio12 > best_ratio:
            best_ratio = ratio12
            best_cols = remaining.copy()

        corr = X_subset.corr().abs()
        if corr.isna().all().all():
            print("Corrélations non définies, arrêt de la sélection automatique.")
            break

        np.fill_diagonal(corr.values, np.nan)
        mean_corr = corr.mean(axis=0, skipna=True)
        drop_candidate = mean_corr.idxmin()
        print(f"Suppression de la variable la moins corrélée: {drop_candidate}")
        remaining = [col for col in remaining if col != drop_candidate]

    print(f"Objectif de {target_ratio*100:.0f}% non atteint, "
          f"utilisation du meilleur sous-ensemble ({len(best_cols)} variables -> {best_ratio*100:.2f}%).")
    return X[best_cols]


def run_pca(X_std: np.ndarray, max_components: int = 10) -> PCA:
    n_features = X_std.shape[1]
    n_components = min(max_components, n_features)
    pca = PCA(n_components=n_components, random_state=42)
    pca.fit(X_std)
    return pca


def save_explained_variance(pca: PCA) -> pd.DataFrame:
    ev = pca.explained_variance_
    evr = pca.explained_variance_ratio_
    dims = [f"Dim{i+1}" for i in range(len(evr))]
    df_ev = pd.DataFrame({
        "Dimension": dims,
        "Eigenvalue": ev,
        "%_variance": np.round(evr * 100, 2),
        "%_cumulative": np.round(np.cumsum(evr) * 100, 2),
    })
    df_ev.to_csv(OUT_DIR / "explained_variance.csv", index=False)

    # Graphe des éboulis
    plt.figure(figsize=(8, 5))
    plt.bar(range(1, len(evr) + 1), evr * 100)
    plt.plot(range(1, len(evr) + 1), np.cumsum(evr) * 100, marker="o")
    plt.xlabel("Dimensions")
    plt.ylabel("% explained variance")
    plt.title("Scree plot (explained vs cumulative)")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "explained_variance.png", dpi=200)
    plt.close()

    return df_ev


def biplot_variables(pca: PCA, feature_names: list[str], top_k: int = 30) -> pd.DataFrame:
    # Charges factorielles : composantes x variables
    loadings = pca.components_.T
    df_load = pd.DataFrame(loadings, index=feature_names,
                           columns=[f"Dim{i+1}" for i in range(loadings.shape[1])])
    df_load.to_csv(OUT_DIR / "loadings.csv")

    # Pour le cercle des corrélations sur Dim1-Dim2
    vx = df_load["Dim1"].values
    vy = df_load["Dim2"].values
    strength = np.sqrt(vx**2 + vy**2)
    # Sélectionner les top_k vecteurs les plus « longs »
    idx = np.argsort(-strength)[:min(top_k, len(strength))]

    plt.figure(figsize=(7, 7))
    # Cercle unité
    theta = np.linspace(0, 2 * np.pi, 512)
    plt.plot(np.cos(theta), np.sin(theta), linestyle="--", linewidth=1)
    plt.axhline(0, color="black", linewidth=0.6)
    plt.axvline(0, color="black", linewidth=0.6)

    # Flèches et labels
    for i in idx:
        plt.arrow(0, 0, vx[i], vy[i],
                  head_width=0.02, head_length=0.02, length_includes_head=True, alpha=0.7)
        name = feature_names[i]
        plt.text(vx[i] * 1.05, vy[i] * 1.05, name, fontsize=7)

    plt.xlabel("Dim1")
    plt.ylabel("Dim2")
    plt.title("Correlation circle (variable biplot)")
    plt.xlim(-1.1, 1.1)
    plt.ylim(-1.1, 1.1)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "biplot_variables.png", dpi=200)
    plt.close()

    return df_load


def plot_individuals(X_std: np.ndarray, pca: PCA, cat: pd.Series | None) -> pd.DataFrame:
    # Coordonnées des individus
    scores = pca.transform(X_std)
    df_scores = pd.DataFrame({"Dim1": scores[:, 0]})

    if pca.n_components_ >= 2:
        df_scores["Dim2"] = scores[:, 1]

    # Tenter de colorier par variable catégorielle (track_genre_top)
    if cat is not None:
        df_scores["cat"] = cat.astype("category")
        # Grouper les modalités rares
        top_levels = df_scores["cat"].value_counts().index[:12]
        mask_top = df_scores["cat"].isin(top_levels)
        df_scores["cat_plot"] = df_scores["cat"].astype(str)
        df_scores.loc[~mask_top, "cat_plot"] = "Autre"
        categories = df_scores["cat_plot"].astype("category").cat.categories.tolist()
        colors = plt.get_cmap("tab20").colors
        color_map = {c: colors[i % len(colors)] for i, c in enumerate(categories)}

        plt.figure(figsize=(8, 6))
        for c in categories:
            sub = df_scores[df_scores["cat_plot"] == c]
            if pca.n_components_ >= 2:
                plt.scatter(sub["Dim1"], sub["Dim2"], s=10, alpha=0.7, label=str(c), c=[color_map[c]])
            else:
                plt.scatter(sub["Dim1"], np.zeros(len(sub)), s=10, alpha=0.7,
                            label=str(c), c=[color_map[c]])
        plt.legend(title="track_genre_top", fontsize=8, markerscale=1.5, ncol=2)
    else:
        plt.figure(figsize=(8, 6))
        if pca.n_components_ >= 2:
            plt.scatter(df_scores["Dim1"], df_scores["Dim2"], s=10, alpha=0.7)
        else:
            plt.scatter(df_scores["Dim1"], np.zeros(len(df_scores)), s=10, alpha=0.7)

    evr = pca.explained_variance_ratio_
    xlab = f"Dim1 ({evr[0]*100:.1f}%)"
    ylab = f"Dim2 ({evr[1]*100:.1f}%)" if pca.n_components_ >= 2 else "Dim2 (not available)"
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title("Individuals scatter (first factorial plane)")
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "individuals_scatter.png", dpi=200)
    plt.close()

    return df_scores


def run() -> int:
    print("Running ACP main...")
    ensure_outdir()

    df = load_data(CSV_PATH)
    X_num, cat = pick_features(df)
    X_selected = optimize_feature_subset(X_num, target_ratio=0.50, min_features=4)
    X_std, feature_names = standardize_impute(X_selected)

    pca = run_pca(X_std, max_components=10)
    ev_table = save_explained_variance(pca)
    print("Explained variance (premières dimensions):")
    print(ev_table.head())

    _ = biplot_variables(pca, feature_names, top_k=30)
    _ = plot_individuals(X_std, pca, cat)

    # Sauvegarder un mini résumé texte
    with open(OUT_DIR / "summary.txt", "w", encoding="utf-8") as f:
        f.write("PCA completed.\n")
        f.write(f"Observations: {X_std.shape[0]} | Numeric variables: {X_std.shape[1]}\n")
        ratio12 = float(np.sum(pca.explained_variance_ratio_[:2])) * 100
        f.write(f"Dim1+Dim2 cumulative variance: {ratio12:.2f}%\n")
        f.write("Selected variables: " + ", ".join(feature_names) + "\n")
        f.write(ev_table.to_string(index=False))

    print(f"Fichiers écrits dans: {OUT_DIR}")
    return 0


def main() -> int:
    try:
        return run()
    except FileNotFoundError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        print("Vérifie le chemin vers cleaned_data/merged_tracks.csv", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Erreur inattendue: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
