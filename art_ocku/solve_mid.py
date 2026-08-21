import numpy as np, time, sys
import scipy.sparse as spa, scipy.sparse.linalg as sla
def solve_full(M, save=None):
    idx={}; states=[]
    for r in range(1,M-1):
        for b in range(1,M-r):
            g=M-r-b
            if g>=1: idx[(r,b)]=len(states); states.append((r,b))
    n=len(states); rows=[];cols=[];vals=[]
    rhsR=np.zeros(n); rhsG=np.zeros(n)
    for k,(r,b) in enumerate(states):
        g=M-r-b; wRB=r*b; wBG=b*g; wGR=g*r; W=wRB+wBG+wGR
        rows.append(k);cols.append(k);vals.append(W)
        if b-1>=1: rows.append(k);cols.append(idx[(r+1,b-1)]);vals.append(-wRB)
        else: rhsG[k]+=wRB
        if g-1>=1: rows.append(k);cols.append(idx[(r,b+1)]);vals.append(-wBG)
        else: rhsR[k]+=wBG
        if r-1>=1: rows.append(k);cols.append(idx[(r-1,b)]);vals.append(-wGR)
    A=spa.csc_matrix((vals,(rows,cols)),shape=(n,n))
    lu=sla.splu(A)
    PR=lu.solve(rhsR); PG=lu.solve(rhsG)
    ET=lu.solve(np.full(n, M*(M-1)/2.0))
    PB=1-PR-PG
    mag=np.sqrt((PR-1/3)**2+(PG-1/3)**2+(PB-1/3)**2)
    print(f"M={M}: min mag {mag.min():.3e}  (n={n})")
    if save:
        np.savez_compressed(save, M=M, states=np.array(states,np.int32), PR=PR, PG=PG, ET=ET)
    return mag.min()
for M,sv in [(512,'field512.npz'), (640,'field640.npz'), (768,'field768.npz')]:
    solve_full(M, sv)
