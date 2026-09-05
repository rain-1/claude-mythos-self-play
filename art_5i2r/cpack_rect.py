"""cpack_rect.py — a hexagonal circle packing of a leaf-shaped region, repacked onto a PAGE:
the same tangency graph packed in the Euclidean plane with boundary angle sums pi (straight sides)
and pi/2 at four chosen corner vertices  =>  a rectangle whose aspect ratio is a conformal invariant
(the modulus of the quadrilateral).  Certificate: an independent exact conformal map
  region --(MFS harmonic solve)--> disc --(Möbius)--> upper half-plane --(elliptic F)--> rectangle
with the same four corners; compare centres and the modulus 2K(k)/K'(k).
"""
import numpy as np, json, time, sys
from matplotlib.path import Path
from collections import deque, defaultdict
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from scipy.special import ellipk


class Leaf:
    """polar region r(theta) = 1 + sum a_m cos(m theta + phi_m); star-shaped from 0."""
    def __init__(self, terms=((3, 0.30, 0.0), (5, 0.14, -0.9), (2, 0.10, 1.2), (7, 0.05, 0.4))):
        self.terms = terms

    def r(self, th):
        return 1 + sum(a * np.cos(m * th + p) for m, a, p in self.terms)

    def boundary(self, n=4000):
        th = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return self.r(th) * np.exp(1j * th)

    def inside(self, w):
        w = np.asarray(w, complex)
        th = np.angle(w)
        return np.abs(w) < self.r(th)


class Offset:
    """the region shrunk by a normal offset delta (the carrier of a hex packing of spacing h has its
    boundary centres ~h/2 inside the true boundary): r~(theta) = r - delta*sqrt(r^2+r'^2)/r."""
    def __init__(self, region, delta):
        self.base, self.delta = region, delta
        self.terms = region.terms

    def r(self, th):
        r0 = self.base.r(th)
        dr = (self.base.r(th + 1e-6) - self.base.r(th - 1e-6)) / 2e-6
        return r0 - self.delta * np.sqrt(r0 * r0 + dr * dr) / r0

    def boundary(self, n=4000):
        th = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return self.r(th) * np.exp(1j * th)

    def inside(self, w):
        w = np.asarray(w, complex)
        return np.abs(w) < self.r(np.angle(w))


def hex_mesh(region, h, R=1.7):
    n = int(R / h) + 3
    I, J = np.meshgrid(np.arange(-n, n + 1), np.arange(-2 * n, 2 * n + 1), indexing='ij')
    I = I.ravel(); J = J.ravel()
    w = h * (I + J / 2) + 1j * h * (np.sqrt(3) / 2) * J
    keep = region.inside(w)
    idx = -np.ones(len(w), int); idx[keep] = np.arange(keep.sum())
    key = {(int(i), int(j)): int(k) for i, j, k in zip(I[keep], J[keep], idx[keep])}
    W = w[keep]
    faces = []
    for (i, j), k in key.items():
        a = key.get((i + 1, j)); b = key.get((i, j + 1)); c = key.get((i + 1, j + 1))
        if a is not None and b is not None:
            faces.append((k, a, b))
        if a is not None and b is not None and c is not None:
            faces.append((a, c, b))
    faces = np.array(faces, int)
    Pf = W[faces]
    cross = ((Pf[:, 1] - Pf[:, 0]).conj() * (Pf[:, 2] - Pf[:, 0])).imag
    faces[cross < 0] = faces[cross < 0][:, [0, 2, 1]]
    for _ in range(60):
        V = len(W)
        deg_f = np.bincount(faces.ravel(), minlength=V)
        es = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
        eu = np.unique(es, axis=0)
        deg_e = np.bincount(eu.ravel(), minlength=V)
        bdv = deg_f == deg_e - 1
        bad = (deg_f == 0) | ((deg_f != deg_e) & ~bdv) | (bdv & (deg_f < 2))
        if not bad.any():
            break
        keepv = ~bad
        remap = -np.ones(V, int); remap[keepv] = np.arange(keepv.sum())
        faces = remap[faces[keepv[faces].all(axis=1)]]
        W = W[keepv]
    V = len(W)
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    A = sp.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(V, V))
    ncomp, lab = connected_components(A, directed=False)
    if ncomp > 1:
        big = np.argmax(np.bincount(lab)); keepv = lab == big
        remap = -np.ones(V, int); remap[keepv] = np.arange(keepv.sum())
        faces = remap[faces[keepv[faces].all(axis=1)]]; W = W[keepv]; V = len(W)
    es = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    eu, ecount = np.unique(es, axis=0, return_counts=True)
    bd_edges = eu[ecount == 1]
    boundary = np.zeros(V, bool); boundary[bd_edges.ravel()] = True
    # boundary cycle order (CCW)
    nb = defaultdict(list)
    for a, b in bd_edges:
        nb[a].append(b); nb[b].append(a)
    start = int(bd_edges[0, 0]); cyc = [start]; prev = -1; cur = start
    while True:
        nxts = [x for x in nb[cur] if x != prev]
        if not nxts:
            break
        nxt = nxts[0]
        if nxt == start:
            break
        cyc.append(nxt); prev, cur = cur, nxt
    cyc = np.array(cyc)
    area = np.sum((W[cyc].conj() * np.roll(W[cyc], -1)).imag)
    if area < 0:
        cyc = cyc[::-1]
    return dict(W=W, faces=faces, boundary=boundary, edges=eu, euler=V - len(eu) + len(faces), h=h,
                cycle=cyc, single_cycle=(len(cyc) == boundary.sum()))


def eangles(rv, ru, rw):
    a = rv + ru; b = rv + rw; c = ru + rw
    ca = (a * a + b * b - c * c) / (2 * a * b)
    return np.arccos(np.clip(ca, -1, 1))


def pack_euclid(mesh, corners, tol=1e-12, maxit=40000, verbose=True, r0=None):
    faces, bd = mesh['faces'], mesh['boundary']
    V = len(bd)
    corners_mask = np.zeros(V, bool); corners_mask[list(corners)] = True
    target = np.where(bd, np.pi, 2 * np.pi); target[corners_mask] = np.pi / 2
    C = np.concatenate([faces[:, [0, 1, 2]], faces[:, [1, 2, 0]], faces[:, [2, 0, 1]]])
    cv, cu, cw = C[:, 0], C[:, 1], C[:, 2]
    r = np.full(V, 1.0) if r0 is None else r0.copy()
    t0 = time.time()
    for it in range(maxit):
        th = np.bincount(cv, eangles(r[cv], r[cu], r[cw]), minlength=V)
        err = np.abs(th - target).max()
        if verbose and (it % 500 == 0 or err < tol):
            print(f'   it {it:5d} max|theta-target|={err:.2e} r in [{r.min():.3g},{r.max():.3g}] {time.time()-t0:.0f}s', flush=True)
        if err < tol:
            break
        eps = 1e-6
        r2 = r * (1 + eps)
        th2 = np.bincount(cv, eangles(r2[cv], r[cu], r[cw]), minlength=V)
        dth = (th2 - th) / eps
        step = -(th - target) / np.minimum(dth, -1e-12)
        step = np.clip(step, -0.5, 0.5)
        r = r * np.exp(0.85 * step)
        r /= r.mean()
    return r, th, it, target


def layout_euclid(mesh, r, v0, v1):
    faces = mesh['faces']; V = len(r)
    z = np.full(V, np.nan + 0j); placed = np.zeros(V, bool)
    z[v0] = 0; z[v1] = r[v0] + r[v1]; placed[[v0, v1]] = True
    vf = defaultdict(list)
    for fi, f in enumerate(faces):
        for v in f:
            vf[v].append(fi)
    q = deque(vf[v0] + vf[v1]); seen = set()
    while q:
        fi = q.popleft()
        if fi in seen:
            continue
        f = faces[fi]; pl = placed[f]
        if pl.sum() < 2:
            continue
        seen.add(fi)
        if pl.sum() == 3:
            for v in f:
                q.extend(vf[v])
            continue
        k = int(np.where(~pl)[0][0]); w = f[k]; v = f[(k + 1) % 3]; u = f[(k + 2) % 3]
        iv = int(np.where(f == v)[0][0]); nxt = f[(iv + 1) % 3]
        sign = +1.0 if nxt == u else -1.0
        alpha = float(eangles(np.array([r[v]]), np.array([r[u]]), np.array([r[w]]))[0])
        ang = np.angle(z[u] - z[v]) + sign * alpha
        z[w] = z[v] + (r[v] + r[w]) * np.exp(1j * ang)
        placed[w] = True; q.extend(vf[w])
    return z, placed


# ------------------------------------------------------------ exact map: MFS + elliptic
class ExactMap:
    """phi: region -> unit disc, phi(0)=0, phi'(0)>0, by the method of fundamental solutions."""
    def __init__(self, region, N=2400, M=600, d=0.45):
        th = np.linspace(0, 2 * np.pi, N, endpoint=False)
        wb = region.r(th) * np.exp(1j * th)
        ths = np.linspace(0, 2 * np.pi, M, endpoint=False) + np.pi / M
        # sources: pushed outward along the normal of the boundary curve
        rb = region.r(ths)
        dr = (region.r(ths + 1e-6) - region.r(ths - 1e-6)) / 2e-6
        pos = rb * np.exp(1j * ths)
        tang = (dr + 1j * rb) * np.exp(1j * ths)
        nrm = -1j * tang / np.abs(tang)
        self.s = pos + d * nrm * (2 * np.pi * rb / M) * (M / 40)   # ~ a few local spacings outward
        # least squares for u = q0 + sum q_j log|w - s_j| = -log|w| on boundary
        A = np.c_[np.ones(N), np.log(np.abs(wb[:, None] - self.s[None, :]))]
        rhs = -np.log(np.abs(wb))
        q, *_ = np.linalg.lstsq(A, rhs, rcond=None)
        self.q0, self.q = q[0], q[1:]
        # residual on a fresh boundary set
        th2 = np.linspace(0, 2 * np.pi, 3 * N, endpoint=False) + 0.37 * (th[1] - th[0])
        wb2 = region.r(th2) * np.exp(1j * th2)
        u2 = self.q0 + np.log(np.abs(wb2[:, None] - self.s[None, :])) @ self.q
        self.bdry_resid = float(np.abs(u2 + np.log(np.abs(wb2))).max())
        self.u0 = self.q0 + np.sum(self.q * np.log(np.abs(self.s)))
        xg, wg = np.polynomial.legendre.leggauss(64)
        self.sg = 0.5 * (xg + 1); self.wg = 0.5 * wg

    def G(self, w):
        """G(w) = u(0) + int_0^w G'(t) dt along the ray (region star-shaped from 0)"""
        w = np.asarray(w, complex)
        t = w[..., None] * self.sg               # (..., 64)
        Gp = (self.q[None, :] / (t[..., None] - self.s[None, None, :])).sum(-1)   # (...,64)
        return self.u0 + w * (Gp * self.wg).sum(-1)

    def __call__(self, w):
        return w * np.exp(self.G(w))


def rect_map_setup(p):
    """p: 4 points on the unit circle in CCW order (images of the corners).
    Returns k, and a Möbius D->H sending them to -1/k, -1, 1, 1/k, plus K, K'."""
    # rotate so that p[0] is far from the pole (we send the point -p0*e^{i eps} to infinity? simpler:)
    # D -> H : T(z) = i (1 + z e^{-i a}) / (1 - z e^{-i a}) with a chosen so that no corner is near e^{ia}
    angs = np.angle(p)
    # choose a in the largest gap between consecutive corner angles, opposite of p[0]..p[3] gaps
    s = np.sort(np.mod(angs, 2 * np.pi)); gaps = np.diff(np.r_[s, s[0] + 2 * np.pi])
    g = np.argmax(gaps); a = s[g] + gaps[g] / 2
    T = lambda z: 1j * (1 + z * np.exp(-1j * a)) / (1 - z * np.exp(-1j * a))
    x = np.real(T(p))
    order = np.argsort(x)
    # cyclic shift so that CCW order p0..p3 corresponds to increasing x: since T preserves orientation,
    # the CCW order on the circle is increasing x on the real line up to a cyclic rotation
    shift = int(np.where(order == 0)[0][0])
    idx = np.roll(np.arange(4), -shift)     # not needed further; we compute the real Möbius on sorted x
    xs = x[order]
    lam = (xs[2] - xs[0]) * (xs[3] - xs[1]) / ((xs[2] - xs[1]) * (xs[3] - xs[0]))
    A = 2 * lam - 1
    k = A - np.sqrt(A * A - 1)
    if not (0 < k < 1):
        k = A + np.sqrt(A * A - 1)
    # real Möbius m with m(xs0)=-1/k, m(xs1)=-1, m(xs2)=1  (then m(xs3)=1/k by cross-ratio)
    def mob3(x1, x2, x3, y1, y2, y3):
        # m(x) = (a x + b)/(c x + d): solve linear system for a,b,c with d=1 (assume finite)
        Mx = np.array([[x1, 1, -y1 * x1], [x2, 1, -y2 * x2], [x3, 1, -y3 * x3]], float)
        rhs = np.array([y1, y2, y3])
        abc = np.linalg.solve(Mx, rhs)
        return lambda x: (abc[0] * x + abc[1]) / (abc[2] * x + 1)
    m = mob3(xs[0], xs[1], xs[2], -1 / k, -1, 1)
    Kk = ellipk(k * k); Kp = ellipk(1 - k * k)
    return dict(k=float(k), K=float(Kk), Kp=float(Kp), modulus=float(2 * Kk / Kp), T=T, m=m,
                order=order, corner_x=xs, check4=float(m(xs[3]) - 1 / k))


def F_elliptic(z, k):
    import mpmath as mp
    mp.mp.dps = 20
    out = np.empty(len(z), complex)
    for i, zz in enumerate(z):
        zz = mp.mpc(zz.real, zz.imag)
        phi = mp.asin(zz)
        out[i] = complex(mp.ellipf(phi, k * k))
    return out


def corners_by_harmonic_measure(region, mesh, arcs=(0.30, 0.20, 0.30), start_dir=0.2):
    """boundary vertices nearest to the boundary points cutting the boundary into arcs of the given
    harmonic measures (from the exact map of the carrier-offset domain); the 4th arc is the rest."""
    W, cyc = mesh['W'], mesh['cycle']
    rc = Offset(region, 0.5 * mesh['h'])
    ex = ExactMap(rc)
    th = np.linspace(0, 2 * np.pi, 6000, endpoint=False)
    wb = rc.r(th) * np.exp(1j * th)
    ph = np.unwrap(np.angle(ex(wb)))
    ph0 = np.interp(start_dir, th, ph)
    targets = ph0 + 2 * np.pi * np.cumsum([0.0] + list(arcs))
    pts = []
    for t in targets:
        # phase is increasing in theta (orientation preserved); wrap
        tt = np.mod(t - ph[0], 2 * np.pi) + ph[0]
        i = int(np.argmin(np.abs(ph - tt)))
        pts.append(wb[i])
    corners = [int(cyc[np.argmin(np.abs(W[cyc] - p))]) for p in pts]
    return corners, rc, ex


def build(h, region=None, corner_dirs=None, arcs=(0.30, 0.20, 0.30), verbose=True, ncert=600):
    region = region or Leaf()
    t0 = time.time()
    mesh = hex_mesh(region, h)
    W, bd, cyc = mesh['W'], mesh['boundary'], mesh['cycle']
    assert mesh['single_cycle'], 'boundary is not a single cycle'
    if corner_dirs is not None:
        corners = []
        for d in corner_dirs:
            ang = np.mod(np.angle(W[cyc]) - d + np.pi, 2 * np.pi) - np.pi
            corners.append(int(cyc[np.argmin(np.abs(ang))]))
    else:
        corners, _, _ = corners_by_harmonic_measure(region, mesh, arcs)
    if verbose:
        print(f'mesh h={h}: V={len(W)} faces={len(mesh["faces"])} boundary={bd.sum()} euler={mesh["euler"]} corners={corners} {time.time()-t0:.1f}s', flush=True)
    r, th, it, target = pack_euclid_fast(mesh, corners, verbose=verbose)
    v0 = int(np.argmin(np.abs(W)))
    edges = mesh['edges']
    nbv = np.concatenate([edges[edges[:, 0] == v0][:, 1], edges[edges[:, 1] == v0][:, 0]])
    v1 = int(nbv[np.argmax((W[nbv] - W[v0]).real)])
    z, placed = layout_euclid(mesh, r, v0, v1)
    assert placed.all(), f'unplaced {(~placed).sum()}'
    # normalise: corner0 -> origin, side corner0->corner1 along +x, scale so that side = 2K (later)
    c0, c1, c2, c3 = [z[c] for c in corners]
    rot = np.exp(-1j * np.angle(c1 - c0))
    zn = (z - c0) * rot
    L1 = abs(zn[corners[1]]); L2 = abs(zn[corners[2]] - zn[corners[1]])
    rn = r * abs(rot)
    # tangency and straightness certificates
    d = np.abs(zn[edges[:, 0]] - zn[edges[:, 1]]); s = rn[edges[:, 0]] + rn[edges[:, 1]]
    tang = np.abs(d - s) / s
    # boundary straightness: max distance of boundary centres from the rectangle [0,L1]x[0,L2]
    zb = zn[bd]
    dist_rect = np.minimum.reduce([np.abs(zb.imag), np.abs(zb.imag - L2), np.abs(zb.real), np.abs(zb.real - L1)])
    cert = dict(V=int(len(W)), boundary=int(bd.sum()), faces=int(len(mesh['faces'])), euler=int(mesh['euler']), h=h,
                iters=int(it), max_angle_err=float(np.abs(th - target).max()),
                max_tangency_rel=float(tang.max()), L1=float(L1), L2=float(L2), modulus_discrete=float(L1 / L2),
                boundary_off_rectangle_max=float(dist_rect.max()), corners=corners)
    # ---- exact map
    if ncert:
        region_c = Offset(region, 0.5 * h)          # carrier-corrected comparison domain
        ex = ExactMap(region_c)
        # the exact quadrilateral's corners: the offset-boundary points NEAREST the corner vertices
        thb = np.linspace(0, 2 * np.pi, 12000, endpoint=False)
        wbb = region_c.r(thb) * np.exp(1j * thb)
        pc = np.array([wbb[np.argmin(np.abs(wbb - W[c]))] for c in corners])
        cert['corner_projection_dist'] = float(np.abs(pc - W[corners]).max())
        p = ex(pc)
        p = p / np.abs(p)
        setup = rect_map_setup(p)
        cert.update(mfs_boundary_resid=ex.bdry_resid, k=setup['k'], modulus_exact=setup['modulus'],
                    corner_vertex_off_boundary=float(np.abs(np.abs(ex(W[corners])) - 1).max()),
                    cross_ratio_check=setup['check4'])
        # per-point comparison on a random interior subset + all corners
        rng = np.random.default_rng(1)
        inner = np.where(~bd & region_c.inside(W))[0]
        sel = rng.choice(inner, min(ncert, len(inner)), replace=False)
        zex = F_elliptic(setup['m'](np.real(setup['T'](ex(W[sel])))) if False else setup['m'](setup['T'](ex(W[sel]))), setup['k'])
        # exact rectangle: corners at F(-1/k)=-K+iK', F(-1)=-K, F(1)=K, F(1/k)=K+iK'  -> map to [0,2K]x[0,K']
        zr = zex + setup['K']
        # discrete rectangle scaled to width 2K
        scale = 2 * setup['K'] / L1
        zd = zn[sel] * scale
        # both have corner0 at ... need the same corner labelling: find which exact corner is at 0
        # align: the exact rectangle may be a reflection/rotation of the labelling; test the 8 symmetries
        best = None
        for flipx in (False, True):
            for flipy in (False, True):
                for swap in (False, True):
                    t = zr.copy()
                    if swap:
                        t = t.imag + 1j * t.real
                    Lx = 2 * setup['K'] if not swap else setup['Kp']; Ly = setup['Kp'] if not swap else 2 * setup['K']
                    if flipx:
                        t = (Lx - t.real) + 1j * t.imag
                    if flipy:
                        t = t.real + 1j * (Ly - t.imag)
                    # rescale discrete to this width
                    sc = Lx / L1
                    e = np.abs(zn[sel] * sc - t)
                    if best is None or np.median(e) < best[4]:
                        best = (float(e.max()), float(e.mean()), (flipx, flipy, swap), sc, float(np.median(e)))
        cert.update(map_err_max=best[0], map_err_mean=best[1], map_symmetry=best[2],
                    map_err_relative_to_width=best[0] / (2 * setup['K']),
                    modulus_rel_err=abs(L1 / L2 - setup['modulus']) / setup['modulus'] if best[2][2] is False else abs(L1 / L2 - 1 / setup['modulus']) * setup['modulus'])
    if verbose:
        print(json.dumps({k: v for k, v in cert.items()}, indent=1, default=str), flush=True)
    return dict(mesh=mesh, r=rn, z=zn, cert=cert, region=region, corners=corners, L1=L1, L2=L2, v0=v0,
                region_c=Offset(region, 0.5 * h))


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.08
    P = build(h)
    np.savez(f'rect_h{h}.npz', W=P['mesh']['W'], faces=P['mesh']['faces'], boundary=P['mesh']['boundary'],
             edges=P['mesh']['edges'], r=P['r'], z=P['z'], corners=P['corners'])
    json.dump(P['cert'], open(f'rect_cert_h{h}.json', 'w'), indent=1, default=str)


def pack_euclid_fast(mesh, corners, tol=1e-11, verbose=True):
    """Newton–Krylov on log-radii (one angle equation replaced by the scale fix; Gauss–Bonnet makes
    the angle system rank-deficient by exactly one). Falls back to the Jacobi/Newton sweep."""
    from scipy.optimize import root
    faces, bd = mesh['faces'], mesh['boundary']
    V = len(bd)
    cm = np.zeros(V, bool); cm[list(corners)] = True
    target = np.where(bd, np.pi, 2 * np.pi); target[cm] = np.pi / 2
    C = np.concatenate([faces[:, [0, 1, 2]], faces[:, [1, 2, 0]], faces[:, [2, 0, 1]]])
    cv, cu, cw = C[:, 0], C[:, 1], C[:, 2]
    v0 = int(np.where(~bd)[0][0])
    t0 = time.time()

    def theta(x):
        r = np.exp(x)
        return np.bincount(cv, eangles(r[cv], r[cu], r[cw]), minlength=V)

    def F(x):
        f = theta(x) - target
        f[v0] = x[v0]
        return f
    x = np.zeros(V)
    for rnd in range(6):
        sol = root(F, x, method='krylov', options=dict(fatol=tol, maxiter=300, disp=False,
                                                       jac_options=dict(method='lgmres', inner_maxiter=100, outer_k=10)))
        x = sol.x
        if np.abs(F(x)).max() < 1e-10:
            break
    x = sol.x
    r = np.exp(x); th = theta(x)
    err = np.abs(th - target).max()
    if verbose:
        print(f'   krylov: success={sol.success} nfev={sol.nfev if hasattr(sol, "nfev") else "?"} max|theta-target|={err:.2e} {time.time()-t0:.1f}s', flush=True)
    if err > 1e-12:
        if verbose:
            print('   polishing with local sweeps from the krylov solution', flush=True)
        r, th, it, target = pack_euclid(mesh, corners, tol=1e-12, maxit=20000, verbose=verbose, r0=r / r.mean())
        return r, th, it, target
    r /= r.mean()
    return r, th, int(sol.nit), target
