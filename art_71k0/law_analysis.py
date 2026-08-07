"""Final asymptotic-law analysis for MO 513971 mu_n.
- local slopes d(mu)/d(lnln n) between adjacent anchors
- fits: a + b lnln n (b free) vs b fixed = 1/ln2 (log2log2 law) vs 2
- holdout prediction test: fit on n <= 2048, predict 8192/12288/16384
"""
import json, numpy as np

mc = {}
for fn in ["mc_mu.json", "mc_mu2.json"]:
    try:
        for k, v in json.load(open(fn)).items():
            if int(k) not in mc or v['trials'] > mc[int(k)]['trials']:
                mc[int(k)] = v
    except FileNotFoundError:
        pass
ns = np.array(sorted(mc))
mu = np.array([mc[n]['mu'] for n in ns])
se = np.array([mc[n]['se'] for n in ns])
print("anchors:", list(ns))

print("\nlocal slope d mu / d lnln n:")
for i in range(1, len(ns)):
    x0, x1 = np.log(np.log(ns[i-1])), np.log(np.log(ns[i]))
    s = (mu[i]-mu[i-1])/(x1-x0)
    err = np.hypot(se[i], se[i-1])/(x1-x0)
    print(f"  {ns[i-1]:>6} -> {ns[i]:>6}: slope {s:6.3f} +- {err:.3f}")

for nmin in [32, 128, 512, 2048]:
    sel = ns >= nmin
    x = np.log(np.log(ns[sel])); y = mu[sel]; w = 1/se[sel]**2
    A = np.vstack([np.ones(sel.sum()), x]).T
    W = np.diag(w)
    coef = np.linalg.solve(A.T@W@A, A.T@W@y)
    resid = y - A@coef
    chi2 = float(np.sum(w*resid**2))
    print(f"fit n>={nmin:5d}: mu = {coef[0]:.3f} + {coef[1]:.3f} lnln n   "
          f"chi2/dof={chi2/(sel.sum()-2):.2f}")
print(f"reference slopes: 1/ln2 = {1/np.log(2):.4f}   2.0")

# holdout: fit on n <= 2048 (n>=64), predict the top three
sel = (ns >= 64) & (ns <= 2048)
x = np.log(np.log(ns[sel])); y = mu[sel]; w = 1/se[sel]**2
A = np.vstack([np.ones(sel.sum()), x]).T
coef = np.linalg.solve(A.T@np.diag(w)@A, A.T@np.diag(w)@y)
print(f"\nholdout fit (64<=n<=2048): a={coef[0]:.3f} b={coef[1]:.3f}")
for n in ns[ns > 2048]:
    pred = coef[0] + coef[1]*np.log(np.log(n))
    obs = mc[int(n)]['mu']
    print(f"  n={n:>6}: predicted {pred:.3f}  observed {obs:.3f} +- {mc[int(n)]['se']:.3f}"
          f"   pull {(obs-pred)/mc[int(n)]['se']:+.1f} sigma")
