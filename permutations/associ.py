import numpy as np

def trees(n):
    if n==0: return [None]
    res=[]
    for k in range(n):
        for L in trees(k):
            for R in trees(n-1-k): res.append((L,R))
    return res

def leaves(T): return 1 if T is None else leaves(T[0])+leaves(T[1])

def loday(T):
    acc=[]
    def rec(t):
        if t is None: return
        L,R=t; rec(L); acc.append(leaves(L)*leaves(R)); rec(R)
    rec(T); return acc

def right_rotations(T):
    """trees obtained by ONE right rotation somewhere (Tamari covers): ((A,B),C)->(A,(B,C))."""
    if T is None: return []
    L,R=T; res=[]
    if L is not None:
        A,B=L; res.append((A,(B,R)))     # right rotation at root
    for nl in right_rotations(L): res.append((nl,R))
    for nr in right_rotations(R): res.append((L,nr))
    return res

def neighbors(T):
    """all trees differing by one rotation (either direction) = associahedron edges."""
    res=set(right_rotations(T))
    # left rotations = inverse: T' such that T in right_rotations(T')
    # simpler: also compute left rotations directly
    def leftrot(t):
        if t is None: return []
        L,R=t; out=[]
        if R is not None:
            B,C=R; out.append(((L,B),C))
        for nl in leftrot(L): out.append((nl,R))
        for nr in leftrot(R): out.append((L,nr))
        return out
    res|=set(leftrot(T))
    return res

def build(n=4):
    T=trees(n); idx={t:i for i,t in enumerate(T)}
    V=np.array([loday(t) for t in T],dtype=float)
    edges=set(); covers=[]
    for t in T:
        for u in neighbors(t):
            a,b=idx[t],idx[u]; edges.add((min(a,b),max(a,b)))
        for u in right_rotations(t):
            covers.append((idx[t],idx[u]))   # Tamari cover t -> u (up)
    return T,idx,V,sorted(edges),covers

if __name__=="__main__":
    for n in [3,4]:
        T,idx,V,edges,covers=build(n)
        nv=len(T); ne=len(edges); F=2-nv+ne
        cat=[1,1,2,5,14,42][n]
        print(f"n={n}: vertices={nv} (Catalan={cat}) edges={ne} faces(Euler)={F}  covers={len(covers)}")
