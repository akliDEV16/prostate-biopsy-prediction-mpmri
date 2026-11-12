
import streamlit as st
from html import escape

from src.ui.styles import load_page_css


# ============================================================
# CONFIGURATION
# ============================================================

load_page_css("ai_project")


# ============================================================
# DONNÉES DU PROJET
# ============================================================

PATIENTS_TOTAL = 462
CANCER_COUNT = 248
NO_CANCER_COUNT = 214

FEATURES = [
    {
        "name": "Âge du patient",
        "variable": "patient_age",
        "description": (
            "Âge du patient au moment de l'étude."
        ),
        "category": "clinical",
    },
    {
        "name": "PSA",
        "variable": "log_psa",
        "description": (
            "Valeur du PSA après transformation logarithmique "
            "pour réduire son asymétrie."
        ),
        "category": "clinical",
    },
    {
        "name": "Toucher rectal",
        "variable": "dre_result",
        "description": (
            "Résultat du toucher rectal enregistré dans "
            "les données cliniques."
        ),
        "category": "clinical",
    },
    {
        "name": "Antécédents de biopsies",
        "variable": "prior_biopsies",
        "description": (
            "Nombre de biopsies antérieures."
        ),
        "category": "clinical",
    },
    {
        "name": "Groupe clinique",
        "variable": "is_TN",
        "description": (
            "Indicateur précisant l'appartenance au groupe TN "
            "plutôt qu'au groupe BN."
        ),
        "category": "clinical",
    },
    {
        "name": "Volume prostatique",
        "variable": "prostate_volume_mri",
        "description": (
            "Volume de la prostate mesuré à partir de l'IRM."
        ),
        "category": "prostate",
    },
    {
        "name": "Densité du PSA",
        "variable": "psa_density_mri",
        "description": (
            "Densité du PSA calculée à partir des informations "
            "disponibles dans l'examen IRM."
        ),
        "category": "prostate",
    },
    {
        "name": "Nombre de lésions",
        "variable": "no_of_lesions",
        "description": (
            "Nombre de lésions indiqué dans les données cliniques."
        ),
        "category": "radiology",
    },
    {
        "name": "PI-RADS maximal",
        "variable": "pirads_max",
        "description": (
            "Score PI-RADS le plus élevé parmi les lésions "
            "décrites pour le patient."
        ),
        "category": "radiology",
    },
    {
        "name": "Dimension maximale",
        "variable": "dim_max",
        "description": (
            "Dimension maximale des lésions décrites à l'IRM."
        ),
        "category": "radiology",
    },
]


MODEL_RESULTS = {
    "Régression logistique": {
        "auc": 0.9013,
        "balanced_accuracy": 0.8220,
        "accuracy": 0.8240,
        "description": (
            "Un modèle statistique qui estime la probabilité "
            "d'appartenance à une classe à partir des variables "
            "médicales fournies."
        ),
    },
    "Random Forest": {
        "auc": 0.8994,
        "balanced_accuracy": 0.8211,
        "accuracy": 0.8225,
        "description": (
            "Un ensemble d'arbres de décision dont les prédictions "
            "sont combinées pour produire une classification."
        ),
    },
}


# ============================================================
# FONCTIONS D'AFFICHAGE
# ============================================================

def section_heading(number, title, subtitle=None):
    """Affiche le titre d'une section."""

    subtitle_html = (
        f"<p>{subtitle}</p>"
        if subtitle else ""
    )

    st.html(
        f"""
        <div class="ai-section-heading">
            <span class="ai-section-number">{number}</span>

            <div>
                <h2>{title}</h2>
                {subtitle_html}
            </div>
        </div>
        """
    )


def info_card(icon, title, description, variable=None):
    """Affiche une carte descriptive."""

    variable_html = (
        f'<span class="ai-variable-name">{variable}</span>'
        if variable else ""
    )

    st.html(
        f"""
        <div class="ai-info-card">
            <div class="ai-card-icon">{icon}</div>

            <div class="ai-card-content">
                <h4>{title}</h4>
                {variable_html}
                <p>{description}</p>
            </div>
        </div>
        """
    )


def resource_link(label, url, description=None):
    """Affiche un lien vers une ressource externe."""

    description_html = (
        f'<p class="ai-resource-description">{description}</p>'
        if description else ""
    )

    st.html(
        f"""
        <div class="ai-resource">
            <a href="{url}" target="_blank"
               rel="noopener noreferrer">
                <span>{label}</span>
                <span class="ai-resource-arrow">↗</span>
            </a>
            {description_html}
        </div>
        """
    )


def model_card(number, title, tag, description, details):
    """Affiche une carte de présentation d'un modèle."""

    details_html = "".join(
        f"<li>{item}</li>"
        for item in details
    )

    st.html(
        f"""
        <div class="ai-model-card">

            <div class="ai-model-top">
                <span class="ai-model-number">{number}</span>
                <span class="ai-model-tag">{tag}</span>
            </div>

            <h3>{title}</h3>

            <p>{description}</p>

            <ul>
                {details_html}
            </ul>

        </div>
        """
    )


def feature_group(title, subtitle, features):
    """Affiche les variables d'un groupe avec détails au survol."""

    st.markdown(f"#### {title}")
    st.caption(subtitle)

    cards_html = "".join(
        f"""
        <div class="ai-feature-card" tabindex="0">
            <div class="ai-feature-front">
                <h4>{escape(feature['name'])}</h4>

            </div>
            <div class="ai-feature-tooltip">
                <span class="ai-feature-code">{escape(feature['variable'])}</span>
                <p>{escape(feature['description'])}</p>
            </div>
        </div>
        """
        for feature in features
    )

    st.html(f'<div class="ai-feature-grid">{cards_html}</div>')


def pipeline_timeline(steps):
    """Affiche les étapes de préparation sous forme de frise verticale."""

    steps_html = "".join(
        f"""
        <div class="ai-timeline-item">
            <span class="ai-timeline-number">{number}</span>
            <div class="ai-timeline-content">
                <h4>{escape(title)}</h4>
                <p>{escape(description)}</p>
            </div>
        </div>
        """
        for number, title, description in steps
    )

    st.html(f'<div class="ai-timeline">{steps_html}</div>')


# ============================================================
# PAGE PRINCIPALE
# ============================================================

def main():

    # --------------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------------

    st.title("Notre intelligence artificielle")

    st.write(
        """
        Derrière ProstaAI se trouve une approche de Machine Learning
        qui exploite des informations cliniques et radiologiques
        pour estimer la présence ou l'absence d'un cancer
        de la prostate.
        """
    )

    st.html(
        """
        <div class="ai-intro-panel">

            <div class="ai-intro-content">
                <span class="ai-eyebrow">APPROCHE DE MACHINE LEARNING</span>

                <h3>Transformer les données médicales en prédiction</h3>

                <p>
                    À partir de caractéristiques recueillies avant
                    la biopsie, ProstaAI étudie les relations entre
                    les informations médicales et le résultat
                    de la biopsie.
                </p>

                <div class="ai-intro-tags">
                    <span>Classification binaire</span>
                    <span>Données structurées</span>
                    <span>Machine Learning</span>
                </div>
            </div>

            <div class="ai-intro-visual">
                <div class="ai-visual-node">Données médicales</div>
                <div class="ai-visual-line"></div>
                <div class="ai-visual-node ai-visual-model">
                    Modèle IA
                </div>
                <div class="ai-visual-line"></div>
                <div class="ai-visual-output">
                    <span>Présence ou absence</span>
                    <strong>de cancer</strong>
                </div>
            </div>

        </div>
        """
    )

    st.info(
        "ProstaAI est un projet expérimental de recherche. "
        "Ses prédictions ne remplacent ni une biopsie, "
        "ni l'avis d'un professionnel de santé."
    )

    st.divider()

    # --------------------------------------------------------
    # SECTION 01 : PRINCIPE DE L'APPROCHE IA
    # --------------------------------------------------------

    section_heading(
        "01",
        "Comment fonctionne notre approche IA ?",
        "Comprendre le principe de la classification binaire."
    )

    st.write(
        """
        L'objectif de ProstaAI est d'apprendre à partir de données
        médicales déjà associées à un résultat de biopsie connu.
        Les modèles recherchent des relations entre les différentes
        caractéristiques des patients et la classe à prédire.
        """
    )

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        info_card(
            "01",
            "Classe négative",
            (
                "La biopsie de référence ne met pas en évidence "
                "de cancer. Cette situation correspond à la classe 0."
            ),
            "is_cancer = 0",
        )

    with col2:
        info_card(
            "02",
            "Classe positive",
            (
                "La biopsie de référence met en évidence un cancer. "
                "Cette situation correspond à la classe 1."
            ),
            "is_cancer = 1",
        )

    st.html(
        """
        <div class="ai-note">
            <strong>À retenir</strong>
            <p>
                Le modèle apprend à partir du résultat de biopsie
                utilisé comme cible pendant l'entraînement.
                Les variables d'entrée sont sélectionnées pour
                être disponibles avant cette biopsie.
            </p>
        </div>
        """
    )

    st.divider()

    # --------------------------------------------------------
    # SECTION 02 : BASE DE DONNEES
    # --------------------------------------------------------

    section_heading(
        "02",
        "La base de données utilisée",
        "Une base clinique et radiologique consacrée à l'IRM multiparamétrique."
    )

    st.write(
        """
        Le projet s'appuie sur la base AI4AR – mpMRI Database.
        Les données cliniques et radiologiques ont été nettoyées,
        fusionnées puis sélectionnées afin de construire un tableau
        d'apprentissage contenant une ligne par patient.
        """
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.metric(
            "Patients retenus",
            f"{PATIENTS_TOTAL}",
            help="Effectif du tableau final utilisé dans le projet.",
        )

    with col2:
        st.metric(
            "Avec cancer",
            f"{CANCER_COUNT}",
            f"{CANCER_COUNT / PATIENTS_TOTAL:.1%}",
        )

    with col3:
        st.metric(
            "Sans cancer",
            f"{NO_CANCER_COUNT}",
            f"{NO_CANCER_COUNT / PATIENTS_TOTAL:.1%}",
        )

    st.markdown("#### Répartition des classes")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="ai-class-row">
                <span class="ai-class-dot ai-dot-positive"></span>
                <strong>Cancer</strong>
                <span>{CANCER_COUNT} patients</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(CANCER_COUNT / PATIENTS_TOTAL)

        st.markdown(
            f"""
            <div class="ai-class-row">
                <span class="ai-class-dot ai-dot-negative"></span>
                <strong>Pas de cancer</strong>
                <span>{NO_CANCER_COUNT} patients</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(NO_CANCER_COUNT / PATIENTS_TOTAL)

    with col2:
        st.html(
            """
            <div class="ai-dataset-note">
                <h4>Population étudiée</h4>
                <p>
                    L'étude retient les groupes cliniques BN
                    (Biopsy Naïve) et TN (Previous Negative Biopsies),
                    pour lesquels le résultat de biopsie est connu.
                </p>
                <p>
                    Les patients appartenant aux autres groupes
                    ne sont pas inclus dans le tableau final
                    d'apprentissage.
                </p>
            </div>
            """
        )

    resource_link(
        "Consulter la base AI4AR",
        "https://ai4ar.opi.org.pl/en/the-mpmri-database/",
        "Source des données cliniques et radiologiques.",
    )

    st.divider()

    # --------------------------------------------------------
    # SECTION 03 : VARIABLES
    # --------------------------------------------------------

    section_heading(
        "03",
        "Quelles informations sont exploitées ?",
        "Dix variables décrivent chaque patient avant la biopsie."
    )

    st.write(
        """
        Les modèles utilisent dix caractéristiques numériques.
        Elles regroupent des informations cliniques, des mesures
        prostatiques et des caractéristiques radiologiques.
        """
    )

    clinical_features = [
        f for f in FEATURES if f["category"] == "clinical"
    ]

    prostate_features = [
        f for f in FEATURES if f["category"] == "prostate"
    ]

    radiology_features = [
        f for f in FEATURES if f["category"] == "radiology"
    ]

    with st.expander(
        "Informations cliniques",
        expanded=True,
    ):
        feature_group(
            "Données cliniques",
            "Informations relatives au patient et à son historique médical.",
            clinical_features,
        )

    with st.expander(
        "Caractéristiques prostatiques",
        expanded=True,
    ):
        feature_group(
            "Mesures prostatiques",
            "Mesures associées à la prostate et au PSA.",
            prostate_features,
        )

    with st.expander(
        "Informations radiologiques",
        expanded=True,
    ):
        feature_group(
            "Caractéristiques de l'IRM",
            "Informations extraites des descriptions radiologiques des lésions.",
            radiology_features,
        )

    st.html(
        """
        <div class="ai-note">
            <strong>Une distinction importante</strong>
            <p>
                Les modèles n'analysent pas directement les images
                IRM. Ils exploitent des caractéristiques structurées
                issues des informations cliniques et des descriptions
                radiologiques.
            </p>
        </div>
        """
    )

    st.divider()

    # --------------------------------------------------------
    # SECTION 04 : PREPARATION DES DONNEES
    # --------------------------------------------------------

    section_heading(
        "04",
        "De la donnée à l'apprentissage",
        "Les données passent par plusieurs étapes avant d'être utilisées."
    )

    st.write(
        """
        Avant l'entraînement, les données brutes doivent être
        contrôlées, nettoyées et transformées. Les informations
        cliniques et radiologiques sont ensuite regroupées
        au niveau de chaque patient.
        """
    )

    pipeline_steps = [
        (
            "01",
            "Chargement des données",
            "Lecture des fichiers cliniques et radiologiques de la base AI4AR.",
        ),
        (
            "02",
            "Nettoyage et contrôle",
            "Correction des formats, conversion des valeurs et vérification de cohérence.",
        ),
        (
            "03",
            "Fusion des informations",
            "Association des données cliniques et du résumé radiologique pour chaque patient.",
        ),
        (
            "04",
            "Sélection et construction",
            "Sélection des groupes BN et TN, création de la cible et des variables dérivées.",
        ),
        (
            "05",
            "Imputation des valeurs manquantes",
            "Remplacement des valeurs manquantes par la médiane calculée sur les données d'entraînement.",
        ),
        (
            "06",
            "Mise à l'échelle",
            "Standardisation des variables pour la régression logistique. Cette étape n'est pas nécessaire pour Random Forest.",
        ),
        (
            "07",
            "Entraînement et évaluation",
            "Apprentissage des modèles et estimation de leurs performances par validation croisée.",
        ),
    ]

    pipeline_timeline(pipeline_steps)

    st.html(
        """
        <div class="ai-note">
            <strong>Prévention de la fuite de données</strong>
            <p>
                L'imputation et la standardisation sont intégrées
                aux pipelines et ajustées uniquement sur les données
                d'entraînement de chaque pli de validation croisée.
                Cela évite d'utiliser indirectement les informations
                du pli de validation pendant le prétraitement.
            </p>
        </div>
        """
    )

    st.divider()

    # --------------------------------------------------------
    # SECTION 05 : MODELES
    # --------------------------------------------------------

    section_heading(
        "05",
        "Les modèles de Machine Learning",
        "Deux approches de classification ont été développées et comparées."
    )

    st.write(
        """
        Le projet étudie deux modèles complémentaires.
        La régression logistique constitue une approche statistique
        de classification, tandis que Random Forest combine
        plusieurs arbres de décision.
        """
    )

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        model_card(
            "01",
            "Régression logistique",
            "Modèle statistique",
            (
                "Elle estime une probabilité d'appartenance "
                "à une classe à partir d'une combinaison "
                "des variables d'entrée."
            ),
            [
                "Modèle de classification supervisée.",
                "Utilise une combinaison pondérée des variables.",
                "Nécessite une mise à l'échelle dans notre pipeline.",
                "Fournit une probabilité exploitable pour la classification.",
            ],
        )

    with col2:
        model_card(
            "02",
            "Random Forest",
            "Ensemble d'arbres",
            (
                "Il construit plusieurs arbres de décision "
                "et combine leurs prédictions pour obtenir "
                "une classification."
            ),
            [
                "Modèle de classification supervisée.",
                "Utilise 300 arbres dans notre configuration.",
                "Peut représenter des relations non linéaires.",
                "Ne nécessite pas de standardisation dans notre pipeline.",
            ],
        )

    st.html(
        """
        <div class="ai-note">
            <strong>Pourquoi comparer deux modèles ?</strong>
            <p>
                Un modèle plus complexe n'est pas nécessairement
                plus performant. La comparaison permet d'étudier
                les résultats obtenus avec deux approches différentes
                sur les mêmes données et selon le même protocole
                d'évaluation.
            </p>
        </div>
        """
    )

    st.divider()

    # --------------------------------------------------------
    # SECTION 06 : EVALUATION
    # --------------------------------------------------------

    section_heading(
        "06",
        "Comment évaluer les modèles ?",
        "Les performances sont estimées par validation croisée répétée."
    )

    st.write(
        """
        Pour éviter de dépendre d'un seul découpage des données,
        les modèles sont évalués avec une validation croisée
        stratifiée répétée : cinq plis, répétés trois fois,
        soit quinze évaluations.
        """
    )
   

    st.markdown("#### Comparaison des performances moyennes")

    results_table = {
        "Métrique": [
            "AUC",
            "Balanced Accuracy",
            "Accuracy",
        ],
        "Régression logistique": [
            "90,13 %",
            "82,20 %",
            "82,40 %",
        ],
        "Random Forest": [
            "89,94 %",
            "82,11 %",
            "82,25 %",
        ],
    }

    table_rows = "".join(
        f"""
        <tr>
            <th scope="row">{escape(metric)}</th>
            <td>{escape(logistic)}</td>
            <td>{escape(forest)}</td>
        </tr>
        """
        for metric, logistic, forest in zip(
            results_table["Métrique"],
            results_table["Régression logistique"],
            results_table["Random Forest"],
        )
    )

    st.html(
        f"""
        <div class="ai-results-table-wrapper">
            <table class="ai-results-table">
                <thead>
                    <tr>
                        <th>Métrique</th>
                        <th>Régression logistique</th>
                        <th>Random Forest</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
        """
    )

    st.caption(
        "Valeurs moyennes obtenues sur les quinze découpages "
        "de validation croisée. Les résultats détaillés et "
        "leur interprétation seront présentés dans la page Résultats."
    )

main()
