import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import FactorAnalysis
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity


CSV_PATH: str = "data/merged_tracks.csv"
OUTPUT_PATH: str = "graphs/matthieu/"
COL_1: str = "artist_location"
COL_2: str = "track_genre_top"


def main() -> None:
    data: pd.DataFrame = load_data()

    print(f"\nColumns selected: {COL_1} and {COL_2}\n")
    contingency_table = get_contingency_table(data, COL_1, COL_2)
    standardized_contingency_table: pd.DataFrame = standardize_contingency_table(
        contingency_table
    )

    p_val, p_val_std = get_p_val(contingency_table, standardized_contingency_table)
    print(f"\np-val with standardization: {p_val_std}\np-val without std: {p_val}\n")

    if (p_val > 0.5 or p_val_std > 0.5):
        print("Factor Analysis of Correspondence irrelevant")
        exit(0)

    nb_factors: int = get_nb_factors(contingency_table, standardized_contingency_table)
    afc(standardized_contingency_table, nb_factors)


def load_data() -> pd.DataFrame:
    print("\nLoading CSV...")
    data: pd.DataFrame
    try:
        data = pd.read_csv(
            CSV_PATH,
            low_memory=False,
            # nrows=1000
        )
    except FileNotFoundError:
        print("CSV not found. Make sure to run this script from the root of the repository.")
        exit(1)
    print("CSV loaded.\n")
    return data


def get_contingency_table(data: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
    return pd.crosstab(data[col1], data[col2])


def standardize_contingency_table(contingency_table: pd.DataFrame) -> pd.DataFrame:
    temp: pd.DataFrame = contingency_table.sub(contingency_table.mean())
    x_scaled: pd.DataFrame = temp.div(contingency_table.std())
    return x_scaled


def get_p_val(
    contingency_table: pd.DataFrame, standardized_contingency_table: pd.DataFrame
) -> tuple:
    _, p_val = calculate_bartlett_sphericity(contingency_table)
    _, p_val_std = calculate_bartlett_sphericity(standardized_contingency_table)
    return (p_val, p_val_std)


def get_nb_factors(contingency_table: pd.DataFrame, X_scaled: pd.DataFrame) -> int:
    print("\nGet nb factors...")
    max_nb_factors: int = min(
        contingency_table.shape[0], contingency_table.shape[1] - 1
    )
    fa = FactorAnalyzer(n_factors=max_nb_factors, rotation=None)
    fa.fit(X_scaled)
    ev, v = fa.get_eigenvalues()
    fa_res = fa.loadings_
    print("\nLoadings:")
    print(fa_res)

    nb_factors: int = 0
    for v in ev:
        if v > 1:
            nb_factors += 1

    # fa_new = FactorAnalysis(n_components=max_nb_factors, random_state=0)
    # X_transformed = fa_new.fit_transform(X_scaled)

    columns = [f"col_{i}" for i in range(max_nb_factors)]
    df_factors = pd.DataFrame(fa.loadings_, columns=columns, index=X_scaled.columns)
    print("\ndf_factors:")
    print(df_factors)

    fig, ax = plt.subplots()
    labels = [str(i + 1).zfill(1) for i in range(len(ev))]
    ax.bar(labels, ev, label=labels)
    ax.set_xlabel("Factors")
    ax.set_ylabel("Eigenvalues")
    plt.title("Scree Plot")
    plt.savefig(fname=f"{OUTPUT_PATH}afc_get_nb_factors")

    print(f"\nnb factors: {nb_factors}\n")
    return nb_factors


def afc(X_scaled: pd.DataFrame, nb_factors: int) -> None:
    print("\nAFC...")
    methods = [
        ("FA No rotation", FactorAnalysis(nb_factors)),
        ("FA Varimax", FactorAnalysis(nb_factors, rotation="varimax")),
        ("FA Quartimax", FactorAnalysis(nb_factors, rotation="quartimax")),
    ]
    fig, axes = plt.subplots(ncols=3, figsize=(10, 8), sharex=True, sharey=True)

    for ax, (method, fa) in zip(axes, methods):
        fa = fa.fit(X_scaled)

        components = fa.components_
        ax.scatter(components[0, :], components[1, :])
        ax.axhline(0, -1, 1, color="k")
        ax.axvline(0, -1, 1, color="k")
        for i, j, z in zip(components[0, :], components[1, :], X_scaled.columns):
            ax.text(i + 0.02, j + 0.02, str(z), ha="center")
        ax.set_title(str(method))
        if ax.get_subplotspec().is_first_col():
            ax.set_ylabel("Factor 1")
        ax.set_xlabel("Factor 2")

    plt.tight_layout()
    plt.savefig(fname=f"{OUTPUT_PATH}afc")
    
    print("Done.")
    print(f"Graphs saved in {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
