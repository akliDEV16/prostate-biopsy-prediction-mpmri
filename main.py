"""
Lance le projet de bout en bout :
tableau du modèle -> validation croisée (avec réponse naïve) -> entraînement final.

Commande (depuis la racine du projet, CSV déjà placés dans data/raw/) :
    python main.py
"""
from src.data.prepare_data import build_model_table, get_X_y, save_model_table
from src.features.split_data import make_cv
from src.models.evaluate import evaluate_all, save_results
from src.models.train import build_pipelines, train_all


def main():
    print("=== 1. Tableau du modèle ===")
    table = build_model_table(verbose=True)
    chemin_table = save_model_table(table)
    print(f"Tableau sauvegardé : {chemin_table}")

    X, y = get_X_y(table)
    cv = make_cv()
    pipelines = build_pipelines()

    print(f"\n=== 2. Validation croisée : {cv.get_n_splits()} découpes ===")
    detail, resume = evaluate_all(pipelines, X, y, cv)
    dossier = save_results(detail, resume)
    print(resume.round(3).to_string())
    print(f"\nRésultats sauvegardés dans : {dossier}")

    print("\n=== 3. Entraînement final sur tous les patients ===")
    fichiers = train_all(pipelines, X, y)
    for name, chemin in fichiers.items():
        print(f"{name} -> {chemin}")


if __name__ == "__main__":
    main()