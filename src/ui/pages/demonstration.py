from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from src.data.prepare_data import FEATURES
from src.ui.styles import load_page_css

# CONFIGURATION
load_page_css("demonstration")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"

MODELES = {
    "Régression logistique": "regression_logistique.joblib",
    "Random Forest": "random_forest.joblib",
}

SEUIL = 0.5                              # même seuil que la page Résultats
AGE_MIN, AGE_MAX = 18, 100
PSA_MAX = 200.0                          # données observées : jusqu'à environ 105 ng/mL
VOLUME_MIN, VOLUME_MAX = 5.0, 400.0      # données observées : 12,8 à 286 mL
DIMENSION_MAX = 60.0                     # données observées : 0 à 45 mm
PIRADS_OPTIONS = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]   # valeurs présentes dans les données
CLE_RESULTAT = "demo_resultat"


# OUTILS DE FORMAT
def fr(valeur, decimales=2):
    """Formate un nombre avec une virgule décimale, à la française."""
    return f"{valeur:.{decimales}f}".replace(".", ",")


# FONCTIONS D'AFFICHAGE
def titre_section(numero, titre, sous_titre=None):
    """Affiche le titre d'une section numérotée."""
    sous_titre_html = f"<p>{sous_titre}</p>" if sous_titre else ""
    st.html(
        f"""
        <div class="demo-section-heading">
            <span class="demo-section-number">{numero}</span>
            <div>
                <h2>{titre}</h2>
                {sous_titre_html}
            </div>
        </div>
        """
    )


def encadre(titre, message, genre="info"):
    """Affiche un encadré d'information ou d'avertissement."""
    st.html(
        f"""
        <div class="demo-note demo-note-{genre}">
            <strong>{titre}</strong>
            <p>{message}</p>
        </div>
        """
    )


def jauge(nom, probabilite):
    """Carte d'un modèle : probabilité estimée et position par rapport au seuil."""
    pourcentage = probabilite * 100
    if probabilite >= SEUIL:
        libelle, classe = "Cancer probable", "demo-verdict-probable"
    else:
        libelle, classe = "Cancer peu probable", "demo-verdict-peu-probable"

    st.html(
        f"""
        <article class="demo-model-result">
            <span class="demo-model-name">{nom}</span>
            <div class="demo-probability">{pourcentage:.0f} <small>%</small></div>
            <div class="demo-gauge" aria-label="Probabilité estimée : {pourcentage:.0f} %">
                <div class="demo-gauge-fill" style="width:{pourcentage:.1f}%"></div>
                <div class="demo-gauge-threshold"></div>
            </div>
            <div class="demo-gauge-scale"><span>0 %</span><span>100 %</span></div>
            <span class="demo-verdict {classe}">{libelle}</span>
        </article>
        """
    )


def valeurs_derivees(patient):
    """Affiche les deux valeurs calculées à partir de la saisie."""
    st.html(
        f"""
        <div class="demo-derived">
            <div>
                <span>log(1 + PSA)</span>
                <strong>{fr(patient['log_psa'])}</strong>
            </div>
            <div>
                <span>Densité du PSA (PSA / volume)</span>
                <strong>{fr(patient['psa_density_mri'])} ng/mL par mL</strong>
            </div>
        </div>
        """
    )


# CHARGEMENT
@st.cache_resource(show_spinner=False)
def charger_modeles():
    """Charge les pipelines entraînés une seule fois (imputation et mise à l'échelle inclus)."""
    return {nom: joblib.load(MODELS_DIR / fichier) for nom, fichier in MODELES.items()}


# CALCULS
def valider(groupe, nb_biopsies, aucune_lesion, nb_lesions, dimension):
    """Renvoie la liste des incohérences de saisie (liste vide si tout est correct)."""
    erreurs = []
    if groupe == "BN" and nb_biopsies > 0:
        erreurs.append(
            "Un patient du groupe BN n'a jamais été biopsié : "
            "le nombre de biopsies antérieures doit être 0."
        )
    if groupe == "TN" and nb_biopsies < 1:
        erreurs.append(
            "Un patient du groupe TN a eu au moins une biopsie négative : "
            "indiquez au moins 1 biopsie antérieure."
        )
    if not aucune_lesion and dimension <= 0:
        erreurs.append("La dimension maximale doit être supérieure à 0 mm pour une lésion décrite.")
    return erreurs


def construire_patient(age, psa, volume, groupe, nb_biopsies, toucher_anormal,
                       aucune_lesion, nb_lesions, pirads, dimension):
    """
    Transforme la saisie en une ligne aux mêmes variables et dans le même ordre
    que le tableau d'entraînement (prepare_data.py) :
    log(1 + PSA) et densité = PSA / volume de la prostate.
    """
    if aucune_lesion:
        nb_lesions, pirads, dimension = 0, 0.0, 0.0   # codage utilisé pour « aucune lésion »

    ligne = {
        "patient_age": age,
        "log_psa": np.log1p(psa),
        "prostate_volume_mri": volume,
        "psa_density_mri": psa / volume,
        "dre_result": int(toucher_anormal),
        "prior_biopsies": nb_biopsies,
        "is_TN": int(groupe == "TN"),
        "no_of_lesions": nb_lesions,
        "pirads_max": pirads,
        "dim_max": dimension,
    }
    return pd.DataFrame([ligne])[FEATURES]


def predire(modeles, patient):
    """Probabilité estimée de cancer (classe 1) pour chaque modèle."""
    resultats = {}
    for nom, modele in modeles.items():
        colonne = list(modele.classes_).index(1)
        resultats[nom] = float(modele.predict_proba(patient)[0, colonne])
    return resultats


def comparer(probabilites):
    """Phrase pédagogique sur l'accord ou le désaccord entre les deux modèles."""
    valeurs = list(probabilites.values())
    ecart = abs(valeurs[0] - valeurs[1]) * 100
    meme_decision = (valeurs[0] >= SEUIL) == (valeurs[1] >= SEUIL)

    if meme_decision:
        accord = "Les deux modèles donnent la même prédiction au seuil de 50 %."
    else:
        accord = (
            "Les deux modèles ne donnent pas la même prédiction au seuil de 50 % : "
            "ce patient se situe près de la frontière de décision."
        )
    return f"{accord} Écart entre les deux estimations : {ecart:.0f} points de pourcentage."


# PAGE PRINCIPALE
def main():
    st.title("Démonstration")

    # SECTION 01 : INTRODUCTION
    titre_section(
        "01",
        "Comprendre la démonstration",
        "Les modèles estiment la probabilité de cancer à partir du profil d'un patient que vous décrivez."
    )

    st.html(
        """
        <section class="demo-intro-panel">
            <span class="demo-eyebrow">PRÉDICTION À PARTIR DE DONNÉES</span>
            <h3>Tester les modèles sur un patient de votre choix</h3>
            <p>
                Les variables saisies sont les mêmes que celles utilisées pour entraîner les modèles :
                des données cliniques (âge, PSA, toucher rectal, antécédents de biopsie) et des données
                de l'IRM multiparamétrique (volume prostatique, lésions, PI-RADS, dimension).
                Chaque modèle renvoie une probabilité, comparée au seuil de 50 %.
            </p>
            <div class="demo-tags">
                <span>10 variables</span>
                <span>2 modèles</span>
                <span>Résultat expérimental</span>
            </div>
        </section>
        """
    )

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.html(
            """
            <div class="demo-step-card">
                <span class="demo-step-number">1</span>
                <h4>Décrire le patient</h4>
                <p>Renseignez le profil clinique : âge, PSA, groupe, toucher rectal et biopsies antérieures.</p>
            </div>
            """
        )
    with col2:
        st.html(
            """
            <div class="demo-step-card">
                <span class="demo-step-number">2</span>
                <h4>Ajouter les données IRM</h4>
                <p>Indiquez le volume prostatique, les lésions décrites, le PI-RADS maximal et la dimension.</p>
            </div>
            """
        )
    with col3:
        st.html(
            """
            <div class="demo-step-card">
                <span class="demo-step-number">3</span>
                <h4>Lire l'estimation</h4>
                <p>Lancez la prédiction, puis comparez les deux modèles et leurs limites.</p>
            </div>
            """
        )

    encadre(
        "Résultat expérimental, pas un diagnostic",
        "Cet outil fournit une estimation statistique issue d'une base de 462 patients. "
        "Il ne constitue pas un diagnostic médical et ne doit servir à aucune décision clinique.",
        genre="avertissement"
    )

    # SECTION 02 : SAISIE
    titre_section(
        "02",
        "Saisie des données du patient",
        "Renseignez les champs puis lancez la prédiction. Les champs IRM sont ignorés si aucune lésion n'est cochée."
    )

    with st.container(border=True, key="demo_form_card"):
        with st.form("demo_formulaire"):
            col_clinique, col_irm = st.columns(2, gap="large")

            with col_clinique:
                st.markdown("#### Profil clinique")
                age = st.number_input(
                    "Âge (années)", min_value=AGE_MIN, max_value=AGE_MAX, value=68, step=1
                )
                psa = st.number_input(
                    "PSA total (ng/mL)", min_value=0.1, max_value=PSA_MAX, value=8.0, step=0.1
                )
                groupe = st.radio(
                    "Groupe clinique",
                    ["BN", "TN"],
                    horizontal=True,
                    help=(
                        "BN : patient jamais biopsié. "
                        "TN : patient ayant eu au moins une biopsie négative."
                    ),
                )
                nb_biopsies = st.number_input(
                    "Biopsies antérieures", min_value=0, max_value=9, value=0, step=1
                )
                toucher = st.radio(
                    "Toucher rectal",
                    ["Normal", "Anormal"],
                    horizontal=True,
                )

            with col_irm:
                st.markdown("#### Données de l'IRM multiparamétrique")
                volume = st.number_input(
                    "Volume prostatique (mL)",
                    min_value=VOLUME_MIN, max_value=VOLUME_MAX, value=50.0, step=0.5
                )
                aucune_lesion = st.checkbox("Aucune lésion à l'IRM")
                nb_lesions = st.number_input(
                    "Nombre de lésions",
                    min_value=1, max_value=3, value=1, step=1,
                    help="Ignoré si « Aucune lésion à l'IRM » est coché."
                )
                pirads = st.selectbox(
                    "PI-RADS maximal",
                    PIRADS_OPTIONS,
                    index=PIRADS_OPTIONS.index(4.0),
                    format_func=lambda valeur: fr(valeur, 1),
                    help="Score le plus élevé parmi les lésions décrites (ignoré si aucune lésion)."
                )
                dimension = st.number_input(
                    "Dimension maximale de la lésion (mm)",
                    min_value=0.0, max_value=DIMENSION_MAX, value=15.0, step=0.5,
                    help="Ignorée si « Aucune lésion à l'IRM » est coché."
                )

            soumis = st.form_submit_button("Lancer la prédiction", type="primary")

    if soumis:
        erreurs = valider(groupe, nb_biopsies, aucune_lesion, nb_lesions, dimension)
        if erreurs:
            st.session_state.pop(CLE_RESULTAT, None)
            for erreur in erreurs:
                st.error(erreur)
        else:
            try:
                modeles = charger_modeles()
            except FileNotFoundError:
                st.error(
                    "Les modèles entraînés sont introuvables dans le dossier models/. "
                    "Lancez d'abord `python main.py`."
                )
                return

            patient = construire_patient(
                age, psa, volume, groupe, nb_biopsies, toucher == "Anormal",
                aucune_lesion, nb_lesions, pirads, dimension
            )
            st.session_state[CLE_RESULTAT] = {
                "probabilites": predire(modeles, patient),
                "patient": patient.iloc[0].to_dict(),
            }

    # SECTION 03 : RÉSULTAT
    titre_section(
        "03",
        "Résultat de la prédiction",
        "Une probabilité estimée par modèle, à comparer au seuil de décision de 50 %."
    )

    resultat = st.session_state.get(CLE_RESULTAT)
    if resultat is None:
        encadre(
            "Aucune prédiction pour le moment",
            "Renseignez le patient dans la section 02 puis cliquez sur « Lancer la prédiction ».",
        )
    else:
        colonnes = st.columns(len(MODELES), gap="medium")
        for colonne, (nom, probabilite) in zip(colonnes, resultat["probabilites"].items()):
            with colonne:
                jauge(nom, probabilite)

        encadre("Comparaison des modèles", comparer(resultat["probabilites"]))
        valeurs_derivees(resultat["patient"])

    # SECTION 04 : INTERPRÉTATION
    titre_section(
        "04",
        "Interpréter le résultat",
        "Ce que l'estimation signifie, et ce qu'elle ne signifie pas."
    )

    st.html(
        """
        <div class="demo-interp-grid">
            <article class="demo-interp-card">
                <span class="demo-card-kicker">LIRE UNE PROBABILITÉ</span>
                <h4>Une estimation, pas une certitude</h4>
                <p>
                    Une probabilité de 70 % signifie que, parmi des patients aux caractéristiques proches
                    dans les données d'entraînement, le cancer était présent dans une proportion
                    comparable. Elle ne dit rien de certain sur le patient lui-même.
                </p>
            </article>
            <article class="demo-interp-card">
                <span class="demo-card-kicker">LE SEUIL DE 50 %</span>
                <h4>Une convention de présentation</h4>
                <p>
                    Le seuil sépare « probable » et « peu probable » pour faciliter la lecture.
                    Une probabilité proche de 50 % est une zone d'incertitude, où les deux modèles
                    peuvent facilement diverger.
                </p>
            </article>
            <article class="demo-interp-card">
                <span class="demo-card-kicker">LES DEUX MODÈLES</span>
                <h4>Deux approches, un même protocole</h4>
                <p>
                    La régression logistique est un modèle linéaire, dont la sortie est facile à relire.
                    La Random Forest combine des arbres de décision et capture des interactions entre variables.
                </p>
            </article>
        </div>
        """
    )

    encadre(
        "Limites de cette démonstration",
        "Les modèles ont été entraînés sur les 462 patients de la base AI4AR : "
        "les estimations affichées ici ne mesurent donc pas la performance sur de nouveaux patients. "
        "Ces performances, obtenues par validation croisée, sont présentées dans la page Résultats. "
        "Les données IRM dépendent de l'interprétation des radiologues et ne sont pas validées "
        "sur d'autres centres.",
        genre="avertissement"
    )


if __name__ == "__main__":
    main()
