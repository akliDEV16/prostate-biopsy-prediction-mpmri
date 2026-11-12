# ProstaAI — Prédiction du résultat de biopsie prostatique à partir de l'IRM multiparamétrique

Projet académique d'intelligence artificielle. Il étudie si des données **cliniques** et **radiologiques** (IRM multiparamétrique) permettent d'estimer le résultat d'une biopsie prostatique, avant que la biopsie ne soit réalisée.

> **Avertissement** — ProstaAI est un prototype de recherche. Il **ne constitue pas un dispositif médical** et ne doit servir à aucune décision clinique.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Données](#données)
- [Utilisation](#utilisation)
- [Méthodologie](#méthodologie)
- [Résultats](#résultats)
- [Application web](#application-web)
- [Limites](#limites)
- [Équipe et remerciements](#équipe-et-remerciements)
- [Licence](#licence)

---

## Fonctionnalités

- Construction d'un tableau **à l'échelle du patient** à partir de deux fichiers bruts (clinique et radiologique).
- Contrôles automatiques : refus de toute variable qui contient le résultat de la biopsie (fuite de données), vérification de la population attendue.
- Comparaison de trois approches avec **le même protocole** : une référence naïve, une régression logistique et une Random Forest.
- Évaluation par **validation croisée stratifiée répétée** (5 plis × 3 répétitions).
- Entraînement final et sauvegarde des modèles.
- Application **Streamlit** multipage : explication du sujet, présentation de l'IA, démonstration interactive, résultats, méthodologie et formulaire d'avis.

---

## Structure du projet

```
prostate-biopsy-prediction-mpmri/
├── app.py                      # Point d'entrée de l'application Streamlit
├── main.py                     # Pipeline complet : tableau -> validation croisée -> entraînement
├── requirements.txt            # Versions épinglées des dépendances
├── data/
│   ├── raw/                    # Fichiers bruts (non versionnés, voir Données)
│   └── processed/              # Tableau du modèle généré (non versionné)
├── models/                     # Modèles entraînés (.joblib, non versionnés)
├── results/
│   ├── cv_details.csv          # Scores de chaque découpe (modèle × pli × répétition)
│   └── cv_resume.csv           # Moyenne et écart-type par modèle
├── notebooks/                  # Expérimentations
└── src/
    ├── data/                   # Chargement, nettoyage, fusion, construction du tableau
    │   ├── load_data.py
    │   ├── clean_data.py
    │   ├── merge_data.py
    │   ├── prepare_data.py     # Tableau final, liste des variables, contrôles
    │   ├── inspect_data.py
    │   ├── inspect_alignement.py
    │   └── aklimansouri.py
    ├── features/               # Transformations apprises (imputation, mise à l'échelle, découpage)
    │   ├── imputation.py
    │   ├── scaling.py
    │   └── split_data.py
    ├── models/                 # Pipelines, évaluation, entraînement, contrôles de plausibilité
    │   ├── train.py
    │   ├── evaluate.py
    │   └── sanity_checks.py
    └── ui/                     # Application Streamlit
        ├── components/footer.py
        ├── pages/              # Une page par fichier
        └── styles/             # Une feuille CSS par page + common.css
```

---

## Installation

Le projet a été préparé avec **Python 3.12** (les fichiers compilés présents dans le dépôt sont au format `cpython-312`).

```bash
# 1. Cloner le dépôt
git clone https://github.com/dyhia-hachemi/prostate-biopsy-prediction-mpmri.git
cd prostate-biopsy-prediction-mpmri

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate

# 3. Installer les dépendances (versions épinglées)
pip install -r requirements.txt
```

Les versions principales sont : `scikit-learn==1.5.2`, `pandas==2.2.3`, `numpy==1.26.4`, `imbalanced-learn==0.12.4`, `streamlit==1.67.0`.

> Les fichiers `.joblib` et les données sont ignorés par Git (voir `.gitignore`). Si vous clonez le dépôt, ajoutez les données dans `data/raw/` puis lancez la construction du tableau (étape 1 de [Utilisation](#utilisation)).

---

## Données

Le projet utilise la base **AI4AR Prostate mpMRI Database**, publiée sous licence **CC BY 4.0**.

Placez les fichiers suivants dans `data/raw/` :

| Fichier | Contenu |
|---|---|
| `AI4A4_PCa_clinical.csv` | Une ligne par patient : variables cliniques et résultat de biopsie (cible) |
| `AI4AR_PCa_radiological.csv` | Observations radiologiques : une ou plusieurs lignes par lésion, selon le radiologue |
| `opis-medyczno-radiologiczny.pdf` | Dictionnaire des variables (document de référence) |

> Le nom du fichier clinique est écrit `AI4A4_…` (et non `AI4AR_…`) : utilisez exactement ce nom, comme dans le code.

### Population retenue

Le tableau final conserve les patients des groupes :

- **BN** (*Biopsy Naïve*) : jamais biopsiés ;
- **TN** (*Previous Negative Biopsies*) : biopsies antérieures négatives ;

dont le résultat de biopsie est connu. Le tableau contient **462 patients** : **248 avec cancer** et **214 sans cancer**.

### Variables d'entrée (10)

Toutes sont connues **avant** la biopsie.

| Variable | Description |
|---|---|
| `patient_age` | Âge du patient |
| `log_psa` | Logarithme du PSA : `log(1 + PSA)` |
| `prostate_volume_mri` | Volume prostatique mesuré à l'IRM (mL) |
| `psa_density_mri` | Densité du PSA : `PSA / volume` |
| `dre_result` | Toucher rectal : 0 = négatif, 1 = positif |
| `prior_biopsies` | Nombre de biopsies antérieures |
| `is_TN` | 1 si groupe TN, 0 si groupe BN |
| `no_of_lesions` | Nombre de lésions décrites à l'IRM |
| `pirads_max` | Score PI-RADS maximal parmi les lésions |
| `dim_max` | Dimension maximale des lésions (mm) |

**Cible** : `y_cancer` = 1 si la biopsie montre un cancer, 0 sinon.

### Valeurs manquantes

- Les valeurs manquantes sont **imputées à l'intérieur du pipeline** (médiane), donc uniquement à partir des patients d'entraînement de chaque pli.
- Cas particulier : sans aucune lésion décrite, les variables IRM sont codées à 0.

---

## Utilisation

Les commandes sont à lancer depuis la racine du projet.

### 1. Construire le tableau du modèle

```bash
python -m src.data.prepare_data
```

Produit `data/processed/ai4ar_model_table.csv` et vérifie la population (462 patients, 248 cancers, 214 sans cancer). Le script s'arrête avec un message explicite si les données ne correspondent pas.

### 2. Lancer le pipeline complet

```bash
python main.py
```

Enchaîne :

1. construction du tableau du modèle ;
2. validation croisée des trois approches, avec écriture de `results/cv_details.csv` et `results/cv_resume.csv` ;
3. entraînement final de la régression logistique et de la Random Forest sur tous les patients, sauvegardé dans `models/`.

### 3. Contrôles de plausibilité (facultatif)

```bash
python -m src.models.sanity_checks
```

Affiche l'AUC de chaque variable seule (pour repérer une éventuelle fuite) et compare la clinique seule à la clinique + IRM.

### 4. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre dans le navigateur (par défaut `http://localhost:8501`).

---

## Méthodologie

### Pipeline de traitement

1. **Collecte** : chargement des fichiers clinique et radiologique (`src/data/load_data.py`).
2. **Nettoyage** : suppression des espaces, conversion en valeurs numériques, contrôle des identifiants et des plages (`clean_data.py`).
3. **Résumé IRM par patient** : pour chaque patient, PI-RADS maximal, dimension maximale et nombre de lésions. Les avis multiples d'un même radiologue sont regroupés, puis résumés par la médiane par lésion.
4. **Fusion** clinique + IRM par `patient_id`, en conservant le nombre de lignes du fichier clinique (`merge_data.py`).
5. **Tableau final** : sélection de la population, création de la cible et des variables dérivées, contrôle qu'aucune variable interdite n'est utilisée (`prepare_data.py`).

### Modèles comparés

| Modèle | Prétraitement | Paramètres |
|---|---|---|
| **Réponse naïve** (référence) | Imputation médiane | `DummyClassifier`, stratégie `most_frequent` |
| **Régression logistique** | Imputation médiane + `StandardScaler` | `max_iter=1000`, `random_state=0` |
| **Random Forest** | Imputation médiane (sans mise à l'échelle) | 300 arbres, `random_state=0` |

### Protocole d'évaluation

- **Validation croisée stratifiée répétée** : 5 plis, 3 répétitions, soit 15 évaluations par modèle (`RepeatedStratifiedKFold`, `random_state=0`).
- Chaque pipeline est **cloné et ajusté uniquement sur le train de chaque pli** : médianes d'imputation et paramètres de mise à l'échelle n'utilisent jamais les patients de test.
- Métriques : **ROC-AUC**, **balanced accuracy** et **accuracy**, avec le seuil de décision à 0,5.

---

## Résultats

Résultats de la validation croisée (moyenne ± écart-type sur les 15 découpes), extraits de `results/cv_resume.csv` :

| Modèle | ROC-AUC | Balanced accuracy | Accuracy |
|---|---|---|---|
| Réponse naïve | 0,500 ± 0,000 | 0,500 ± 0,000 | 0,537 ± 0,004 |
| **Régression logistique** | **0,901 ± 0,036** | **0,822 ± 0,035** | **0,824 ± 0,034** |
| Random Forest | 0,899 ± 0,023 | 0,821 ± 0,029 | 0,823 ± 0,028 |

**Lecture.** Les deux modèles atteignent des performances proches : l'écart d'AUC (0,002) est très inférieur à la variabilité entre découpes. Aucun ne se détache clairement de l'autre. Les deux dépassent nettement la référence naïve.

Pour l'analyse des erreurs, les courbes ROC et les matrices de confusion, voir la page **Résultats** de l'application.

---

## Application web

| Page | Contenu |
|---|---|
| **Accueil** | Présentation du projet et accès aux sections |
| **Comprendre le cancer** | Cancer de la prostate, biopsie, lecture de l'IRM et PI-RADS |
| **Notre IA** | Données utilisées, variables, modèles et choix techniques |
| **Démonstration** | Saisie d'un patient et estimation des deux modèles (résultat expérimental) |
| **Résultats** | Métriques, comparaison, courbes ROC, matrices de confusion, analyse des erreurs |
| **Méthodologie** | Étapes de préparation, apprentissage et évaluation |
| **À propos** | Équipe, cadre académique et formulaire d'avis |

Les avis envoyés depuis la page **À propos** sont ajoutés, sans nom ni coordonnées, au fichier `data/feedback/avis_prostaai.csv` (créé automatiquement).

Les pages **Démonstration** et **Résultats** lisent les modèles et les résultats générés par `main.py`. Si `models/` ou `results/` sont vides, l'application l'indique et propose de lancer `python main.py`.

---

## Limites

- **Pas un dispositif médical.** Le modèle est un prototype de recherche ; il ne remplace ni un diagnostic ni l'avis d'un professionnel de santé.
- **Pas de validation externe.** Les performances proviennent d'une seule base, évaluée par validation croisée interne. Elles ne garantissent pas le comportement sur d'autres centres ou d'autres appareils d'IRM.
- **Données rétrospectives.** Les variables IRM (PI-RADS, dimension, nombre de lésions) dépendent de l'interprétation des radiologues.
- **Effectif modeste** (462 patients) : les intervalles de confiance restent larges.
- **Démonstration biaisée.** Les modèles affichés dans la page Démonstration sont entraînés sur les 462 patients ; leurs estimations ne mesurent donc pas la performance sur de nouveaux patients.
- **Seuil de 50 %** : c'est une convention de présentation, non optimisée selon un objectif clinique.

---

## Équipe et remerciements

Projet réalisé dans le cadre d'un travail académique à l'**Université Mouloud Mammeri de Tizi-Ouzou (UMMTO)**, Faculté de génie électrique et informatique, département informatique.

- Mansouri Akli
- Hachemi Dyhia


---

## Licence

- **Données** : AI4AR Prostate mpMRI Database, licence **CC BY 4.0**. Citez la base d'origine si vous réutilisez les données.
- **Code** : *à compléter par les auteurs* (choisir une licence et l'indiquer ici, par exemple MIT).
