"""
Provenance for 01_the_corner.py — how sofa_path.npy was produced.
==================================================================
We do NOT hard-code Gerver's sofa. We define the sofa as the intersection of a
width-1 L-corridor over all rotations theta in [0, pi/2], parametrised by the
path of the corridor's inner corner c(theta), and MAXIMISE the intersection's
area by coordinate ascent. By the arm-swap symmetry the sofa is symmetric about
the y-axis, so we only free the path on [0, pi/4] and mirror it (cx -> -cx).

Two passes: a coarse search (13 control points, 300^2 grid) then a refinement
(25 control points, 520^2 grid) reaching area ~2.172 — within 2% of Gerver's
proven optimum 2.2195... The result is saved as sofa_path.npy (shape (2, nc)).
Runtime ~5 min total. Re-run only to regenerate the motion.
"""
import numpy as np

def in_L(u, v):                       # fixed width-1 L, inner corner at (1,1)
    return (((v >= 0)&(v <= 1)&(u <= 1)) | ((u >= 0)&(u <= 1)&(v <= 1)))

def build_grid(N, xr, yr):
    xs = np.linspace(*xr, N); ys = np.linspace(*yr, int(N*(yr[1]-yr[0])/(xr[1]-xr[0])))
    X, Y = np.meshgrid(xs, ys)
    return X, Y, (xs[1]-xs[0])*(ys[1]-ys[0])

def optimise(nc, X, Y, cell, nt=160, init=None, iters=600, step0=0.06):
    ctrl_t = np.linspace(0, np.pi/4, nc)
    thetas = np.linspace(0, np.pi/2, nt); CT = np.cos(-thetas); ST = np.sin(-thetas)
    def expand(cxh, cyh):
        cx = np.zeros(nt); cy = np.zeros(nt)
        for i, th in enumerate(thetas):
            if th <= np.pi/4:
                cx[i] = np.interp(th, ctrl_t, cxh); cy[i] = np.interp(th, ctrl_t, cyh)
            else:
                tm = np.pi/2-th
                cx[i] = -np.interp(tm, ctrl_t, cxh); cy[i] = np.interp(tm, ctrl_t, cyh)
        return cx, cy
    def area(cxh, cyh):
        cx, cy = expand(cxh, cyh); inside = np.ones(X.shape, bool)
        for i in range(nt):
            dx = X-cx[i]; dy = Y-cy[i]
            u = CT[i]*dx-ST[i]*dy+1.0; v = ST[i]*dx+CT[i]*dy+1.0
            inside &= in_L(u, v)
        return inside.sum()*abs(cell)
    if init is None:
        cxh = np.linspace(1.0, 0.0, nc); cyh = np.full(nc, 1.0)
    else:
        cxh, cyh = init
    best = area(cxh, cyh); step = step0
    for _ in range(iters):
        improved = False
        for k in range(nc):
            for arr in (cxh, cyh):
                for s in (step, -step):
                    old = arr[k]; arr[k] = old+s; A = area(cxh, cyh)
                    if A > best+1e-6:
                        best = A; improved = True
                    else:
                        arr[k] = old
        if not improved:
            step *= 0.6
            if step < 0.004:
                break
    return cxh, cyh, best

if __name__ == "__main__":
    X, Y, cell = build_grid(300, (-3.0, 3.0), (-1.4, 1.4))
    cxh, cyh, a = optimise(13, X, Y, cell, nt=120, step0=0.25)
    print("coarse area", round(a, 4))
    t0 = np.linspace(0, np.pi/4, 13); t1 = np.linspace(0, np.pi/4, 25)
    init = (np.interp(t1, t0, cxh), np.interp(t1, t0, cyh))
    X, Y, cell = build_grid(520, (-2.8, 2.8), (-1.3, 1.55))
    cxh, cyh, a = optimise(25, X, Y, cell, nt=200, init=init)
    print("refined area", round(a, 5), "(Gerver optimum 2.2195)")
    np.save("sofa_path.npy", np.stack([cxh, cyh]))
    print("saved sofa_path.npy")
