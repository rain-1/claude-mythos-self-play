"""fit_test2.py — hunting a non-fitting fold image of an ELLIPSE (MO 7016): k random folds (any
directions), then the best rigid fit; report the worst misfit found."""
import numpy as np, json, time, sys
import fold
from fit_test import best_fit, figures
rng = np.random.default_rng(1)
figs = figures()
res = {}
t0 = time.time()
for name in ('ellipse 0.85', 'ellipse 0.7', 'ellipse 0.97'):
    if name == 'ellipse 0.7':
        t = np.linspace(0, 2 * np.pi, 720, endpoint=False); F = np.c_[np.cos(t), 0.7 * np.sin(t)]
    else:
        F = figs[name]
    diam = 2.0
    for k in (2, 3, 4):
        worst = 0.0
        for trial in range(25):
            fig = fold.Folded(F)
            fold.random_fold_sequence(fig, k, rng, frac=(0.05, 0.45))
            S = fig.hull_pts()
            if len(S) > 350:
                S = S[rng.choice(len(S), 350, replace=False)]
            b = best_fit(S, F, starts=10)
            worst = max(worst, b)
        res[f'{name} k={k}'] = float(worst / diam)
        print(name, k, res[f'{name} k={k}'], time.time() - t0, flush=True)
json.dump(res, open('fit_test2.json', 'w'), indent=1)
