"""Machinery for the level-table piece (MO 513737).

Terrain: h(x,y) = (1 - r^2) * sum_m A_m cos(kx_m x + ky_m y + phi_m)
on the closed unit disk; h = 0 on the boundary circle, smooth everywhere.
All evaluation is ANALYTIC (no grids), so Newton polishing is exact.

Config space of a table placement: center c = (cx, cy), rotation theta.
 - tripod (equilateral triangle, side d): feet at c + Rc*(cos(theta + 2pi i/3),
   sin(...)), Rc = d/sqrt(3).  Level <=> u1 = h(f2)-h(f1) = 0 and
   u2 = h(f3)-h(f1) = 0: two equations, three unknowns -> solution CURVES.
 - square table (side d): feet at c + Rs*(cos(theta + pi/2 i), ...), Rs = d/sqrt(2).
   Balanced (all four lifted feet coplanar) <=> g = h1 - h2 + h3 - h4 = 0
   (exact: the two diagonals share their xy midpoint, so coplanarity is
   equality of the lifted midpoints).  One equation -> a 2-surface.
   Level <=> h1 = h2 = h3 = h4: three equations -> isolated points (if any).
"""
import numpy as np

TAU = 2 * np.pi


def make_terrain(seed=7, nmodes=16, kmin=2.5, kmax=6.5, amp=1.0):
    rng = np.random.default_rng(seed)
    kmag = rng.uniform(kmin, kmax, nmodes)
    kang = rng.uniform(0, TAU, nmodes)
    kx = kmag * np.cos(kang)
    ky = kmag * np.sin(kang)
    ph = rng.uniform(0, TAU, nmodes)
    A = rng.uniform(0.4, 1.0, nmodes) / np.sqrt(nmodes)
    A *= amp
    return dict(kx=kx, ky=ky, ph=ph, A=A)


def h_eval(T, x, y):
    """Analytic terrain height. x, y arrays (broadcast)."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    w = 1.0 - (x * x + y * y)
    s = np.zeros(np.broadcast(x, y).shape)
    for kx, ky, ph, A in zip(T['kx'], T['ky'], T['ph'], T['A']):
        s += A * np.cos(kx * x + ky * y + ph)
    return w * s


def h_grad(T, x, y):
    """Analytic gradient of h."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    s = np.zeros(np.broadcast(x, y).shape)
    sx = np.zeros_like(s)
    sy = np.zeros_like(s)
    for kx, ky, ph, A in zip(T['kx'], T['ky'], T['ph'], T['A']):
        arg = kx * x + ky * y + ph
        c = np.cos(arg)
        sn = np.sin(arg)
        s += A * c
        sx += -A * kx * sn
        sy += -A * ky * sn
    w = 1.0 - (x * x + y * y)
    hx = -2 * x * s + w * sx
    hy = -2 * y * s + w * sy
    return hx, hy


def feet(cx, cy, theta, Rc, nlegs):
    """Foot positions: lists of arrays fx[i], fy[i]."""
    fx, fy = [], []
    for i in range(nlegs):
        a = theta + TAU * i / nlegs
        fx.append(cx + Rc * np.cos(a))
        fy.append(cy + Rc * np.sin(a))
    return fx, fy


def tri_uv(T, cx, cy, theta, Rc):
    fx, fy = feet(cx, cy, theta, Rc, 3)
    h1 = h_eval(T, fx[0], fy[0])
    h2 = h_eval(T, fx[1], fy[1])
    h3 = h_eval(T, fx[2], fy[2])
    return h2 - h1, h3 - h1


def tri_jac(T, cx, cy, theta, Rc):
    """Jacobian of (u1,u2) wrt (cx,cy,theta): shape (...,2,3)."""
    fx, fy = feet(cx, cy, theta, Rc, 3)
    g = [h_grad(T, fx[i], fy[i]) for i in range(3)]
    # d f_i/d cx = (1,0); /d cy = (0,1); /d theta = Rc*(-sin a_i, cos a_i)
    J = np.empty(np.broadcast(np.asarray(cx), np.asarray(cy)).shape + (2, 3))
    for row, i in ((0, 1), (1, 2)):
        gx_i, gy_i = g[i]
        gx_0, gy_0 = g[0]
        a_i = theta + TAU * i / 3
        a_0 = theta
        J[..., row, 0] = gx_i - gx_0
        J[..., row, 1] = gy_i - gy_0
        J[..., row, 2] = (Rc * (-np.sin(a_i) * gx_i + np.cos(a_i) * gy_i)
                          - Rc * (-np.sin(a_0) * gx_0 + np.cos(a_0) * gy_0))
    return J


def sq_uvw(T, cx, cy, theta, Rs):
    fx, fy = feet(cx, cy, theta, Rs, 4)
    h = [h_eval(T, fx[i], fy[i]) for i in range(4)]
    return h[1] - h[0], h[2] - h[0], h[3] - h[0]


def sq_jac(T, cx, cy, theta, Rs):
    fx, fy = feet(cx, cy, theta, Rs, 4)
    g = [h_grad(T, fx[i], fy[i]) for i in range(4)]
    J = np.empty(np.broadcast(np.asarray(cx), np.asarray(cy)).shape + (3, 3))
    for row, i in ((0, 1), (1, 2), (2, 3)):
        gx_i, gy_i = g[i]
        gx_0, gy_0 = g[0]
        a_i = theta + TAU * i / 4
        a_0 = theta
        J[..., row, 0] = gx_i - gx_0
        J[..., row, 1] = gy_i - gy_0
        J[..., row, 2] = (Rs * (-np.sin(a_i) * gx_i + np.cos(a_i) * gy_i)
                          - Rs * (-np.sin(a_0) * gx_0 + np.cos(a_0) * gy_0))
    return J


# ---------------------------------------------------------------- level triangles
def tri_curve_points(T, d, ngrid=640, ntheta=768, cmax=None, verbose=False):
    """Extract points on the level-triangle solution curves.

    Sheet extraction: for each center on an (ngrid x ngrid) lattice, find all
    theta-roots of u1 in [0, 2pi/3) by dense scan + linear interp; record u2
    there.  Then match roots between x-neighbours (nearest theta) and detect
    sign changes of u2 -> secant point -> Newton polish on (u1,u2)=0 with the
    pseudo-inverse step.  Returns (cx, cy, th, k) arrays of polished solutions
    (k = common height) and diagnostics.
    """
    Rc = d / np.sqrt(3)
    if cmax is None:
        cmax = 1.0 - Rc
    period = TAU / 3
    th = np.linspace(0, period, ntheta + 1)   # includes endpoint: u1 is NOT
    xs = np.linspace(-cmax, cmax, ngrid)      # 2pi/3-periodic (only the joint
    ys = np.linspace(-cmax, cmax, ngrid)      # solution set is), so scan the
    KMAX = 16                                  # closed interval edge-by-edge.
    root_th = np.full((ngrid, ngrid, KMAX), np.nan)
    root_u2 = np.full((ngrid, ngrid, KMAX), np.nan)

    # chunk over rows of centers
    for i0 in range(0, ngrid, 32):
        i1 = min(i0 + 32, ngrid)
        CX, CY, TH = np.meshgrid(xs[i0:i1], ys, th, indexing='ij')
        mask = CX[..., 0] ** 2 + CY[..., 0] ** 2 <= cmax ** 2
        u1, u2 = tri_uv(T, CX, CY, TH, Rc)
        u1n = u1[..., 1:]
        u1 = u1[..., :-1]
        sc = (u1 * u1n < 0)
        # linear interp root
        frac = np.where(sc, u1 / (u1 - u1n + 1e-300), 0.0)
        throot = TH[..., :-1] + frac * (period / ntheta)
        # u2 at interpolated root (linear interp of u2 too)
        u2n = u2[..., 1:]
        u2 = u2[..., :-1]
        u2r = u2 + frac * (u2n - u2)
        for ii in range(i1 - i0):
            for jj in range(ngrid):
                if not mask[ii, jj]:
                    continue
                w = np.where(sc[ii, jj])[0]
                nw = min(len(w), KMAX)
                root_th[i0 + ii, jj, :nw] = throot[ii, jj, w[:nw]]
                root_u2[i0 + ii, jj, :nw] = u2r[ii, jj, w[:nw]]
        if verbose and i0 % 128 == 0:
            print(f'  tri scan {i0}/{ngrid}')
    # neighbour pairing along x and y
    cand = []
    for axis in (0, 1):
        ta = root_th
        ua = root_u2
        tb = np.roll(root_th, -1, axis=axis)
        ub = np.roll(root_u2, -1, axis=axis)
        # periodic theta distance between all slot pairs
        dth = np.abs(ta[..., :, None] - tb[..., None, :])
        dth = np.minimum(dth, period - dth)
        # match: nearest slot in b for each slot in a
        with np.errstate(invalid='ignore'):
            jbest = np.nanargmin(np.where(np.isnan(dth), np.inf, dth), axis=-1)
        ii, jj, kk = np.indices(jbest.shape)
        tb_m = tb[ii, jj, jbest]
        ub_m = ub[ii, jj, jbest]
        dth_m = np.take_along_axis(dth, jbest[..., None], axis=-1)[..., 0]
        ok = (~np.isnan(ta)) & (~np.isnan(tb_m)) & (dth_m < period / 12) \
             & (ua * ub_m < 0)
        # exclude wrap row/col
        if axis == 0:
            ok[-1, :, :] = False
        else:
            ok[:, -1, :] = False
        w = np.where(ok)
        t = ua[w] / (ua[w] - ub_m[w])
        cx = xs[w[0]] + (t * (xs[1] - xs[0]) if axis == 0 else 0.0)
        cy = ys[w[1]] + (t * (ys[1] - ys[0]) if axis == 1 else 0.0)
        thm = ta[w] + t * (((tb_m[w] - ta[w] + period / 2) % period) - period / 2)
        cand.append((cx, cy, thm % period))
    cx = np.concatenate([c[0] for c in cand])
    cy = np.concatenate([c[1] for c in cand])
    thc = np.concatenate([c[2] for c in cand])

    # Newton polish with pseudo-inverse (2 eqs, 3 unknowns)
    for _ in range(6):
        u1, u2 = tri_uv(T, cx, cy, thc, Rc)
        J = tri_jac(T, cx, cy, thc, Rc)
        F = np.stack([u1, u2], axis=-1)
        JJt = np.einsum('...ik,...jk->...ij', J, J)
        det = JJt[..., 0, 0] * JJt[..., 1, 1] - JJt[..., 0, 1] * JJt[..., 1, 0]
        det = np.where(np.abs(det) < 1e-30, 1e-30, det)
        inv00 = JJt[..., 1, 1] / det
        inv11 = JJt[..., 0, 0] / det
        inv01 = -JJt[..., 0, 1] / det
        lam0 = inv00 * F[..., 0] + inv01 * F[..., 1]
        lam1 = inv01 * F[..., 0] + inv11 * F[..., 1]
        step = J[..., 0, :] * lam0[..., None] + J[..., 1, :] * lam1[..., None]
        cx = cx - step[..., 0]
        cy = cy - step[..., 1]
        thc = thc - step[..., 2]
    u1, u2 = tri_uv(T, cx, cy, thc, Rc)
    res = np.abs(u1) + np.abs(u2)
    keep = (res < 1e-10) & (cx ** 2 + cy ** 2 <= cmax ** 2)
    cx, cy, thc = cx[keep], cy[keep], thc[keep] % period
    fx, fy = feet(cx, cy, thc, Rc, 3)
    k = h_eval(T, fx[0], fy[0])
    return cx, cy, thc, k


# ---------------------------------------------------------------- level squares
def sq_level_points(T, d, ngrid=192, ntheta=256, cmax=None):
    """Find isolated level-square configurations by dense grid + 3D Newton."""
    Rs = d / np.sqrt(2)
    if cmax is None:
        cmax = 1.0 - Rs
    period = TAU / 4
    th = np.linspace(0, period, ntheta, endpoint=False)
    xs = np.linspace(-cmax, cmax, ngrid)
    cand = []
    cell = max(2 * cmax / ngrid, period / ntheta)
    for i0 in range(0, ngrid, 24):
        i1 = min(i0 + 24, ngrid)
        CX, CY, TH = np.meshgrid(xs[i0:i1], xs, th, indexing='ij')
        u, v, w = sq_uvw(T, CX, CY, TH, Rs)
        # generous threshold: |u| < C*cell (C ~ max |grad| * lever)
        thr = 8.0 * cell
        m = (np.abs(u) < thr) & (np.abs(v) < thr) & (np.abs(w) < thr) \
            & (CX ** 2 + CY ** 2 <= cmax ** 2)
        if m.any():
            cand.append((CX[m], CY[m], TH[m]))
    if not cand:
        return (np.array([]),) * 4
    cx = np.concatenate([c[0] for c in cand])
    cy = np.concatenate([c[1] for c in cand])
    thc = np.concatenate([c[2] for c in cand])
    # 3D Newton
    for _ in range(12):
        u, v, w = sq_uvw(T, cx, cy, thc, Rs)
        J = sq_jac(T, cx, cy, thc, Rs)
        F = np.stack([u, v, w], axis=-1)
        try:
            step = np.linalg.solve(J, F[..., None])[..., 0]
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(J.reshape(-1, 3, 3), F.reshape(-1, 3))[0]
        nrm = np.linalg.norm(step, axis=-1)
        step = step * np.minimum(1.0, 0.1 / (nrm + 1e-30))[..., None]
        cx, cy, thc = cx - step[..., 0], cy - step[..., 1], thc - step[..., 2]
    u, v, w = sq_uvw(T, cx, cy, thc, Rs)
    res = np.abs(u) + np.abs(v) + np.abs(w)
    keep = (res < 1e-11) & (cx ** 2 + cy ** 2 <= cmax ** 2) & ~np.isnan(res)
    cx, cy, thc = cx[keep], cy[keep], thc[keep] % period
    if len(cx) == 0:
        return (np.array([]),) * 4
    # dedupe
    pts = np.stack([cx, cy, np.cos(4 * thc) * 0.2, np.sin(4 * thc) * 0.2], axis=1)
    order = np.lexsort((pts[:, 1], pts[:, 0]))
    uniq = []
    for idx in order:
        p = pts[idx]
        if all(np.linalg.norm(p - pts[j]) > 1e-5 for j in uniq):
            uniq.append(idx)
    cx, cy, thc = cx[uniq], cy[uniq], thc[uniq]
    fx, fy = feet(cx, cy, thc, Rs, 4)
    k = h_eval(T, fx[0], fy[0])
    return cx, cy, thc, k


# ---------------------------------------------------------------- balanced field
def balanced_tilt_field(T, d, ngrid=512, ntheta=384, cmax=None):
    """For each center: min over balanced orientations of the resting-plane tilt.

    Returns (field, count) where field[i,j] = min tilt angle (radians) over the
    theta-roots of g = h1-h2+h3-h4 (balanced configs), count = number of roots
    in [0, pi/2).  NaN outside the allowed center disk.
    """
    Rs = d / np.sqrt(2)
    if cmax is None:
        cmax = 1.0 - Rs
    period = np.pi / 2
    th = np.linspace(0, period, ntheta, endpoint=False)
    xs = np.linspace(-cmax, cmax, ngrid)
    tilt = np.full((ngrid, ngrid), np.nan)
    count = np.zeros((ngrid, ngrid), dtype=np.int32)
    for i0 in range(0, ngrid, 16):
        i1 = min(i0 + 16, ngrid)
        CX, CY, TH = np.meshgrid(xs[i0:i1], xs, th, indexing='ij')
        fx, fy = feet(CX, CY, TH, Rs, 4)
        h = [h_eval(T, fx[i], fy[i]) for i in range(4)]
        g = h[0] - h[1] + h[2] - h[3]
        gn = np.roll(g, -1, axis=2)
        # handle period boundary: g(theta + pi/2) = -g(theta) -> last-to-first
        gn[..., -1] = -g[..., 0]
        sc = g * gn < 0
        frac = np.where(sc, g / (g - gn + 1e-300), 0.0)
        throot = TH + frac * (period / ntheta)
        # tilt of resting plane at each root: plane through 4 coplanar feet
        # normal from two diagonal vectors: D1 = f3-f1, D2 = f4-f2 (3D lifted)
        h_r = [h[i] + frac * (np.roll(h[i], -1, axis=2) - h[i]) for i in range(4)]
        fx_r, fy_r = feet(CX, CY, throot, Rs, 4)
        d1 = np.stack([fx_r[2] - fx_r[0], fy_r[2] - fy_r[0], h_r[2] - h_r[0]], axis=-1)
        d2 = np.stack([fx_r[3] - fx_r[1], fy_r[3] - fy_r[1], h_r[3] - h_r[1]], axis=-1)
        nrm = np.cross(d1, d2)
        tl = np.arccos(np.clip(np.abs(nrm[..., 2]) /
                               (np.linalg.norm(nrm, axis=-1) + 1e-300), 0, 1))
        tl = np.where(sc, tl, np.inf)
        block_tilt = tl.min(axis=2)
        block_cnt = sc.sum(axis=2)
        mask = CX[..., 0] ** 2 + CY[..., 0] ** 2 <= cmax ** 2
        sl = tilt[i0:i1]
        sl[mask] = block_tilt[mask]
        count[i0:i1][mask] = block_cnt[mask]
    return tilt, count, xs


# ---------------------------------------------------------------- curve tracing
def _tri_project(T, p, Rc, iters=4):
    """Newton-project points (n,3) onto the level-triangle curve."""
    cx, cy, th = p[:, 0], p[:, 1], p[:, 2]
    for _ in range(iters):
        u1, u2 = tri_uv(T, cx, cy, th, Rc)
        J = tri_jac(T, cx, cy, th, Rc)
        F = np.stack([u1, u2], axis=-1)
        JJt = np.einsum('...ik,...jk->...ij', J, J)
        det = JJt[..., 0, 0] * JJt[..., 1, 1] - JJt[..., 0, 1] * JJt[..., 1, 0]
        det = np.where(np.abs(det) < 1e-30, 1e-30, det)
        lam0 = (JJt[..., 1, 1] * F[..., 0] - JJt[..., 0, 1] * F[..., 1]) / det
        lam1 = (-JJt[..., 1, 0] * F[..., 0] + JJt[..., 0, 0] * F[..., 1]) / det
        step = J[..., 0, :] * lam0[..., None] + J[..., 1, :] * lam1[..., None]
        cx, cy, th = cx - step[..., 0], cy - step[..., 1], th - step[..., 2]
    return np.stack([cx, cy, th], axis=-1)


def trace_tri_curves(T, d, seeds, cmax, step=0.002, maxsteps=20000):
    """Pseudo-arclength tracing of level-triangle curves from seed points.

    seeds: (n,3) array of polished on-curve points.  Returns a list of
    components, each a dict with 'pts' (m,3) and 'closed' bool; and marks
    which seeds were absorbed.  Spatial hash dedupe with cell ~ 2.5*step.
    """
    period = TAU / 3
    Rc = d / np.sqrt(3)
    cell = 3.0 * step
    visited = set()

    def keys(p):
        # theta wraps with period; scale theta comparable to xy (lever Rc)
        return (int(np.floor(p[0] / cell)), int(np.floor(p[1] / cell)),
                int(np.floor((p[2] % period) * Rc / cell)))

    def tangent(p):
        J = tri_jac(T, p[0], p[1], p[2], Rc)
        t = np.cross(J[0], J[1])
        n = np.linalg.norm(t)
        return t / (n + 1e-300)

    comps = []
    for s in seeds:
        if keys(s) in visited:
            continue
        pts_all = []
        closed = False
        for direction in (1.0, -1.0):
            p = s.copy()
            t = tangent(p) * direction
            pts = [p.copy()]
            for it in range(maxsteps):
                q = p + step * t
                q = _tri_project(T, q[None, :], Rc)[0]
                tn = tangent(q)
                if np.dot(tn, t) < 0:
                    tn = -tn
                p, t = q, tn
                pts.append(p.copy())
                if p[0] ** 2 + p[1] ** 2 > cmax ** 2:
                    break
                dth = (p[2] - s[2]) % period
                dth = min(dth, period - dth)
                if it > 10 and np.hypot(p[0] - s[0], p[1] - s[1]) < 1.6 * step \
                        and dth * Rc < 1.6 * step:
                    closed = True
                    break
            pts_all.append(np.array(pts))
            if closed:
                break
        if closed:
            comp = pts_all[0]
        else:
            comp = np.concatenate([pts_all[1][::-1], pts_all[0]])
        for p in comp[::2]:
            visited.add(keys(p))
            # also mark neighbours to be robust
        if len(comp) > 6:
            comps.append(dict(pts=comp, closed=closed))
    return comps
