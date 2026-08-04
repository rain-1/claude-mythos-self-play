"""MO 137177: maximize B_n = sum_{i<j} |PiPj|^2 over convex polygons with unit sides.
Parametrize by exterior angles theta_i>0, sum=2pi; closure sum e^{i phi_j}=0.
B = n * sum |P_i - centroid|^2."""
import numpy as np
from scipy.optimize import minimize
rng = np.random.default_rng(7)

def verts(theta):
    phi = np.cumsum(theta) - theta[0]          # phi_0 = 0
    e = np.stack([np.cos(phi), np.sin(phi)], 1)
    P = np.vstack([[0,0], np.cumsum(e,0)])[:-1]
    return P, e

def B(theta):
    P,_ = verts(theta)
    c = P.mean(0)
    return len(theta)*((P-c)**2).sum()

def negB(theta): return -B(theta)

def cons(n):
    return [
      {'type':'eq','fun': lambda t: t.sum()-2*np.pi},
      {'type':'eq','fun': lambda t: np.cos(np.cumsum(t)-t[0]).sum()},
      {'type':'eq','fun': lambda t: np.sin(np.cumsum(t)-t[0]).sum()},
    ]

results = {}
for n in range(4, 17):
    reg = np.full(n, 2*np.pi/n)
    Breg = B(reg)
    best = None
    for trial in range(40):
        t0 = reg + (0.6 if trial else 0.0)*rng.standard_normal(n)*2*np.pi/n
        t0 = np.abs(t0); t0 *= 2*np.pi/t0.sum()
        r = minimize(negB, t0, constraints=cons(n), bounds=[(1e-9, 2*np.pi)]*n,
                     method='SLSQP', options={'maxiter':800,'ftol':1e-14})
        if r.success and (best is None or -r.fun > best[0]):
            best = (-r.fun, r.x.copy())
    Bopt, topt = best
    dev = np.abs(topt - 2*np.pi/n).max()
    results[n] = (Breg, Bopt, dev)
    print(f"n={n:2d}  B_regular={Breg:.10f}  B_opt={Bopt:.10f}  excess={Bopt-Breg:+.2e}  max|theta-reg|={dev:.3e}")
