"""
Imputation des valeurs manquantes.

L'imputeur APPREND (la médiane de chaque colonne) : il doit être ajusté sur le train de chaque pli
Ne jamais l'appliquer au tableau entier avant la validation croisée.
"""
from sklearn.impute import SimpleImputer

# CONFIGURATION
STRATEGY = "median"   


def make_imputer(strategy=STRATEGY):
    return SimpleImputer(strategy=strategy)


if __name__ == "__main__":
    import pandas as pd
    from src.data.prepare_data import get_X_y, load_model_table

    X, _ = get_X_y(load_model_table())
    imputeur = make_imputer().fit(X)   
    X_imp = pd.DataFrame(imputeur.transform(X), columns=X.columns)
    manquants = X.isna().sum()
    print("Manquants avant :", manquants[manquants > 0].to_dict())
    print("Manquants après :", int(X_imp.isna().sum().sum()))
    print("Médianes apprises :", dict(zip(X.columns, imputeur.statistics_.round(2))))