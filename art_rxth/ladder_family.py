"""300 family members (a,e) and their collapse onto the universal curve."""
import numpy as np, json
from ladder import mass_curve

rng = np.random.default_rng(20260824)
pts = []
for i in range(300):
    a = float(np.exp(rng.uniform(np.log(0.05), np.log(20.0))))
    s = np.sqrt(2*a)
    eu = float(np.exp(rng.uniform(np.log(0.07), np.log(15.0))))   # target e/s
    e = eu * s
    M, _, err = mass_curve(e, nrows=1500, a=a)
    Mu, _, erru = mass_curve(eu, nrows=1500, a=0.5)
    pts.append(dict(a=a, e=e, M=float(M), eu=eu, Mu=float(Mu),
                    resid=float(M - s*Mu), err=float(err)))
    if (i+1) % 60 == 0:
        print(f"{i+1}/300  max|resid| so far = {max(abs(p['resid']) for p in pts):.2e}", flush=True)

json.dump(pts, open('family_pts.json','w'))
r = max(abs(p['resid']) for p in pts)
print(f"REDUCTION CERTIFICATE over 300 members: max |Mbar(a,e) - sqrt(2a) m(e/sqrt(2a))| = {r:.3e}")
