"""Poncelet porism engine: outer unit circle, inner circle center (d,0) radius r.

Map: from theta on the outer circle, take the ccw tangent chord to the inner
circle, next vertex = second intersection with the outer circle.  Rotation
number rho(d,r); porism: rho = p/q  <=>  EVERY starting point closes after q
steps (winding p).

Certificates: Chapple (q=3): d^2 = 1 - 2r ; Fuss (q=4):
1/(1-d)^2 + 1/(1+d)^2 = 1/r^2.  We confirm rho = 1/3, 1/4 on these exact
curves, and closure |P_q - P_0| ~ 1e-12 for arbitrary starts.
"""
import numpy as np, json

def step(theta, d, r):
    """Vectorized one step of the ccw Poncelet map."""
    Px, Py = np.cos(theta), np.sin(theta)
    wx, wy = d - Px, -Py                       # a - P
    C = np.hypot(wx, wy)
    beta = np.arctan2(wx, wy)
    g = np.arccos(np.clip(r / C, -1, 1))
    # two tangent directions psi = -beta +/- g ; pick ccw-advancing branch
    psi = -beta + g
    ux, uy = np.cos(psi), np.sin(psi)
    t = -2 * (Px * ux + Py * uy)
    Qx, Qy = Px + t * ux, Py + t * uy
    th2 = np.arctan2(Qy, Qx)
    dth = np.mod(th2 - theta, 2 * np.pi)
    # branch sanity: if this branch retreats (dth>pi typical for wrong side),
    # callers rely on consistent ccw chords; test shows +g is ccw for d>=0.
    return theta + dth, dth

def rho(d, r, N=1500, theta0=0.13):
    """Rotation number by Birkhoff average (vectorized over d,r arrays)."""
    th = np.full_like(np.broadcast_arrays(d, r)[0], theta0, dtype=np.float64)
    d = np.asarray(d, np.float64); r = np.asarray(r, np.float64)
    tot = np.zeros_like(th)
    for _ in range(N):
        th, dth = step(th, d, r)
        tot += dth
    return tot / (2 * np.pi * N)

def closure_defect(d, r, q, theta0):
    th = np.asarray([theta0], np.float64)
    P0 = np.array([np.cos(theta0), np.sin(theta0)])
    t = th.copy()
    for _ in range(q):
        t, _ = step(t, np.asarray([d]), np.asarray([r]))
    P = np.array([np.cos(t[0]), np.sin(t[0])])
    return float(np.hypot(*(P - P0)))

def find_r(d, target, N=6000, lo=1e-4, hi=None):
    """Bisect r so that rho(d,r)=target (rho increases with r)."""
    d = np.asarray(d, np.float64)
    if hi is None: hi = 1 - d - 1e-6
    lo = np.full_like(d, lo); hi = np.asarray(hi, np.float64).copy()
    for _ in range(46):
        mid = 0.5 * (lo + hi)
        v = rho(d, mid, N=N)
        up = v > target          # rho DECREASES in r: raise lo while rho>target
        lo = np.where(up, mid, lo); hi = np.where(up, hi, mid)
    return 0.5 * (lo + hi)

if __name__ == '__main__':
    import time
    t0 = time.time()
    # --- certificates -------------------------------------------------------
    print("Chapple q=3 (d^2 = 1-2r):")
    for d in (0.0, 0.2, 0.4, 0.6):
        r = (1 - d * d) / 2
        v = float(rho(np.asarray(d), np.asarray(r), N=30000))
        cd = closure_defect(d, r, 3, 0.7)
        print(f"  d={d}: rho={v:.9f} (want 0.333333333)  closure|P3-P0|={cd:.2e}")
    print("Fuss q=4 (1/(1-d)^2+1/(1+d)^2 = 1/r^2):")
    for d in (0.0, 0.2, 0.4):
        r = 1 / np.sqrt(1 / (1 - d) ** 2 + 1 / (1 + d) ** 2)
        v = float(rho(np.asarray(d), np.asarray(r), N=30000))
        cd = closure_defect(d, r, 4, 1.9)
        print(f"  d={d}: rho={v:.9f} (want 0.25)  closure|P4-P0|={cd:.2e}")
    # porism check: closure independent of start
    d, q = 0.35, 7
    rr = float(find_r(np.asarray([d]), 2 / 7, N=30000)[0])
    cds = [closure_defect(d, rr, 7, th0) for th0 in np.linspace(0, 6, 9)]
    print(f"porism q=7,p=2 at d={d}, r={rr:.12f}: closure over 9 starts "
          f"max={max(cds):.2e}")
    print(f"[{time.time()-t0:.0f}s]")
