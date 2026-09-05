"""cpack.py — circle packings as discrete conformal maps (Thurston / Rodin–Sullivan).

1. Region  Omega = f(D),  f(z) = z + a2 z^2 + a3 z^3 + a4 z^4 + a5 z^5  (sum k|a_k| < 1 => univalent).
2. Regular hexagonal circle packing of Omega with spacing h (radius h/2).
3. The SAME tangency graph repacked in the unit disc as the maximal packing (boundary circles are
   horocycles) — Collins–Stephenson iteration in hyperbolic radii, Newton per vertex.
4. Layout in the Poincaré disc, normalised so the circle at the source origin sits at 0 and its
   +x neighbour lies on the positive real axis.
5. Certificate: the packing's centres against the exact inverse map f^{-1} (Newton, 1e-14);
   tangency residuals; angle sums; horocycle consistency.
"""
import numpy as np, json, time, sys
from matplotlib.path import Path


class Flower:
    def __init__(self, coef=(0.15, 0.06, 0.05j, 0.08)):
        self.a = np.array([0, 1] + list(coef), complex)   # f(z) = sum a_k z^k

    def f(self, z):
        z = np.asarray(z, complex)
        return sum(self.a[k] * z ** k for k in range(len(self.a)))

    def fp(self, z):
        z = np.asarray(z, complex)
        return sum(k * self.a[k] * z ** (k - 1) for k in range(1, len(self.a)))

    def boundary(self, n=4000):
        th = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return self.f(np.exp(1j * th))

    def inside(self, w):
        bd = self.boundary()
        p = Path(np.c_[bd.real, bd.imag])
        w = np.asarray(w, complex)
        return p.contains_points(np.c_[w.real, w.imag])

    def inverse(self, w, iters=60):
        """f^{-1}(w) for w in Omega, by Newton from several starts; returns z with |z|<1."""
        w = np.asarray(w, complex)
        best = np.full(w.shape, np.nan + 0j)
        bestres = np.full(w.shape, np.inf)
        for scale in (1.0, 0.7, 0.85, 0.5, 0.95):
            z = w * scale
            for _ in range(iters):
                z = z - (self.f(z) - w) / self.fp(z)
                z = np.where(np.abs(z) > 1.5, z / np.abs(z) * 0.9, z)
            res = np.abs(self.f(z) - w)
            ok = (res < 1e-11) & (np.abs(z) < 1.0)
            take = ok & (res < bestres)
            best[take] = z[take]; bestres[take] = res[take]
        return best


def hex_mesh(flower, h):
    """hex lattice points inside Omega; faces = lattice triangles with all vertices inside."""
    R = 1.6
    n = int(R / h) + 3
    I, J = np.meshgrid(np.arange(-n, n + 1), np.arange(-2 * n, 2 * n + 1), indexing='ij')
    I = I.ravel(); J = J.ravel()
    w = h * (I + J / 2) + 1j * h * (np.sqrt(3) / 2) * J
    keep = flower.inside(w) & (np.abs(w) < R)
    idx = -np.ones(len(w), int)
    idx[keep] = np.arange(keep.sum())
    key = {(int(i), int(j)): int(k) for i, j, k in zip(I[keep], J[keep], idx[keep])}
    W = w[keep]
    faces = []
    # lattice triangles: (i,j),(i+1,j),(i,j+1)  [up]  and (i+1,j),(i+1,j+1),(i,j+1) [down]
    for (i, j), k in key.items():
        a = key.get((i + 1, j)); b = key.get((i, j + 1)); c = key.get((i + 1, j + 1))
        if a is not None and b is not None:
            faces.append((k, a, b))
        if a is not None and b is not None and c is not None:
            faces.append((a, c, b))
    faces = np.array(faces, int)
    # orientation: make CCW in the source plane
    P = W[faces]
    cross = ((P[:, 1] - P[:, 0]).conj() * (P[:, 2] - P[:, 0])).imag
    faces[cross < 0] = faces[cross < 0][:, [0, 2, 1]]
    # prune to a clean disc: keep the largest face-connected component, drop vertices with < 1 face,
    # and repeatedly drop boundary vertices whose link is not a single path.
    for _ in range(20):
        V = len(W)
        deg_f = np.bincount(faces.ravel(), minlength=V)
        edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
        es = np.sort(edges, axis=1)
        eu, ecount = np.unique(es, axis=0, return_counts=True)
        deg_e = np.bincount(eu.ravel(), minlength=V)
        # for a boundary vertex with a single-path link: faces = edges-1; interior: faces = edges
        bad = (deg_f == 0) | ((deg_f != deg_e) & (deg_f != deg_e - 1))
        # boundary vertices with no interior neighbour cannot be laid out (ears): drop them
        bdv = deg_f == deg_e - 1
        interior_v = deg_f == deg_e
        has_int_nb = np.zeros(V, bool)
        has_int_nb[eu[interior_v[eu[:, 1]], 0]] = True
        has_int_nb[eu[interior_v[eu[:, 0]], 1]] = True
        bad |= bdv & ~has_int_nb
        if not bad.any():
            break
        keepv = ~bad
        remap = -np.ones(V, int); remap[keepv] = np.arange(keepv.sum())
        fk = keepv[faces].all(axis=1)
        faces = remap[faces[fk]]
        W = W[keepv]
    V = len(W)
    # largest face-connected component
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    A = sp.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(V, V))
    ncomp, lab = connected_components(A, directed=False)
    if ncomp > 1:
        big = np.argmax(np.bincount(lab))
        keepv = lab == big
        remap = -np.ones(V, int); remap[keepv] = np.arange(keepv.sum())
        faces = remap[faces[keepv[faces].all(axis=1)]]
        W = W[keepv]
        V = len(W)
    deg_f = np.bincount(faces.ravel(), minlength=V)
    es = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    eu, ecount = np.unique(es, axis=0, return_counts=True)
    bd_edges = eu[ecount == 1]
    boundary = np.zeros(V, bool); boundary[bd_edges.ravel()] = True
    E = len(eu)
    euler = V - E + len(faces)
    return dict(W=W, faces=faces, boundary=boundary, edges=eu, euler=euler, h=h)


# ---------------------------------------------------------------- hyperbolic angles
def angles(rv, ru, rw, inf_u, inf_w):
    """angle at v in the hyperbolic triangle of mutually tangent circles (radii rv,ru,rw);
    inf_u/inf_w flag horocycles (infinite radius). Vectorised."""
    out = np.empty_like(rv)
    both = inf_u & inf_w
    onlyu = inf_u & ~inf_w
    onlyw = inf_w & ~inf_u
    fin = ~inf_u & ~inf_w
    # finite
    a = rv[fin] + ru[fin]; b = rv[fin] + rw[fin]; c = ru[fin] + rw[fin]
    ca = (np.cosh(a) * np.cosh(b) - np.cosh(c)) / (np.sinh(a) * np.sinh(b))
    out[fin] = np.arccos(np.clip(ca, -1, 1))
    # u horocycle
    b = rv[onlyu] + rw[onlyu]
    ca = (np.cosh(b) - np.exp(rw[onlyu] - rv[onlyu])) / np.sinh(b)
    out[onlyu] = np.arccos(np.clip(ca, -1, 1))
    b = rv[onlyw] + ru[onlyw]
    ca = (np.cosh(b) - np.exp(ru[onlyw] - rv[onlyw])) / np.sinh(b)
    out[onlyw] = np.arccos(np.clip(ca, -1, 1))
    out[both] = np.arccos(np.clip(1 - 2 * np.exp(-2 * rv[both]), -1, 1))
    return out


def pack(mesh, tol=1e-12, maxit=20000, verbose=True):
    """Collins–Stephenson in hyperbolic radii; boundary vertices are horocycles."""
    faces, bd = mesh['faces'], mesh['boundary']
    V = len(bd)
    # corner list: for each face and each corner, (v, u, w)
    corners = np.concatenate([faces[:, [0, 1, 2]], faces[:, [1, 2, 0]], faces[:, [2, 0, 1]]])
    cv, cu, cw = corners[:, 0], corners[:, 1], corners[:, 2]
    interior = ~bd
    nint = interior.sum()
    r = np.full(V, 0.5)
    r[bd] = np.inf
    infu, infw = bd[cu], bd[cw]
    keep = interior[cv]
    cv, cu, cw, infu, infw = cv[keep], cu[keep], cw[keep], infu[keep], infw[keep]
    target = 2 * np.pi
    t0 = time.time()
    for it in range(maxit):
        rr = r.copy(); rr[bd] = 1.0  # placeholder for arrays (masked by flags)
        th = np.bincount(cv, angles(rr[cv], rr[cu], rr[cw], infu, infw), minlength=V)
        err = np.abs(th[interior] - target).max()
        if verbose and (it % 200 == 0 or err < tol):
            print(f'   it {it:5d}  max|theta-2pi| = {err:.2e}  r in [{r[interior].min():.3g},{r[interior].max():.3g}]  {time.time()-t0:.0f}s', flush=True)
        if err < tol:
            break
        # Newton per vertex in log r (theta is decreasing in r_v)
        eps = 1e-6
        rr2 = rr.copy(); rr2[interior] *= (1 + eps)
        th2 = np.bincount(cv, angles(rr2[cv], rr[cu], rr[cw], infu, infw), minlength=V)
        dth = (th2 - th) / eps                      # d theta / d log r
        step = np.zeros(V)
        step[interior] = -(th[interior] - target) / np.minimum(dth[interior], -1e-9)
        step = np.clip(step, -0.7, 0.7)
        r[interior] = r[interior] * np.exp(0.9 * step[interior])
        r[interior] = np.clip(r[interior], 1e-6, 30.0)
    return r, th, it


# ---------------------------------------------------------------- Poincaré layout
def mob(z, c):        # isometry sending c -> 0
    return (z - c) / (1 - np.conj(c) * z)


def mob_inv(zeta, c):
    return (zeta + c) / (1 + np.conj(c) * zeta)


def layout(mesh, r, v0, v1):
    faces, bd, W = mesh['faces'], mesh['boundary'], mesh['W']
    V = len(bd)
    z = np.full(V, np.nan + 0j)
    placed = np.zeros(V, bool)
    z[v0] = 0.0; placed[v0] = True
    d = r[v0] + r[v1]
    z[v1] = np.tanh(d / 2) if not bd[v1] else 1.0 + 0j
    placed[v1] = True
    # face adjacency by shared edge: BFS over faces
    from collections import deque, defaultdict
    vf = defaultdict(list)
    for fi, f in enumerate(faces):
        for v in f:
            vf[v].append(fi)
    q = deque(vf[v0] + vf[v1])
    seen = set()
    rr = r.copy(); rr[bd] = 1.0
    it = 0
    while q:
        fi = q.popleft()
        if fi in seen:
            continue
        f = faces[fi]
        pl = placed[f]
        if pl.sum() < 2:
            continue
        seen.add(fi)
        if pl.sum() == 3:
            for v in f:
                q.extend(vf[v])
            continue
        # exactly two placed: choose pivot = a placed INTERIOR vertex
        k = int(np.where(~pl)[0][0])
        w = f[k]; v = f[(k + 1) % 3]; u = f[(k + 2) % 3]   # face order (v,u,w) is a cyclic rotation? keep orientation
        # faces are CCW as (f0,f1,f2); the corner order around v: next vertex after v is u (CCW)
        # we need the angle at pivot between the other placed vertex and the target.
        # candidates for pivot: v or u (whichever is interior)
        if bd[v] and bd[u]:
            seen.discard(fi)
            continue
        if bd[v]:
            v, u = u, v
        # orientation: in CCW face (p, q, s), going around p the direction from q to s is CCW.
        # find positions: idx of v in f
        iv = int(np.where(f == v)[0][0])
        nxt = f[(iv + 1) % 3]     # CCW-next after v
        # if u is CCW-next after v then w is at +alpha from u; else w is at -alpha from u
        sign = +1.0 if nxt == u else -1.0
        alpha = float(angles(np.array([rr[v]]), np.array([rr[u]]), np.array([rr[w]]),
                             np.array([bd[u]]), np.array([bd[w]]))[0])
        zu = mob(z[u], z[v])
        psi = np.angle(zu)
        ang = psi + sign * alpha
        if bd[w]:
            zeta = np.exp(1j * ang)
        else:
            zeta = np.tanh((rr[v] + rr[w]) / 2) * np.exp(1j * ang)
        z[w] = mob_inv(zeta, z[v])
        if bd[w]:
            z[w] = z[w] / abs(z[w])
        placed[w] = True
        q.extend(vf[w])
        it += 1
    # fallback sweeps for anything the BFS missed
    for _ in range(50):
        todo = np.where(~placed)[0]
        if len(todo) == 0:
            break
        prog = False
        for w in todo:
            for fi in vf[w]:
                f = faces[fi]
                others = [x for x in f if x != w]
                v, u = others
                if not (placed[v] and placed[u]):
                    continue
                if bd[v] and bd[u]:
                    continue
                if bd[v]:
                    v, u = u, v
                iv = int(np.where(f == v)[0][0]); nxt = f[(iv + 1) % 3]
                sign = +1.0 if nxt == u else -1.0
                alpha = float(angles(np.array([rr[v]]), np.array([rr[u]]), np.array([rr[w]]),
                                     np.array([bd[u]]), np.array([bd[w]]))[0])
                ang = np.angle(mob(z[u], z[v])) + sign * alpha
                zeta = np.exp(1j * ang) if bd[w] else np.tanh((rr[v] + rr[w]) / 2) * np.exp(1j * ang)
                z[w] = mob_inv(zeta, z[v])
                if bd[w]:
                    z[w] /= abs(z[w])
                placed[w] = True; prog = True
                break
        if not prog:
            break
    return z, placed


def euclid_circles(mesh, r, z):
    """Euclidean centre/radius of each hyperbolic circle in the Poincaré disc; horocycles sized by
    tangency to an interior neighbour (all neighbours checked)."""
    bd, faces = mesh['boundary'], mesh['faces']
    V = len(bd)
    C = np.zeros(V, complex); R = np.zeros(V)
    fin = ~bd
    rho = np.tanh(r[fin] / 2)
    zv = z[fin]
    dirn = np.where(np.abs(zv) > 1e-14, -zv / np.maximum(np.abs(zv), 1e-300), 1.0)
    p1 = mob_inv(rho * dirn, zv); p2 = mob_inv(-rho * dirn, zv)
    C[fin] = (p1 + p2) / 2; R[fin] = np.abs(p1 - p2) / 2
    # horocycles
    edges = mesh['edges']
    from collections import defaultdict
    nb = defaultdict(list)
    for a, b in edges:
        nb[a].append(b); nb[b].append(a)
    horo_spread = 0.0
    for v in np.where(bd)[0]:
        p = z[v]
        vals = []
        for u in nb[v]:
            if bd[u]:
                continue
            c, Ru = C[u], R[u]
            pc = (p.conj() * c).real
            rho_h = (1 + abs(c) ** 2 - Ru ** 2 - 2 * pc) / (2 * (1 - pc + Ru))
            vals.append(rho_h)
        if vals:
            R[v] = np.mean(vals); C[v] = (1 - R[v]) * p
            horo_spread = max(horo_spread, np.ptp(vals) / max(np.mean(vals), 1e-300))
    return C, R, horo_spread


def certify(mesh, C, R, z, r, th, flower):
    bd, edges, W = mesh['boundary'], mesh['edges'], mesh['W']
    fin = ~bd
    # tangency residuals
    d = np.abs(C[edges[:, 0]] - C[edges[:, 1]])
    s = R[edges[:, 0]] + R[edges[:, 1]]
    tang = np.abs(d - s) / s
    # exact map
    zex = flower.inverse(W)
    err = np.abs(C[fin] - zex[fin])
    # derivative comparison: R_v/(h/2) vs |(f^{-1})'(w)| = 1/|f'(z)|
    deriv = 1 / np.abs(flower.fp(zex[fin]))
    ratio = R[fin] / (mesh['h'] / 2)
    return dict(V=int(len(bd)), interior=int(fin.sum()), boundary=int(bd.sum()), faces=int(len(mesh['faces'])),
                euler=int(mesh['euler']), h=mesh['h'],
                max_angle_err=float(np.abs(th[fin] - 2 * np.pi).max()),
                max_tangency_rel=float(tang.max()), mean_tangency_rel=float(tang.mean()),
                map_err_max=float(err.max()), map_err_mean=float(err.mean()),
                map_err_rms=float(np.sqrt((err ** 2).mean())),
                deriv_ratio_median=float(np.median(ratio / deriv)),
                deriv_rel_err_max=float(np.abs(ratio / deriv - 1).max()),
                deriv_rel_err_mean=float(np.abs(ratio / deriv - 1).mean()),
                nan_inverse=int(np.isnan(zex).sum()))


def build(h, coef=(0.15, 0.06, 0.05j, 0.08), verbose=True):
    fl = Flower(coef)
    t0 = time.time()
    mesh = hex_mesh(fl, h)
    if verbose:
        print(f'mesh h={h}: V={len(mesh["W"])} faces={len(mesh["faces"])} boundary={mesh["boundary"].sum()} euler={mesh["euler"]}  {time.time()-t0:.1f}s', flush=True)
    r, th, it = pack(mesh, verbose=verbose)
    W = mesh['W']
    v0 = int(np.argmin(np.abs(W)))
    # +x neighbour of v0
    edges = mesh['edges']
    nb = np.concatenate([edges[edges[:, 0] == v0][:, 1], edges[edges[:, 1] == v0][:, 0]])
    v1 = int(nb[np.argmax((W[nb] - W[v0]).real)])
    z, placed = layout(mesh, r, v0, v1)
    assert placed.all(), f'unplaced {(~placed).sum()}'
    C, R, hs = euclid_circles(mesh, r, z)
    cert = certify(mesh, C, R, z, r, th, fl)
    cert['horocycle_spread'] = float(hs); cert['iters'] = int(it); cert['coef'] = [str(c) for c in coef]
    if verbose:
        print(json.dumps(cert, indent=1), flush=True)
    return dict(mesh=mesh, r=r, z=z, C=C, R=R, cert=cert, flower=fl, v0=v0, v1=v1)


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.08
    P = build(h)
    np.savez(f'pack_h{h}.npz', W=P['mesh']['W'], faces=P['mesh']['faces'], boundary=P['mesh']['boundary'],
             edges=P['mesh']['edges'], r=P['r'], z=P['z'], C=P['C'], R=P['R'])
    json.dump(P['cert'], open(f'cert_h{h}.json', 'w'), indent=1)
