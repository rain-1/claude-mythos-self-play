import json, sys, math, numpy as np
from scipy import stats, optimize

def load(fn):
    d = json.load(open(fn))
    return d

def surv(vals, L, ks):
    """vals: T (or -1 censored at 2^L). returns P(T > 2^k) (T>=2^k means uncovered after 2^k - 1 disks;
    we use 'still uncovered after N=2^k disks' i.e. T > N)."""
    v = np.array([x if x > 0 else np.inf for x in vals], float)
    return np.array([(v > 2.0 ** k).mean() for k in ks])

def fit_loglog(ks, S, n, kmin, kmax):
    m = (ks >= kmin) & (ks <= kmax) & (S > 0)
    x = np.log(ks[m] * math.log(2)); y = np.log(S[m])
    w = np.sqrt(n * S[m] / (1 - S[m] + 1e-12))
    A = np.vstack([x, np.ones_like(x)]).T
    sol, *_ = np.linalg.lstsq(A * w[:, None], y * w, rcond=None)
    return -sol[0], math.exp(sol[1])

def fit_power(ks, S, n, kmin, kmax):
    m = (ks >= kmin) & (ks <= kmax) & (S > 0)
    x = ks[m] * math.log(2); y = np.log(S[m])
    w = np.sqrt(n * S[m] / (1 - S[m] + 1e-12))
    A = np.vstack([x, np.ones_like(x)]).T
    sol, *_ = np.linalg.lstsq(A * w[:, None], y * w, rcond=None)
    return -sol[0], math.exp(sol[1])

def main(fn, out=None):
    d = load(fn); R = d['R']; L = d['Nmax_log2']; runs = d['runs']; n = len(runs)
    lines = []
    P = lines.append
    P(f"### R = {R}: {n} runs, N_max = 2^{L} = {2.0**L:.3g}\n")
    T = [r['T'] for r in runs]; Trim = [r['Trim'] for r in runs]
    fail = [r['fail_at'] for r in runs]
    cens = sum(1 for t, f in zip(T, fail) if t < 0 and f < 0)
    nf = sum(1 for f in fail if f > 0)
    P(f"covered by 2^{L}: {sum(1 for t in T if t>0)}  censored: {cens}  certified permanent failure: {nf}  "
      f"ambiguous-leaf events total: {sum(r['amb'] for r in runs)}\n")
    ks = np.arange(0, L + 1)
    if R <= 1.0:
        S = surv(T, L, ks); Sr = surv(Trim, L, ks)
    else:
        # R>1: "still uncovered" includes certified failures
        S = surv([t if t > 0 else -1 for t in T], L, ks); Sr = None
        Fk = np.array([np.mean([(f > 0 and f <= 2 ** k) for f in fail]) for k in ks])
    # quantiles
    v = np.sort(np.array([x if x > 0 else np.inf for x in T], float))
    qs = [0.1, 0.25, 0.5, 0.75, 0.9]
    qtxt = []
    for q in qs:
        x = v[int(q * (n - 1))]
        qtxt.append(f"q{int(q*100)}: " + (f"{x:.3g}" if np.isfinite(x) else f">2^{L}"))
    P("Quantiles of T: " + ", ".join(qtxt) + "\n")
    if R <= 1.0:
        vr = np.sort(np.array([x if x > 0 else np.inf for x in Trim], float))
        P("Quantiles of T_rim (circle |x|=R covered): " + ", ".join(
            f"q{int(q*100)}: " + (f"{vr[int(q*(n-1))]:.3g}" if np.isfinite(vr[int(q*(n-1))]) else f">2^{L}") for q in qs) + "\n")
    # holes
    H = np.array([r['holes'] for r in runs], float)  # n x (L+1); index k = after 2^k - 1 disks
    hist = np.array(d['hist'], float)
    P("| k | N=2^k | P(T>N) | P(T_rim>N) | E[#holes] | E[#holes \\| alive] | E[rim holes] | E[holes, depth bins 1-4/5-8/9-12/13+] |")
    P("|---|---|---|---|---|---|---|---|")
    for k in list(range(2, L, 2)):
        al = H[:, k] > 0
        hk = hist[k] / n
        P(f"| {k} | {2.0**k:.3g} | {S[k]:.3f} | {Sr[k] if Sr is not None else float('nan'):.3f} | {H[:,k].mean():.2f} | "
          f"{H[al,k].mean() if al.any() else 0:.1f} | {hk[0]:.2f} | {hk[1:5].sum():.2f}/{hk[5:9].sum():.2f}/{hk[9:13].sum():.2f}/{hk[13:].sum():.2f} |")
    P("")
    if R > 1.0:
        P("Certified-failure fraction by N: " + ", ".join(f"2^{k}: {Fk[k]:.3f}" for k in range(4, L + 1, 4)) + "\n")
    # fits
    res = {}
    for (a, b) in [(6, L), (10, L), (20, L)]:
        if R <= 1.0:
            al, c = fit_loglog(ks, S, n, a, b); pw, cp = fit_power(ks, S, n, a, b)
            res[(a, b)] = (al, c, pw, cp)
            P(f"fit k in [{a},{b}]: P(T>N) ~ {c:.3g} (log N)^-{al:.3f}   |  power-law alt: {cp:.3g} N^-{pw:.4f}")
            alr, cr = fit_loglog(ks, Sr, n, a, b)
            P(f"      rim: P(T_rim>N) ~ {cr:.3g} (log N)^-{alr:.3f}")
    P("")
    # goodness of the two laws on [10,L]: residuals
    if R <= 1.0:
        m = (ks >= 10) & (ks <= L)
        for name, f in [("loglog", fit_loglog), ("power", fit_power)]:
            a_, c_ = f(ks, S, n, 10, L)
            pred = c_ * ((ks * math.log(2)) ** (-a_) if name == "loglog" else np.exp(-a_ * ks * math.log(2)))
            chi = (((S - pred) ** 2) / (pred * (1 - pred) / n))[m].sum()
            P(f"chi2-like misfit ({name}, k=10..{L}): {chi:.1f} over {m.sum()} (correlated) points")
        # 1/log N law with free c
        P("Ratios S(N)*log N (constant if c/log N) at k=8,16,24,32,40,48: " +
          ", ".join(f"{S[k]*k*math.log(2):.2f}" for k in [8, 16, 24, 32, 40, 48] if k <= L))
        P("Ratios S(N)*sqrt(log N) at same k: " +
          ", ".join(f"{S[k]*math.sqrt(k*math.log(2)):.3f}" for k in [8, 16, 24, 32, 40, 48] if k <= L))
        P("")
    # last hole
    lastd = []; onrim = 0; ncov = 0; rel = []
    for r in runs:
        if r['T'] > 0 and r['last'] is not None:
            ncov += 1
            x, y = r['last']; dd = max(R - math.hypot(x, y), 0.0)
            rT = 1 / math.sqrt(r['T'])
            lastd.append(dd)
            if r['Trim'] == r['T']:
                onrim += 1
            rel.append(dd / rT)
    lastd = np.array(lastd); rel = np.array(rel)
    if ncov:
        P(f"Last-hole location ({ncov} covered runs): fraction with T = T_rim (last uncovered point ON the circle |x|=R): "
          f"{onrim/ncov:.3f}")
        P(f"  fraction of last holes with depth R-|x| < r_T: {(rel<1).mean():.3f};  < 4 r_T: {(rel<4).mean():.3f};  < 0.05: {(lastd<0.05).mean():.3f};"
          f" < 0.2: {(lastd<0.2).mean():.3f}  (area shares of depth<0.05, <0.2: {1-((R-0.05)/R)**2:.3f}, {1-((R-0.2)/R)**2:.3f})")
        P(f"  median depth {np.median(lastd):.3g}; median depth/r_T {np.median(rel):.3g}")
        # by T range
        Tc = np.array([r['T'] for r in runs if r['T'] > 0], float)
        Trc = np.array([r['Trim'] for r in runs if r['T'] > 0], float)
        P("  | T range | runs | frac T=T_rim | median depth | median log2(depth/r_T) (non-rim) |")
        P("  |---|---|---|---|---|")
        edges = [0, 2**10, 2**20, 2**30, 2**40, 2**60]
        for a, b in zip(edges[:-1], edges[1:]):
            m = (Tc > a) & (Tc <= b)
            if m.sum() == 0:
                continue
            nr = m & (Trc < Tc)
            P(f"  | ({a:.3g}, {b:.3g}] | {m.sum()} | {(Trc[m]==Tc[m]).mean():.3f} | {np.median(lastd[m]):.3g} | "
              f"{np.median(np.log2(np.maximum(rel[nr],1e-9))) if nr.any() else float('nan'):.2f} |")
        P("")
    txt = "\n".join(lines)
    print(txt)
    if out:
        open(out, 'w').write(txt)
    return S, Sr


def mechanism(fn):
    d = load(fn); R = d['R']; runs = d['runs']
    rows = []
    for r in runs:
        if r['T'] > 0 and r['Trim'] > 0 and r['Trim'] < r['T'] and r['last'] is not None:
            x, y = r['last']; dd = max(R - math.hypot(x, y), 1e-300)
            rows.append((math.log2(r['T']), math.log2(r['Trim']), math.log2(1 / dd ** 2)))
    a = np.array(rows)
    if len(a) < 5:
        return
    print(f"Mechanism check ({len(a)} covered runs with T_rim < T):")
    print(f"  birth generation of last hole g_b := log2(depth^-2); rim death gen g_r := log2 T_rim; g_T := log2 T")
    print(f"  fraction with g_b <= g_r + 2 (last hole 'born' before the rim was covered): {(a[:,2] <= a[:,1] + 2).mean():.3f}")
    print(f"  fraction with g_b <= g_T/2: {(a[:,2] <= a[:,0]/2).mean():.3f}")
    print(f"  Spearman(g_r, g_T) = {stats.spearmanr(a[:,1], a[:,0])[0]:.3f};  Spearman(g_b, g_r) = {stats.spearmanr(a[:,2], a[:,1])[0]:.3f}")
    for lo, hi in [(0, 20), (20, 30), (30, 40), (40, 60)]:
        m = (a[:, 0] > lo) & (a[:, 0] <= hi)
        if m.sum():
            print(f"  g_T in ({lo},{hi}]: n={m.sum()}, median g_r={np.median(a[m,1]):.1f}, median g_b={np.median(a[m,2]):.1f}, "
                  f"median sqrt(g_T)={np.median(np.sqrt(a[m,0])):.1f}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None); mechanism(sys.argv[1])
