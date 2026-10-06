import numpy as np
from grin import lens_map, nrm
# ray eq in sigma: x'' = grad(n^2/2), x' = n t
def n2(kind, x):
    r2 = (x*x).sum()
    return {'lune': 2 - r2, 'fish': 4/(1+r2)**2, 'eaton': 2/np.sqrt(r2) - 1}[kind]
def grad(kind, x, h=1e-6):
    g = np.zeros(3)
    for i in range(3):
        e = np.zeros(3); e[i] = h
        g[i] = (n2(kind, x+e) - n2(kind, x-e)) / (4*h)
    return g
rng = np.random.default_rng(1)
for kind in ['lune', 'fish', 'eaton']:
    errs = []
    for trial in range(6):
        P = nrm(rng.standard_normal(3)); d = nrm(rng.standard_normal(3))
        if d @ P > 0: d = -d
        x = P.copy(); p = d.copy() * np.sqrt(n2(kind, P)); h = 2e-4; L = 0
        for it in range(200000):
            # RK4 on (x,p)
            def f(x, p): return p, grad(kind, x)
            k1 = f(x, p); k2 = f(x+h/2*k1[0], p+h/2*k1[1]); k3 = f(x+h/2*k2[0], p+h/2*k2[1]); k4 = f(x+h*k3[0], p+h*k3[1])
            xn = x + h/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); pn = p + h/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
            L += np.linalg.norm(xn - x)
            if (xn*xn).sum() > 1 and it > 10:
                # interpolate
                x, p = xn, pn; break
            x, p = xn, pn
        X, D, Lc = lens_map(kind, P[None], d[None])
        errs.append((np.linalg.norm(X[0]-nrm(x)), np.linalg.norm(D[0]-nrm(p)), abs(Lc[0]-L)))
    print(kind, np.max(errs, 0))
