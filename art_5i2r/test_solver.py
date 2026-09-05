import numpy as np, time
from cpack_rect import *
from scipy.optimize import root
region = Leaf(); h = 0.025
mesh = hex_mesh(region, h)
corners, rc, ex = corners_by_harmonic_measure(region, mesh, (0.30,0.20,0.30))
faces, bd = mesh['faces'], mesh['boundary']; V = len(bd)
cm = np.zeros(V, bool); cm[corners] = True
target = np.where(bd, np.pi, 2*np.pi); target[cm] = np.pi/2
C = np.concatenate([faces[:, [0,1,2]], faces[:, [1,2,0]], faces[:, [2,0,1]]]); cv, cu, cw = C[:,0], C[:,1], C[:,2]
v0 = int(np.where(~bd)[0][0])
def theta(x):
    r = np.exp(x); return np.bincount(cv, eangles(r[cv], r[cu], r[cw]), minlength=V)
def F(x):
    f = theta(x) - target; f[v0] = x[v0]; return f
t0 = time.time()
x = np.zeros(V)
for rnd in range(6):
    sol = root(F, x, method='krylov', options=dict(fatol=1e-11, maxiter=300, disp=False, jac_options=dict(method='lgmres', inner_maxiter=100, outer_k=10)))
    x = sol.x; err = np.abs(F(x)).max()
    print(f'round {rnd} success={sol.success} nit={sol.nit} err={err:.2e} {time.time()-t0:.1f}s', flush=True)
    if err < 1e-10: break
