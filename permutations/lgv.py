import numpy as np
from math import comb
from itertools import permutations

def lgv_determinant_check():
    """LGV: # non-intersecting families of up/right paths from sources to sinks = det[ paths(A_i->B_j) ].
       Sources A_i=(0, a_i), sinks B_j=(W, b_j); single up/right path count = C(W + (b-a), W) style.
       Verify det == brute-force count of non-intersecting families for a small case."""
    # sources a=[0,1,2] sinks b=[2,3,4]; grid up/right steps, path A_i->B_j count = C(dx+dy, dx)
    A=[0,1,2]; B=[2,3,4]; W=3
    def npaths(a,b):
        dx=W; dy=b-a
        if dy<0: return 0
        return comb(dx+dy,dx)
    M=np.array([[npaths(a,b) for b in B] for a in A])
    det=round(np.linalg.det(M))
    # brute force: count families of 3 monotone paths (each a sequence of unit E/N steps) A_i->B_i
    # represent a path A_i->B_i as a lattice monotone path; enumerate, check non-intersecting (vertex-disjoint)
    def all_paths(a,b):
        dx=W; dy=b-a
        if dy<0: return []
        # sequences of dx E and dy N
        from itertools import combinations
        res=[]
        for Npos in combinations(range(dx+dy),dy):
            x=0;y=a;cells=[(0,a)]
            s=set(Npos)
            for t in range(dx+dy):
                if t in s: y+=1
                else: x+=1
                cells.append((x,y))
            res.append(cells)
        return res
    P=[all_paths(A[i],B[i]) for i in range(3)]
    cnt=0
    for p0 in P[0]:
        s0=set(p0)
        for p1 in P[1]:
            s1=set(p1)
            if s0&s1: continue
            for p2 in P[2]:
                if (s0|s1)&set(p2): continue
                cnt+=1
    return det, cnt

if __name__=="__main__":
    det,cnt=lgv_determinant_check()
    print(f"LGV: det(M)={det}  brute-force non-intersecting families={cnt}  match={det==cnt}")
