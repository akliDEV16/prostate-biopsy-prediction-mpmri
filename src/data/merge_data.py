"""
Fusion du tableau clinique et du résumé IRM : une ligne par patient.

Règles pour les patients sans lésion décrite à l'IRM :
  - le clinique indique 0 lésion (ou rien d'annoncé) : pirads_max, dim_max et
    n_lesions_irm valent 0 ("aucune lésion suspecte retenue") ;
  - le clinique annonce au moins une lésion (no_of_lesions > 0) mais le fichier IRM
    n'a aucune ligne : l'information IRM est INCONNUE, laissée manquante.
Un indicateur a_lesion_irm garde la trace de ces choix.
"""
from src.data.clean_data import clean_all
from src.data.load_data import load_all
from src.features.feature_extraction import summarize_lesions

# CONFIGURATION
IRM_COLUMNS = ["pirads_max", "dim_max", "n_lesions_irm"]


def merge_clinical_irm(clin, rad, verbose=True):
    """Renvoie le tableau clinique enrichi des colonnes IRM (même nombre de lignes)."""
    resume = summarize_lesions(rad, verbose=False)
    n_avant = len(clin)

    df = clin.merge(resume, how="left", left_on="patient_id", right_index=True,
                    validate="one_to_one")
    if len(df) != n_avant:
        raise ValueError(f"La fusion a changé le nombre de patients : {n_avant} -> {len(df)}")

    # Patients sans ligne IRM : 0, SAUF si le clinique annonce une lésion (IRM inconnue)
    df["a_lesion_irm"] = df["n_lesions_irm"].notna().astype(int)
    sans_irm = df["a_lesion_irm"] == 0
    annonce_une_lesion = df["no_of_lesions"] > 0
    df.loc[sans_irm & ~annonce_une_lesion, IRM_COLUMNS] = 0

    # Les seules valeurs IRM manquantes admises : "sans IRM mais lésion annoncée"
    irm_inconnue = sans_irm & annonce_une_lesion
    inattendus = int(df.loc[~irm_inconnue, IRM_COLUMNS].isna().sum().sum())
    if inattendus:
        raise ValueError(f"{inattendus} valeur(s) IRM manquantes inattendues après fusion")

    # Incohérences no_of_lesions / fichier IRM : signalées, pas corrigées
    nb = df["no_of_lesions"]
    df["incoherence_lesions"] = (
        (irm_inconnue | ((nb.fillna(0) == 0) & ~sans_irm))
    ).astype(int)

    if verbose:
        print("\n=== Fusion clinique + IRM ===")
        print(f"Patients                                : {n_avant} -> {len(df)}")
        print(f"Avec lésion décrite à l'IRM             : {int((~sans_irm).sum())}")
        print(f"Sans lésion décrite (codés à 0)         : {int((sans_irm & ~annonce_une_lesion).sum())}")
        print(f"IRM inconnue (lésion annoncée, 0 ligne) : {int(irm_inconnue.sum())}")
        print(f"Incohérences no_of_lesions / IRM        : {int(df['incoherence_lesions'].sum())} "
              "(colonne 'incoherence_lesions')")
    return df


if __name__ == "__main__":
    clin, rad = clean_all(*load_all(), verbose=False)
    fusion = merge_clinical_irm(clin, rad)
    print("\nAperçu :")
    print(fusion[["patient_id", "clinical_group", "no_of_lesions", "pirads_max",
                  "dim_max", "a_lesion_irm", "incoherence_lesions"]].head(8).to_string(index=False))