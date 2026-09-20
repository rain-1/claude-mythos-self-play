import numpy as np, json, time, fit_test as ft
F = ft.figures()['reuleaux']
nrm, off = ft.poly_edges(F)
print('self-outside', ft.outside_dist(F, nrm, off), flush=True)
diam = np.linalg.norm(F[:, None] - F[None], axis=2).max()
worst = 0.0; t0 = time.time()
for trial in range(30):
    fig = ft.two_parallel_folds(F, ft.rng)
    S = fig.hull_pts()
    if len(S) > 400:
        S = S[ft.rng.choice(len(S), 400, replace=False)]
    worst = max(worst, ft.best_fit(S, F, starts=12))
print('reuleaux', worst / diam, time.time() - t0)
json.dump(dict(worst_misfit_over_diameter=float(worst / diam), trials=30), open('fit_reuleaux.json', 'w'))
