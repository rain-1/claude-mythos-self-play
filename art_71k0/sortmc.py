"""MO 513971 Monte-Carlo: T(A) for random n x n Bernoulli(p) matrices.
Rows packed to bytes; lexicographic sorts via Python's sort on bytes objects
(memcmp semantics = true lex order on fixed-width binary strings).

Modes:
  mu     : sweep n at p=1/2, many trials -> mu_n estimates + distribution
  sparse : sweep density c (mean ones per row) at fixed n
  hero   : generate one doubly-sorted fixed point + full history at large n
"""
import numpy as np, sys, json, time

rng = np.random.default_rng(20260807)

def pack_rows(A):
    return np.packbits(A, axis=1)

def sort_T(A, want_history=False, max_steps=None):
    """Alternating sorts starting with R; returns (T, A_final, history).
    history = list of (kind, permutation) actually applied (identity sorts of
    an already-sorted side are counted by T but recorded too)."""
    n = A.shape[0]
    if max_steps is None: max_steps = 4 * n + 8
    hist = []
    t = 0
    while True:
        t += 1
        if t % 2 == 1:                                   # row sort
            kb = pack_rows(A).tobytes()
            m = A.shape[1] // 8 if A.shape[1] % 8 == 0 else (A.shape[1] + 7) // 8
            rows = [kb[i*m:(i+1)*m] for i in range(n)]
            order = sorted(range(n), key=rows.__getitem__)
            A = A[order]
            if want_history: hist.append(('R', order))
            # terminal iff columns sorted
            kbc = pack_rows(np.ascontiguousarray(A.T))
            mc = kbc.shape[1]; b = kbc.tobytes()
            cols = [b[j*mc:(j+1)*mc] for j in range(A.shape[1])]
            if all(cols[j] <= cols[j+1] for j in range(len(cols)-1)):
                return t, A, hist
        else:                                            # column sort
            kbc = pack_rows(np.ascontiguousarray(A.T))
            mc = kbc.shape[1]; b = kbc.tobytes()
            cols = [b[j*mc:(j+1)*mc] for j in range(A.shape[1])]
            order = sorted(range(A.shape[1]), key=cols.__getitem__)
            A = A[:, order]
            if want_history: hist.append(('C', order))
            kb = pack_rows(A)
            m = kb.shape[1]; b = kb.tobytes()
            rows = [b[i*m:(i+1)*m] for i in range(n)]
            if all(rows[i] <= rows[i+1] for i in range(len(rows)-1)):
                return t, A, hist
        if t > max_steps:
            raise RuntimeError("no convergence")

def mode_mu():
    plan = [(8, 60000), (12, 60000), (16, 60000), (24, 40000), (32, 40000),
            (48, 30000), (64, 30000), (96, 20000), (128, 20000), (192, 12000),
            (256, 12000), (384, 8000), (512, 8000), (768, 5000), (1024, 5000),
            (1536, 2500), (2048, 2000), (3072, 1000), (4096, 800),
            (6144, 400), (8192, 300), (12288, 150), (16384, 100)]
    out = {}
    for n, trials in plan:
        t0 = time.time(); Ts = np.empty(trials, np.int32)
        for k in range(trials):
            A = (rng.random((n, n)) < 0.5)
            Ts[k], _, _ = sort_T(A)
        mu = Ts.mean(); se = Ts.std(ddof=1)/np.sqrt(trials)
        cnt = np.bincount(Ts, minlength=16)[:16]
        out[n] = dict(trials=trials, mu=float(mu), se=float(se),
                      dist=[int(c) for c in cnt])
        print(f"n={n:6d} trials={trials:6d} mu={mu:.4f} +- {se:.4f} "
              f"dist={list(cnt[1:10])}  ({time.time()-t0:.0f}s)", flush=True)
        json.dump(out, open("mc_mu.json", "w"), indent=1)

def mode_mu2():
    plan = [(2048, 2500), (3072, 1200), (4096, 1000), (6144, 500),
            (8192, 400), (12288, 180), (16384, 120)]
    out = {}
    for n, trials in plan:
        t0 = time.time(); Ts = np.empty(trials, np.int32)
        for k in range(trials):
            A = (rng.random((n, n)) < 0.5)
            Ts[k], _, _ = sort_T(A)
        mu = Ts.mean(); se = Ts.std(ddof=1)/np.sqrt(trials)
        cnt = np.bincount(Ts, minlength=16)[:16]
        out[n] = dict(trials=trials, mu=float(mu), se=float(se),
                      dist=[int(c) for c in cnt])
        print(f"n={n:6d} trials={trials:6d} mu={mu:.4f} +- {se:.4f} "
              f"dist={list(cnt[1:12])}  ({time.time()-t0:.0f}s)", flush=True)
        json.dump(out, open("mc_mu2.json", "w"), indent=1)

def mode_sparse():
    n = 2048
    out = {}
    for c in [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
        p = c / n; trials = 300
        Ts = np.empty(trials, np.int32)
        for k in range(trials):
            A = (rng.random((n, n)) < p)
            Ts[k], _, _ = sort_T(A)
        print(f"c={c:7.1f} mu={Ts.mean():.3f} +- {Ts.std(ddof=1)/np.sqrt(trials):.3f} "
              f"max={Ts.max()}", flush=True)
        out[str(c)] = dict(mu=float(Ts.mean()), se=float(Ts.std(ddof=1)/np.sqrt(trials)),
                           max=int(Ts.max()))
        json.dump(out, open("mc_sparse.json", "w"), indent=1)

def mode_hero(n=4096, c=6.0, tag="hero"):
    p = c / n
    A0 = (rng.random((n, n)) < p)
    T, Af, hist = sort_T(A0.copy(), want_history=True)
    print(f"hero n={n} c={c}: T={T}, ones={Af.sum()}", flush=True)
    np.savez_compressed(f"{tag}_n{n}_c{c}.npz",
                        A0=np.packbits(A0), Af=np.packbits(Af), T=T,
                        hists=np.array([h[0] for h in hist]),
                        perms=np.array([h[1] for h in hist], dtype=object),
                        allow_pickle=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "mu"
    if mode == "mu": mode_mu()
    elif mode == "mu2": mode_mu2()
    elif mode == "sparse": mode_sparse()
    elif mode == "hero":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
        c = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
        mode_hero(n, c)
