"""
Découpage en plis de validation croisée (stratifié et répété).

Avec 462 patients, la validation croisée répétée donne une estimation plus stable
qu'un seul jeu de test de 20 %.
"""
import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold

# CONFIGURATION 
RANDOM_STATE = 0
N_SPLITS = 5
N_REPEATS = 5


def make_cv(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE):
    return RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats,
                                   random_state=random_state)


if __name__ == "__main__":
    from src.data.prepare_data import get_X_y, load_model_table

    X, y = get_X_y(load_model_table())
    cv = make_cv()
    print(f"{len(X)} patients, {cv.get_n_splits()} découpes "
          f"({N_REPEATS} répétitions x {N_SPLITS} plis)")

    # Contrôle sur la première répétition : chaque patient est testé exactement une fois
    vus = np.zeros(len(X), dtype=int)
    for i, (train, test) in enumerate(cv.split(X, y)):
        if i < N_SPLITS:
            vus[test] += 1
            print(f"pli {i + 1} : train {len(train)} | test {len(test)} | "
                  f"cancers dans le test : {y.iloc[test].mean() * 100:.0f} %")
    assert (vus == 1).all()
    print("Contrôle : chaque patient est dans un test exactement une fois par répétition : OK")