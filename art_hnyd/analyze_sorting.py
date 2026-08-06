"""Fit candidate asymptotic laws to mu_n data; examine T-distribution structure."""
import json, numpy as np

mc = json.load(open("mc_scale.json"))
try:
    tu = json.load(open("mc_topup.json"))
except FileNotFoundError:
    tu = {}
ex = json.load(open("exact_small.json"))

# merge: exact where available, MC else; topup pooled with base MC
data = {}
for n_s, d in mc.items():
    n = int(n_s)
    data[n] = dict(mu=d['mu'], se=d['se'], w=d['trials'], dist=dict(d['dist']))
for n_s, d in tu.items():
    n = int(n_s)
    if n in data:
        w0, w1 = data[n]['w'], d['trials']
        mu = (data[n]['mu'] * w0 + d['mu'] * w1) / (w0 + w1)
        dist = data[n]['dist'].copy()
        for t, c in d['dist'].items():
            dist[t] = dist.get(t, 0) + c
        data[n] = dict(mu=mu, se=(data[n]['se'] * w0 + d['se'] * w1) / (w0 + w1) / np.sqrt(2),
                       w=w0 + w1, dist=dist)
    else:
        data[n] = dict(mu=d['mu'], se=d['se'], w=d['trials'], dist=dict(d['dist']))
for n_s, d in ex.items():
    n = int(n_s)
    data[n] = dict(mu=d['mu_f'], se=0.0005, w=10**9, dist={str(k): v for k, v in d['dist'].items()})

ns = np.array(sorted(data))
mus = np.array([data[n]['mu'] for n in ns])
ses = np.array([max(data[n]['se'], 1e-4) for n in ns])
print("n, mu, se:")
for n, m, s in zip(ns, mus, ses):
    print(f"  {n:6d} {m:.4f} {s:.4f}")

# fits on n >= 16 (asymptotic regime-ish)
mask = ns >= 16
X = ns[mask].astype(float)
Y = mus[mask]
W = 1 / ses[mask] ** 2

def wls(F):
    """weighted least squares mu = a + b*F(n); returns a, b, chi2/dof"""
    f = F(X)
    A = np.stack([np.ones_like(f), f], 1)
    AtW = A.T * W
    coef = np.linalg.solve(AtW @ A, AtW @ Y)
    resid = Y - A @ coef
    chi2 = float((W * resid ** 2).sum())
    return coef, chi2 / (len(Y) - 2)

cands = {
    "a + b lnln n": lambda x: np.log(np.log(x)),
    "a + b log2log2 n": lambda x: np.log2(np.log2(x)),
    "a + b (ln n)^{1/2}": lambda x: np.sqrt(np.log(x)),
    "a + b (ln n)^{1/3}": lambda x: np.log(x) ** (1 / 3),
    "a + b ln n": lambda x: np.log(x),
    "a + b lnlnln-free (ln ln)^2": lambda x: np.log(np.log(x)) ** 2,
}
print("\nfits on n>=16:")
for name, F in cands.items():
    (a, b), red = wls(F)
    print(f"  {name:28s} a={a:.3f} b={b:.3f}  chi2/dof={red:.1f}")

# tail structure: P(T >= t) vs n
print("\nP(T>=t):")
for t in [5, 6, 7, 8]:
    row = []
    for n in ns[ns >= 32]:
        dist = data[n]['dist']
        tot = sum(dist.values())
        p = sum(c for k, c in dist.items() if int(k) >= t) / tot
        row.append(f"{n}:{p:.3f}")
    print(f"  t={t}: " + " ".join(row))
json.dump({int(n): {k: v for k, v in data[n].items() if k != 'w'} for n in ns},
          open("mu_merged.json", "w"), indent=1)
