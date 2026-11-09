"""
Nettoyage de la FORME des données brutes AI4AR.

Corrige la forme (noms de colonnes, espaces, types) et vérifie les valeurs.
Ne supprime aucune ligne ni colonne et ne fait aucun choix de modélisation.
"""
import pandas as pd

from src.data.load_data import load_all

# CONFIGURATION
CLINICAL_REQUIRED = [
    "patient_id", "patient_age", "clinical_group", "prior_biopsies", "dre_result",
    "psa_result", "prostate_volume_mri", "psa_density_mri", "no_of_lesions", "is_cancer",
]
RADIOLOGICAL_REQUIRED = [
    "patient_id", "radiologist_id", "lesion_id", "dimension", "lesion_pirads", "patient_pirads",
]

# Colonnes à convertir en nombres (la virgule décimale est acceptée)
CLINICAL_NUMERIC = [
    "patient_id", "patient_age", "prior_biopsies", "dre_result", "psa_result",
    "prostate_volume_us", "psa_density_us", "prostate_volume_mri", "psa_density_mri",
    "no_of_lesions", "is_cancer", "TBx_SBx_state", "isup_group",
]
RADIOLOGICAL_NUMERIC = ["patient_id", "lesion_id", "dimension", "lesion_pirads", "patient_pirads"]

# Valeurs attendues 
VALID_CLINICAL_GROUPS = {"BN", "TN", "AS", "R"}
BINARY_COLUMNS = ["is_cancer", "dre_result", "TBx_SBx_state"]
CLINICAL_RANGES = {
    "patient_age": (18, 110), "psa_result": (0, 1000), "prostate_volume_mri": (5, 500),
    "psa_density_mri": (0, 20), "prior_biopsies": (0, 30), "no_of_lesions": (0, 10),
    "isup_group": (1, 5),
}
RADIOLOGICAL_RANGES = {"lesion_pirads": (1, 5), "patient_pirads": (1, 5), "dimension": (0.5, 150)}


# OUTILS INTERNES
def _strip_column_names(df):
    """
    Retire les espaces autour des noms de colonnes. 
    Renvoie la liste des noms modifiés.
    """
    avant = df.columns.astype(str).tolist()
    apres = [c.strip() for c in avant]
    modifies = [a for a, b in zip(avant, apres) if a != b]
    df.columns = apres
    doublons = df.columns[df.columns.duplicated()].tolist()
    if doublons:
        raise ValueError(f"Colonnes en double après nettoyage des noms : {doublons}")
    return modifies


def _strip_text_values(df):
    """
    Retire les espaces autour des valeurs textuelles. 
    Renvoie le nombre de valeurs modifiées.
    """
    n_modifiees = 0
    for col in df.select_dtypes(include=["object", "string"]).columns:
        ancien = df[col]
        nouveau = ancien.map(lambda v: v.strip() if isinstance(v, str) else v)
        n_modifiees += int((ancien.notna() & (nouveau != ancien)).sum())
        df[col] = nouveau
    return n_modifiees


def _check_required(df, required, name):
    manquantes = [c for c in required if c not in df.columns]
    if manquantes:
        raise ValueError(f"[{name}] colonnes indispensables absentes : {manquantes}")


def _to_numeric(series):
    """
    Convertit en nombres. 
    Renvoie (série convertie, valeurs qui n'ont pas pu l'être).
    """
    nettoyee = series.map(lambda v: v.strip().replace(",", ".") if isinstance(v, str) else v)
    numerique = pd.to_numeric(nettoyee, errors="coerce")
    echecs = series.notna() & numerique.isna()
    return numerique, sorted(set(series[echecs].astype(str)))


def _convert_numeric(df, columns):
    """
    Convertit les colonnes demandées. 
    Renvoie (colonnes converties, échecs par colonne).
    """
    converties, echecs = [], {}
    for col in columns:
        if col not in df.columns:
            continue
        etait_numerique = pd.api.types.is_numeric_dtype(df[col])
        df[col], valeurs_en_echec = _to_numeric(df[col])
        if not etait_numerique:
            converties.append(col)
        if valeurs_en_echec:
            echecs[col] = valeurs_en_echec
    return converties, echecs


def _check_ids(df, name, id_columns):
    """
    Les identifiants ne doivent être ni manquants ni non entiers. 
    Les convertit en entiers.
    """
    for col in id_columns:
        if df[col].isna().any():
            raise ValueError(f"[{name}] '{col}' manquant sur {int(df[col].isna().sum())} ligne(s)")
        if (df[col] % 1 != 0).any():
            raise ValueError(f"[{name}] '{col}' contient des valeurs non entières")
        df[col] = df[col].astype(int)


def _check_ranges(df, ranges):
    problemes = []
    for col, (bas, haut) in ranges.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        n_hors = int(((s < bas) | (s > haut)).sum())
        if n_hors:
            problemes.append(f"'{col}' : {n_hors} valeur(s) hors de [{bas}, {haut}] "
                             f"(min {s.min()}, max {s.max()})")
    return problemes


def _check_binary(df, columns):
    problemes = []
    for col in columns:
        if col not in df.columns:
            continue
        inattendues = set(df[col].dropna().unique()) - {0, 1, 0.0, 1.0}
        if inattendues:
            problemes.append(f"'{col}' devrait valoir 0 ou 1 : {sorted(inattendues)}")
    return problemes


def _report(name, shape_avant, shape_apres, renommees, n_valeurs, converties, echecs, problemes):
    """
    Affiche un bloc court : uniquement ce qui a changé ou posé problème.
    """
    print(f"\n=== Nettoyage : {name} ===")
    print(f"Forme                    : {shape_avant} -> {shape_apres}")
    print(f"Noms de colonnes corrigés: {renommees if renommees else 'aucun'}")
    print(f"Valeurs texte corrigées  : {n_valeurs}")
    print(f"Converties en nombres    : {converties if converties else 'aucune'}")
    if echecs:
        for col, valeurs in echecs.items():
            print(f"ATTENTION non convertible: '{col}' -> {valeurs[:5]}")
    if problemes:
        for p in problemes:
            print(f"ATTENTION                : {p}")
    elif not echecs:
        print("Contrôles                : OK")


# NETTOYAGE DES DEUX FICHIERS
def clean_clinical(df, verbose=True):
    """
    Nettoie le fichier clinique. 
    Renvoie une copie ; l'original n'est pas modifié.
    """
    df = df.copy()
    shape_avant = df.shape
    renommees = _strip_column_names(df)
    n_valeurs = _strip_text_values(df)
    _check_required(df, CLINICAL_REQUIRED, "clinique")
    converties, echecs = _convert_numeric(df, CLINICAL_NUMERIC)

    _check_ids(df, "clinique", ["patient_id"])
    if df["patient_id"].duplicated().any():
        raise ValueError(f"[clinique] patient_id en double : "
                         f"{df.loc[df['patient_id'].duplicated(), 'patient_id'].tolist()[:10]}")

    df["clinical_group"] = df["clinical_group"].map(lambda v: v.upper() if isinstance(v, str) else v)
    problemes = []
    inconnus = set(df["clinical_group"].dropna().unique()) - VALID_CLINICAL_GROUPS
    if inconnus:
        problemes.append(f"clinical_group : valeurs inattendues {sorted(inconnus)}")
    problemes += _check_binary(df, BINARY_COLUMNS)
    problemes += _check_ranges(df, CLINICAL_RANGES)

    if verbose:
        _report("clinique", shape_avant, df.shape, renommees, n_valeurs, converties, echecs, problemes)
    return df


def clean_radiological(df, verbose=True):
    """
    Nettoie le fichier radiologique (une ligne par lésion ET par radiologue).
    """
    df = df.copy()
    shape_avant = df.shape
    renommees = _strip_column_names(df)
    n_valeurs = _strip_text_values(df)
    _check_required(df, RADIOLOGICAL_REQUIRED, "radiologique")
    converties, echecs = _convert_numeric(df, RADIOLOGICAL_NUMERIC)

    _check_ids(df, "radiologique", ["patient_id", "lesion_id"])
    if df["radiologist_id"].isna().any():
        raise ValueError("[radiologique] 'radiologist_id' manquant")

    problemes = _check_ranges(df, RADIOLOGICAL_RANGES)
    n_doublons = int(df.duplicated(subset=["patient_id", "radiologist_id", "lesion_id"]).sum())
    if n_doublons:
        problemes.append(f"{n_doublons} ligne(s) avec la même clé (patient, radiologue, lésion)")

    if verbose:
        _report("radiologique", shape_avant, df.shape, renommees, n_valeurs, converties, echecs, problemes)
    return df


def clean_all(clinical, radiological, verbose=True):
    """
    Nettoie les deux tableaux. 
    Renvoie (clinique, radiologique) nettoyés.
    """
    return clean_clinical(clinical, verbose), clean_radiological(radiological, verbose)


if __name__ == "__main__":
    brut_clin, brut_rad = load_all()
    clin, rad = clean_all(brut_clin, brut_rad)
    print("\nTypes après nettoyage (extrait) :")
    print(clin[["patient_id", "psa_result", "is_cancer", "no_of_lesions"]].dtypes.to_string())