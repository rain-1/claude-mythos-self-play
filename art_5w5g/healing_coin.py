"""
healing_coin.py — the poster's n=5 near-miss, made exact.

Their structure: coins {1/2, 1/3, 1/3, 1/4, 1/5, 1/5} + one more coin that
WOULD complete a rigid court if its radius were 1/4 — but the court only
closes when that coin shrinks to rho = 0.99991.../4. We reproduce the basin
(seeded from their published picture), maximize rho, read off the active
tangency graph, then solve the closure system in 50-digit arithmetic and
find rho's minimal polynomial with PSLQ. The healing coin is not a coin:
its radius is not 1/n for any integer n.
"""

import numpy as np
from scipy.optimize import minimize
import json

R_FIXED = [1/2, 1/4, 1/5, 1/3, 1/3, None, 1/5]   # None = the healing coin
X0 = np.array([
    [0.21, 0.52],     # A 1/2 top
    [-0.71, 0.27],    # B 1/4 left
    [-0.39, -0.06],   # C 1/5 inner
    [0.12, -0.25],    # D 1/3 center
    [0.70, -0.08],    # E 1/3 right
    [-0.53, -0.50],   # F healing coin (~1/4)
    [-0.18, -0.74],   # G 1/5 bottom
])
IDX_F = 5


def solve_basin():
    N = 7
    z0 = np.concatenate([X0.ravel(), [0.24]])

    def unpack(z):
        return z[:-1].reshape(N, 2), z[-1]

    def radii(rho):
        return np.array([r if r is not None else rho for r in R_FIXED])

    cons = []

    def tray_c(z):
        x, rho = unpack(z)
        r = radii(rho)
        return (1 - r) ** 2 - (x ** 2).sum(1)

    pairs = [(i, j) for i in range(N) for j in range(i + 1, N)]

    def pair_c(z):
        x, rho = unpack(z)
        r = radii(rho)
        return np.array([((x[i] - x[j]) ** 2).sum() - (r[i] + r[j]) ** 2
                         for i, j in pairs])

    res = minimize(lambda z: -z[-1], z0,
                   constraints=[{"type": "ineq", "fun": tray_c},
                                {"type": "ineq", "fun": pair_c}],
                   method="SLSQP", options={"maxiter": 600, "ftol": 1e-15})
    x, rho = unpack(res.x)
    return x, rho


def main():
    x, rho = solve_basin()
    print(f"healing coin rho = {rho:.15f}")
    print(f"4*rho            = {4*rho:.15f}   (poster: 0.99991...)")
    r = np.array([rr if rr is not None else rho for rr in R_FIXED])
    # active contacts
    cts = []
    for i in range(7):
        if abs(np.hypot(*x[i]) - (1 - r[i])) < 1e-7:
            cts.append(("tray", i))
    for i in range(7):
        for j in range(i + 1, 7):
            if abs(np.hypot(*(x[i] - x[j])) - (r[i] + r[j])) < 1e-7:
                cts.append(("pair", i, j))
    print("active contacts:", cts)
    n_unk = 15
    print(f"unknowns 2N+1={n_unk}, constraints={len(cts)} (+1 rotation gauge)")

    # exact solve: mpmath Newton on the square tangency system
    from mpmath import mp, mpf, matrix, norm, sqrt as msqrt, pslq
    mp.dps = 60
    X = matrix([mpf(v) for v in x.ravel()] + [mpf(rho)])

    def F(X):
        xs = [[X[2*i], X[2*i+1]] for i in range(7)]
        rho_ = X[14]
        rr = [mpf(1)/2, mpf(1)/4, mpf(1)/5, mpf(1)/3, mpf(1)/3, rho_, mpf(1)/5]
        eqs = []
        for c in cts:
            if c[0] == "tray":
                i = c[1]
                eqs.append(xs[i][0]**2 + xs[i][1]**2 - (1 - rr[i])**2)
            else:
                _, i, j = c
                eqs.append((xs[i][0]-xs[j][0])**2 + (xs[i][1]-xs[j][1])**2
                           - (rr[i]+rr[j])**2)
        # gauge: fix coin A's angle: x_A * y0 - y_A * x0 = 0 along initial dir
        eqs.append(xs[0][0]*mpf(x[0][1]) - xs[0][1]*mpf(x[0][0]))
        return matrix(eqs)

    def J(X, h=mpf(10)**-20):
        m = len(F(X))
        Jm = matrix(m, 15)
        for k in range(15):
            Xp = matrix(X); Xp[k] += h
            Xm = matrix(X); Xm[k] -= h
            d = (F(Xp) - F(Xm)) / (2*h)
            for i in range(m):
                Jm[i, k] = d[i]
        return Jm

    for it in range(60):
        f = F(X)
        Jm = J(X)
        # least squares via normal equations (m >= 15)
        JT = Jm.T
        dX = (JT * Jm) ** -1 * (JT * f)
        X = X - dX
        if norm(f) < mpf(10)**-52:
            break
    print(f"Newton residual: {float(norm(F(X))):.2e}  iters {it}")
    rho_exact = X[14]
    print(f"rho to 50 digits: {mp.nstr(rho_exact, 50)}")
    print(f"4*rho           : {mp.nstr(4*rho_exact, 50)}")

    # minimal polynomial via PSLQ
    for deg in (2, 3, 4, 5, 6, 8):
        vec = [rho_exact**k for k in range(deg + 1)]
        rel = pslq(vec, maxcoeff=10**12, maxsteps=200000)
        if rel:
            print(f"degree {deg}: minimal polynomial coeffs (asc) = {rel}")
            # verify
            val = sum(c * rho_exact**k for k, c in enumerate(rel))
            print(f"  residual: {float(abs(val)):.2e}")
            break
    json.dump({"rho": float(rho_exact), "four_rho": float(4*rho_exact),
               "contacts": [list(c) for c in cts],
               "minpoly": [int(c) for c in rel] if rel else None,
               "x": x.tolist()},
              open("healing_coin.json", "w"))


if __name__ == "__main__":
    main()
