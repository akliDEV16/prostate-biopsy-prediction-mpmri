
from pathlib import Path
import streamlit as st


STYLES_DIR = Path(__file__).parent


def load_css(filename):
    """Charge un fichier CSS."""

    css_path = STYLES_DIR / filename

    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as file:
            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


def load_global_css():
    """Charge les styles communs à toute l'application."""

    load_css("common.css")


def load_page_css(page_name):
    """Charge uniquement le CSS spécifique à une page."""

    load_css(f"{page_name}.css")
