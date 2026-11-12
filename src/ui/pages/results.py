from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.base import clone
from sklearn.metrics import roc_auc_score, roc_curve

from src.data.prepare_data import get_X_y, load_model_table
from src.features.split_data import N_REPEATS, make_cv
from src.models.train import LOGREG_NAME, NAIVE_NAME, RF_NAME, build_pipelines
from src.ui.styles import load_page_css

# CONFIGURATION
load_page_css("results")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = PROJECT_ROOT / "results"

SEUIL = 0.5                                   # même seuil que la page Démonstration
MODELES_ETUDIES = [LOGREG_NAME, RF_NAME]
TOUS_LES_MODELES = [LOGREG_NAME, RF_NAME, NAIVE_NAME]
NOMS = {
    NAIVE_NAME: "Réponse naïve",
    LOGREG_NAME: "Régression logistique",
    RF_NAME: "Random Forest",
}
COULEURS = {
    NAIVE_NAME: "#8A9BAA",
    LOGREG_NAME: "#438CCB",
    RF_NAME: "#10B981",
}


# OUTILS DE FORMAT
def fr(valeur, decimales=3):
    """Formate un nombre avec une virgule décimale, à la française."""
    return f"{valeur:.{decimales}f}".replace(".", ",")


# FONCTIONS D'AFFICHAGE
def titre_section(numero, titre, sous_titre=None):
    """Affiche le titre d'une section numérotée."""
    sous_titre_html = f"<p>{sous_titre}</p>" if sous_titre else ""
    st.html(
        f"""
        <div class="res-section-heading">
            <span class="res-section-number">{numero}</span>
            <div>
                <h2>{titre}</h2>
                {sous_titre_html}
            </div>
        </div>
        """
    )


def encadre(titre, message, genre="info"):
    """Affiche un encadré de lecture ou de limite."""
    st.html(
        f"""
        <div class="res-note res-note-{genre}">
            <strong>{titre}</strong>
            <p>{message}</p>
        </div>
        """
    )


def carte_metrique(indice, titre, description, valeur=None):
    """Carte d'une métrique d'évaluation, avec sa valeur si elle est fournie."""
    valeur_html = f'<div class="res-kpi-value">{valeur}</div>' if valeur else ""
    st.html(
        f"""
        <article class="res-metric-card">
            <span class="res-card-kicker">MÉTRIQUE {indice}</span>
            <h4>{titre}</h4>
            {valeur_html}
            <p>{description}</p>
        </article>
        """
    )


def style_graphique(fig, ax):
    """Applique la charte graphique de l'application aux figures matplotlib."""
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    for bord in ax.spines.values():
        bord.set_color("#D3E5F4")
    ax.tick_params(colors="#536B80")
    ax.xaxis.label.set_color("#28649B")
    ax.yaxis.label.set_color("#28649B")
    ax.grid(True, color="#E5EFF7", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()


# CHARGEMENT
@st.cache_data(show_spinner=False)
def charger_resultats():
    """Lit les scores produits par main.py (résumé et détail par découpe)."""
    resume = pd.read_csv(RESULTS_DIR / "cv_resume.csv", index_col="modele")
    details = pd.read_csv(RESULTS_DIR / "cv_details.csv")
    return resume, details


@st.cache_data(show_spinner="Calcul des prédictions de validation…")
def calculer_predictions():
    """
    Recalcule, pour chaque patient, la probabilité prédite par des modèles qui ne l'ont
    jamais vu (validation croisée). Même découpage que main.py, donc cohérent avec cv_details.csv.
    Chaque patient est testé une fois par répétition : on moyenne les N_REPEATS prédictions.
    """
    table = load_model_table()
    X, y = get_X_y(table)
    cv = make_cv()
    pipelines = build_pipelines()

    probabilites = {}
    for nom in MODELES_ETUDIES:
        somme = np.zeros(len(y))
        for train, test in cv.split(X, y):
            modele = clone(pipelines[nom]).fit(X.iloc[train], y.iloc[train])
            somme[test] += modele.predict_proba(X.iloc[test])[:, 1]
        probabilites[nom] = somme / N_REPEATS

    meta = table[["clinical_group", "no_of_lesions"]].reset_index(drop=True)
    return {"y": y.to_numpy(), "proba": probabilites, "meta": meta}


# CALCULS
def matrice_confusion(y, proba):
    """Effectifs des vrais/faux positifs et négatifs au seuil de décision."""
    prediction = (proba >= SEUIL).astype(int)
    return {
        "vn": int(np.sum((y == 0) & (prediction == 0))),
        "fp": int(np.sum((y == 0) & (prediction == 1))),
        "fn": int(np.sum((y == 1) & (prediction == 0))),
        "vp": int(np.sum((y == 1) & (prediction == 1))),
    }


def sous_groupes(meta):
    """Masques booléens des sous-groupes utilisés pour l'analyse des erreurs."""
    return {
        "Groupe BN (jamais biopsié)": (meta["clinical_group"] == "BN").to_numpy(),
        "Groupe TN (biopsie négative antérieure)": (meta["clinical_group"] == "TN").to_numpy(),
        "IRM sans lésion": (meta["no_of_lesions"] == 0).to_numpy(),
        "IRM avec lésion": (meta["no_of_lesions"] > 0).to_numpy(),
    }


def bien_classes(y, proba, masque):
    """Effectif et taux de bonne classification dans un sous-groupe."""
    n = int(masque.sum())
    if n == 0:
        return n, np.nan
    prediction = (proba >= SEUIL).astype(int)
    return n, float(np.mean(prediction[masque] == y[masque]))


# GRAPHIQUES
def graphique_auc_par_decoupe(details):
    """Dispersion de l'AUC sur les 15 découpes, avec la moyenne de chaque modèle."""
    fig, ax = plt.subplots(figsize=(7.5, 3.9))
    for i, nom in enumerate(TOUS_LES_MODELES):
        valeurs = details.loc[details["modele"] == nom, "auc"].to_numpy()
        decalage = np.linspace(-0.14, 0.14, len(valeurs))
        ax.scatter(
            i + decalage, valeurs,
            color=COULEURS[nom], alpha=0.8, s=30,
            edgecolor="white", linewidth=0.5, zorder=3,
        )
        ax.hlines(valeurs.mean(), i - 0.3, i + 0.3,
                  color=COULEURS[nom], linewidth=2.5, zorder=4)

    ax.axhline(0.5, color="#A9C9E4", linestyle="--", linewidth=1.2, zorder=1)
    ax.set_xticks(range(len(TOUS_LES_MODELES)))
    ax.set_xticklabels([NOMS[nom] for nom in TOUS_LES_MODELES])
    ax.set_ylabel("AUC par découpe")
    ax.set_ylim(0.4, 1.02)
    style_graphique(fig, ax)
    return fig


def graphique_roc(y, probabilites):
    """Courbes ROC des deux modèles, calculées sur les prédictions hors pli."""
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    ax.plot([0, 1], [0, 1], linestyle="--", color="#A9C9E4", linewidth=1.5,
            label="Hasard (AUC = 0,5)")
    for nom in MODELES_ETUDIES:
        fpr, tpr, _ = roc_curve(y, probabilites[nom])
        auc = roc_auc_score(y, probabilites[nom])
        ax.plot(fpr, tpr, color=COULEURS[nom], linewidth=2.5,
                label=f"{NOMS[nom]} (AUC = {fr(auc, 2)})")

    ax.set_xlabel("1 − spécificité (faux positifs)")
    ax.set_ylabel("Sensibilité (vrais positifs)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, loc="lower right")
    style_graphique(fig, ax)
    return fig


# HTML
def tableau_performances(resume):
    """Tableau récapitulatif : moyenne ± écart-type de chaque métrique."""
    lignes = []
    for nom in TOUS_LES_MODELES:
        r = resume.loc[nom]
        lignes.append(
            f"""
            <tr>
                <th>{NOMS[nom]}</th>
                <td>{fr(r['auc_moyenne'])} <small>± {fr(r['auc_ecart_type'])}</small></td>
                <td>{fr(r['balanced_accuracy_moyenne'])} <small>± {fr(r['balanced_accuracy_ecart_type'])}</small></td>
                <td>{fr(r['accuracy_moyenne'])} <small>± {fr(r['accuracy_ecart_type'])}</small></td>
            </tr>
            """
        )
    return f"""
    <div class="res-table-wrapper">
        <table class="res-table">
            <thead>
                <tr>
                    <th>Modèle</th>
                    <th>ROC-AUC</th>
                    <th>Balanced accuracy</th>
                    <th>Accuracy</th>
                </tr>
            </thead>
            <tbody>{''.join(lignes)}</tbody>
        </table>
    </div>
    """


def carte_matrice(nom, cm):
    """Matrice de confusion 2 × 2 d'un modèle, au seuil de décision."""
    return f"""
    <article class="res-cm-card">
        <h4>{NOMS[nom]}</h4>
        <div class="res-cm-grid">
            <span class="res-cm-corner"></span>
            <span class="res-cm-head">Prédit : sans cancer</span>
            <span class="res-cm-head">Prédit : cancer</span>

            <span class="res-cm-side">Réel : sans cancer</span>
            <div class="res-cm-cell res-cm-ok"><b>{cm['vn']}</b><small>vrais négatifs</small></div>
            <div class="res-cm-cell res-cm-err"><b>{cm['fp']}</b><small>faux positifs</small></div>

            <span class="res-cm-side">Réel : cancer</span>
            <div class="res-cm-cell res-cm-err"><b>{cm['fn']}</b><small>faux négatifs</small></div>
            <div class="res-cm-cell res-cm-ok"><b>{cm['vp']}</b><small>vrais positifs</small></div>
        </div>
    </article>
    """


def tableau_sous_groupes(y, probabilites, meta):
    """Taux de bonne classification par sous-groupe, pour chaque modèle étudié."""
    lignes = []
    for libelle, masque in sous_groupes(meta).items():
        n, _ = bien_classes(y, probabilites[LOGREG_NAME], masque)
        taux = [bien_classes(y, probabilites[nom], masque)[1] for nom in MODELES_ETUDIES]
        lignes.append(
            f"<tr><th>{libelle}</th><td>{n}</td>"
            f"<td>{fr(taux[0], 2)}</td><td>{fr(taux[1], 2)}</td></tr>"
        )
    return f"""
    <div class="res-table-wrapper">
        <table class="res-table">
            <thead>
                <tr>
                    <th>Sous-groupe</th>
                    <th>Patients</th>
                    <th>{NOMS[LOGREG_NAME]}</th>
                    <th>{NOMS[RF_NAME]}</th>
                </tr>
            </thead>
            <tbody>{''.join(lignes)}</tbody>
        </table>
    </div>
    """


# PAGE PRINCIPALE
def main():
    st.title("Résultats expérimentaux")

    try:
        resume, details = charger_resultats()
    except FileNotFoundError:
        st.warning(
            "Les fichiers de résultats sont introuvables dans le dossier results/. "
            "Lancez `python main.py` depuis la racine du projet."
        )
        return

    meilleur = resume.loc[MODELES_ETUDIES, "auc_moyenne"].idxmax()

    # SECTION 01 : PRÉSENTATION
    titre_section(
        "01",
        "Présentation des expériences",
        "Deux modèles de classification sont comparés à une référence naïve, avec le même protocole."
    )

    st.html(
        """
        <section class="res-intro-panel">
            <div>
                <span class="res-eyebrow">PROTOCOLE</span>
                <h3>Évaluer sur des patients non vus pendant l'apprentissage</h3>
                <p>
                    Les 462 patients de la base sont répartis en 5 plis, en conservant la proportion de cancers.
                    Ce découpage est répété 3 fois : chaque modèle est donc évalué 15 fois.
                    À chaque pli, l'imputation et la mise à l'échelle sont ajustées uniquement sur les patients
                    d'entraînement du pli.
                </p>
                <div class="res-tags">
                    <span>462 patients</span>
                    <span>10 variables</span>
                    <span>5 plis × 3 répétitions</span>
                </div>
            </div>
        </section>
        """
    )

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.html(
            f"""
            <div class="res-kpi-card">
                <span class="res-card-kicker">MEILLEURE AUC MOYENNE</span>
                <div class="res-kpi-value">{fr(resume.loc[meilleur, 'auc_moyenne'])}</div>
                <p>{NOMS[meilleur]}</p>
            </div>
            """
        )
    with col2:
        st.html(
            f"""
            <div class="res-kpi-card">
                <span class="res-card-kicker">CAS PATIENTS</span>
                <div class="res-kpi-value">248 / 214</div>
                <p>Cancers / sans cancer</p>
            </div>
            """
        )
    with col3:
        st.html(
            f"""
            <div class="res-kpi-card">
                <span class="res-card-kicker">RÉFÉRENCE NAÏVE</span>
                <div class="res-kpi-value">{fr(resume.loc[NAIVE_NAME, 'auc_moyenne'], 2)}</div>
                <p>AUC d'un modèle qui ne fait que deviner</p>
            </div>
            """
        )

    # SECTION 02 : MÉTRIQUES
    titre_section(
        "02",
        "Métriques d'évaluation",
        "Le problème est une classification binaire : cancer (1) ou absence de cancer (0)."
    )

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        carte_metrique(
            "01", "ROC-AUC",
            "Probabilité que le modèle classe un patient atteint au-dessus d'un patient sain, "
            "tiré au hasard. 0,5 correspond au hasard, 1 à une séparation parfaite.",
        )
    with col2:
        carte_metrique(
            "02", "Balanced accuracy",
            "Moyenne de la sensibilité et de la spécificité. Elle reste pertinente "
            "lorsque les deux classes n'ont pas le même effectif.",
        )
    with col3:
        carte_metrique(
            "03", "Accuracy",
            "Part des prédictions correctes sur l'ensemble des patients. Elle est donnée "
            "à titre de repère, car elle dépend du seuil de décision de 50 %.",
        )

    # SECTION 03 : PERFORMANCES
    titre_section(
        "03",
        "Performances des modèles",
        "Moyenne et écart-type sur les 15 découpes de validation croisée."
    )
    st.html(tableau_performances(resume))

    # SECTION 04 : COMPARAISON
    titre_section(
        "04",
        "Comparaison des modèles",
        "Chaque point est une découpe ; le trait épais indique la moyenne."
    )

    with st.container(border=True, key="res_auc_card"):
        st.pyplot(graphique_auc_par_decoupe(details))
        plt.close("all")

    ecart = abs(resume.loc[LOGREG_NAME, "auc_moyenne"] - resume.loc[RF_NAME, "auc_moyenne"])
    variabilite = max(resume.loc[nom, "auc_ecart_type"] for nom in MODELES_ETUDIES)
    if ecart < variabilite:
        conclusion = (
            f"L'écart d'AUC entre les deux modèles ({fr(ecart)}) est inférieur à la variabilité "
            f"entre découpes ({fr(variabilite)}) : aucun modèle ne se détache clairement de l'autre."
        )
    else:
        conclusion = (
            f"L'écart d'AUC entre les deux modèles ({fr(ecart)}) dépasse la variabilité entre découpes "
            f"({fr(variabilite)}) : la différence peut être prise en compte."
        )
    encadre("Lecture", conclusion)

    # SECTION 05 : COURBES ROC
    titre_section(
        "05",
        "Courbes ROC",
        "Chaque courbe montre le compromis entre détection des cancers et fausses alertes, selon le seuil."
    )

    predictions = calculer_predictions()
    with st.container(border=True, key="res_roc_card"):
        st.pyplot(graphique_roc(predictions["y"], predictions["proba"]))
        plt.close("all")
    encadre(
        "Pourquoi cette courbe peut différer légèrement de l'AUC du tableau",
        "La courbe est tracée à partir des prédictions hors pli moyennées sur les 3 répétitions. "
        "Le tableau de la section 03 est la moyenne des AUC calculées sur chacun des 15 découpes."
    )

    # SECTION 06 : MATRICES DE CONFUSION
    titre_section(
        "06",
        "Matrices de confusion",
        "Décisions au seuil de 50 % : probabilité ≥ 0,5 → cancer prédit. Chaque cellule indique un effectif de patients."
    )

    cartes = "".join(
        carte_matrice(nom, matrice_confusion(predictions["y"], predictions["proba"][nom]))
        for nom in MODELES_ETUDIES
    )
    st.html(f'<div class="res-cm-wrapper">{cartes}</div>')

    # SECTION 07 : ANALYSE DES ERREURS
    titre_section(
        "07",
        "Analyse des erreurs",
        "Où les modèles se trompent-ils le plus souvent ? Taux de bonne classification par sous-groupe."
    )
    st.html(tableau_sous_groupes(predictions["y"], predictions["proba"], predictions["meta"]))
    encadre(
        "Limites observées",
        "Les faux négatifs (cancers non détectés) sont l'erreur la plus importante sur le plan clinique. "
        "Les sous-groupes sont de petite taille : leurs taux doivent être lus avec prudence.",
        genre="avertissement"
    )

    # SECTION 08 : DISCUSSION
    titre_section(
        "08",
        "Discussion",
        "Interprétation des résultats, points forts et limites de l'approche."
    )

    st.html(
        """
        <div class="res-discussion-grid">
            <article class="res-discussion-card res-discussion-positive">
                <span class="res-card-kicker">POINTS FORTS</span>
                <h4>Une évaluation rigoureuse</h4>
                <ul>
                    <li>Validation croisée répétée : chaque patient est testé 3 fois, sur des modèles qui ne l'ont pas vu.</li>
                    <li>Imputation et mise à l'échelle ajustées dans chaque pli : pas de fuite d'information.</li>
                    <li>Une référence naïve (AUC 0,5) permet de mesurer le gain réel des modèles.</li>
                    <li>Variables connues avant la biopsie : aucune variable issue du résultat n'est utilisée.</li>
                </ul>
            </article>
            <article class="res-discussion-card res-discussion-limit">
                <span class="res-card-kicker">LIMITES</span>
                <h4>Ce que ces résultats ne couvrent pas</h4>
                <ul>
                    <li>Une seule base de données, sans validation sur un jeu externe ou un autre centre.</li>
                    <li>Des données rétrospectives : la qualité des variables IRM dépend des radiologues.</li>
                    <li>Un effectif modeste (462 patients) : les intervalles de confiance restent larges.</li>
                    <li>Le seuil de 50 % est une convention, non optimisée selon un objectif clinique.</li>
                </ul>
            </article>
        </div>
        """
    )

    encadre(
        "Interprétation",
        "Les deux modèles atteignent des performances proches, avec une AUC moyenne d'environ 0,90. "
        "Ce résultat indique une bonne capacité à classer les patients, mais il est une étape de recherche : "
        "il ne constitue pas une validation clinique ni un outil de diagnostic.",
    )


if __name__ == "__main__":
    main()
