import requests
import streamlit as st

from src.ui.styles import load_page_css

# CONFIGURATION
load_page_css("about")

# Liens externes
UMMTO_URL = "https://www.ummto.dz/"
MIRAI_LINKEDIN_URL = "https://www.linkedin.com/in/mirai-club-505a90441/"
GITHUB_REPO_URL = "https://github.com/dyhia-hachemi/prostate-biopsy-prediction-mpmri"
GITHUB_LOGO_URL = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"


# ENREGISTREMENT DES AVIS DANS GOOGLE SHEETS
def save_feedback(avis, propositions):
    """
    Envoie les avis et propositions vers Google Sheets
    via Google Apps Script.
    """

    # Récupérer l'URL depuis les secrets Streamlit
    url = st.secrets["google_sheets"]["web_app_url"]

    # Préparer les données
    payload = {
        "avis": avis.strip(),
        "propositions": propositions.strip()
    }

    # Envoyer les données à Google Apps Script
    response = requests.post(
        url,
        json=payload,
        timeout=20
    )

    response.raise_for_status()

    # Lire la réponse du script
    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "La réponse de Google Apps Script est invalide."
        ) from exc

    # Vérifier si l'enregistrement a réussi
    if not result.get("success"):
        raise RuntimeError(
            result.get("message", "Échec de l'enregistrement.")
        )

    return True

# LOGOS (intégrés au fichier : aucun dossier d'assets nécessaire)
UMMTO_LOGO_URI = "data:image/png;base64,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"
MIRAI_LOGO_URI = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBw8NEA8NDQ0NDQ0NDw4PDQ0NDQ8NDQ0QFREWFhURFRUYHSkgGBslGxUWITEhMSkrMi86FyAzOD8uNygtLisBCgoKDg0OGBAQGCslHx0rLi0vLS4uLSstKy0tLS0tLS0rLS0tLS0rLSsrLSstLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAOEA4QMBEQACEQEDEQH/xAAcAAEBAAIDAQEAAAAAAAAAAAAAAQYHAgQFCAP/xABIEAACAgEBBQQEBwwIBwAAAAAAAQIDBBEFBhITIQcxQWEUUXOBFSIyNXGTswgWIzM0UlRysbLR0hdCU1VidJHBJCWhtNPh8f/EABoBAQEAAwEBAAAAAAAAAAAAAAABAgMEBQb/xAAvEQEAAgECAwYFBAMBAAAAAAAAAQIDETEEEjITFCFBUVIiM3GBkQVTYdEVI6FC/9oADAMBAAIRAxEAPwDdgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAYRNQGoDUCpgTUBqA1AagNQLqA1AagNQGoAABNQGoF1AagNQJqBUA1AgDUAFVAAgwIAAICgQCsCAUAgAAAASAAAABAAAEYACgRAVgQAFIgUAEAAEAoBoAgDAAAAAAAABQAAAAAAQABUQRWBAoARA1KgBQAAAAAAAAAAAABQAAAAAAAAAAARBFYECgBAAioA2AAAQCgAAAKAAgFAAAAAAAcdCCpgUoAAAQYEABSIBhFQAAACgAIBQAAAAAABtLq2kl3t9EgPNs3gwoNxlmYya71zofxNsYMs+MVn8M4x3nycfvkwP03F+uh/Evds3sn8L2V/ST75MD9OxfrofxHds3sn8HZX9JPvjwP03F+uh/Ed2y+yfwdlf0l3MLOpyYudFtd0Yy4ZSrkpJS0T0enjo1/qa70tSdLRowtWa7w7GhigAAAEEGFQIBRAUIIAFAgFAAAAAAAAAEnNRTlJpRim233JLvYiNRp/ereazPnKMZShiJ/g6l040v68/W36vA+g4XhK4o1nqeliwxSP5eCjtbQKAAjZvZZ+S3/wCal9lWeH+pfNj6OHiuqPozJnnOYTAAAAQYEABRAUIAAoAAAAAAAAAoHGMk+5p9Wuj16p6NAeRvjNxwMtro3S4+6TUX/wBGzo4WNc1Pq2YY+OGqdi7Cyc2TVFesY9J2zfBVD6ZeL8lqz3c3E48UfFL0L5K03ZFRuRTLmcW1KXKmPHdGqCmqo+Lk+Lu6Pw8Djt+oXjTTHu0zxE+3d1vvd2d/fVP1cf5jLvXEftL2uT2L97uzv76p+rj/ADDvXEftHa5PYfe7s7++qfq4/wAw71xH7Una5PYzPcnZ9ONRZHHyY5dc7nLmRjwpS4Ipx73r3L/U87i8lsl9bV0nRy5rTafGNGQs5WoSAAACCDCoEAogKACAUAAAAAAAA8zb+8GJs2vm5l0ak9eCHWVtr9UILrL/AG8dDOmO150rCxWZ2ac3s7UMvN4qcPiwcZ6puMl6Vav8U18heUevmehi4WtfG3jLdWkRu7fZXvV6FKOLkTfouTJtSk+lFzfyv1Zdz9z9ZlxPD89eau8Mr01rrDbu2sD0uizHcuBW8KlJd6ippvTz0TPOxZJx3i0eTRS3LOrWW8+8PM/4LD/A4NGtcVW3Hn6d8pPxjr4ePe+/p7PC8Lp/syeNp/478WLT4rby/bcbpVtT1egz/dmTjurH9f6Y596/Vip6DpAj9sPFnfZCmpa2WyUIrzfi/Jd/uMMl4pWbTtCWtERrLd+ysCGLTXj1/Jqilr4yffKT829X7z5nJknJabT5vLtbmmZdowYgAAAAMCBAKRAoAIBQAAAAebt7b+Js2vn5uRXRX/V4nrOx/mwiusn5JGVazadIGLbG7SaszG2ln141kcbZrq0UpLnXQfWUuFdIvTuWrM7YpiYj1NGa4eXXfXXfTNWVXQjZXOPdOElqmjXMaTpI1B90A2rdmtf2eX09a4quh28HtZsxtYQmpLVdzO+PFvh6WL1hH3/tZtrszjZs/djfdzwMnCum1mY+LN49jfxrqn8RdfGUNV9K0fgzz78NHb102mWrs/8AZH8sRSPbd7NOzijnen0t8KtxlXxaa8PFxR10955n6jbl5Lek/wBOXiZ05ZeiuzWH6bP6mP8AMaf8pb2ww73Pof0bQ/TLPqY/zD/KW9sHep9Hrbt7nV4Frv50r58DjDigoKvXva6vrp0/1OfiONtmry6aNeTPN400ZMcbQAAAAAAYECAUiBQAAAAAAYv2l7ev2Xs27LxeDnxlTCDsjxxjxzUXLTXq0n0M8dea0QPmPau1MjNtlkZd9mRdLvnZLVpepLuivJaI9KtYrGkNkQ2DuB8wbw/q1/uM58nzasZ3et2Ib4cufwPkz/B2uUsGT7oWPWUqdfBS6yXnqvFDicX/ALhlePN2PugPxuzvZ5f71ReC2t9lxtSRs5cv8Eu/yfrOzXSWzXR72K/iR9/7Tors2xs4z1VtUl0fXr7v/ZJ6olfOHvY9/GvU13o6qzq31nVsDsq/G5Xsqv3pHmfqfTX7ubitobGPHcQAAAAAAAAAMCAAKgAAAAAAAMC7b/ma/wBti/bRN2DrgfNh6Da2b2f/ADBvD+rX+4zmyfNqwndryE5RalCTjKLUoyi2pRknqpJ+DTOuY1bmZ7573LbOPsyyeiy8eGVVmRS6cetXDYvKaTfk014Grhqck2hhj82J2R1TR0zGsNmjYle6r+BsHadKbarsWZBdfiq6ajcvoSSf0J+s0Yc+mScdvsY7+PLLGLl8at+qX+zOyd4bXbqscHqv/vkbInRlE6Nm9klinZlSX9lV7nxS6HD+pTrWv3a+JnWsNlM8hxiYAAAAAAAAAwiAAKgoAAAAAADA+2/5mv8AbYv20Tdg64HzWeg2tp9mWJZkbE2/TTB2W2RgoQj8qTVcnovPoc2WdMlZYTu1ojsbnLDXWf0omPeUr5uybWb6Q7LoKWxsGMkpRlXcnFrVNO6zVNHkZ/my579TWvaBus9m5ClXF+h3T4qH3qt+NL+jXp619DPT4bP2ldJ3h1Y780fy/DdvdPL2k06a+XRr8bJtTjUvXw+M35L36GebiKY99/RbXircG6m6lGy4y5Up2W2qKttm/laa6JRXSK6vz82eVmz2yz4+Tlvkm273jQwEAAAAAAABQIwIAAICgAAAABAMD7bl/wAmv9ti/bRNuDrgfNh6La3l9zr+T7Q9vR9nI4uK3hrndjvbLud6FkfCGPDTEzJt2Rivi4+Q+rXlGfVrz4l6jdw2XmjlneGdJ8mu8bvl9K/YdVN5bI3l+5sZPpLsr+Z8D2dv29h5HEfMs579Usiz9n05UOVk1Qur4oy4LI8UeKL1T0NVbTWdYlImY2diEFFKMUoxSSUUtEl6kiIoAAkAAAAAAAAAMCBAKqAAAAAAAQGB9t/zNf7bF+2ibsHXA+az0G1vL7nX8n2h7ej7ORx8V1Q1zu2jtvZVOfj24mRHipvg4yXivFSXqkmk0/WjnraazrCPmHa+7mRgZtuzpVztvUkqVXXKTyIPVwnCK6vVeruaa8D1MWStq8zfWYbE3Q7IbLOG7a0nVDvWHTJc2XlZYukfoXXzRoy8X5U/LG2T0bf2fg1YtUMfHrjVTUuGuuC0jFa6/tbfvOGZmZ1lqdggAAAAAAAAAAAAEGFQIBSIFAAAAAABgfbf8zX+2xftom7B1wQ+az0G1vL7nX8n2h7ej7ORx8V1Q1zu28cqPzePXx83lw5qjwK3hXMUNdeHi79NfAD9AAAAAAAAAAAAAAACCDCowABAUAAAAAAGM9o27921dn24WNKqFtllMlK6Uo16QsUnq0m+5eo2Y7RW2sjUX9CO1f7fZ/113/jOrvNfRnzNkdlG5uTsWrKry50TeRZVODonOaSjFp68UV6znzZIvOsMZZ2aUAAAAAAAAAAAAAAAAAAAYHECogpQAAAAAAAAAEgADUAAAAAAAAAAAAAAAAAjAgHJAAAAAAAAYX2v7Quxdk3XY11lFsbcZRsqm4TSdqTWq8jZiiJtpJDFex/fHJldLZe1LbZ3ZFcMrBtvlxTnCdany+J96cGpL6JLyNmakac1VnRs/b+16dn412ZkS0qog5vr1k+6MF5ttJfSaIiZnSEaP3M3p2rlbZwXlZOTGjPstvhjcySx3S1coqMPzVKtpfq6nVelYpOnkrbHaXl24+yc66iydNtdcHCyuThOD5sFqmu7o2c+ONbxCOPZlmW5GycK6+yd11kLXOyyTnObV00tW+/okMkaXmIJa/2h8JbR3hz9mY+18rBqqjzYcErJ1xUa6dYqCktNXNvvN0ctccTMaj2p9n+3IJyq3oyJWLrGNldsYN+Cb5ktF7mY9pT2jvdlG9uXn+mYO0eGWZs6xQnbGMY8xcUoNSS6cSlB9UlqmvfMtIjSY8xsHU0jRW8u39q7XydpZOx8q+nA2TStORZOEcjhk+Ka0+VJrmSXlBes6q1rWI5vNW09wt5Y7WwKcpNc1LlZUF/UvilxdPBPVSXlJGjJXltoj2toScabpJtNVWNNdGmoPRmEDAewvauTmYGRZl5F2TZHMlCM7rJWSUeRU+FN+Grb95uzREW8BsY0gAAAAAEYAAgKAAAAADQDA+2/5mv9ti/bRNuDrgjdie827tlmxdj7Zw9YZ2y8LDm5QXxpURrjLXz4H8b6HIzpb4prO0kOrtXeCzfDI2dsvHjKnHUI5W02tfiTj0ml64x10i/F2L1GUV7KJtP2XZ6W3saFO9WxqaoKuqnDprrhFaRhCKyUor3IxrOuKyMz7V/mbaHsofbQNWLrghx7JfmXZ/s7vt7C5uuVndrjMydoU7z7SnsnHpycvl6Ou96Q5XKo4pfLj114fHxN0RXso5iNHf3n343o2dSrcvAwcWuyXLjdXB3OE2tV3XSSfR6arToKY8Vp8JldIZX2Ubq+gUW5tmVDMydp8F9l9Tbq4HrJKLfWTbnJt6Lv006GrLfmnTTZinbHvO9nYDopk1l7Q4qKuH5cK9Pwti0666PhXnNeoYac1vHyGGbg79Yex8GGH8GbUstk5WZVkcevhttl0emsteFJKK8kZ5KTa2usDo9mu8tWztrW0QrvxtmbUs4aa8mPBKizX8F3PTTWThr6nHXuM8tNaa+cLo3ptP8AEX+xt/cZyQjW/wBzv825P+el/wBvSb8/UNpGgAAAAAAjAAEQUoAAAAAB4O/O7nwvhWYKv9H5k6p81183TgmpacPEu/T1mdLcttR3thbLWJh42FKStWNj1Y7nwcKtUIKLfDq9NdO7VmMzrOo6m7m6WBsp2ywcZUO/h5r47LG0tdEuJvRdX0RZtM7jzNq7lPJ2xiba9KUFiVRr9G5HFzNOb15nF0/G/mvuLF9KzX1Hr727E+EsLIwVbyfSYxjzeDmcGk4y14dVr8n1+JKzyzqJujsP4MwsfBdvP9HjNc1Q5XHxWSn8nV6fK07/AAF7c1pkl5OzdyXRtjJ236VxLKrdfo3I4eDWNa15nF1/F/mrvLN/hioyLbGy6c6i3Fya1ZTfBwnF9/lJPwaejT8GkYxMx4wPA7P90r9i1WY0s/0zGlNzorlQ6p47b+MlLjaaffpouur8WZXvzTqOvnbivK2vVtjKy+bXiqPouEqOGNTitYNzcnrpNufyV109RYyaV5YGaamsYn2hbk17corrlb6PfRZx05HL5rimtJwa1XR6J9/fFGdLzSR7uLh2rFjj33q67kcqzIVfBzJcPDzODV6N9+mpj5jw+zrc97DxrcV5PpXNvd3MVPI4da4Q4dOKWvyNddfEyvfmnUZUYAAAAAABgQCgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgQAQUoAAAAAAAAAAAAAAAAAAAAAAAAAAAAMCBAKAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwIwgFCClAAAAAAAAAAAAAAAAAAAAAAAAAAAAEZBAKUUgFAAAAAAAAAAAAAAAAAAAAAAAAAAAIgDIIAKOWgAAAAAAAAAAAAAAAAAAIAAAAAAAAAYHFEFaAgAo5AAAAAAAAAAAAAAAAAACAUAAAAAAACAADAEEA//2Q=="


def logo_html(uri, alt, texte_secours):
    """Balise <img> du logo intégré au fichier."""
    if not uri:
        return f'<span class="about-logo-fallback">{texte_secours}</span>'
    return f'<img src="{uri}" alt="{alt}">'


def liens_html(liens):
    """Boutons de liens sociaux d'un membre (ouverts dans un nouvel onglet)."""
    return "".join(
        f'<a class="about-social-link" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'{libelle} <span aria-hidden="true">↗</span></a>'
        for libelle, url in liens
    )


def team_card(name, role, specialty, initials, liens):
    st.html(f"""
        <article class="about-team-card">
            <div class="about-avatar">{initials}</div>
            <div class="about-team-info">
                <h3>{name}</h3>
                <p class="about-team-role">{role}</p>
                <p class="about-team-specialty">{specialty}</p>
                <div class="about-social-links">{liens_html(liens)}</div>
            </div>
        </article>
    """)


# PAGE PRINCIPALE
def main():
    st.title("À propos")

    # Présentation
    st.html("""
        <section class="about-hero">
            <div class="about-hero-content">
                <span class="about-eyebrow">NOVEMBRE BLEU · 2026–2027</span>
                <h2>Prosta<span>AI</span></h2>
                <p class="about-hero-lead">
                    Explorer le potentiel de l'intelligence artificielle
                    dans l'étude du cancer de la prostate.
                </p>
                <p class="about-hero-description">
                    ProstaAI est un projet académique qui étudie l'utilisation
                    de données cliniques et d'imagerie par résonance magnétique
                    pour expérimenter des approches de prédiction liées au
                    cancer de la prostate.
                </p>
                <div class="about-tags">
                    <span>Intelligence artificielle</span>
                    <span>Santé</span>
                    <span>Recherche appliquée</span>
                </div>
            </div>
            <div class="about-hero-mark" aria-hidden="true">
                <div class="about-mark-circle"><span>AI</span><small>HEALTH</small></div>
                <div class="about-mark-orbit about-mark-orbit-one"></div>
                <div class="about-mark-orbit about-mark-orbit-two"></div>
                <span class="about-mark-dot"></span>
            </div>
        </section>
        <div class="about-disclaimer">
            <span class="about-disclaimer-icon">i</span>
            <p>
                ProstaAI est un prototype expérimental à vocation académique et
                pédagogique. Il ne constitue pas un dispositif médical et ne
                remplace ni un diagnostic, ni l'avis d'un professionnel de santé.
            </p>
        </div>
    """)

    st.divider()

    # Équipe
    st.html("""
        <div class="about-section-heading">
            <span class="about-section-kicker">LES CONTRIBUTEURS</span>
            <h2>Une équipe universitaire</h2>
        </div>
    """)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        team_card(
            "Mansouri Akli",
            "Étudiant en Master 2",
            "Systèmes informatiques intelligents",
            "MA",
            [
                ("LinkedIn", "https://www.linkedin.com/in/mansouri-akli-0a6383282"),
                ("GitHub", "https://github.com/akliDEV16"),
            ],
        )
    with col2:
        team_card(
            "Hachemi Dyhia",
            "Étudiante en 5ᵉ année ingénieur",
            "Spécialité Intelligence artificielle",
            "HD",
            [
                ("LinkedIn", "https://www.linkedin.com/in/dyhia-hachemi-18214a317"),
                ("GitHub", "https://github.com/dyhia-hachemi"),
            ],
        )

    st.divider()

    # Cadre académique
    st.html(f"""
        <div class="about-section-heading">
            <span class="about-section-kicker">LE CADRE ACADÉMIQUE</span>
            <h2>Un projet ancré à l'UMMTO</h2>
            <p>ProstaAI s'inscrit dans un environnement universitaire consacré
            à la formation et à l'innovation technologique.</p>
        </div>

        <a class="about-link-card" href="{UMMTO_URL}" target="_blank" rel="noopener noreferrer"
           aria-label="Site de l'Université Mouloud Mammeri de Tizi-Ouzou (nouvel onglet)">
            <section class="about-university-card">
                <div class="about-university-icon">
                    {logo_html(UMMTO_LOGO_URI, "Logo de l'Université Mouloud Mammeri de Tizi-Ouzou", 'UMMTO')}
                </div>

                <div class="about-university-details">
                    <h3>Université Mouloud Mammeri de Tizi-Ouzou</h3>
                    <p>Faculté de Génie électrique et informatique</p>
                    <p>Département Informatique</p>
                    <div class="about-university-year">
                        Année universitaire 2026–2027
                    </div>
                    <span class="about-card-cta">Visiter le site de l'UMMTO ↗</span>
                </div>
            </section>
        </a>
    """)

    st.html(f"""
        <a class="about-link-card" href="{MIRAI_LINKEDIN_URL}" target="_blank" rel="noopener noreferrer"
           aria-label="Page LinkedIn du club MIRAI (nouvel onglet)">
            <div class="about-club-card">
                <div class="about-club-icon">
                    {logo_html(MIRAI_LOGO_URI, 'Logo du club MIRAI', 'MIRAI')}
                </div>

                <div class="about-club-details">
                    <h3>Club MIRAI</h3>
                    <p>Club d'intelligence artificielle de l'UMMTO</p>
                    <p>
                        Un espace d'apprentissage, de partage et d'innovation
                        autour de l'intelligence artificielle et des nouvelles technologies.
                    </p>
                    <div class="about-club-tag">
                        Membres du club
                    </div>
                    <span class="about-card-cta">Voir la page LinkedIn du club ↗</span>
                </div>
            </div>
        </a>
    """)

    st.divider()

    # Dépôt GitHub
    st.html("""
        <div class="about-section-heading">
            <span class="about-section-kicker">RESSOURCES</span>
            <h2>Explorer le projet</h2>
            <p>Retrouvez les éléments techniques et les ressources de développement
            dans le dépôt du projet.</p>
        </div>
    """)
    st.html(f"""
        <div class="about-github-card">
            <div class="about-github-icon">
                <img src="{GITHUB_LOGO_URL}" alt="Logo GitHub">
            </div>

            <div class="about-github-info">
                <h3>Code source sur GitHub</h3>
                <p>prostate-biopsy-prediction-mpmri</p>
            </div>

            <a href="{GITHUB_REPO_URL}" target="_blank" rel="noopener noreferrer">
                Voir le dépôt ↗
            </a>
        </div>
    """)

    st.divider()

    # Avis des visiteurs
    st.html("""
        <div class="about-section-heading">
            <span class="about-section-kicker">PARTICIPATION DES VISITEURS</span>
            <h2>Votre avis nous intéresse</h2>
            <p>Une remarque, une idée ou une suggestion ? Votre retour nous aide
            à identifier les points à améliorer et à explorer.</p>
        </div>
        <div class="about-feedback-intro">
            <strong>Partagez librement votre expérience.</strong>
            <p>Votre contribution est enregistrée sans demander votre nom
            ni vos coordonnées.</p>
        </div>
    """)

    
    # Formulaire des avis et propositions
    with st.form("prostaai_feedback_form", clear_on_submit=True):

        feedback = st.text_area(
            "Votre avis",
            placeholder=(
                "Qu'avez-vous pensé de ProstaAI ? "
                "Votre expérience, vos remarques..."
            ),
            height=120,
            max_chars=2000,
        )

        suggestions = st.text_area(
            "Vos propositions d'amélioration",
            placeholder=(
                "Quelles fonctionnalités ou améliorations "
                "aimeriez-vous retrouver dans ProstaAI ?"
            ),
            height=120,
            max_chars=2000,
        )

        submitted = st.form_submit_button(
            "Envoyer ma contribution",
            type="primary",
            use_container_width=True
        )

        if submitted:

            if not feedback.strip() and not suggestions.strip():
                st.warning(
                    "Veuillez renseigner au moins un avis "
                    "ou une proposition."
                )

            else:
                try:
                    save_feedback(feedback, suggestions)

                    st.success(
                        "Merci pour votre contribution ! "
                        "Votre réponse a bien été enregistrée."
                    )

                except Exception as e:
                    st.error(
                        "L'enregistrement a échoué. "
                        "Veuillez réessayer."
                    )

                    # Détail technique utile pendant le développement
                    st.caption(f"Détail technique : {e}")

if __name__ == "__main__":
    main()