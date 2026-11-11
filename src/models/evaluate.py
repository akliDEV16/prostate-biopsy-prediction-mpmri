"""
Évaluation par validation croisée répétée stratifiée.

cross_validate clone le Pipeline à chaque pli et ne l'ajuste que sur le train du pli :
l'imputation et la mise à l'échelle n'apprennent jamais des patients du test.
"""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import cross_validate

# CONFIGURATION
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results"

SCORING = {
    "auc": "roc_auc",
    "balanced_accuracy": "balanced_accuracy",
    "accuracy": "accuracy",
}


# ÉVALUATION
def evaluate_one(pipeline, X, y, cv):
    """
    Renvoie un tableau à une ligne par découpe (pli x répétition).
    """
    resultats = cross_validate(pipeline, X, y, cv=cv, scoring=SCORING, n_jobs=-1)
    return pd.DataFrame({m: resultats[f"test_{m}"] for m in SCORING})


def summarize(folds):
    """
    Moyenne et écart-type de chaque métrique, sur toutes les découpes.
    """
    lignes = {}
    for m in SCORING:
        lignes[f"{m}_moyenne"] = folds[m].mean()
        lignes[f"{m}_ecart_type"] = folds[m].std()
    return pd.Series(lignes)


def evaluate_all(pipelines, X, y, cv):
    """
    Renvoie (détail par découpe, résumé par modèle).
    """
    details, resumes = {}, {}
    for name, pipe in pipelines.items():
        folds = evaluate_one(pipe, X, y, cv)
        details[name] = folds
        resumes[name] = summarize(folds)

    detail = pd.concat(details, names=["modele", "decoupe"]).reset_index()
    resume = pd.DataFrame(resumes).T
    resume.index.name = "modele"
    return detail, resume


# SAUVEGARDE
def save_results(detail, resume, results_dir=RESULTS_DIR):
    """
    Écrit les scores dans results/ : détail par découpe et résumé.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(results_dir / "cv_details.csv", index=False)
    resume.round(4).to_csv(results_dir / "cv_resume.csv")
    return results_dir