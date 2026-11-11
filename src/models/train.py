"""
Pipelines d'entraînement : imputation, mise à l'échelle (régression logistique) et modèle.

Tout ce qui apprend (médiane, moyenne, écart-type, arbres) est dans le Pipeline :
il est donc ajusté à chaque pli de validation croisée, jamais sur tout le tableau.
"""
from pathlib import Path

import joblib
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.features.imputation import make_imputer
from src.features.scaling import make_scaler

# CONFIGURATION
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
RANDOM_STATE = 0

NAIVE_NAME = "reponse_naive"
LOGREG_NAME = "regression_logistique"
RF_NAME = "random_forest"

LOGREG_PARAMS = {"max_iter": 1000, "random_state": RANDOM_STATE}
RF_PARAMS = {"n_estimators": 300, "random_state": RANDOM_STATE, "n_jobs": 1}


# PIPELINES
def build_pipelines():
    """
    Renvoie un dictionnaire {nom : Pipeline non entraîné}.
    La réponse naïve prédit toujours la classe majoritaire : c'est la référence.
    """
    return {
        NAIVE_NAME: Pipeline([
            ("imputation", make_imputer()),
            ("modele", DummyClassifier(strategy="most_frequent")),
        ]),
        LOGREG_NAME: Pipeline([
            ("imputation", make_imputer()),
            ("echelle", make_scaler()),
            ("modele", LogisticRegression(**LOGREG_PARAMS)),
        ]),
        RF_NAME: Pipeline([
            ("imputation", make_imputer()),
            ("modele", RandomForestClassifier(**RF_PARAMS)),
        ]),
    }


# ENTRAÎNEMENT FINAL
def train_all(pipelines, X, y, models_dir=MODELS_DIR):
    """
    Entraîne sur tous les patients les modèles (sans la réponse naïve)
    et sauvegarde chacun dans models/. Renvoie {nom : chemin du fichier}.
    """
    models_dir.mkdir(parents=True, exist_ok=True)
    fichiers = {}
    for name, pipe in pipelines.items():
        if name == NAIVE_NAME:
            continue
        pipe.fit(X, y)
        chemin = models_dir / f"{name}.joblib"
        joblib.dump(pipe, chemin)
        fichiers[name] = chemin
    return fichiers