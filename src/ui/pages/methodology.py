import streamlit as st
from html import escape

from src.ui.styles import load_page_css

# CONFIGURATION
load_page_css("methodology")

# DONNÉES ISSUES DU PIPELINE DU PROJET
PATIENTS_TOTAL = 462
CANCER_COUNT = 248
NO_CANCER_COUNT = 214

# FONCTIONS D'AFFICHAGE
def section_heading(number, title, subtitle=None):
    """Affiche un titre de section numéroté, harmonisé avec la page IA."""
    subtitle_html = f"<p>{escape(subtitle)}</p>" if subtitle else ""

    st.html(
        f"""
        <div class="ai-section-heading">
            <span class="ai-section-number">{escape(number)}</span>
            <div>
                <h2>{escape(title)}</h2>
                {subtitle_html}
            </div>
        </div>
        """
    )


def note_box(title, message, kind="info"):
    """Affiche une note visuelle cohérente avec les encadrés de la page IA."""
    st.html(
        f"""
        <div class="method-note method-note-{escape(kind)}">
            <strong>{escape(title)}</strong>
            <p>{escape(message)}</p>
        </div>
        """
    )


def timeline(items):
    """Affiche une frise verticale d'étapes."""
    rows = []
    for number, title, description in items:
        rows.append(
            f"""
            <div class="method-timeline-item">
                <span class="method-timeline-number">{escape(number)}</span>
                <div class="method-timeline-content">
                    <h4>{escape(title)}</h4>
                    <p>{escape(description)}</p>
                </div>
            </div>
            """
        )
    st.html(f'<div class="method-timeline">{"".join(rows)}</div>')


def model_card(title, label, description, details):
    details_html = "".join(f"<li>{escape(item)}</li>" for item in details)
    st.html(
        f"""
        <article class="method-model-card">
            <div class="method-model-top">
                <span class="method-model-label">{escape(label)}</span>
            </div>
            <h3>{escape(title)}</h3>
            <p>{escape(description)}</p>
            <ul>{details_html}</ul>
        </article>
        """
    )
    
# PAGE PRINCIPALE
def main():
    # INTRODUCTION
    st.title("Méthodologie")
    st.write(
        "Cette page présente les étapes suivies pour construire le jeu de données, "
        "préparer les variables, entraîner les approches étudiées et évaluer leurs performances."
    )

    st.html(
        """
        <section class="method-intro-panel">
            <div class="method-intro-content">
                <span class="method-eyebrow">DÉMARCHE EXPÉRIMENTALE</span>
                <h3>Des données médicales à l'évaluation des modèles</h3>
                <p>
                    La démarche repose sur la préparation de données cliniques et radiologiques,
                    la construction d'un tableau à l'échelle du patient, puis l'étude de plusieurs
                    approches de classification.
                </p>
                <div class="method-tags">
                    <span>AI4AR – mpMRI</span>
                    <span>10 variables d'entrée</span>
                    <span>Classification binaire</span>
                </div>
            </div>
            <div class="method-intro-visual" aria-label="Étapes de la démarche">
                <div class="method-intro-node">Données cliniques + IRM</div>
                <span class="method-intro-connector"></span>
                <div class="method-intro-node">Préparation des données</div>
                <span class="method-intro-connector"></span>
                <div class="method-intro-node method-intro-node-primary">Apprentissage</div>
                <span class="method-intro-connector"></span>
                <div class="method-intro-result">Évaluation des modèles</div>
            </div>
        </section>
        """
    )

    # SECTION 01 — VUE GLOBALE
    section_heading(
        "01",
        "Vue globale de la méthodologie",
        "Les grandes étapes suivies dans le pipeline de traitement."
    )
    st.html(
        """
        <div class="method-pipeline">
            <div class="method-pipeline-step">
                <span>ÉTAPE 01</span>
                <strong>Collecte</strong>
                <small>Fichiers clinique et radiologique</small>
            </div>
            <div class="method-pipeline-arrow">→</div>
            <div class="method-pipeline-step">
                <span>ÉTAPE 02</span>
                <strong>Préparation</strong>
                <small>Nettoyage, fusion et sélection</small>
            </div>
            <div class="method-pipeline-arrow">→</div>
            <div class="method-pipeline-step">
                <span>ÉTAPE 03</span>
                <strong>Tableau patient</strong>
                <small>Fusion et agrégation clinique–IRM</small>
            </div>
            <div class="method-pipeline-arrow">→</div>
            <div class="method-pipeline-step">
                <span>ÉTAPE 04</span>
                <strong>Apprentissage</strong>
                <small>Trois approches comparées</small>
            </div>
            <div class="method-pipeline-arrow">→</div>
            <div class="method-pipeline-step">
                <span>ÉTAPE 05</span>
                <strong>Évaluation</strong>
                <small>Validation croisée répétée</small>
            </div>
        </div>
        """
    )
    st.write(
        "Chaque patient est représenté par une seule ligne dans le tableau final. "
        "Les informations issues des lésions IRM sont d'abord résumées à l'échelle du patient, "
        "puis associées aux informations cliniques."
    )
    st.divider()

    # SECTION 02 — COLLECTE ET SÉLECTION
    section_heading(
        "02",
        "Collecte et sélection des données",
        "Deux sources complémentaires sont réunies pour constituer la population étudiée."
    )

    col_clinical, col_radiological = st.columns(2, gap="medium")

    with col_clinical:
        st.html(
            """
            <div class="method-source-card">
                <div class="method-source-icon">01</div>
                <span class="method-card-kicker">SOURCE CLINIQUE</span>
                <h3>Fichier clinique</h3>
                <p>Une ligne par patient, contenant les informations cliniques et le résultat de biopsie utilisé comme cible.</p>
            </div>
            """
        )

    with col_radiological:
        st.html(
            """
            <div class="method-source-card">
                <div class="method-source-icon">02</div>
                <span class="method-card-kicker">SOURCE RADIOLOGIQUE</span>
                <h3>Fichier radiologique</h3>
                <p>Plusieurs observations possibles pour une lésion, selon les radiologues qui l'ont décrite.</p>
            </div>
            """
        )

    st.html(
        f"""
        <div class="method-cohort-panel">
            <div class="method-cohort-heading">
                <div>
                    <span class="method-card-kicker">POPULATION RETENUE</span>
                    <h3>{PATIENTS_TOTAL} patients</h3>
                </div>
                <span class="method-cohort-caption">Groupes BN et TN · résultat de biopsie connu</span>
            </div>
            <div class="method-cohort-bar">
                <span class="method-cohort-cancer" style="width:{CANCER_COUNT / PATIENTS_TOTAL * 100:.2f}%"></span>
                <span class="method-cohort-no-cancer" style="width:{NO_CANCER_COUNT / PATIENTS_TOTAL * 100:.2f}%"></span>
            </div>
            <div class="method-cohort-legend">
                <div><span class="method-legend-dot method-dot-cancer"></span><strong>Avec cancer</strong><b>{CANCER_COUNT}</b><small>{CANCER_COUNT / PATIENTS_TOTAL:.1%}</small></div>
                <div><span class="method-legend-dot method-dot-no-cancer"></span><strong>Sans cancer</strong><b>{NO_CANCER_COUNT}</b><small>{NO_CANCER_COUNT / PATIENTS_TOTAL:.1%}</small></div>
            </div>
        </div>
        """
    )

    note_box(
        "Critère de sélection",
        "Le tableau final conserve les patients des groupes BN (Biopsy Naïve) et TN "
        "(Previous Negative Biopsies) pour lesquels la variable is_cancer est renseignée. "
        "Les autres groupes et les résultats de biopsie manquants sont exclus de cette population."
    )
    st.divider()
    
    # SECTION 03 — NETTOYAGE ET PRÉPARATION
    section_heading(
        "03",
        "Nettoyage et préparation des données",
        "Les données sont contrôlées, rapprochées et structurées avant l'apprentissage."
    )

    timeline([
        (
            "01",
            "Contrôle des fichiers bruts",
            "Suppression des espaces superflus dans les noms de colonnes et les valeurs textuelles, "
            "conversion des colonnes attendues en valeurs numériques et vérification des identifiants, "
            "des valeurs binaires et des plages définies."
        ),
        (
            "02",
            "Résumé des observations IRM",
            "Les lignes sans PI-RADS exploitable ni dimension utile sont écartées. Les avis multiples "
            "d'un même radiologue pour une même lésion sont regroupés, puis les observations des "
            "radiologues sont résumées par la médiane au niveau de chaque lésion."
        ),
        (
            "03",
            "Agrégation à l'échelle du patient",
            "Pour chaque patient, le pipeline retient le PI-RADS maximal, la dimension maximale et "
            "le nombre de lésions décrites à l'IRM."
        ),
        (
            "04",
            "Fusion clinique–IRM",
            "Le résumé radiologique est associé au fichier clinique par patient_id, avec une fusion "
            "qui conserve le nombre de lignes du fichier clinique. Les cas où l'information IRM est "
            "inconnue sont distingués des cas où aucune lésion n'est décrite."
        ),
        (
            "05",
            "Construction du tableau final",
            "La population BN/TN est sélectionnée, la cible y_cancer est créée à partir de is_cancer, "
            "puis les variables dérivées log_psa et is_TN sont ajoutées. Le tableau est contrôlé "
            "avant d'être sauvegardé."
        ),
    ])

    st.html(
        """
        <div class="method-detail-grid">
            <div class="method-detail-card">
                <span class="method-detail-label">TRANSFORMATION</span>
                <h4>log_psa</h4>
                <p>Transformation logarithmique appliquée au PSA avec <code>log1p</code>.</p>
            </div>
            <div class="method-detail-card">
                <span class="method-detail-label">VARIABLE DÉRIVÉE</span>
                <h4>is_TN</h4>
                <p>Indicateur binaire construit à partir du groupe clinique : TN = 1, BN = 0.</p>
            </div>
            <div class="method-detail-card">
                <span class="method-detail-label">CIBLE</span>
                <h4>y_cancer</h4>
                <p>Variable de classification issue de <code>is_cancer</code> : 0 = sans cancer, 1 = cancer.</p>
            </div>
        </div>
        """
    )

    note_box(
        "Gestion particulière des informations IRM manquantes",
        "Lorsqu'aucune ligne radiologique n'est disponible et que le fichier clinique n'annonce "
        "pas de lésion, les variables IRM résumées sont codées à 0. Si le fichier clinique annonce "
        "au moins une lésion mais qu'aucune ligne IRM ne correspond, les valeurs IRM restent manquantes."
    )


    st.divider()

    # SECTION 04 — PRÉTRAITEMENT ET MODÈLES
    section_heading(
        "04",
        "Prétraitement et apprentissage",
        "Les opérations qui apprennent des paramètres sont intégrées aux pipelines des modèles."
    )

    st.html(
        """
        <div class="method-preprocess-flow">
            <div class="method-preprocess-step">
                <span>ENTRÉE</span>
                <strong>Variables numériques</strong>
                <small>10 caractéristiques par patient</small>
            </div>
            <span class="method-preprocess-arrow">→</span>
            <div class="method-preprocess-step">
                <span>PRÉTRAITEMENT</span>
                <strong>Imputation médiane</strong>
                <small>Remplacement des valeurs manquantes</small>
            </div>
            <span class="method-preprocess-arrow">→</span>
            <div class="method-preprocess-step">
                <span>SELON LE MODÈLE</span>
                <strong>Mise à l'échelle</strong>
                <small>Appliquée à la régression logistique</small>
            </div>
        </div>
        """
    )

    st.markdown("#### Approches étudiées")
    st.caption("Une référence naïve et deux modèles de classification sont évalués avec le même protocole.")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        model_card(
            "Réponse naïve",
            "Référence",
            "Une baseline qui prédit systématiquement la classe majoritaire observée dans les données d'entraînement.",
            [
                "DummyClassifier",
                "Stratégie : most_frequent",
                "Permet de disposer d'un point de comparaison simple.",
            ],
        )

    with col2:
        model_card(
            "Régression logistique",
            "Modèle linéaire",
            "Un modèle de classification qui estime l'appartenance à une classe à partir des variables d'entrée.",
            [
                "Imputation par médiane",
                "StandardScaler après imputation",
                "max_iter = 1000",
            ],
        )

    with col3:
        model_card(
            "Random Forest",
            "Ensemble d'arbres",
            "Un ensemble d'arbres de décision dont les prédictions sont combinées pour produire une classification.",
            [
                "Imputation par médiane",
                "300 arbres de décision",
                "Pas de standardisation dans le pipeline",
            ],
        )
    st.divider()

    # SECTION 05 — ÉVALUATION
    section_heading(
        "05",
        "Protocole d'évaluation",
        "Une validation croisée stratifiée et répétée permet de comparer les approches."
    )

    st.html(
        """
        <div class="method-cv-panel">
            <div class="method-cv-summary">
                <div>
                    <span class="method-card-kicker">VALIDATION CROISÉE</span>
                    <strong>5 plis × 3 répétitions</strong>
                    <p>15 évaluations par approche</p>
                </div>
                <div class="method-cv-badge">Repeated Stratified K-Fold</div>
            </div>
            <div class="method-cv-repeats">
                <div class="method-repeat">
                    <span>Répétition 1</span>
                    <div class="method-folds"><i></i><i></i><i></i><i></i><i></i></div>
                </div>
                <div class="method-repeat">
                    <span>Répétition 2</span>
                    <div class="method-folds"><i></i><i></i><i></i><i></i><i></i></div>
                </div>
                <div class="method-repeat">
                    <span>Répétition 3</span>
                    <div class="method-folds"><i></i><i></i><i></i><i></i><i></i></div>
                </div>
            </div>
            <p class="method-cv-caption">Chaque répétition répartit les patients en cinq plis en conservant autant que possible la proportion des classes.</p>
        </div>
        """
    )

    st.markdown("#### Indicateurs de performance")

    metric_col1, metric_col2, metric_col3 = st.columns(3, gap="medium")

    with metric_col1:
        st.html(
            """
            <div class="method-metric-card">
                <span>01</span><h4>ROC-AUC</h4>
                <p>Mesure la capacité du modèle à distinguer les deux classes sur différents seuils.</p>
            </div>
            """
        )

    with metric_col2:
        st.html(
            """
            <div class="method-metric-card">
                <span>02</span><h4>Balanced Accuracy</h4>
                <p>Moyenne des taux de bonne classification calculés séparément pour chaque classe.</p>
            </div>
            """
        )

    with metric_col3:
        st.html(
            """
            <div class="method-metric-card">
                <span>03</span><h4>Accuracy</h4>
                <p>Proportion totale de prédictions correctes parmi les observations évaluées.</p>
            </div>
            """
        )

    note_box(
        "Limiter les fuites entre entraînement et validation",
        "À chaque pli, le pipeline est réajusté uniquement sur les données d'entraînement du pli. "
        "Les médianes d'imputation et les paramètres de standardisation ne sont donc pas appris "
        "à partir des patients utilisés pour la validation."
    )


if __name__ == "__main__":
    main()
