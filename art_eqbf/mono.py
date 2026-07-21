"""Monodromy computation for the governing cubic along complex loops.
Line in the base: L(w) = q* + w*(du, (4/3)dv, dv) with (du,dv) the hero-slice
direction; complex w.  Roots of c T^3 - 2T^2 + bT - 2a continued along loops."""
import numpy as np

DU, DV = 0.55, 1.0   # direction in hero-slice coords (toward upper cusp-ish)

def abc(w):
    return (-0.25 + DU * w, (4.0 / 3.0) * DV * w, DV * w)

def roots_at(w):
    a, b, c = abc(w)
    return np.roots([c, -2.0, b, -2.0 * a])

def disc_w():
    """Discriminant of the cubic as a numpy polynomial in w (for branch pts)."""
    import sympy as sp
    ws = sp.symbols('w')
    a = sp.Rational(-1, 4) + sp.nsimplify(DU) * ws
    b = sp.Rational(4, 3) * sp.nsimplify(DV) * ws
    c = sp.nsimplify(DV) * ws
    D = 18 * a * b * c - 16 * a + b ** 2 - c * b ** 3 - 27 * a ** 2 * c ** 2
    p = sp.Poly(sp.expand(D), ws)
    return np.array([complex(x) for x in p.all_coeffs()])

def continue_loop(center, radius, N=6000):
    """Continue the 3 roots around circle center+radius*e^{i theta}.
    Returns paths (N+1, 3) complex and the permutation sigma with
    paths[-1, i] approx paths[0, sigma[i]]."""
    th = np.linspace(0, 2 * np.pi, N + 1)
    ws = center + radius * np.exp(1j * th)
    t0 = roots_at(ws[0])
    paths = np.empty((N + 1, 3), complex)
    paths[0] = t0
    cur = t0.copy()
    for k in range(1, N + 1):
        r = roots_at(ws[k])
        # greedy nearest matching (3 roots: try all 6 permutations exactly)
        best, bp = None, None
        import itertools
        for perm in itertools.permutations(range(3)):
            d = sum(abs(r[list(perm)][i] - cur[i]) ** 2 for i in range(3))
            if best is None or d < best:
                best, bp = d, perm
        cur = r[list(bp)]
        paths[k] = cur
    # permutation: match end to start
    sigma = [int(np.argmin(np.abs(paths[0] - paths[-1][i]))) for i in range(3)]
    err = max(np.abs(paths[-1][i] - paths[0][sigma[i]]) for i in range(3))
    return paths, tuple(sigma), err

if __name__ == "__main__":
    coef = disc_w()
    bps = np.roots(coef)
    print("branch points in w-plane:")
    for b in sorted(bps, key=lambda z: abs(z)):
        print(f"   {b:.6f}   |w| = {abs(b):.6f}")
    # ring A: small circle around 0 (inside all branch points)
    rA = 0.5 * min(abs(b) for b in bps)
    pA, sA, eA = continue_loop(0, rA)
    print("ring A (around the wall c=0)   radius", round(rA, 4), "perm", sA, "err", f"{eA:.2e}")
    # ring B: small circle around the nearest branch point alone
    b1 = min(bps, key=lambda z: abs(z))
    sep = min(abs(b1 - b2) for b2 in bps if abs(b2 - b1) > 1e-9)
    rB = 0.35 * min(sep, abs(b1))
    pB, sB, eB = continue_loop(b1, rB)
    print("ring B (around one branch pt)  center", np.round(b1, 4), "radius", round(rB, 4), "perm", sB, "err", f"{eB:.2e}")
    # ring C: big circle around everything
    rC = 1.6 * max(abs(b) for b in bps)
    pC, sC, eC = continue_loop(0, rC)
    print("ring C (around all)            radius", round(rC, 4), "perm", sC, "err", f"{eC:.2e}")
