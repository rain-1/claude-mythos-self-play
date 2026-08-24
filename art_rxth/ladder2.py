"""Refinements: the second zero e* of m, convergence audit, asymptotics."""
import numpy as np, json
from ladder import mass_curve

out = json.load(open('ladder_curve.json'))

# --- convergence audit at extremes ---
for e in (0.05, 0.1, 20.0, 50.0):
    m3,_,e3 = mass_curve(e, nrows=3000)
    m6,_,e6 = mass_curve(e, nrows=6000)
    print(f"e={e:6.2f}  m(3000)={m3:+.10f}  m(6000)={m6:+.10f}  diff={m6-m3:+.2e}")

# --- second zero: bisection ---
lo, hi = 0.36, 0.70
flo = mass_curve(lo, nrows=6000)[0]
fhi = mass_curve(hi, nrows=6000)[0]
print(f"bracket: m({lo})={flo:+.6f}  m({hi})={fhi:+.6f}")
for _ in range(45):
    mid = 0.5*(lo+hi)
    fm = mass_curve(mid, nrows=6000)[0]
    if (fm < 0) == (flo < 0): lo, flo = mid, fm
    else: hi, fhi = mid, fm
estar = 0.5*(lo+hi)
print(f"second zero e* = {estar:.12f}")
print(f"  candidates: 1/2={0.5}, 1/sqrt5={5**-0.5:.12f}, 2/5={0.4}, "
      f"1/phi^2={((5**0.5-1)/2)**2:.12f}, e*^2={estar**2:.12f}, 1/e*={1/estar:.12f}")
out['estar'] = estar

# check m(1/2) exactly at rational points near
for e in (0.5, 0.45, 0.4142135623730951-0.0, np.sqrt(2)-1):
    print(f"m({e:.6f}) = {mass_curve(float(e), nrows=6000)[0]:+.10f}")

# --- large-e asymptotics: exponent fit ---
es = [10., 20., 40., 80., 160., 320.]
ms = []
for e in es:
    m,_,err = mass_curve(e, nrows=8000)
    ms.append(m); print(f"e={e:6.0f}  m={m:+.6f} err~{err:.1e}  m/e={m/e:+.5f}  m/(e ln e)={m/(e*np.log(e)):+.5f}")
import numpy as np
le, lm = np.log(es), np.log(-np.array(ms))
sl = np.polyfit(le, lm, 1)
print(f"large-e log-log slope: {sl[0]:.4f}")
out['large_e'] = list(zip(es, ms))

# --- small-e asymptotics ---
es2 = [0.02, 0.04, 0.08, 0.16]
ms2 = []
for e in es2:
    m,_,err = mass_curve(e, nrows=8000)
    ms2.append(m); print(f"e={e:5.2f}  m={m:+.6f} err~{err:.1e}  m*e={m*e:+.6f}  m*e^2={m*e*e:+.6f}")
le2, lm2 = np.log(es2), np.log(-np.array(ms2))
sl2 = np.polyfit(le2, lm2, 1)
print(f"small-e log-log slope: {sl2[0]:.4f}")
out['small_e'] = list(zip(es2, ms2))

json.dump(out, open('ladder_curve.json','w'))
print("updated ladder_curve.json")
