import numpy as np, pickle, time
import scipy.sparse as spa, scipy.sparse.linalg as sla
import sys
sys.setrecursionlimit(100000)
from chameleon import solve_triangle
M = 2048
t0=time.time()
# extended: also expected wall-clock time E[T] (in units of days, i.e. one meeting/day incl. null meetings)
idx = {}
states = []
for r in range(1, M-1):
    for b in range(1, M-r):
        g = M - r - b
        if g >= 1:
            idx[(r,b)] = len(states)
            states.append((r,b))
n = len(states)
rows=[]; cols=[]; vals=[]
rhsR = np.zeros(n); rhsG = np.zeros(n)
for k,(r,b) in enumerate(states):
    g = M - r - b
    wRB=r*b; wBG=b*g; wGR=g*r; W=wRB+wBG+wGR
    rows.append(k); cols.append(k); vals.append(W)
    if b-1>=1: rows.append(k); cols.append(idx[(r+1,b-1)]); vals.append(-wRB)
    else: rhsG[k]+=wRB
    if g-1>=1: rows.append(k); cols.append(idx[(r,b+1)]); vals.append(-wBG)
    else: rhsR[k]+=wBG
    if r-1>=1: rows.append(k); cols.append(idx[(r-1,b)]); vals.append(-wGR)
A = spa.csc_matrix((vals,(rows,cols)), shape=(n,n))
print("assembled", n, "states", time.time()-t0); t0=time.time()
lu = sla.splu(A)
print("LU done", time.time()-t0); t0=time.time()
PR = lu.solve(rhsR); PG = lu.solve(rhsG)
# E[T_wall]: W*h = C(M,2)*1 + sum w h'   -> A h = C(M,2)*ones
C2 = M*(M-1)/2.0
ET = lu.solve(np.full(n, C2))
print("solves done", time.time()-t0)
# residual check
res = abs(A@PR - rhsR).max()
print("residual PR:", res)
np.savez_compressed('hero2048.npz', M=M, states=np.array(states,np.int32), PR=PR, PG=PG, ET=ET)
print("saved hero2048.npz")
