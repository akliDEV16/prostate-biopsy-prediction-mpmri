
import streamlit as st
import streamlit.components.v1 as components

from src.ui.styles import load_page_css

# Configuration
load_page_css("prostate_cancer")

# Illustrations SVG
PROSTATE_LESION_SVG = """
<svg viewBox="0 0 620 300" xmlns="http://www.w3.org/2000/svg">
    <rect width="620" height="300" rx="16" fill="#F4F9FD"/>

    <!-- Prostate -->
    <path d="M165 110
             C190 55 270 55 310 85
             C350 55 430 55 455 110
             C490 190 420 245 310 245
             C200 245 130 190 165 110 Z"
          fill="#E8B3A6" stroke="#C8796C" stroke-width="4"/>

    <!-- Urètre -->
    <path d="M310 75 L310 240"
          stroke="#438CCB" stroke-width="12"
          stroke-linecap="round"/>

    <!-- Lésion schématique -->
    <path d="M375 120
             C395 100 425 112 428 135
             C435 160 410 180 385 170
             C365 160 360 140 375 120 Z"
          fill="#F43F5E" stroke="#C52F4A" stroke-width="3"/>

    <!-- Légendes -->
    <g font-family="Arial" font-size="16" fill="#34536B">
        <text x="30" y="70">Tissu prostatique</text>
        <path d="M150 75 L190 100"
              stroke="#6D8AA1" stroke-width="1.5"/>

        <text x="455" y="120">Zone suspecte</text>
        <path d="M445 125 L425 140"
              stroke="#6D8AA1" stroke-width="1.5"/>

        <text x="455" y="220">Urètre</text>
        <path d="M445 215 L320 215"
              stroke="#6D8AA1" stroke-width="1.5"/>
    </g>
</svg>
"""

# Fonctions d'affichage
def display_svg(svg_content, height=350):
    """Affiche une illustration SVG dans un document HTML isolé."""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow: hidden;
            }}

            svg {{
                display: block;
                width: 100%;
                height: auto;
                max-height: {height}px;
            }}
        </style>
    </head>
    <body>
        {svg_content}
    </body>
    </html>
    """

    components.html(
        html_content,
        height=height,
        scrolling=False
    )


def section_heading(title):
    """Affiche le titre d'une section."""

    st.html(
        f"""
        <div class="medical-section-heading">
            <h2>{title}</h2>
        </div>
        """
    )


def resource_link(label, url, description=None):
    """Affiche un lien vers une ressource externe."""

    description_html = (
        f'<span class="resource-description">{description}</span>'
        if description else ""
    )

    st.html(
        f"""
        <a class="resource-link"
           href="{url}"
           target="_blank"
           rel="noopener noreferrer">

            <span>{label}</span>
            <span class="resource-arrow">↗</span>

        </a>

        {description_html}
        """
    )


def info_card(icon, title, description):
    """Affiche une carte informative."""

    with st.container(border=True):
        st.markdown(f"#### {icon} {title}")
        st.write(description)


def biopsy_process():
    """Affiche les étapes allant du prélèvement au résultat."""

    steps = [
        (
            "01",
            "Prélèvement des tissus",
            "Plusieurs fragments de tissu prostatique sont prélevés "
            "à l'aide d'une aiguille."
        ),
        (
            "02",
            "Analyse anatomopathologique",
            "Les fragments prélevés sont examinés au microscope "
            "par un anatomopathologiste afin de rechercher "
            "d'éventuelles cellules cancéreuses."
        ),
        (
            "03",
            "Établissement du résultat",
            "Un compte rendu précise la présence ou l'absence "
            "de cellules cancéreuses dans les tissus analysés."
        )
    ]

    steps_html = ""

    for number, title, description in steps:
        steps_html += f"""
            <div class="biopsy-list-item">

                <span class="biopsy-list-number">
                    {number}
                </span>

                <div class="biopsy-list-content">
                    <strong>{title}</strong>
                    <p>{description}</p>
                </div>

            </div>
        """

    st.html(
        f"""
        <div class="biopsy-list">
            {steps_html}
        </div>
        """
    )

# Contenu de la page
def main():

    # En-tête
    st.title("Comprendre le cancer de la prostate")
    st.markdown(
        """
        Découvrez la prostate, les principaux éléments associés
        au cancer prostatique et les examens utilisés dans son
        exploration, de la mesure du PSA à la biopsie.
        """
    )
    st.divider()

    # 1. Anatomie de la prostate
    section_heading(
        "La prostate : une petite glande, un rôle important"
    )
    col_image, col_text = st.columns(
        [1, 1],
        gap="small"
    )
    with col_image:
        st.image(
            "https://www.prostate.fr/wp-content/uploads/sites/12/2014/10/prostate-legende.jpg",
            caption=(
                "Schéma anatomique simplifié à visée pédagogique. "
                "Il ne représente pas une image médicale réelle. "
                "Source : prostate.fr"
            ),
            use_container_width=True
        )
    with col_text:
        st.markdown(
            """
            La **prostate** est une glande de l'appareil reproducteur
            masculin. Elle se situe :

            - sous la vessie ;
            - devant le rectum ;
            - autour de la partie initiale de l'urètre.

            Elle participe à la production du liquide constituant
            le sperme.

            Avec l'âge, son volume peut augmenter. Cette augmentation
            n'est pas nécessairement liée à un cancer.

            L'hyperplasie bénigne de la prostate (HBP) est une
            augmentation non cancéreuse du volume prostatique.
            """
        )
    resource_link(
        "Consulter : anatomie de la prostate — SEER",
        "https://training.seer.cancer.gov/prostate/anatomy/"
    )
    st.divider()

    # 2. Comprendre le cancer
    section_heading(
        "Qu'est-ce que le cancer de la prostate ?"
    )
    col1, col2 = st.columns(2)
    with col1:
        st.html(
            """
            <div class="comparison-card">
                <h3>Organisation habituelle</h3>

                <p>
                    Les cellules se développent et se renouvellent
                    selon les mécanismes habituels de l'organisme.
                </p>
            </div>
            """
        )
    with col2:
        st.html(
            """
            <div class="comparison-card">
                <h3>Développement anormal</h3>

                <p>
                    Certaines cellules acquièrent des anomalies
                    et peuvent se multiplier de manière incontrôlée.
                </p>
            </div>
            """
        )
    display_svg(
        PROSTATE_LESION_SVG,
        height=300
    )
    st.caption(
        "Représentation conceptuelle d'une zone suspecte dans la prostate."
    )
    st.markdown(
        """
        L’IRM permet de repérer et d’évaluer une zone suspecte ; seule l’analyse histologique d’un prélèvement permet de confirmer un cancer.

        Le cancer de la prostate se développe à partir de cellules
        prostatiques. Son évolution est variable : certaines formes
        progressent lentement, tandis que d'autres peuvent être plus
        agressives.
        """
    )
    st.warning(
        """
        La présence d'un facteur de risque, d'un PSA élevé ou d'une
        anomalie à l'IRM ne suffit pas à confirmer un cancer.
        """
    )
    resource_link(
        "Comprendre les modifications de la prostate — NCI",
        "https://www.cancer.gov/types/prostate/understanding-prostate-changes"
    )
    st.divider()

    # 3. Facteurs de risque et manifestations
    section_heading(
        "Facteurs de risque et manifestations"
    )

    risk_col1, risk_col2 = st.columns(2)

    with risk_col1:

        st.markdown("#### Facteurs de risque")

        info_card(
            "◷",
            "Âge",
            "Le risque de cancer de la prostate augmente avec l'âge."
        )

        info_card(
            "⌂",
            "Antécédents familiaux",
            "Avoir un parent proche atteint peut augmenter le risque."
        )

        info_card(
            "◇",
            "Facteurs génétiques",
            "Certaines modifications héréditaires, notamment BRCA1 "
            "et BRCA2, peuvent être associées à un risque accru."
        )

    with risk_col2:

        st.markdown("#### Manifestations possibles")

        info_card(
            "↕",
            "Troubles urinaires",
            "Difficultés à uriner, jet faible ou besoin fréquent "
            "d'uriner. Ces signes ne sont pas spécifiques au cancer."
        )

        info_card(
            "!",
            "Signes tardifs",
            "Certaines formes avancées peuvent s'accompagner de douleurs "
            "osseuses ou d'autres symptômes."
        )

        info_card(
            "!",
            "Absence de symptômes",
            "Un cancer de la prostate peut être présent sans provoquer "
            "de symptômes, notamment à un stade précoce."
        )

    st.warning(
        "Les symptômes urinaires peuvent également être liés à une "
        "hyperplasie bénigne ou à d'autres affections. Ils ne permettent "
        "pas, à eux seuls, de diagnostiquer un cancer."
    )

    resource_link(
        "Facteurs de risque et symptômes — NCI",
        "https://www.cancer.gov/types/prostate/understanding-prostate-changes"
    )

    st.divider()

    # 4. Examens pré-biopsie
    section_heading(
        "Les examens avant la biopsie"
    )

    tab_psa, tab_dre, tab_irm = st.tabs(
        [
            "PSA",
            "Toucher rectal",
            "IRM multiparamétrique"
        ]
    )

    # PSA
    with tab_psa:

        st.markdown("### Antigène prostatique spécifique (PSA)")

        st.markdown(
            """
            Le PSA est une protéine produite principalement
            par la prostate et mesurée dans le sang.

            Une concentration élevée peut être observée dans
            différentes situations :

            - cancer de la prostate ;
            - hyperplasie bénigne ;
            - inflammation ou infection prostatique ;
            - autres facteurs temporaires.

            Le PSA n'est donc pas un marqueur spécifique du cancer.
            """
        )

        resource_link(
            "Comprendre le test PSA — NCI",
            "https://www.cancer.gov/types/prostate/psa-fact-sheet"
        )

    # Toucher rectal
    with tab_dre:

        st.markdown("### Toucher rectal (DRE)")

        st.markdown(
            """
            Le toucher rectal est un examen clinique permettant au
            professionnel de santé de palper la prostate à travers
            la paroi rectale.

            Il peut notamment permettre de rechercher :

            - une irrégularité de la surface ;
            - une zone dure ou un nodule ;
            - une asymétrie ou une anomalie de consistance.

            Cet examen ne permet pas, à lui seul, de confirmer
            ou d'exclure un cancer.
            """
        )

        st.info(
            "Dans le projet ProstaAI, le résultat du toucher rectal "
            "constitue une variable clinique parmi les données étudiées."
        )

    # IRM multiparamétrique
    with tab_irm:

        st.markdown("### IRM multiparamétrique de la prostate")

        st.markdown(
            """
            L'IRM multiparamétrique (mpMRI) combine plusieurs séquences
            d'imagerie afin de caractériser les tissus prostatiques
            et de localiser d'éventuelles lésions suspectes.

            Elle peut notamment apporter des informations sur :

            - la localisation des lésions ;
            - leur dimension ;
            - leur apparence sur différentes séquences ;
            - leur classification PI-RADS.
            """
        )

        st.html(
            """
            <div class="irm-feature-grid">
                <div>
                    <strong>T2</strong>
                    <span>Informations anatomiques</span>
                </div>

                <div>
                    <strong>DWI / ADC</strong>
                    <span>Diffusion de l'eau</span>
                </div>

                <div>
                    <strong>DCE</strong>
                    <span>Rehaussement dynamique</span>
                </div>
            </div>
            """
        )

        resource_link(
            "Comprendre un compte rendu d'IRM prostatique — RadiologyInfo",
            "https://www.radiologyinfo.org/en/info/article-prostate-mri-report"
        )

    st.divider()

    # 5. Classification PI-RADS interactive
    section_heading(
        "La classification PI-RADS"
    )

    st.markdown(
        """
        Le système PI-RADS standardise la description des anomalies
        observées à l'IRM prostatique. Il classe le niveau de suspicion
        de cancer prostatique cliniquement significatif.
        """
    )

    pirads_descriptions = {
        1: {
            "level": "Très faible",
            "description": (
                "Un cancer cliniquement significatif est très peu probable."
            ),
            "color": "#10B981"
        },
        2: {
            "level": "Faible",
            "description": (
                "Un cancer cliniquement significatif est peu probable."
            ),
            "color": "#72B99A"
        },
        3: {
            "level": "Intermédiaire",
            "description": (
                "Le résultat est indéterminé : la présence d'un cancer "
                "significatif est équivoque."
            ),
            "color": "#D6A64B"
        },
        4: {
            "level": "Élevé",
            "description": (
                "Un cancer cliniquement significatif est probable."
            ),
            "color": "#E78B69"
        },
        5: {
            "level": "Très élevé",
            "description": (
                "Un cancer cliniquement significatif est très probable."
            ),
            "color": "#D95B68"
        }
    }

    selected_pirads = st.radio(
        "Sélectionnez une catégorie PI-RADS :",
        options=[1, 2, 3, 4, 5],
        horizontal=True,
        format_func=lambda value: f"PI-RADS {value}",
        key="selected_pirads"
    )

    pirads_info = pirads_descriptions[selected_pirads]

    st.html(
        f"""
        <div class="pirads-detail">
            <div class="pirads-score"
                 style="background-color: {pirads_info['color']}">
                {selected_pirads}
            </div>

            <div>
                <span class="pirads-level">
                    {pirads_info['level']}
                </span>

                <h3>Catégorie PI-RADS {selected_pirads}</h3>

                <p>{pirads_info['description']}</p>
            </div>
        </div>
        """
    )

    st.caption(
        "Cette présentation est pédagogique. Le score PI-RADS est "
        "attribué par un radiologue selon les critères d'interprétation "
        "de l'IRM ; il ne constitue pas un diagnostic histologique."
    )

    resource_link(
        "Référentiel PI-RADS v2.1 — American College of Radiology",
        "https://www.acr.org/Clinical-Resources/Clinical-Tools-and-Reference/Reporting-and-Data-Systems/PI-RADS"
    )

    resource_link(
        "Lire un compte rendu PI-RADS — RadiologyInfo",
        "https://www.radiologyinfo.org/en/info/article-prostate-mri-report"
    )

    st.divider()

    # 6. La biopsie prostatique
    section_heading(
        "La biopsie prostatique"
    )

    st.markdown(
        """
        La biopsie consiste à prélever de petits fragments de tissu
        prostatique qui seront ensuite examinés au microscope par
        un anatomopathologiste.
        """
    )

    biopsy_col1, biopsy_col2 = st.columns(2)

    with biopsy_col1:

        st.html(
            """
            <div class="biopsy-card">

                <h3>Biopsie systématique</h3>

                <p>
                    Des prélèvements sont réalisés dans différentes
                    régions de la prostate selon un protocole défini.
                </p>

                <ul>
                    <li>Échantillonnage de plusieurs zones</li>
                    <li>Prélèvements selon une distribution organisée</li>
                </ul>
            </div>
            """
        )

    with biopsy_col2:

        st.html(
            """
            <div class="biopsy-card">

                <h3>Biopsie ciblée</h3>

                <p>
                    Les prélèvements ciblent une ou plusieurs lésions
                    suspectes repérées sur l'IRM.
                </p>

                <ul>
                    <li>Localisation à partir de l'imagerie</li>
                    <li>Ciblage des zones suspectes</li>
                </ul>
            </div>
            """
        )

    st.markdown("#### Du prélèvement au résultat")

    biopsy_process()

    resource_link(
        "Biopsie prostatique : déroulement et principes — RadiologyInfo",
        "https://www.radiologyinfo.org/en/info/prostate-biopsy"
    )

    st.divider()

    # 7. Conclusion et lien avec ProstaAI
    section_heading(
        "Pourquoi ces informations sont-elles importantes pour ProstaAI ?"
    )

    st.markdown(
        """
        Le projet ProstaAI étudie l'utilisation de méthodes
        d'apprentissage automatique pour estimer le résultat
        d'une biopsie prostatique à partir de données disponibles
        avant la biopsie.

        Les informations cliniques et radiologiques décrites dans
        cette page constituent le contexte médical des variables
        étudiées par les modèles.
        """
    )

    st.html(
        """
        <div class="project-connection">

            <div>
                <span>DONNÉES CLINIQUES</span>
                <strong>Âge, PSA, toucher rectal...</strong>

                <div class="connection-plus">
                    <strong>+</strong>
                </div>

                <span>DONNÉES RADIOLOGIQUES</span>
                <strong>PI-RADS, lésions, dimensions...</strong>
            </div>

            <div class="connection-result">
                <span><strong> → </strong> PROSTA AI</span>
                <strong>Estimation du résultat de biopsie</strong>
            </div>

        </div>
        """
    )

    st.warning(
        "**Important :** ProstaAI est un prototype de recherche "
        "académique. Il ne constitue pas un dispositif médical, "
        "ne remplace pas l'avis d'un professionnel de santé et "
        "ne doit pas être utilisé pour prendre une décision "
        "diagnostique ou thérapeutique."
    )

# Exécution
if __name__ == "__main__":
    main()
