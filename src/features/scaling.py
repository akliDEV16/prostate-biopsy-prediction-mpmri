"""
Mise à l'échelle:
Utile pour la régression logistique ; inutile pour les arbres (Random Forest).
Comme l'imputeur, le scaler apprend (moyenne, écart-type).
"""
from sklearn.preprocessing import StandardScaler


def make_scaler():
    return StandardScaler()


if __name__ == "__main__":
    from src.data.prepare_data import get_X_y, load_model_table
    from src.features.imputation import make_imputer

    X, _ = get_X_y(load_model_table())
    X_imp = make_imputer().fit_transform(X)   
    X_std = make_scaler().fit_transform(X_imp)
    print("Moyennes après mise à l'échelle :", X_std.mean(axis=0).round(2))
    print("Écarts-types                    :", X_std.std(axis=0).round(2))