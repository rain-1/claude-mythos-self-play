"""cylopt.py m trials — m cylinders of radius r touching a unit ball, disjoint interiors; maximise r.
Axis j: passes through (1+r) s_j, direction u_j perpendicular to s_j.  Need dist(axis_i, axis_j) >= 2r.
Parametrise s by a 3-vector (normalised), u by an angle in the tangent plane."""
import sys, numpy as np
from scipy.optimize import minimize

def frame(s):
    s = s / np.linalg.norm(s)
    a = np.array([1.0, 0, 0]) if abs(s[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(s, a); e1 /= np.linalg.norm(e1)
    return s, e1, np.cross(s, e1)

def axes(x, m):
    r = x[-1]; P = []; U = []
    for j in range(m):
        s, e1, e2 = frame(x[4 * j:4 * j + 3]); th = x[4 * j + 3]
        P.append((1 + r) * s); U.append(np.cos(th) * e1 + np.sin(th) * e2)
    return np.array(P), np.array(U), r

def linedist(p1, u1, p2, u2):
    n = np.cross(u1, u2); nn = np.linalg.norm(n)
    if nn < 1e-9:
        w = p2 - p1; return np.linalg.norm(w - (w @ u1) * u1)
    return abs((p2 - p1) @ n) / nn

def cons(x, m):
    P, U, r = axes(x, m)
    return np.array([linedist(P[i], U[i], P[j], U[j]) - 2 * r for i in range(m) for j in range(i + 1, m)])

def run(m, trials, seed=0):
    rng = np.random.default_rng(seed); best = (0, None)
    for t in range(trials):
        x0 = np.concatenate([np.concatenate([rng.standard_normal(3), [rng.uniform(0, np.pi)]]) for _ in range(m)] + [[0.3]])
        res = minimize(lambda x: -x[-1], x0, constraints=[{'type': 'ineq', 'fun': cons, 'args': (m,)}],
                       bounds=[(None, None)] * (4 * m) + [(0.05, 3)], method='SLSQP', options=dict(maxiter=600, ftol=1e-12))
        if res.success and cons(res.x, m).min() > -1e-8 and res.x[-1] > best[0]:
            best = (res.x[-1], res.x)
    return best

if __name__ == '__main__':
    m, trials = int(sys.argv[1]), int(sys.argv[2])
    r, x = run(m, trials, int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    print('m', m, 'best r %.9f' % r)
    np.save(f'data/cyl{m}.npy', x)
    P, U, _ = axes(x, m)
    for p, u in zip(P, U): print(np.round(p, 5), np.round(u, 5))
