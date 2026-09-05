"""doyle.py — Doyle spirals: hexagonal circle packings of the punctured plane that are the discrete
exponential map.  Circles: centre a^m b^n, radius k |a^m b^n|.  Tangency of hex neighbours:
   |a-1| = k(1+|a|),  |b-1| = k(1+|b|),  |a-b| = k(|a|+|b|),
and the (p,q) closure  p log a + q log b = 2 pi i  (so the lattice of log-centres contains 2 pi i:
the spiral has p arms one way, q the other).  5 real unknowns, 5 real equations.
Certificate: exact tangencies + NO overlaps among all circle pairs in a large annulus.
"""
import numpy as np, json, sys
from scipy.optimize import fsolve


def solve(p, q, seed=0, tries=200):
    rng = np.random.default_rng(seed)
    def F(x):
        al = x[0] + 1j * x[1]; be = x[2] + 1j * x[3]; k = x[4]
        a, b = np.exp(al), np.exp(be)
        cl = p * al + q * be - 2j * np.pi
        return [abs(a - 1) - k * (1 + abs(a)), abs(b - 1) - k * (1 + abs(b)), abs(a - b) - k * (abs(a) + abs(b)),
                cl.real, cl.imag]
    best = None
    for t in range(tries):
        x0 = np.array([rng.uniform(-0.6, 0.6), rng.uniform(-1.2, 1.2), rng.uniform(-0.6, 0.6), rng.uniform(-1.2, 1.2), rng.uniform(0.05, 0.6)])
        x, info, ier, msg = fsolve(F, x0, full_output=True, xtol=1e-14)
        if ier != 1 or not (0 < x[4] < 0.95):
            continue
        res = np.abs(F(x)).max()
        if res > 1e-11:
            continue
        a, b = np.exp(x[0] + 1j * x[1]), np.exp(x[2] + 1j * x[3])
        # non-degenerate: |a| != 1 or |b| != 1 and a != b
        if abs(a - b) < 1e-8 or abs(abs(a) - 1) + abs(abs(b) - 1) < 1e-8:
            continue
        cand = dict(a=a, b=b, k=float(x[4]), res=float(res))
        if not overlaps(cand):
            return cand
        best = best or cand
    return best


def circles(sol, rmin=1e-3, rmax=1.0, mrange=60):
    a, b, k = sol['a'], sol['b'], sol['k']
    la, lb = np.log(a), np.log(b)
    M, N = np.meshgrid(np.arange(-mrange, mrange + 1), np.arange(-mrange, mrange + 1), indexing='ij')
    M = M.ravel(); N = N.ravel()
    lz = M * la + N * lb
    z = np.exp(lz)
    keep = (np.abs(z) > rmin) & (np.abs(z) < rmax)
    z, M, N = z[keep], M[keep], N[keep]
    # dedupe (a^p b^q = 1 identifies lattice points)
    key = np.round(z.real, 9) + 1j * np.round(z.imag, 9)
    _, ui = np.unique(key, return_index=True)
    z, M, N = z[ui], M[ui], N[ui]
    return z, k * np.abs(z), M, N


def overlaps(sol, tol=1e-9):
    z, R, M, N = circles(sol, 0.02, 1.0, 40)
    from scipy.spatial import cKDTree
    pts = np.c_[z.real, z.imag]
    tree = cKDTree(pts)
    pairs = tree.query_pairs(2 * R.max())
    for i, j in pairs:
        d = abs(z[i] - z[j])
        if d < R[i] + R[j] - tol * (R[i] + R[j]):
            return True
    return False


def certify(sol):
    z, R, M, N = circles(sol, 0.02, 1.0, 40)
    from scipy.spatial import cKDTree
    pts = np.c_[z.real, z.imag]
    tree = cKDTree(pts)
    pairs = np.array(list(tree.query_pairs(2 * R.max())))
    d = np.abs(z[pairs[:, 0]] - z[pairs[:, 1]]); s = R[pairs[:, 0]] + R[pairs[:, 1]]
    gap = (d - s) / s
    tang = np.abs(gap) < 1e-9
    return dict(n_circles=int(len(z)), min_gap_rel=float(gap.min()), n_tangent_pairs=int(tang.sum()),
                mean_tangencies_per_circle=float(2 * tang.sum() / len(z)),
                a=[sol['a'].real, sol['a'].imag], b=[sol['b'].real, sol['b'].imag], k=sol['k'], res=sol['res'])


if __name__ == '__main__':
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    q = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    sol = solve(p, q)
    print(p, q, sol)
    if sol:
        print(json.dumps(certify(sol), indent=1))
