"""Deep-row runs: settle the asymptotic exponents and refine e*."""
import numpy as np, json

def mass_deep(e, nrows, a=0.5, sample=200):
    s = np.sqrt(2*a)
    A = np.array([e], dtype=np.float64)
    prevS = None; hist = []
    for n in range(1, nrows+1):
        interior = a/A[:-1] + a/A[1:]
        A = np.concatenate(([e], interior, [e])) if n >= 2 else np.array([e, e])
        S = ((-1)**n) * (A - s).sum()
        if prevS is not None and (n % sample == 0 or n == nrows):
            hist.append((n, 0.5*(S+prevS)))
        prevS = S
    return hist

out = json.load(open('ladder_curve.json'))

print("=== large e, nrows=60000, Richardson on last thirds ===")
res = {}
for e in (10., 20., 40., 80., 160., 320.):
    h = mass_deep(e, 60000)
    n1, m1 = h[len(h)//2]; n2, m2 = h[-1]
    # power-law tail fit m(n) = m_inf + c n^-t using three points
    na, ma = h[len(h)//3]
    # assume t=1 Richardson: m_inf ~ m2 + (m2-m1)*n1/(n2-n1)
    rich = m2 + (m2 - m1)*n1/(n2 - n1)
    res[e] = (m2, rich)
    print(f"e={e:6.0f} m(60000)={m2:+.6f} rich(t=1)={rich:+.6f} last-drift={m2-m1:+.2e}")
es = np.array(sorted(res))
mr = np.array([res[e][1] for e in es])
sl = np.polyfit(np.log(es), np.log(-mr), 1)
print(f"log-log slope (richardson): {sl[0]:.4f}")
print("m/(e ln e):", " ".join(f"{res[e][1]/(e*np.log(e)):+.4f}" for e in es))
print("m/e^{4/3} :", " ".join(f"{res[e][1]/e**(4/3):+.4f}" for e in es))
out['large_e_deep'] = {str(e): res[e] for e in res}

print("=== small e, nrows=60000 ===")
res2 = {}
for e in (0.01, 0.02, 0.04, 0.08, 0.16):
    h = mass_deep(e, 60000)
    n1, m1 = h[len(h)//2]; n2, m2 = h[-1]
    rich = m2 + (m2 - m1)*n1/(n2 - n1)
    res2[e] = (m2, rich)
    print(f"e={e:5.2f} m(60000)={m2:+.6f} rich={rich:+.6f} drift={m2-m1:+.2e}")
es2 = np.array(sorted(res2))
mr2 = np.array([res2[e][1] for e in es2])
sl2 = np.polyfit(np.log(es2), np.log(-mr2), 1)
print(f"small-e log-log slope: {sl2[0]:.4f}")
print("m*e      :", " ".join(f"{res2[e][1]*e:+.4f}" for e in es2))
print("m*e*ln(1/e):", " ".join(f"{res2[e][1]*e/np.log(1/e):+.4f}" for e in es2))
out['small_e_deep'] = {str(e): res2[e] for e in res2}

print("=== e* refinement, nrows=20000 ===")
def mval(e):
    return mass_deep(e, 20000, sample=20000//2)[-1][1]
lo, hi = 0.605, 0.62
flo, fhi = mval(lo), mval(hi)
for _ in range(50):
    mid = 0.5*(lo+hi); fm = mval(mid)
    if (fm < 0) == (flo < 0): lo, flo = mid, fm
    else: hi, fhi = mid, fm
    if hi-lo < 1e-13: break
estar = 0.5*(lo+hi)
print(f"e* = {estar:.13f}")
out['estar_refined'] = estar

# peak of the hump
from scipy.optimize import minimize_scalar
r = minimize_scalar(lambda e: -mass_deep(e, 8000, sample=4000)[-1][1], bounds=(estar, 1.0), method='bounded', options={'xatol':1e-10})
print(f"hump peak at e={r.x:.10f}, m={-r.fun:.10f}")
out['hump'] = (r.x, -r.fun)

json.dump(out, open('ladder_curve.json','w'))
print("done")
