import streamlit as st

from src.ui.styles import load_page_css

load_page_css("home")


def render_navigation_card(
    key,
    icon,
    title,
    description,
    page_path
):
    """
    Affiche une carte interactive :
    - État normal : icône et titre.
    - Survol : description à la place du contenu initial.
    """

    if st.button(
        title,
        key=key,
        icon=icon,
        use_container_width=True,
        type="secondary"
    ):
        st.switch_page(page_path)

def main():

    # SECTION 1 : PRESENTATION PRINCIPALE
    st.title("ProstaAI")

    st.subheader(
        "Explorer le potentiel de l'IA dans "
        "l'analyse du cancer de la prostate."
    )

    st.write(
        """
        Un projet de recherche consacré à l'estimation
        du résultat d'une biopsie prostatique à partir
        de données cliniques et radiologiques issues
        de l'IRM multiparamétrique.
        """
    )

    if st.button(
        "Explorer la démonstration",
        key="main_demo_button",
        type="primary"
    ):
        st.switch_page(
            "src/ui/pages/demonstration.py"
        )

    st.divider()

    # SECTION 2 : CHIFFRES CLES

    st.markdown("### ProstaAI en chiffres")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Patients étudiés",
            value=" "
        )

    with col2:
        st.metric(
            label="Variables utilisées",
            value=" "
        )

    with col3:
        st.metric(
            label="Modèles étudiés",
            value=" "
        )

    st.divider()

    # SECTION 3 : EXPLORER LE PROJET
    st.markdown("### Explorer le projet")

    st.write(
        "Accédez aux différentes sections pour découvrir "
        "notre démarche et nos résultats."
    )

    # Première rangée
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        render_navigation_card(
            key="card_subject",
            icon=":material/medical_services:",
            title="Comprendre le sujet",
            description=(
                "Découvrez le cancer de la prostate, "
                "les biopsies et les données utilisées "
                "dans notre étude."
            ),
            page_path="src/ui/pages/prostate_cancer.py"
        )

    with col2:
        render_navigation_card(
            key="card_ai",
            icon=":material/psychology:",
            title="Notre intelligence artificielle",
            description=(
                "Découvrez les modèles de Machine Learning "
                "et leur rôle dans notre projet."
            ),
            page_path="src/ui/pages/ai_project.py"
        )

    # Deuxième rangée
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        render_navigation_card(
            key="card_results",
            icon=":material/monitoring:",
            title="Résultats expérimentaux",
            description=(
                "Explorez les performances et les résultats "
                "de l'évaluation des modèles."
            ),
            page_path="src/ui/pages/results.py"
        )

    with col2:
        render_navigation_card(
            key="card_methodology",
            icon=":material/account_tree:",
            title="Méthodologie",
            description=(
                "Suivez les étapes de préparation des données, "
                "d'entraînement et d'évaluation."
            ),
            page_path="src/ui/pages/methodology.py"
        )


main()
