"""CHSH correlation-plane certificates.
S  = E11+E12+E21-E22,  S' = E11-E12+E21+E22  (minus moved).
Claims to verify numerically:
  local deterministic -> 16 strategies, projections, classical bound |S|<=2
  singlet + planar measurements -> reach = disc S^2+S'^2 <= 8 (Tsirelson circle)
  no-signaling polytope -> projected hull
  Horodecki criterion on random states."""
import numpy as np
rng = np.random.default_rng(58)

# ---- local deterministic strategies ----
pts = set()
for a1 in (-1,1):
 for a2 in (-1,1):
  for b1 in (-1,1):
   for b2 in (-1,1):
    E = np.array([[a1*b1, a1*b2],[a2*b1, a2*b2]])
    S  = E[0,0]+E[0,1]+E[1,0]-E[1,1]
    Sp = E[0,0]-E[0,1]+E[1,0]+E[1,1]
    pts.add((S,Sp))
print("local deterministic (S,S') points:", sorted(pts))

# ---- singlet reach ----
def SSp(a1,a2,b1,b2):
    c = lambda u,v: -np.cos(u-v)
    E11,E12,E21,E22 = c(a1,b1),c(a1,b2),c(a2,b1),c(a2,b2)
    return E11+E12+E21-E22, E11-E12+E21+E22
# max of alpha*S+beta*S' over angles, for many directions -> boundary radius
best = []
for th in np.linspace(0, 2*np.pi, 73):
    al, be = np.cos(th), np.sin(th)
    # random restarts + local refine
    A = rng.uniform(0,2*np.pi,(4000,4))
    v = al*SSp(*A.T)[0] + be*SSp(*A.T)[1]
    x = A[np.argmax(v)]
    from scipy.optimize import minimize
    f = lambda x: -(al*SSp(*x)[0]+be*SSp(*x)[1])
    r = minimize(f, x, method='Nelder-Mead', options=dict(xatol=1e-10,fatol=1e-12))
    best.append(-r.fun)
best = np.array(best)
print("singlet boundary radius: min %.6f max %.6f  (2*sqrt2 = %.6f)" % (best.min(), best.max(), 2*np.sqrt(2)))

# ---- no-signaling polytope projection ----
# NS behaviors for 2 inputs/2 outputs: 8 PR-box variants + 16 local vertices.
# PR boxes: E_ij = (-1)^{mu i + nu j + sigma} except one cell sign-flipped... use standard:
# PR^{mu nu sig}: p(ab|xy) = 1/2 if a xor b = xy xor (mu x) xor (nu y) xor sig
ns_pts = set()
for mu in (0,1):
 for nu in (0,1):
  for sig in (0,1):
    E = np.zeros((2,2))
    for x in (0,1):
     for y in (0,1):
        # E = p(a=b) - p(a!=b) = +1 if forced equal, -1 if forced unequal
        E[x,y] = 1 - 2*((x*y ^ (mu*x) ^ (nu*y) ^ sig) & 1)
    S  = E[0,0]+E[0,1]+E[1,0]-E[1,1]
    Sp = E[0,0]-E[0,1]+E[1,0]+E[1,1]
    ns_pts.add((S,Sp))
print("PR-box (S,S') points:", sorted(ns_pts))

# ---- Horodecki criterion sanity on random two-qubit pure states ----
# S_max(rho) = 2 sqrt(t1+t2), t = two largest eigenvalues of T^T T
def horodecki(psi):
    # psi: 4-vector; T_ij = <sigma_i x sigma_j>
    sx = np.array([[0,1],[1,0]]); sy = np.array([[0,-1j],[1j,0]]); sz = np.diag([1,-1])
    P = [sx,sy,sz]
    rho = np.outer(psi, psi.conj())
    T = np.array([[np.real(np.trace(rho @ np.kron(P[i],P[j]))) for j in range(3)] for i in range(3)])
    ev = np.sort(np.linalg.eigvalsh(T.T@T))[::-1]
    return 2*np.sqrt(ev[0]+ev[1])
psi_singlet = np.array([0,1,-1,0])/np.sqrt(2)
print("Horodecki S_max(singlet) = %.9f" % horodecki(psi_singlet))
psi_prod = np.kron([1,0],[0,1]).astype(float)
print("Horodecki S_max(product) = %.9f" % horodecki(psi_prod))
# random pure states: S_max distribution range
mx = 0
for _ in range(2000):
    v = rng.normal(size=4)+1j*rng.normal(size=4); v/=np.linalg.norm(v)
    mx = max(mx, horodecki(v))
print("max S_max over 2000 random pure states = %.6f (<= 2.828427)" % mx)
