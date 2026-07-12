"""Exact uniform random partitions of n via Fristedt's conditioning device.

Multiplicities N_k ~ independent Geometric: P(N_k=j) = (1-q^k) q^{kj} with
q = exp(-pi/sqrt(6n)); conditioned on sum(k*N_k) == n the multiset is EXACTLY
uniform over all partitions of n (every partition has weight q^n).

window > 0: accept |sum-n| <= window and repair by adjusting the multiplicity
of part 1 (still a partition of exactly n; measure distortion is O(window/#ones),
used only for background ghost ensembles, never the hero).
"""
import numpy as np

def sample_partitions(n, count, window=0, seed=0, batch=2048, verbose=False):
    q = np.exp(-np.pi / np.sqrt(6.0 * n))
    K = int(np.ceil(np.log(1e-10) / np.log(q)))  # parts beyond K: P(N_k>0)<1e-10
    ks = np.arange(1, K + 1)
    qk = q ** ks
    out, tries = [], 0
    rng = np.random.default_rng(seed)
    while len(out) < count:
        tries += batch
        # geometric via floor(log(U)/log(q^k))
        U = rng.random((batch, K))
        Nk = np.floor(np.log(U) / np.log(qk)[None, :]).astype(np.int64)
        tot = Nk @ ks
        ok = np.abs(tot - n) <= window
        for i in np.where(ok)[0]:
            m = Nk[i].copy()
            d = n - int(tot[i])
            m[0] += d                      # repair with 1-parts
            if m[0] < 0:
                continue
            out.append(m)
            if len(out) >= count:
                break
    if verbose:
        print(f"n={n}: {count} partitions, rate {count/tries:.2e} (K={K})")
    return out

def parts_from_mult(m):
    """multiplicity vector -> sorted parts descending."""
    ks = np.nonzero(m)[0] + 1
    return np.repeat(ks, m[ks - 1])[::-1]

def boundary_staircase(parts):
    """Young diagram boundary as polyline in (x=part length, y=row index) coords,
    from (lambda_1, 0) to (0, #rows). parts sorted descending."""
    xs, ys = [parts[0]], [0]
    for i in range(len(parts)):
        xs.append(parts[i]); ys.append(i + 1)
        if i + 1 < len(parts) and parts[i + 1] != parts[i]:
            xs.append(parts[i + 1]); ys.append(i + 1)
    xs.append(0); ys.append(len(parts))
    return np.array(xs, float), np.array(ys, float)

if __name__ == "__main__":
    # verification 1: exact uniformity at n=20 (p(20)=627)
    def enum_partitions(n):
        sols = []
        def rec(rem, maxpart, cur):
            if rem == 0:
                sols.append(tuple(cur)); return
            for p in range(min(rem, maxpart), 0, -1):
                rec(rem - p, p, cur + [p])
        rec(n, n, [])
        return sols
    n = 20
    allp = enum_partitions(n)
    print(f"p({n}) = {len(allp)}")
    S = sample_partitions(n, 200000, window=0, seed=42, verbose=True)
    from collections import Counter
    cnt = Counter(tuple(parts_from_mult(m).tolist()) for m in S)
    counts = np.array([cnt.get(p, 0) for p in allp])
    M, Kc = counts.sum(), len(allp)
    chi2 = ((counts - M / Kc) ** 2 / (M / Kc)).sum()
    print(f"chi2={chi2:.0f} vs dof={Kc-1} (+-{np.sqrt(2*(Kc-1)):.0f}) -> "
          f"{'UNIFORM OK' if abs(chi2-(Kc-1)) < 4*np.sqrt(2*(Kc-1)) else 'FAIL'}")

    # verification 2: largest part law at n=250000
    n = 250000
    S = sample_partitions(n, 12, window=0, seed=1, verbose=True)
    mx = [parts_from_mult(m)[0] for m in S]
    nparts = [len(parts_from_mult(m)) for m in S]
    c = np.sqrt(6 * n) / (2 * np.pi)
    pred = c * np.log(6 * n / np.pi ** 2)
    print(f"largest part: mean {np.mean(mx):.0f}, theory ~{pred:.0f} "
          f"(Gumbel spread ~{c:.0f})")
    print(f"#parts: mean {np.mean(nparts):.0f} (same law by conjugation)")

    # verification 3: boundary vs Vershik curve
    m = S[0]
    parts = parts_from_mult(m)
    xs, ys = boundary_staircase(parts)
    s = np.sqrt(n)
    # sample curve deviation at interior points
    xg = np.linspace(0.2, 1.5, 400) * s  # bulk; extreme tails are Gumbel territory
    yb = np.interp(xg, xs[::-1], ys[::-1])  # boundary y(x): xs descending
    yv = -np.sqrt(6 * n) / np.pi * np.log(1 - np.exp(-np.pi * xg / np.sqrt(6 * n)))
    dev = np.abs(yb - yv) / s
    print(f"max |boundary - Vershik| = {dev.max():.4f} sqrt(n) units "
          f"(n^-1/4 scale = {n**-0.25:.4f})")
