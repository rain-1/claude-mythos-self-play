"""Shabat polynomials for all bicolored plane trees with n edges (n <= 6/7).

For passport (lambda, mu):  P = g*prod(z-a_i)^lam_i,  P-1 = g*prod(z-b_j)^mu_j
<=>  A_lam(z) - B_mu(z) = c0 (nonzero const), g = 1/c0.
Gauge: black centroid sum(lam_i a_i) = 0 (a_1 eliminated); scale left free,
normalized post-hoc.  Solve by least_squares from random inits; dedup by
rotation-invariant fingerprint; classify by tracing P^{-1}([0,1]) into
(sigma0, sigma1) canonical under <c>-conjugation; match census reps.
"""
import numpy as np, json, itertools
from scipy.optimize import least_squares

def poly_from_roots(roots, mults):
    p = np.array([1.0 + 0j])
    for r, m in zip(roots, mults):
        for _ in range(m):
            p = np.convolve(p, np.array([1.0, -r]))
    return p  # highest degree first, monic

def residual(u, lam, mu, n):
    VB, VW = len(lam), len(mu)
    z = u[:2 * (VB - 1 + VW)].astype(np.float64)
    zz = z[0::2] + 1j * z[1::2]
    a_rest = zz[:VB - 1]
    b = zz[VB - 1:]
    a1 = -(np.sum(np.array(lam[1:]) * a_rest)) / lam[0] if VB > 1 else 0.0 + 0j
    a = np.concatenate([[a1], a_rest])
    A = poly_from_roots(a, lam)
    B = poly_from_roots(b, mu)
    R = A - B                      # degree-n arrays, leading cancels (both monic)
    mid = R[1:n]                   # coeffs of z^{n-1}..z^1 must vanish
    return np.concatenate([mid.real, mid.imag])

def unpack(u, lam, mu):
    VB, VW = len(lam), len(mu)
    zz = u[0::2] + 1j * u[1::2]
    a_rest = zz[:VB - 1]; b = zz[VB - 1:]
    a1 = -(np.sum(np.array(lam[1:]) * a_rest)) / lam[0] if VB > 1 else 0.0 + 0j
    return np.concatenate([[a1], a_rest]), b

def normalize(a, b, lam, mu):
    s = np.sqrt(np.sum(np.array(lam) * np.abs(a) ** 2) + np.sum(np.array(mu) * np.abs(b) ** 2))
    if s < 1e-9: return None
    return a / s, b / s

def fingerprint(a, b, lam, mu):
    """rotation+scale-invariant-ish (scale already normalized) id string."""
    pts = list(zip(a, lam, ['B'] * len(a))) + list(zip(b, mu, ['W'] * len(b)))
    ds = []
    for (z1, m1, c1), (z2, m2, c2) in itertools.combinations(pts, 2):
        ds.append(round(abs(z1 - z2), 4))
    mags = sorted(round(abs(z), 4) for z, _, _ in pts)
    return (tuple(sorted(ds)), tuple(mags))

def solve_passport(lam, mu, n, want, rng, max_restarts=4000):
    """Find `want` distinct solutions (up to rotation); returns list of (a,b,c0)."""
    found = {}
    VB, VW = len(lam), len(mu)
    nun = 2 * (VB - 1 + VW)
    tries = 0
    while len(found) < want and tries < max_restarts:
        tries += 1
        u0 = rng.standard_normal(nun) * 0.8
        sol = least_squares(residual, u0, args=(lam, mu, n), method='trf',
                            xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=2000)
        if sol.cost > 1e-18:
            continue
        a, b = unpack(sol.x, lam, mu)
        A = poly_from_roots(a, lam); B = poly_from_roots(b, mu)
        c0 = (A - B)[-1]
        scale = max(np.max(np.abs(a)), np.max(np.abs(b)), 1e-3)
        if abs(c0) < 1e-8 * scale ** n:
            continue                       # degenerate A == B
        nrm = normalize(a, b, lam, mu)
        if nrm is None: continue
        a, b = nrm
        A = poly_from_roots(a, lam); B = poly_from_roots(b, mu)
        c0 = (A - B)[-1]
        if abs(c0) < 1e-10: continue
        fp = fingerprint(a, b, lam, mu)
        if fp not in found:
            found[fp] = (a, b, c0, tries)
    return list(found.values()), tries

# ------------------------------------------------------------------ tracing
def trace_dessin(a, lam, b, mu, c0, nsteps=60):
    """Trace P^{-1}([0,1]); returns (sigma0, sigma1, edge_paths, ok)."""
    n = int(sum(lam))
    g = 1.0 / c0
    P = g * poly_from_roots(a, lam)
    dP = np.polyder(P)
    ts = 0.5 * (1 - np.cos(np.linspace(0, np.pi, nsteps)))   # cluster at ends
    eps = 1e-4
    ts = eps + (1 - 2 * eps) * ts
    edges = []          # each: dict(black=i, k=branch, path=[z...])
    for i, (ai, m) in enumerate(zip(a, lam)):
        D = g * np.prod([(ai - aj) ** lj for j, (aj, lj) in enumerate(zip(a, lam)) if j != i]) if len(a) > 1 else g
        r0 = (ts[0] / D) ** (1.0 / m)   # principal
        for k in range(m):
            z = ai + r0 * np.exp(2j * np.pi * k / m)
            path = [z]
            okflag = True
            for t in ts[1:]:
                for _ in range(60):
                    pv = np.polyval(P, z) - t
                    dv = np.polyval(dP, z)
                    if abs(dv) < 1e-14: okflag = False; break
                    dz = pv / dv
                    z = z - dz
                    if abs(dz) < 1e-13: break
                path.append(z)
                if not okflag: break
            edges.append(dict(black=i, k=k, path=np.array(path), ok=okflag))
    # attach whites by capacity-constrained optimal assignment:
    # white j must receive exactly mu_j edges (multiplicity slots)
    from scipy.optimize import linear_sum_assignment
    slots = [j for j, m in enumerate(mu) for _ in range(m)]
    if not all(e['ok'] for e in edges) or len(slots) != len(edges):
        return None, None, edges, False
    ends = np.array([e['path'][-1] for e in edges])
    cost = np.abs(ends[:, None] - np.array(b)[None, [j for j in slots]])
    ri, ci = linear_sum_assignment(cost)
    for e_i, s_i in zip(ri, ci):
        edges[e_i]['white'] = slots[s_i]
    # sanity: assigned distance must be within 12x of the multiplicity-aware
    # expected convergence radius ((1-t)/|D_j|)^(1/mu_j)
    for e in edges:
        j = e['white']; m = mu[j]
        Dj = g * np.prod([(b[j] - bj) ** mj for jj, (bj, mj) in
                          enumerate(zip(b, mu)) if jj != j]) if len(b) > 1 else g
        expect = (eps / max(abs(Dj), 1e-12)) ** (1.0 / m)
        if abs(b[j] - e['path'][-1]) > 12 * expect + 1e-6:
            e['ok'] = False
    if not all(e['ok'] for e in edges):
        return None, None, edges, False
    E = len(edges)
    # cyclic orders (counterclockwise)
    sigma0 = [None] * E
    for i in range(len(a)):
        es = [ei for ei, e in enumerate(edges) if e['black'] == i]
        angs = [np.angle(edges[ei]['path'][1] - a[i]) for ei in es]
        order = [es[t] for t in np.argsort(angs)]
        for idx in range(len(order)):
            sigma0[order[idx]] = order[(idx + 1) % len(order)]
    sigma1 = [None] * E
    for j in range(len(b)):
        es = [ei for ei, e in enumerate(edges) if e['white'] == j]
        angs = [np.angle(edges[ei]['path'][-2] - b[j]) for ei in es]
        order = [es[t] for t in np.argsort(angs)]
        for idx in range(len(order)):
            sigma1[order[idx]] = order[(idx + 1) % len(order)]
    return tuple(sigma0), tuple(sigma1), edges, True

def canonical_pair(s0, s1):
    """Relabel so sigma0*sigma1 = c=(0..n-1), then min over <c>-conjugation."""
    n = len(s0)
    prod = tuple(s0[s1[i]] for i in range(n))
    # prod must be an n-cycle
    seen = set(); j = 0; cyc = []
    for _ in range(n):
        cyc.append(j); seen.add(j); j = prod[j]
    if len(seen) != n:
        return None
    # labeling L: cyc[t] -> t makes prod = c
    L = {e: t for t, e in enumerate(cyc)}
    rs0 = [0] * n; rs1 = [0] * n
    for e in range(n):
        rs0[L[e]] = L[s0[e]]
        rs1[L[e]] = L[s1[e]]
    def conj(p, k):
        return tuple(((p[(i - k) % n]) + k) % n for i in range(n))
    return min((conj(tuple(rs0), k), conj(tuple(rs1), k)) for k in range(n))

if __name__ == '__main__':
    import sys, time
    census = json.load(open('trees_census.json'))
    NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    rng = np.random.default_rng(20260901)
    out = {}
    t00 = time.time()
    for n in range(1, NMAX + 1):
        reps = census[str(n)]
        # group census classes by passport
        bypass = {}
        for ridx, r in enumerate(reps):
            key = (tuple(r['passport'][0]), tuple(r['passport'][1]))
            bypass.setdefault(key, []).append(ridx)
        out[n] = []
        for (lam, mu), ridxs in sorted(bypass.items()):
            want = len(ridxs)
            census_keys = set()
            for ridx in ridxs:
                r = reps[ridx]
                can = canonical_pair(tuple(r['sigma0']), tuple(r['sigma1']))
                census_keys.add(str(can))
            classes = {}
            VB, VW = len(lam), len(mu)
            nun = 2 * (VB - 1 + VW)
            tries = 0; extra = set()
            while len([k for k in classes if k in census_keys]) < want and tries < 6000:
                tries += 1
                u0 = rng.standard_normal(nun) * (0.5 + 0.6 * rng.random())
                sol = least_squares(residual, u0, args=(list(lam), list(mu), n),
                                    method='trf', xtol=1e-15, ftol=1e-15,
                                    gtol=1e-15, max_nfev=2000)
                if sol.cost > 1e-18: continue
                a, b = unpack(sol.x, list(lam), list(mu))
                A = poly_from_roots(a, lam); B = poly_from_roots(b, mu)
                c0 = (A - B)[-1]
                scale = max(np.max(np.abs(a)), np.max(np.abs(b)), 1e-3)
                if abs(c0) < 1e-8 * scale ** n: continue
                nrm = normalize(a, b, lam, mu)
                if nrm is None: continue
                a, b = nrm
                A = poly_from_roots(a, lam); B = poly_from_roots(b, mu)
                c0 = (A - B)[-1]
                if abs(c0) < 1e-10: continue
                s0, s1, edges, ok = trace_dessin(a, list(lam), b, list(mu), c0)
                if not ok: continue
                key = str(canonical_pair(s0, s1))
                if key not in census_keys:
                    extra.add(key); continue
                if key not in classes:
                    classes[key] = (a, b, c0, edges)
            got = set(classes)
            status = 'OK' if got == census_keys else \
                     f'MISMATCH got {len(got)}/{want} extra={len(extra)}'
            print(f"n={n} {lam}|{mu}: want {want} "
                  f"({tries} tries) -> {status}", flush=True)
            for key, items in classes.items():
                a, b, c0, edges = items
                out[n].append(dict(
                    lam=list(lam), mu=list(mu), cls=key,
                    a=[[float(z.real), float(z.imag)] for z in a],
                    b=[[float(z.real), float(z.imag)] for z in b],
                    c0=[float(c0.real), float(c0.imag)],
                    paths=[[[float(z.real), float(z.imag)] for z in e['path']]
                           for e in edges],
                    blacks=[e['black'] for e in edges],
                    whites=[e['white'] for e in edges]))
        print(f"  n={n} total solved: {len(out[n])} / {len(reps)}  "
              f"[{time.time()-t00:.0f}s]", flush=True)
    json.dump(out, open(f'shabat_solutions_{NMAX}.json', 'w'))
