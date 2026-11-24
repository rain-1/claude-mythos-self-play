"""Rigid assemblies of n unit squares round the corner of an L-corridor (MO 518136).

Criterion (see RESULTS.md, Lemma 1).  Put the assembly S in the plane, and for a
turning angle t let u=(cos t, sin t), v=(-sin t, cos t), x=u.p, y=v.p,
hx=max x, hy=max y.  S can sit AT the corner with the corridor at angle t,
corridor width w, iff
      g(t) := max_{p in S} min(hx - x, hy - y) <= w,
it lies in the first arm iff Wv(t)=hy-min y <= w, in the second iff Wu(t)<=w.
Because the set of admissible corner positions is a box-star about one point
that moves continuously with t, S passes iff some arc [t0,t1] has
      max( Wv(t0), max_{arc} g, Wu(t1) ) <= w      (or the same with u,v swapped).
width(P) returns the least such w; the area carried is n / w^2.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def verts(P):
    n = P.shape[0]
    V = np.empty((n, 4, 2))
    for i in range(n):
        c = np.cos(P[i, 2]) * 0.5; s = np.sin(P[i, 2]) * 0.5
        V[i, 0, 0] = P[i, 0] + c - s; V[i, 0, 1] = P[i, 1] + s + c
        V[i, 1, 0] = P[i, 0] - c - s; V[i, 1, 1] = P[i, 1] - s + c
        V[i, 2, 0] = P[i, 0] - c + s; V[i, 2, 1] = P[i, 1] - s - c
        V[i, 3, 0] = P[i, 0] + c + s; V[i, 3, 1] = P[i, 1] + s - c
    return V

@njit(cache=True)
def profiles(P, N):
    """g, Wu, Wv on N angles of the full turn."""
    V = verts(P); n = P.shape[0]
    g = np.empty(N); Wu = np.empty(N); Wv = np.empty(N)
    X = np.empty((n, 4)); Y = np.empty((n, 4))
    for k in range(N):
        t = 2 * np.pi * k / N
        c = np.cos(t); s = np.sin(t)
        hx = -1e18; hy = -1e18; lx = 1e18; ly = 1e18
        for i in range(n):
            for j in range(4):
                x = c * V[i, j, 0] + s * V[i, j, 1]
                y = -s * V[i, j, 0] + c * V[i, j, 1]
                X[i, j] = x; Y[i, j] = y
                if x > hx: hx = x
                if y > hy: hy = y
                if x < lx: lx = x
                if y < ly: ly = y
        best = 0.0
        for i in range(n):
            for j in range(4):
                f1 = hx - X[i, j]; f2 = hy - Y[i, j]
                m = f1 if f1 < f2 else f2
                if m > best: best = m
                j2 = (j + 1) % 4
                d1 = f1 - f2
                d2 = (hx - X[i, j2]) - (hy - Y[i, j2])
                if d1 * d2 < 0:
                    tt = d1 / (d1 - d2)
                    m = f1 + tt * ((hx - X[i, j2]) - f1)
                    if m > best: best = m
        g[k] = best; Wu[k] = hx - lx; Wv[k] = hy - ly
    return g, Wu, Wv

@njit(cache=True)
def arc_min(g, a, b):
    """min over arcs i..j (forward, cyclic) of max(a[i], max g[i..j], b[j]); returns (w,i,len)."""
    N = g.shape[0]
    best = 1e18; bi = 0; bl = 0
    for i in range(N):
        if a[i] >= best: continue
        rm = a[i]
        for l in range(N):
            j = (i + l) % N
            if g[j] > rm: rm = g[j]
            if rm >= best: break
            c = rm if rm > b[j] else b[j]
            if c < best:
                best = c; bi = i; bl = l
    return best, bi, bl

@njit(cache=True)
def width(P, N):
    g, Wu, Wv = profiles(P, N)
    w1, i1, l1 = arc_min(g, Wv, Wu)
    w2, i2, l2 = arc_min(g, Wu, Wv)
    if w1 <= w2: return w1, i1, l1, 0
    return w2, i2, l2, 1


@njit(cache=True)
def _feasible(g, a, b, w):
    N = g.shape[0]
    # find a break point (g > w) to unroll the circle
    st = -1
    for i in range(N):
        if g[i] > w: st = i; break
    if st < 0:
        return a.min() <= w and b.min() <= w
    ha = False; hb = False
    for q in range(1, N + 1):
        i = (st + q) % N
        if g[i] > w:
            ha = False; hb = False
        else:
            if a[i] <= w: ha = True
            if b[i] <= w: hb = True
            if ha and hb: return True
    return False

@njit(cache=True)
def width_fast(P, N):
    """same value as width(P,N)[0] in O(N log) : bisection on w over the components of {g <= w}"""
    g, Wu, Wv = profiles(P, N)
    lo = g.min(); hi = max(Wu.min(), Wv[np.argmin(Wu)])
    hi = max(hi, max(Wu[0], Wv[0]))
    for it in range(60):
        mid = 0.5 * (lo + hi)
        if _feasible(g, Wv, Wu, mid): hi = mid
        else: lo = mid
    return hi

@njit(cache=True)
def overlap(P):
    """sum of SAT penetration depths over pairs of unit squares."""
    n = P.shape[0]; tot = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            dx = P[j, 0] - P[i, 0]; dy = P[j, 1] - P[i, 1]
            if dx * dx + dy * dy >= 2.0: continue
            pen = 1e18
            for k in range(2):
                th = P[i, 2] if k == 0 else P[j, 2]
                for q in range(2):
                    ax = np.cos(th + q * np.pi / 2); ay = np.sin(th + q * np.pi / 2)
                    r = 0.0
                    for m in range(2):
                        ph = P[i, 2] if m == 0 else P[j, 2]
                        r += 0.5 * (abs(ax * np.cos(ph) + ay * np.sin(ph)) + abs(-ax * np.sin(ph) + ay * np.cos(ph)))
                    d = r - abs(ax * dx + ay * dy)
                    if d < pen: pen = d
            if pen > 0: tot += pen
    return tot

@njit(cache=True)
def objective(x, N, lam):
    P = x.reshape(-1, 3)
    w = width_fast(P, N)
    return w + lam * overlap(P)

def area(P, N=2880):
    P = np.asarray(P, float).reshape(-1, 3)
    return len(P) / width(P, N)[0] ** 2

if __name__ == "__main__":
    print("unit square", area([[0, 0, 0]]))
    d = (np.sqrt(2) - 1) / 2  # guess; scan
    best = 0
    for d in np.linspace(0, 1, 2001):
        A = area([[0, 0, 0], [-1, d, 0], [1, d, 0]], 1440)
        if A > best: best = A; bd = d
    print("staircase best delta", bd, best, (36 + 24 * np.sqrt(2)) / 49)
