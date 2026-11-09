"""
Cohérence entre le fichier clinique et le fichier radiologique.

Ne modifie rien : affiche des comptes pour décider, avant la fusion,
comment traiter les patients sans lésion décrite à l'IRM.
"""
import pandas as pd

from src.data.clean_data import clean_all
from src.data.load_data import load_all


def check_alignment(clin, rad):
    ids_clin, ids_rad = set(clin["patient_id"]), set(rad["patient_id"])
    print("Patients cliniques                         :", len(ids_clin))
    print("Patients avec au moins une ligne IRM       :", len(ids_rad))
    print("Dans l'IRM mais absents du clinique        :", len(ids_rad - ids_clin))
    print("Cliniques sans aucune ligne IRM            :", len(ids_clin - ids_rad))

    # Nombre de lésions distinctes dans le fichier IRM, par patient (0 si aucune ligne)
    n_irm = rad.groupby("patient_id")["lesion_id"].nunique()
    comp = clin.set_index("patient_id")[["no_of_lesions"]].copy()
    comp["n_irm"] = n_irm.reindex(comp.index).fillna(0).astype(int)

    print("\nno_of_lesions (lignes) contre lésions distinctes dans l'IRM (colonnes) :")
    print(pd.crosstab(comp["no_of_lesions"], comp["n_irm"], dropna=False).to_string())

    sans_irm = comp[(comp["no_of_lesions"] > 0) & (comp["n_irm"] == 0)]
    avec_irm = comp[(comp["n_irm"] > 0) & ~(comp["no_of_lesions"] > 0)]
    print("\nno_of_lesions > 0 mais aucune ligne IRM :", len(sans_irm))
    print("Lignes IRM mais no_of_lesions nul ou manquant :", len(avec_irm))
    print("no_of_lesions manquant :", int(comp["no_of_lesions"].isna().sum()))


if __name__ == "__main__":
    clin, rad = clean_all(*load_all(), verbose=False)
    check_alignment(clin, rad)