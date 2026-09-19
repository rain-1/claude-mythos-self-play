"""affine.py — two-piece affine dissections of convex polygons (MO 515243).

Question (MO 515243): can every convex polygon be cut into TWO mutually affine-congruent pieces if the
pieces may be non-convex?  Dimension count (notes_same.md): a polygonal cut from boundary point p to
boundary point q with m breakpoints, pieces P1, P2 = φ(P1) with φ affine.  Vertex types (convex/reflex)
are affine invariants, so #reflex(P1) = #reflex(P2) forces m even and the polygon's corners split
evenly between the two boundary arcs; for an n-gon that leaves (unknowns − equations) = 4 − n.
So for n ≥ 5 a GENERIC convex n-gon has no two-piece affine dissection, and the symmetric ones
(mirror, central, or affine images of those) are exactly the cheap exceptions.

This script SEARCHES numerically: for a polygon Q, all combinatorial placements of p, q (corners or
edges) and m ∈ {0..4} breakpoints, all cyclic vertex correspondences, least-squares affine fit,
Nelder–Mead over the cut parameters with random restarts.  Residual 0 = a dissection.
"""
import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Polygon, LineString, Point


def poly_perimeter_point(Q, s):
    """point at boundary arclength fraction s in [0,1) (CCW from vertex 0)"""
    n = len(Q)
    L = [np.linalg.norm(Q[(i + 1) % n] - Q[i]) for i in range(n)]
    tot = sum(L); d = (s % 1.0) * tot
    for i in range(n):
        if d <= L[i] or i == n - 1:
            return Q[i] + (Q[(i + 1) % n] - Q[i]) * (d / L[i]), i, d / L[i]
        d -= L[i]


def cyclic_corners(n, i_from, i_to):
    """corner indices strictly after edge i_from ... up to edge i_to going CCW (edge i is q_i -> q_{i+1})"""
    out = []; j = (i_from + 1) % n
    while j != (i_to + 1) % n:
        out.append(j); j = (j + 1) % n
        if len(out) > n: break
    return out


def pieces(Q, p, ep, q, eq, bps, p_is_corner, q_is_corner):
    """vertex lists of the two pieces. p on edge ep (or at corner ep if p_is_corner: p = Q[ep]),
    q on edge eq (or corner Q[eq]). bps: (m,2) breakpoints from p to q."""
    n = len(Q)
    # corners strictly between p and q CCW
    if p_is_corner:
        start_edge = ep          # corners after Q[ep]: ep+1, ...
    else:
        start_edge = ep
    if q_is_corner:
        end_corner_excl = eq     # corners up to eq-1
        arc1 = []
        j = (start_edge + 1) % n
        while j != eq:
            arc1.append(j); j = (j + 1) % n
            if len(arc1) > n: break
    else:
        arc1 = cyclic_corners(n, start_edge, eq)
    if p_is_corner and arc1 and arc1[0] == ep:
        arc1 = arc1[1:]
    # arc2: corners strictly between q and p CCW
    if q_is_corner:
        s2 = eq
    else:
        s2 = eq
    if p_is_corner:
        arc2 = []
        j = (s2 + 1) % n
        while j != ep:
            arc2.append(j); j = (j + 1) % n
            if len(arc2) > n: break
    else:
        arc2 = cyclic_corners(n, s2, ep)
    if q_is_corner and arc2 and arc2[0] == eq:
        arc2 = arc2[1:]
    P1 = [p] + [Q[j] for j in arc1] + [q] + [b for b in bps[::-1]]
    P2 = [q] + [Q[j] for j in arc2] + [p] + [b for b in bps]
    return np.array(P1), np.array(P2), arc1, arc2


def affine_fit(X, Y):
    """least-squares affine map X -> Y; returns (residual sum of squares, A, b)"""
    N = len(X)
    M = np.hstack([X, np.ones((N, 1))])
    sol, res, rk, _ = np.linalg.lstsq(M, Y, rcond=None)
    pred = M @ sol
    return float(((pred - Y) ** 2).sum()), sol[:2].T, sol[2]


def best_correspondence(P1, P2):
    N = len(P1)
    if len(P2) != N:
        return np.inf, None
    best = (np.inf, None)
    for rev in (False, True):
        P2r = P2[::-1] if rev else P2
        for r in range(N):
            Y = np.roll(P2r, -r, axis=0)
            res, A, b = affine_fit(P1, Y)
            if res < best[0]:
                best = (res, (rev, r, A, b))
    return best


def simple_and_inside(Q, p, q, bps):
    poly = Polygon(Q)
    cut = LineString([p] + list(bps) + [q])
    if not cut.is_simple:
        return False
    if len(bps) and not all(poly.contains(Point(b)) for b in bps):
        return False
    # the open cut must stay inside: sample
    pts = np.array(cut.interpolate(f, normalized=True).coords[0] for f in np.linspace(0.02, 0.98, 25)) if False else None
    for f in np.linspace(0.03, 0.97, 33):
        c = cut.interpolate(f, normalized=True)
        if not poly.contains(c):
            return False
    return True


def search(Q, m_list=(0, 1, 2, 3, 4), restarts=24, seed=0, verbose=False):
    """returns list of dicts: (config, m, residual normalised by diameter², cut)"""
    Q = np.asarray(Q, float); n = len(Q)
    diam = max(np.linalg.norm(a - b) for a in Q for b in Q)
    rng = np.random.default_rng(seed)
    cen = Q.mean(0)
    results = []
    # placements: p at corner i or on edge i; q likewise; require distinct locations
    placements = []
    for pc in (True, False):
        for qc in (True, False):
            for i in range(n):
                for j in range(n):
                    if pc and qc and (i == j or (i + 1) % n == j or (j + 1) % n == i):
                        continue  # adjacent corners: a cut along an edge
                    if (not pc) and (not qc) and i == j:
                        continue
                    if pc and (not qc) and (j == i or (j + 1) % n == i):
                        continue  # p is an endpoint of edge j
                    if (not pc) and qc and (i == j or (i + 1) % n == j):
                        continue
                    if pc and qc and i > j:
                        continue  # symmetric
                    placements.append((pc, i, qc, j))
    # inward edge normals for the fast inside test
    E = np.roll(Q, -1, axis=0) - Q
    edge_n = np.stack([-E[:, 1], E[:, 0]], 1); edge_n /= np.linalg.norm(edge_n, axis=1, keepdims=True)
    edge_c = ((Q - Q[0]) * edge_n).sum(1)
    for (pc, i, qc, j) in placements:
        for m in m_list:
            nfree = (0 if pc else 1) + (0 if qc else 1) + 2 * m

            def unpack(x):
                k = 0
                if pc:
                    p = Q[i]
                else:
                    p = Q[i] + (Q[(i + 1) % n] - Q[i]) * (0.5 + 0.5 * np.tanh(x[k])); k += 1
                if qc:
                    q = Q[j]
                else:
                    q = Q[j] + (Q[(j + 1) % n] - Q[j]) * (0.5 + 0.5 * np.tanh(x[k])); k += 1
                bps = []
                for _ in range(m):
                    bps.append(cen + 0.45 * diam * np.tanh(x[k:k + 2]) * 0.8); k += 2
                return p, q, np.array(bps).reshape(m, 2)

            def objective(x):
                p, q, bps = unpack(x)
                P1, P2, a1, a2 = pieces(Q, p, i, q, j, bps, pc, qc)
                if len(P1) != len(P2):
                    return 1e3
                res, _ = best_correspondence(P1, P2)
                # keep breakpoints inside the polygon (soft) — the exact check is done at the end
                pen = 0.0
                for b in bps:
                    # signed distances to the edges of the convex polygon (CCW): inside iff all >= 0
                    d = np.min(edge_n @ (b - Q[0]) - edge_c)
                    if d < 0:
                        pen += 10 * (d / diam) ** 2 + 1e-3
                return res / diam ** 2 + pen

            # vertex-count feasibility check with a random x
            x0 = rng.standard_normal(max(nfree, 1)) * 0.5
            p, q, bps = unpack(x0)
            P1, P2, a1, a2 = pieces(Q, p, i, q, j, bps, pc, qc)
            if len(P1) != len(P2):
                continue
            best = (np.inf, None)
            for r in range(restarts if nfree > 0 else 1):
                x0 = rng.standard_normal(max(nfree, 1)) * 0.7
                if nfree == 0:
                    val = objective(x0); xb = x0
                else:
                    o = minimize(objective, x0, method='Nelder-Mead',
                                 options=dict(maxiter=400 * (1 + nfree), xatol=1e-8, fatol=1e-12))
                    val, xb = o.fun, o.x
                if val < best[0]:
                    best = (val, xb)
            p, q, bps = unpack(best[1])
            ok = simple_and_inside(Q, p, q, bps)
            P1, P2, a1, a2 = pieces(Q, p, i, q, j, bps, pc, qc)
            res, corr = best_correspondence(P1, P2)
            results.append(dict(p_corner=pc, i=i, q_corner=qc, j=j, m=m, residual=res / diam ** 2,
                                valid=bool(ok), p=p.tolist(), q=q.tolist(), bps=bps.tolist(),
                                nverts=len(P1), P1=P1.tolist(), P2=P2.tolist(),
                                corr=(None if corr is None else dict(rev=bool(corr[0]), r=int(corr[1]),
                                                                    A=corr[2].tolist(), b=corr[3].tolist()))))
            if verbose:
                print(f'  p{"C" if pc else "E"}{i} q{"C" if qc else "E"}{j} m={m} nv={len(P1)} res={res / diam ** 2:.3e} ok={ok}')
    return results


def regular(n, r=1.0, rot=0.0):
    a = rot + 2 * np.pi * np.arange(n) / n + np.pi / 2
    return np.stack([r * np.cos(a), r * np.sin(a)], 1)


def random_convex(n, rng, tries=5000):
    """random FAT convex n-gon: sorted random directions with random radii; every corner angle ≥ 0.6 rad and
    every edge ≥ 0.35 (rejection), so nothing is nearly degenerate"""
    for _ in range(tries):
        a = np.sort(rng.uniform(0, 2 * np.pi, n))
        r = rng.uniform(0.65, 1.0, n)
        P = np.stack([r * np.cos(a), r * np.sin(a)], 1)
        ok = True
        for i in range(n):
            u = P[(i + 1) % n] - P[i]; v = P[(i + 2) % n] - P[(i + 1) % n]
            cr = u[0] * v[1] - u[1] * v[0]
            ang = np.arctan2(cr, u @ v)
            if ang < 0.6 or np.linalg.norm(u) < 0.35:
                ok = False; break
        if ok:
            return P
    raise RuntimeError


if __name__ == '__main__':
    import json, time, sys
    rng = np.random.default_rng(3)
    cases = {}
    cases['regular_pentagon'] = regular(5)
    S = np.array([[1.3, 0.55], [0.1, 0.7]])
    cases['affine_regular_pentagon'] = regular(5) @ S.T
    cases['random_pentagon'] = random_convex(5, np.random.default_rng(7))
    cases['random_pentagon_2'] = random_convex(5, np.random.default_rng(11))
    cases['random_quadrilateral'] = random_convex(4, rng)
    # a mirror-symmetric pentagon (apex on the axis, two free vertices mirrored), then a random affine map:
    _r = np.random.default_rng(5)
    _v1 = np.array([0.55, 0.35]); _v2 = np.array([0.8, -0.6])
    _sym = np.array([[0, 1.0], [-_v1[0], _v1[1]], [-_v2[0], _v2[1]], [_v2[0], _v2[1]], [_v1[0], _v1[1]]])
    _S = np.array([[1.25, 0.6], [-0.35, 0.8]])
    cases['affine_mirror_pentagon'] = _sym @ _S.T
    cases['regular_hexagon'] = regular(6)
    cases['random_hexagon'] = random_convex(6, rng)
    out = {}
    t0 = time.time()
    which = sys.argv[1:] or list(cases)
    for name in which:
        Q = cases[name]
        print('==', name, np.round(Q, 3).tolist())
        res = search(Q, m_list=(0, 2, 4), restarts=(8 if 'random' in name else 5), seed=1, verbose=False)
        res.sort(key=lambda d: d['residual'])
        best_by_m = {}
        for d in res:
            if d['valid'] and (d['m'] not in best_by_m or d['residual'] < best_by_m[d['m']]['residual']):
                best_by_m[d['m']] = d
        for m in sorted(best_by_m):
            d = best_by_m[m]
            print(f'   m={m}: best residual {d["residual"]:.3e}  (p{"C" if d["p_corner"] else "E"}{d["i"]}, q{"C" if d["q_corner"] else "E"}{d["j"]}, {d["nverts"]}-gons)')
        out[name] = dict(Q=Q.tolist(), best_by_m={str(m): d for m, d in best_by_m.items()},
                         all_valid_min=min([d['residual'] for d in res if d['valid']] + [np.inf]))
        print('   elapsed', round(time.time() - t0, 1))
        json.dump({name: out[name]}, open(f'cache/affine_{name}.json', 'w'), indent=1)
