"""Equal circles on the square flat torus R^2/Z^2 (MO 490278)."""
import numpy as np, sys, json
from numba import njit

W = np.sqrt(3.0)
RAW25 = [(0,0,0,0),(40,5,13,-6),(-2,15,39,-18),(85,3,-41,33),(43,13,-15,21),(83,18,-2,15),(1,23,11,9),
 (-41,33,37,-3),(111,-9,1,23),(69,1,27,11),(109,6,40,5),(27,11,53,-1),(-15,21,79,-13),
 (137,-21,43,13),(95,-11,69,1),(13,-6,82,-5),(53,-1,95,-11),(11,9,121,-23),(163,-33,85,3),
 (121,-23,111,-9),(39,-18,124,-15),(79,-13,137,-21),(37,-3,163,-33),(124,-15,83,18),(82,-5,109,6)]
def answer25():
    return np.array([[(a+b*W)/122 % 1, (c+d*W)/122 % 1] for a,b,c,d in RAW25])

@njit(cache=True)
def dists(P):
    n = P.shape[0]; out = np.empty(n*(n-1)//2); k = 0
    for i in range(n):
        for j in range(i+1, n):
            dx = P[i,0]-P[j,0]; dx -= np.round(dx)
            dy = P[i,1]-P[j,1]; dy -= np.round(dy)
            out[k] = np.sqrt(dx*dx+dy*dy); k += 1
    return out

@njit(cache=True)
def relax(P, iters, seed):
    """billiards-style: energy sum (d/r)^-p with growing p, then greedy min-distance ascent"""
    np.random.seed(seed)
    n = P.shape[0]
    P = P.copy()
    step = 0.02
    for it in range(iters):
        p = 8.0 + 120.0 * it / iters
        G = np.zeros_like(P)
        dmin = 9.0
        for i in range(n):
            for j in range(i+1, n):
                dx = P[i,0]-P[j,0]; dx -= np.round(dx)
                dy = P[i,1]-P[j,1]; dy -= np.round(dy)
                d = np.sqrt(dx*dx+dy*dy)
                if d < dmin: dmin = d
        for i in range(n):
            for j in range(i+1, n):
                dx = P[i,0]-P[j,0]; dx -= np.round(dx)
                dy = P[i,1]-P[j,1]; dy -= np.round(dy)
                d = np.sqrt(dx*dx+dy*dy)
                if d < 1.6*dmin:
                    f = (dmin/d)**p / d
                    G[i,0] += f*dx; G[i,1] += f*dy; G[j,0] -= f*dx; G[j,1] -= f*dy
        g = 0.0
        for i in range(n):
            g = max(g, np.sqrt(G[i,0]**2+G[i,1]**2))
        s = step * (1.0 - it/iters) * dmin / (g + 1e-300)
        P += s*G
    return P

def polish(P, rounds=60):
    """SLP: maximise t s.t. linearised d_ij >= t on near-contact pairs"""
    from scipy.optimize import linprog
    n = len(P); P = P.copy()
    tr = 0.01
    best = dists(P).min()
    for r in range(rounds):
        rows = []; rhs = []
        dm = best
        for i in range(n):
            for j in range(i+1, n):
                d = P[i]-P[j]; d -= np.round(d); L = np.hypot(*d)
                if L < dm*1.35:
                    u = d/L
                    row = np.zeros(2*n+1)
                    row[2*i:2*i+2] = -u; row[2*j:2*j+2] = u; row[-1] = 1.0
                    rows.append(row); rhs.append(L)
        c = np.zeros(2*n+1); c[-1] = -1
        bounds = [(-tr, tr)]*(2*n) + [(0, None)]
        bounds[0] = (0,0); bounds[1] = (0,0)
        res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=bounds, method="highs")
        if not res.success: break
        Q = P + res.x[:-1].reshape(n,2)
        dq = dists(Q).min()
        if dq > best + 1e-15:
            P = Q; best = dq
        else:
            tr *= 0.5
            if tr < 1e-13: break
    return P % 1.0, best

if __name__ == "__main__":
    A = answer25(); d = dists(A)
    print("answer25 min dist", d.min(), "claimed", np.sqrt((13-6*W)/61), "contacts", (d < d.min()+1e-9).sum())
    N = int(sys.argv[1]); trials = int(sys.argv[2]); seed0 = int(sys.argv[3])
    rng = np.random.default_rng(seed0)
    best = 0; found = {}
    for t in range(trials):
        P = relax(rng.random((N,2)), 4000, seed0*100000+t)
        P, d = polish(P)
        key = round(d, 9); found[key] = found.get(key, 0) + 1
        if d > best + 1e-12:
            best = d; np.save(f"best_{N}_{seed0}.npy", P); print(t, "new best", repr(d), flush=True)
    print(sorted(found.items(), reverse=True)[:8])
