"""appell_asym.py — do ASYMMETRIC three-atom laws have double zeros of Q_n?  Atoms {0, 1, a},
weights (p, r, 1-p-r); unknowns (p, r, Re x0, Im x0); equations Q_n(x0)=Q_{n-1}(x0)=0 (4 real).
Least-squares Newton from random starts; keep solutions inside the open simplex."""
import numpy as np, json, sys
from scipy.optimize import least_squares
def Q(n, x, atoms, w):
    return sum(wi * (x + ai) ** n for ai, wi in zip(atoms, w))
def F(v, n, atoms):
    p, r, xr, xi = v; x = xr + 1j * xi; w = (p, r, 1 - p - r)
    a = Q(n, x, atoms, w); b = Q(n - 1, x, atoms, w)
    return [a.real, a.imag, b.real, b.imag]
rng = np.random.default_rng(0)
found = {}
for a in [-1.0, -0.6, -2.0, 2.5, -0.35, 1.7]:
    atoms = (0.0, 1.0, a)
    for n in [4, 5, 6, 8]:
        sols = []
        for trial in range(400):
            v0 = [rng.uniform(0.01, 0.98), rng.uniform(0.01, 0.98), rng.uniform(-3, 3), rng.uniform(0.05, 3)]
            if v0[0] + v0[1] > 0.99: continue
            res = least_squares(F, v0, args=(n, atoms), xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=2000)
            p, r, xr, xi = res.x
            if res.cost < 1e-24 and p > 1e-6 and r > 1e-6 and p + r < 1 - 1e-6 and abs(xi) > 1e-6:
                key = (round(p, 6), round(r, 6), round(xr, 6), round(abs(xi), 6))
                if key not in sols: sols.append(key)
        found[f'a={a} n={n}'] = sols
        print(f'atoms {atoms} n={n}: {len(sols)} distinct double-zero laws', sols[:4], flush=True)
json.dump({k: [list(s) for s in v] for k, v in found.items()}, open('appell_asym.json', 'w'), indent=1)
