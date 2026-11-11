import streamlit as st

from src.ui.components.footer import render_footer
from src.ui.styles import load_global_css


st.set_page_config(
    page_title="ProstaAI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_global_css()

pages = [
    st.Page(
        "src/ui/pages/home.py",
        title="Accueil",
        icon=":material/home:",
        default=True
    ),
    st.Page(
        "src/ui/pages/prostate_cancer.py",
        title="Comprendre le cancer",
        icon=":material/medical_services:"
    ),
    st.Page(
        "src/ui/pages/ai_project.py",
        title="Notre IA",
        icon=":material/psychology:"
    ),
    st.Page(
        "src/ui/pages/demonstration.py",
        title="Démonstration",
        icon=":material/biotech:"
    ),
    st.Page(
        "src/ui/pages/results.py",
        title="Résultats",
        icon=":material/monitoring:"
    ),
    st.Page(
        "src/ui/pages/methodology.py",
        title="Méthodologie",
        icon=":material/account_tree:"
    ),
    st.Page(
        "src/ui/pages/about.py",
        title="À propos",
        icon=":material/info:"
    )
]

navigation = st.navigation(pages, position="top")

navigation.run()

render_footer()