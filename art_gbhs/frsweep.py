"""frsweep.py — angle of loudest amplitude vs Froude number (Rabaud–Moisy 2013 narrowing),
measured from the linear field for a Gaussian pressure patch of size a = 1/Fr^2."""
import numpy as np, json, wake
rows = []
N = 2048; L = 220.0; dx = L / N
for a in [3.0, 2.0, 1.4, 1.0, 0.7, 0.5, 0.35, 0.25, 0.18, 0.12, 0.08]:
    eta, (x0, y0) = wake.solve(N, L, a=a, mu=0.02, src=(0.1, 0.5))
    psis, prof = wake.angle_profile(eta, x0, y0, 0, dx, dx, 0.3 * L, 0.85 * L, psis=np.linspace(0, 30, 601))
    peak, edge, sm = wake.wedge_from_profile(psis, prof, frac=0.5)
    Fr = 1 / np.sqrt(a)
    rows.append(dict(a=a, Fr=float(Fr), peak_deg=float(peak), edge50_deg=float(edge),
                     ratio_22_over_peak=float(np.interp(22, psis, prof) / sm.max()),
                     ratio_25_over_peak=float(np.interp(25, psis, prof) / sm.max())))
    print(rows[-1], flush=True)
json.dump(rows, open('frsweep.json', 'w'), indent=1)
