"""
Lecture des fichiers AI4AR.

Ce module ne fait QUE lire : aucun nettoyage, aucune validation, aucune conversion.
"""
from pathlib import Path

import pandas as pd

# CONFIGURATION
PROJECT_ROOT = Path(__file__).resolve().parents[2]    
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLINICAL_FILE = RAW_DIR / "AI4A4_PCa_clinical.csv"
RADIOLOGICAL_FILE = RAW_DIR / "AI4AR_PCa_radiological.csv"


# LECTURE
def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {path}\n"
            "Téléchargez les CSV depuis https://ai4ar.opi.org.pl/en/the-mpmri-database/ "
            "et placez-les dans data/raw/."
        )
    return pd.read_csv(path)


def load_clinical() -> pd.DataFrame:
    """Fichier clinique brut : une ligne par patient."""
    return _read(CLINICAL_FILE)


def load_radiological() -> pd.DataFrame:
    """Fichier radiologique brut : une ligne par lésion ET par radiologue."""
    return _read(RADIOLOGICAL_FILE)


def load_all() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Renvoie (clinique, radiologique), tels quels."""
    return load_clinical(), load_radiological()


if __name__ == "__main__":
    clinical, radiological = load_all()
    print("Clinique     :", clinical.shape)
    print("Radiologique :", radiological.shape)