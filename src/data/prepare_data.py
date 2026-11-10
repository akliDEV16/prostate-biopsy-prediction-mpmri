"""
Construit le tableau final du modèle : un patient par ligne.

Étapes : charger -> nettoyer -> fusionner clinique + IRM -> choisir la population
(groupes BN et TN, résultat de biopsie connu) -> créer la cible et les variables
-> contrôler (aucune variable interdite) -> sauvegarder.

Les transformations faites ici n'apprennent rien sur les autres patients (log, indicateur) :
elles ne créent donc aucune fuite. 
L'imputation et la mise à l'échelle, elles, se font dans le Pipeline de validation croisée (src/models).
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.clean_data import clean_all
from src.data.load_data import load_all
from src.data.merge_data import merge_clinical_irm

# CONFIGURATION
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_TABLE_FILE = PROCESSED_DIR / "ai4ar_model_table.csv"

POPULATION_GROUPS = ["BN", "TN"]   # BN : jamais biopsiés ; TN : biopsies précédentes négatives
TARGET_SOURCE = "is_cancer"        # résultat de la biopsie (0 = pas de cancer, 1 = cancer)
TARGET = "y_cancer"

# Variables d'entrée : toutes connues AVANT la biopsie
FEATURES = [
    "patient_age", "log_psa", "prostate_volume_mri", "psa_density_mri",
    "dre_result", "prior_biopsies", "is_TN",
    "no_of_lesions", "pirads_max", "dim_max",
]
SANS_IRM = FEATURES[:7]
IRM = FEATURES[7:]

# Colonnes gardées dans le tableau pour la traçabilité : JAMAIS des variables
TRACEABILITY = ["patient_id", "clinical_group", "isup_group"]

# Colonnes interdites comme variables : elles contiennent le résultat de la biopsie,
# en sont dérivées, ou sont remplies après le diagnostic 
FORBIDDEN_FEATURES = {
    "is_cancer", TARGET, "TBx_SBx_state", "isup_group", "treatment", "eau_risk",
    "tnm_clinical_t", "tnm_pathological_t", "is_TBx", "is_SBx", "no_of_possitive",
    "TBx_case", "SBx_case", "cribriform", "TBx",
    "patient_id", "clinical_group", "a_lesion_irm", "incoherence_lesions", "n_lesions_irm",
}
FORBIDDEN_PREFIXES = ("gs_", "isup", "TBx", "SBx", "tnm_", "eau", "postoperative")

# Population attendue (vérifiée lors des essais précédents)
EXPECTED = {"patients": 462, "cancer": 248, "sans_cancer": 214}


# CONTRÔLES
def check_features(features):
    """
    Refuse toute variable interdite. 
    """
    interdites = [f for f in features
                  if f in FORBIDDEN_FEATURES or f.startswith(FORBIDDEN_PREFIXES)]
    if interdites:
        raise ValueError(f"Variable(s) interdite(s) parmi les features : {interdites}")


def _check_table(table):
    check_features(FEATURES)
    absentes = [c for c in FEATURES + [TARGET] if c not in table.columns]
    if absentes:
        raise ValueError(f"Colonnes absentes du tableau : {absentes}")
    non_numeriques = [c for c in FEATURES if not pd.api.types.is_numeric_dtype(table[c])]
    if non_numeriques:
        raise ValueError(f"Variables non numériques : {non_numeriques}")
    infinies = [c for c in FEATURES if np.isinf(table[c]).any()]
    if infinies:
        raise ValueError(f"Valeurs infinies dans : {infinies}")
    if table["patient_id"].duplicated().any():
        raise ValueError("patient_id en double dans le tableau final")

    obtenu = {"patients": len(table), "cancer": int((table[TARGET] == 1).sum()),
              "sans_cancer": int((table[TARGET] == 0).sum())}
    if obtenu != EXPECTED:
        raise ValueError(f"Population inattendue : obtenu {obtenu}, attendu {EXPECTED}. "
                         "Un nettoyage ou une fusion a changé les données.")


# CONSTRUCTION
def select_population(df, verbose=True):
    """
    Garde les groupes BN et TN dont le résultat de biopsie est connu.
    """
    dans_groupes = df["clinical_group"].isin(POPULATION_GROUPS)
    cible_connue = df[TARGET_SOURCE].notna()
    retenus = df[dans_groupes & cible_connue].copy()
    if verbose:
        print("\n=== Population ===")
        print(f"Patients au départ                        : {len(df)}")
        print(f"Retirés : groupe hors {POPULATION_GROUPS}        : {int((~dans_groupes).sum())}")
        print(f"Retirés : {TARGET_SOURCE} manquant            : {int((dans_groupes & ~cible_connue).sum())}")
        print(f"Patients retenus                          : {len(retenus)}")
    return retenus


def add_target_and_features(df):
    """
    Crée la cible et les deux variables dérivées.
    """
    df = df.copy()
    df[TARGET] = df[TARGET_SOURCE].astype(int)
    df["log_psa"] = np.log1p(df["psa_result"])
    df["is_TN"] = (df["clinical_group"] == "TN").astype(int)
    return df


def build_model_table(verbose=True):
    """
    Construit et contrôle le tableau du modèle.
    """
    clin, rad = clean_all(*load_all(), verbose=False)
    fusion = merge_clinical_irm(clin, rad, verbose=False)
    population = select_population(fusion, verbose)
    table = add_target_and_features(population)
    table = table[TRACEABILITY + [TARGET] + FEATURES].reset_index(drop=True)
    _check_table(table)

    if verbose:
        print("\n=== Tableau du modèle ===")
        print(f"Forme                    : {table.shape}")
        print(f"Cancer / pas de cancer   : {int((table[TARGET] == 1).sum())} / "
              f"{int((table[TARGET] == 0).sum())}")
        print(f"Groupes                  : {table['clinical_group'].value_counts().to_dict()}")
        manquants = (table[FEATURES].isna().sum())
        manquants = manquants[manquants > 0]
        print(f"Valeurs manquantes       : {manquants.to_dict() if len(manquants) else 'aucune'}")
        print("(Les valeurs manquantes seront imputées dans le Pipeline, jamais ici.)")
        print("Contrôles                : variables interdites absentes, population conforme")
    return table


# SAUVEGARDE ET RELECTURE
def save_model_table(table):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(MODEL_TABLE_FILE, index=False)
    return MODEL_TABLE_FILE


def load_model_table():
    """
    Relit le tableau sauvegardé.
    """
    if not MODEL_TABLE_FILE.exists():
        raise FileNotFoundError(f"{MODEL_TABLE_FILE} introuvable : lancez "
                                "python -m src.data.prepare_data")
    table = pd.read_csv(MODEL_TABLE_FILE)
    _check_table(table)
    return table


def get_X_y(table):
    """
    Renvoie (X, y) : uniquement les variables autorisées et la cible.
    """
    check_features(FEATURES)
    return table[FEATURES], table[TARGET]


if __name__ == "__main__":
    table = build_model_table()
    chemin = save_model_table(table)
    print(f"\nFichier écrit : {chemin}")
    print("\nAperçu :")
    print(table.head(5).round(2).to_string(index=False))