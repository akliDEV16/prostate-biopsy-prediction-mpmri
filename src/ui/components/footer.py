
import streamlit as st


def render_footer():
    """
    Affiche le footer commun à toutes les pages.
    """

    footer_html = """
    <footer class="app-footer">

        <div class="footer-glow" aria-hidden="true"></div>

        <div class="footer-info">
            ProstaAI
            <span>|</span>
            Projet académique en intelligence artificielle
            <span>|</span>
            Dataset : AI4AR Prostate mpMRI Database (CC BY 4.0)
        </div>

        <div class="footer-bottom">
            <span>
                Cette application est un prototype
                académique de recherche. Elle ne constitue ni un
                dispositif médical, ni un outil de diagnostic ou
                de dépistage. <br> Ses résultats ne doivent pas être
                utilisés pour prendre des décisions médicales.
            </span>

            <span>© 2026 ProstaAI</span>
        </div>

    </footer>
    """

    st.html(footer_html)
