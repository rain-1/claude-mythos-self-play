"""Top-up MC at large n + per-pass permutation-displacement cascade profiles."""
import numpy as np, json, time
from sort_lib import _row_keys, _lex_argsort, rows_sorted

rng = np.random.default_rng(77000513971)

def run_trial(n):
    A = rng.integers(0, 2, (n, n), dtype=np.int8).astype(np.uint8)
    t = 0
    disps = []
    while True:
        t += 1
        if t % 2 == 1:
            K = _row_keys(A)
            p = _lex_argsort(K)
            B = A[p]
        else:
            K = _row_keys(np.ascontiguousarray(A.T))
            p = _lex_argsort(K)
            B = A[:, p]
        disps.append(int(np.abs(p - np.arange(n)).sum()))
        A = B
        if rows_sorted(A) and rows_sorted(np.ascontiguousarray(A.T)):
            return t, disps

GRID = [(1024, 400), (2048, 250), (4096, 150), (6144, 60), (8192, 40)]
out = {}
for n, trials in GRID:
    t0 = time.time()
    Ts, dprofiles = [], []
    for _ in range(trials):
        t, d = run_trial(n)
        Ts.append(t); dprofiles.append(d)
    Ts = np.array(Ts)
    dist = {int(t): int((Ts == t).sum()) for t in np.unique(Ts)}
    # mean displacement at pass t over trials reaching that pass
    maxT = int(Ts.max())
    md = []
    for tt in range(maxT):
        vals = [d[tt] for d in dprofiles if len(d) > tt]
        md.append(dict(pass_=tt + 1, nreach=len(vals), mean=float(np.mean(vals)),
                       median=float(np.median(vals))))
    out[n] = dict(trials=trials, mu=float(Ts.mean()),
                  se=float(Ts.std(ddof=1) / np.sqrt(len(Ts))), dist=dist, disp=md)
    print(f"n={n} mu={Ts.mean():.4f}+-{Ts.std(ddof=1)/np.sqrt(len(Ts)):.4f} "
          f"dist={dist} [{time.time()-t0:.0f}s]", flush=True)
    json.dump(out, open("mc_topup.json", "w"), indent=1)
print("done")
