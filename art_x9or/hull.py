"""MO 515905: Q = conv(RK ∩ (Z²+t)), K an ellipse at a fixed orientation.  Does
lim R^{1/3} E_t[P(RK) - P(Q)] / ∫κ^{4/3} ds depend on the orientation?"""
import numpy as np
from scipy.special import ellipe

def ellipse_pts(a, b, th, R, t):
    """lattice points (shifted by t) in R*E(a,b,θ) that are extreme per column and per row"""
    c, s = np.cos(th), np.sin(th)
    # quadratic form: x^T A x <= R^2
    A = np.array([[c*c/a**2 + s*s/b**2, c*s*(1/a**2 - 1/b**2)], [c*s*(1/a**2 - 1/b**2), s*s/a**2 + c*c/b**2]])
    pts = []
    for ax in (0, 1):
        A11, A12, A22 = (A[0,0], A[0,1], A[1,1]) if ax == 0 else (A[1,1], A[0,1], A[0,0])
        tx, ty = (t[0], t[1]) if ax == 0 else (t[1], t[0])
        # x-range: x^2 (A11 - A12^2/A22) <= R^2
        xm = R/np.sqrt(A11 - A12**2/A22)
        xs = np.arange(np.ceil(-xm - tx), np.floor(xm - tx) + 1) + tx
        disc = A12**2*xs**2 - A22*(A11*xs**2 - R*R)
        ok = disc >= 0; xs = xs[ok]; disc = np.sqrt(disc[ok])
        y1 = (-A12*xs - disc)/A22; y2 = (-A12*xs + disc)/A22
        lo = np.ceil(y1 - ty) + ty; hi = np.floor(y2 - ty) + ty
        ok = lo <= hi; xs, lo, hi = xs[ok], lo[ok], hi[ok]
        P = np.concatenate([np.stack([xs, lo], 1), np.stack([xs, hi], 1)])
        if ax == 1: P = P[:, ::-1]
        pts.append(P)
    return np.unique(np.concatenate(pts), axis=0)

def hull(P):
    P = P[np.lexsort((P[:, 1], P[:, 0]))]
    def half(P):
        H = []
        for p in P:
            while len(H) >= 2 and ((H[-1][0]-H[-2][0])*(p[1]-H[-2][1]) - (H[-1][1]-H[-2][1])*(p[0]-H[-2][0])) <= 0: H.pop()
            H.append(tuple(p))
        return H
    lo = half(P); up = half(P[::-1])
    return np.array(lo[:-1] + up[:-1])

def perim(H):
    d = np.diff(np.vstack([H, H[:1]]), axis=0); return np.hypot(d[:, 0], d[:, 1]).sum()

def ell_perim(a, b):
    a, b = max(a, b), min(a, b); return 4*a*ellipe(1 - (b/a)**2)

def kappa43(a, b, n=200000):
    s = np.linspace(0, 2*np.pi, n, endpoint=False)
    ds = np.hypot(a*np.sin(s), b*np.cos(s)); k = a*b/ds**3
    return (k**(4/3)*ds).sum()*2*np.pi/n

def stat(a, b, th, R, nt, seed=0):
    rng = np.random.default_rng(seed)
    # stratified translations
    m = int(np.sqrt(nt)); g = (np.arange(m) + 0.5)/m
    T = np.stack(np.meshgrid(g, g), -1).reshape(-1, 2) + (rng.random(2) - 0.5)/m
    Pe = R*ell_perim(a, b)
    D = np.array([Pe - perim(hull(ellipse_pts(a, b, th, R, t % 1))) for t in T])
    return R**(1/3)*D.mean()/kappa43(a, b), R**(1/3)*D.std()/kappa43(a, b)/np.sqrt(len(D))

if __name__ == '__main__':
    import sys
    a, b = 1.0, 0.5
    print('disc check', [stat(1, 1, 0, R, 400) for R in (200, 800)])
    for th in (0.0, np.pi/8, np.pi/4, 0.5*(np.sqrt(5)-1)):
        print('theta', round(th, 4), [tuple(np.round(stat(a, b, th, R, 400), 4)) for R in (200, 800, 3200)], flush=True)
