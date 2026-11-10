"""
Résumé de l'IRM par patient (une ligne par patient).

Entrée : fichier radiologique nettoyé (une ligne par lésion ET par radiologue).
Sortie : pour chaque patient ayant au moins une lésion décrite :
    pirads_max    : PI-RADS de la lésion la plus suspecte
    dim_max       : taille (mm) de la plus grande lésion
    n_lesions_irm : nombre de lésions décrites (contrôle, pas une variable du modèle)

Les patients sans lésion décrite n'apparaissent pas ici : merge_data.py s'en charge.
La colonne TBx (résultat de biopsie par lésion) n'est jamais lue.
"""
import numpy as np

from src.data.clean_data import RADIOLOGICAL_RANGES

# CONFIGURATION
LESION_KEY = ["patient_id", "radiologist_id", "lesion_id"]
USED_COLUMNS = LESION_KEY + ["lesion_pirads", "dimension"]


def _one_reading_per_lesion(rad, verbose=True):
    """
    Garde un seul avis par (patient, radiologue, lésion).

    1. Les lignes vides (ni PI-RADS, ni taille utilisable) sont retirées.
    2. Si un radiologue a saisi plusieurs avis pour la même lésion, on garde la
       valeur la plus élevée de chaque colonne.
    """
    vides = rad["lesion_pirads"].isna() & (rad["dimension"].isna() | (rad["dimension"] == 0))
    rad = rad[~vides]
    n_avant = len(rad)
    rad = rad.groupby(LESION_KEY, as_index=False)[["lesion_pirads", "dimension"]].max()
    if verbose:
        print(f"Lignes vides retirées : {int(vides.sum())} | "
              f"avis multiples fusionnés : {n_avant - len(rad)}")
    return rad


def _mask_implausible_dimensions(rad, verbose=True):
    """
    Remplace les tailles hors des bornes de clean_data.py par 'manquant'.
    """
    bas, haut = RADIOLOGICAL_RANGES["dimension"]
    rad = rad.copy()
    hors = rad["dimension"].notna() & ~rad["dimension"].between(bas, haut)
    rad.loc[hors, "dimension"] = np.nan
    if verbose:
        print(f"Tailles hors de [{bas}, {haut}] mises à 'manquant' : {int(hors.sum())}")
    return rad


def summarize_lesions(rad, verbose=True):
    """
    Renvoie un tableau indexé par patient_id : pirads_max, dim_max, n_lesions_irm.
    """
    rad = _one_reading_per_lesion(rad[USED_COLUMNS], verbose)
    rad = _mask_implausible_dimensions(rad, verbose)

    # une valeur par lésion : médiane entre les radiologues qui l'ont décrite
    par_lesion = rad.groupby(["patient_id", "lesion_id"])[["lesion_pirads", "dimension"]].median()

    # une valeur par patient : la lésion la plus suspecte, la plus grande
    return par_lesion.groupby("patient_id").agg(
        pirads_max=("lesion_pirads", "max"),
        dim_max=("dimension", "max"),
        n_lesions_irm=("lesion_pirads", "size"),
    )


if __name__ == "__main__":
    from src.data.load_data import load_all
    from src.data.clean_data import clean_all

    _, rad_propre = clean_all(*load_all(), verbose=False)
    resume = summarize_lesions(rad_propre)
    print("\nPatients résumés :", len(resume))
    print("Valeurs manquantes :", resume.isna().sum().to_dict())
    print(resume.describe().round(2).to_string())