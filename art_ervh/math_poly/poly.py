"""Core: unit-side polygons in [0,1]^2.
Parametrisation p = [x0, y0, th_0..th_{n-1}]; edge k = (cos th_k, sin th_k), so every
side has length exactly 1; closure v_n = v_0 is a constraint.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "1")
import numpy as np
import numba as nb
from scipy.optimize import least_squares


@nb.njit(cache=True)
def _pseg(px, py, ax, ay, bx, by):
    dx = bx - ax; dy = by - ay
    L = dx * dx + dy * dy
    t = ((px - ax) * dx + (py - ay) * dy) / L if L > 0 else 0.0
    if t < 0: t = 0.0
    if t > 1: t = 1.0
    qx = ax + t * dx - px; qy = ay + t * dy - py
    return np.sqrt(qx * qx + qy * qy)


@nb.njit(cache=True)
def _orient(ax, ay, bx, by, cx, cy):
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


@nb.njit(cache=True)
def segdist_signed(ax, ay, bx, by, cx, cy, dx, dy):
    d = min(_pseg(ax, ay, cx, cy, dx, dy), _pseg(bx, by, cx, cy, dx, dy),
            _pseg(cx, cy, ax, ay, bx, by), _pseg(dx, dy, ax, ay, bx, by))
    o1 = _orient(ax, ay, bx, by, cx, cy); o2 = _orient(ax, ay, bx, by, dx, dy)
    o3 = _orient(cx, cy, dx, dy, ax, ay); o4 = _orient(cx, cy, dx, dy, bx, by)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return -d
    return d


@nb.njit(cache=True)
def residual(p, n, margin, fold, wbox, wsep):
    V = np.empty((n + 1, 2))
    V[0, 0] = p[0]; V[0, 1] = p[1]
    for k in range(n):
        V[k + 1, 0] = V[k, 0] + np.cos(p[2 + k])
        V[k + 1, 1] = V[k, 1] + np.sin(p[2 + k])
    npairs = 0
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            npairs += 1
    r = np.zeros(2 + 4 * n + n + npairs)
    r[0] = V[n, 0] - V[0, 0]; r[1] = V[n, 1] - V[0, 1]
    c = 2
    for k in range(n):
        for a in range(2):
            x = V[k, a]
            r[c] = wbox * (-x if x < 0 else 0.0); c += 1
            r[c] = wbox * (x - 1 if x > 1 else 0.0); c += 1
    # fold: distance between v_{k-1} and v_{k+1}
    for k in range(n):
        km = (k - 1) % n; kp = k + 1
        ddx = V[kp, 0] - V[km, 0]; ddy = V[kp, 1] - V[km, 1]
        dd = np.sqrt(ddx * ddx + ddy * ddy)
        r[c] = wsep * (fold - dd if dd < fold else 0.0); c += 1
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            d = segdist_signed(V[i, 0], V[i, 1], V[i + 1, 0], V[i + 1, 1],
                               V[j, 0], V[j, 1], V[j + 1, 0], V[j + 1, 1])
            r[c] = wsep * (margin - d if d < margin else 0.0); c += 1
    return r


def verts_from_p(p, n):
    th = p[2:2 + n]
    V = np.zeros((n + 1, 2)); V[0] = p[:2]
    V[1:] = p[:2] + np.cumsum(np.c_[np.cos(th), np.sin(th)], axis=0)
    return V[:n]


def p_from_verts(V):
    V = np.asarray(V, float); n = len(V)
    E = np.roll(V, -1, axis=0) - V
    return np.r_[V[0], np.arctan2(E[:, 1], E[:, 0])]


def solve(p0, n, margin=0.005, fold=0.03, wbox=1.0, wsep=1.0, max_nfev=3000):
    f = lambda p: residual(p, n, margin, fold, wbox, wsep)
    res = least_squares(f, p0, method="trf", xtol=1e-15, ftol=1e-15, gtol=1e-15,
                        max_nfev=max_nfev)
    return res.x, res.fun


def exact_check(V):
    """Exact-ish validation in float64. Returns dict."""
    V = np.asarray(V, float); n = len(V)
    E = np.roll(V, -1, axis=0) - V
    lens = np.hypot(E[:, 0], E[:, 1])
    len_err = float(np.max(np.abs(lens - 1)))
    box_err = float(max(0.0, -V.min(), V.max() - 1))
    clear = np.inf; crossing = False
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            a, b = V[i], V[(i + 1) % n]; c, d = V[j], V[(j + 1) % n]
            s = segdist_signed(a[0], a[1], b[0], b[1], c[0], c[1], d[0], d[1])
            if s < 0: crossing = True
            clear = min(clear, abs(s))
    # adjacent edges must not overlap (no 180-degree fold)
    fold = min(np.hypot(*(V[(k + 1) % n] - V[k - 1])) for k in range(n))
    ok = len_err < 1e-9 and box_err < 1e-9 and (not crossing) and clear > 1e-9 and fold > 1e-9
    return dict(ok=ok, len_err=len_err, box_err=box_err, crossing=crossing,
                clearance=float(clear), fold=float(fold))


def orient_ccw(V):
    V = np.asarray(V, float)
    x, y = V[:, 0], V[:, 1]
    A = 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
    return V if A > 0 else V[::-1].copy()


def turns(V):
    V = orient_ccw(V); n = len(V)
    E = np.roll(V, -1, axis=0) - V
    cr = E[:, 0] * np.roll(E[:, 1], -1) - E[:, 1] * np.roll(E[:, 0], -1)
    # turn at vertex k+1; rotate so index = vertex index
    s = "".join("L" if c > 0 else "R" for c in cr)
    return s[-1] + s[:-1]


def canon(s):
    cands = []
    for t in (s, s[::-1]):
        for k in range(len(t)):
            cands.append(t[k:] + t[:k])
    return min(cands)


def interior_angles(V):
    V = orient_ccw(V); n = len(V)
    out = []
    for k in range(n):
        a = V[k - 1] - V[k]; b = V[(k + 1) % n] - V[k]
        ang = np.degrees(np.arctan2(a[0] * b[1] - a[1] * b[0], a @ b))
        # interior angle for CCW polygon measured from b to a
        ang = np.degrees(np.arctan2(b[0] * a[1] - b[1] * a[0], a @ b)) % 360
        out.append(ang)
    return np.array(out)
