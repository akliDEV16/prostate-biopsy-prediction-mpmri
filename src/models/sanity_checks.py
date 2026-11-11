"""
Contrôles de plausibilité (ce n'est pas l'entraînement final) :
1. AUC de chaque variable seule : une variable presque parfaite signalerait une fuite.
2. Clinique seule contre clinique + IRM : ce que l'IRM apporte réellement.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline

from src.data.prepare_data import FEATURES, SANS_IRM, get_X_y, load_model_table
from src.features.imputation import make_imputer
from src.features.scaling import make_scaler
from src.features.split_data import make_cv


def logreg():
    return Pipeline([
        ("imputation", make_imputer()),
        ("echelle", make_scaler()),
        ("modele", LogisticRegression(max_iter=1000)),
    ])


def auc_cv(columns, X, y, cv):
    """
    AUC moyenne en validation croisée, en utilisant seulement les colonnes demandées.
    """
    resultats = cross_validate(logreg(), X[columns], y, cv=cv, scoring="roc_auc", n_jobs=-1)
    return resultats["test_score"].mean()


def main():
    X, y = get_X_y(load_model_table())
    cv = make_cv()

    print("=== 1. AUC de chaque variable seule ===")
    for f in FEATURES:
        print(f"{f:25s} {auc_cv([f], X, y, cv):.3f}")

    print("\n=== 2. Clinique seule contre clinique + IRM ===")
    print(f"sans IRM ({len(SANS_IRM)} variables) : {auc_cv(SANS_IRM, X, y, cv):.3f}")
    print(f"avec IRM ({len(FEATURES)} variables)  : {auc_cv(FEATURES, X, y, cv):.3f}")


if __name__ == "__main__":
    main()