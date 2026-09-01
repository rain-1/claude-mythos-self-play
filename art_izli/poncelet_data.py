"""Generate all data for THE DANCE THAT CANNOT MISS (Poncelet piece)."""
import numpy as np, json, time
from poncelet import step, rho, find_r, closure_defect

def polish_r(d, r0, p, q, theta0=0.31, iters=60):
    """Secant on angular defect g(r) = total winding - 2 pi p after q steps."""
    def g(r):
        th = np.asarray([theta0]); tot = 0.0
        for _ in range(q):
            th, dth = step(th, np.asarray([d]), np.asarray([r]))
            tot += float(dth[0])
        return tot - 2 * np.pi * p
    r1, r2 = r0 * (1 - 1e-6), r0 * (1 + 1e-6)
    g1, g2 = g(r1), g(r2)
    for _ in range(iters):
        if g2 == g1: break
        r3 = r2 - g2 * (r2 - r1) / (g2 - g1)
        r1, g1, r2 = r2, g2, r3
        g2 = g(r2)
        if abs(g2) < 1e-15: break
    return r2, abs(g2)

def orbit_vertices(d, r, q, theta0):
    th = np.asarray([theta0]); out = [float(th[0])]
    for _ in range(q):
        th, _ = step(th, np.asarray([d]), np.asarray([r]))
        out.append(float(th[0]))
    return out

t0 = time.time()
out = {}

# ---- hero: q=7 p=2 heptagram family ----------------------------------------
d_hero = 0.24
r0 = float(find_r(np.asarray([d_hero]), 2 / 7, N=20000)[0])
r_hero, gdef = polish_r(d_hero, r0, 2, 7)
starts = np.linspace(0, 2 * np.pi, 72, endpoint=False)
worst = max(closure_defect(d_hero, r_hero, 7, t) for t in starts)
print(f"HERO 2/7: d={d_hero} r={r_hero:.14f} angdef={gdef:.2e} "
      f"worst closure over 72 starts={worst:.2e}")
out['hero'] = dict(d=d_hero, r=r_hero, p=2, q=7,
                   orbits=[orbit_vertices(d_hero, r_hero, 7, t) for t in starts],
                   worst_closure=worst)

# ---- medallions -------------------------------------------------------------
med_specs = [(1, 3, 0.42), (1, 4, 0.36), (2, 5, 0.3), (3, 8, 0.18)]
out['medallions'] = []
for p, q, d in med_specs:
    if (p, q) == (1, 3):
        r = (1 - d * d) / 2                     # Chapple, exact
    elif (p, q) == (1, 4):
        r = 1 / np.sqrt(1 / (1 - d) ** 2 + 1 / (1 + d) ** 2)   # Fuss, exact
    else:
        r0 = float(find_r(np.asarray([d]), p / q, N=20000)[0])
        r, _ = polish_r(d, r0, p, q)
    st = np.linspace(0, 2 * np.pi, 40, endpoint=False)
    worst = max(closure_defect(d, r, q, t) for t in st)
    print(f"medallion {p}/{q}: d={d} r={r:.12f} worst closure={worst:.2e}")
    out['medallions'].append(dict(d=d, r=float(r), p=p, q=q,
                                  orbits=[orbit_vertices(d, r, q, t) for t in st],
                                  worst_closure=worst))

# ---- rotation-number wash grid ----------------------------------------------
nd, nr = 460, 380
dg = np.linspace(0, 0.93, nd)
rg = np.linspace(0.02, 0.97, nr)
D, R = np.meshgrid(dg, rg)
valid = (D + R < 0.995)
Df, Rf = D[valid], R[valid]
print(f"rho grid: {valid.sum()} valid cells ...", flush=True)
V = rho(Df, Rf, N=650)
G = np.full(D.shape, np.nan)
G[valid] = V
np.save('poncelet_rho.npy', G)
np.save('poncelet_axes.npy', np.array([dg[0], dg[-1], rg[0], rg[-1]]))
print(f"grid done [{time.time()-t0:.0f}s]", flush=True)

# ---- closure curves ---------------------------------------------------------
curves = {}
targets = [(1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, 5), (2, 7), (3, 7),
           (3, 8), (2, 9), (4, 9), (5, 11)]
dsamp = np.linspace(0.0, 0.9, 61)
for p, q in targets:
    rr = find_r(dsamp, p / q, N=5000)
    ok = (rr > 1e-3) & (rr + dsamp < 1)
    curves[f"{p}/{q}"] = dict(d=dsamp[ok].tolist(), r=rr[ok].tolist())
    print(f"curve {p}/{q} done", flush=True)
out['curves'] = curves
# verify: numeric 1/3 curve vs exact Chapple; 1/4 vs Fuss
c3 = np.array(curves['1/3']['r']); dd = np.array(curves['1/3']['d'])
err3 = np.max(np.abs(c3 - (1 - dd ** 2) / 2))
c4 = np.array(curves['1/4']['r']); dd4 = np.array(curves['1/4']['d'])
err4 = np.max(np.abs(c4 - 1 / np.sqrt(1 / (1 - dd4) ** 2 + 1 / (1 + dd4) ** 2)))
print(f"CERTIFICATE: numeric 1/3 curve vs Chapple max err = {err3:.2e}")
print(f"CERTIFICATE: numeric 1/4 curve vs Fuss    max err = {err4:.2e}")
out['certificates'] = dict(chapple_err=float(err3), fuss_err=float(err4))

json.dump(out, open('poncelet_data.json', 'w'))
print(f"ALL DONE [{time.time()-t0:.0f}s]")
