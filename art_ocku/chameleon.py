#!/usr/bin/env python3
"""MO 514406: chameleon cyclic dynamics.

States (r,b,g), r+b+g = M.  Effective transitions (ignoring null meetings):
  (r,b,g) -> (r+1,b-1,g)  weight r*b   (red eats blue)
  (r,b,g) -> (r,b+1,g-1)  weight b*g   (blue eats green)
  (r,b,g) -> (r-1,b,g+1)  weight g*r   (green eats red)
Absorbing verdicts: b=0 -> green wins eventually (G eats R); g=0 -> red wins;
r=0 -> blue wins.  (Once a color is extinct the cyclic chase is deterministic
in outcome.)  P_X(state) = probability X is the last color standing.

Solve the linear system exactly on the open triangle {r,b,g >= 1}.
Unknowns indexed by (r,b), g = M-r-b.
"""
import numpy as np
import scipy.sparse as spa
import scipy.sparse.linalg as sla
import sys, time

def solve_triangle(M, dtype=np.float64):
    """Return dict with P_R, P_G (P_B = 1-P_R-P_G) on interior states."""
    # index map for interior states r>=1,b>=1,g>=1
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
        wRB = r*b; wBG = b*g; wGR = g*r
        W = wRB + wBG + wGR
        rows.append(k); cols.append(k); vals.append(W)
        # -> (r+1, b-1, g): red eats blue.  If b-1==0: green wins (P_R += 0, P_G += w)
        if b-1 >= 1:
            rows.append(k); cols.append(idx[(r+1,b-1)]); vals.append(-wRB)
        else:
            rhsG[k] += wRB          # blue extinct -> green eventually wins
        # -> (r, b+1, g-1): blue eats green.  If g-1==0: red wins
        if g-1 >= 1:
            rows.append(k); cols.append(idx[(r,b+1)]); vals.append(-wBG)
        else:
            rhsR[k] += wBG          # green extinct -> red wins
        # -> (r-1, b, g+1): green eats red.  If r-1==0: blue wins
        if r-1 >= 1:
            rows.append(k); cols.append(idx[(r-1,b)]); vals.append(-wGR)
        # else: blue wins; contributes to neither rhsR nor rhsG
    A = spa.csc_matrix((vals,(rows,cols)), shape=(n,n), dtype=dtype)
    lu = sla.splu(A)
    PR = lu.solve(rhsR)
    PG = lu.solve(rhsG)
    return states, idx, PR, PG

def corner_values(M):
    t0=time.time()
    states, idx, PR, PG = solve_triangle(M)
    k = idx[(1,1)]   # (r,b,g) = (1,1,M-2): N = M-2 greens
    N = M-2
    return N, PR[k], PG[k], time.time()-t0

if __name__ == "__main__":
    Ms = [int(x) for x in sys.argv[1:]] or [52, 102, 202, 402, 802, 1202, 1602, 2002]
    print("N  N*P_R  N*P_G  N*(1-P_B)  [targets 1.2091995762, 0.9940125006, 2.2032120767]")
    for M in Ms:
        N, pr, pg, el = corner_values(M)
        pb = 1 - pr - pg
        print(f"{N:6d}  {N*pr:.10f}  {N*pg:.10f}  {N*(1-pb):.10f}   ({el:.1f}s)")
        sys.stdout.flush()
