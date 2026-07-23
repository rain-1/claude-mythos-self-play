"""Incomplete open Platonic solids — general enumeration (verify preprint counts)."""
import numpy as np
from itertools import permutations

def rot_group_from_verts(V, EDGES):
    """all orthogonal matrices (det+1) permuting the vertex set -> edge perms"""
    V = np.array(V, float)
    n = len(V)
    # candidate rotations: map an orthonormal frame; brute force over vertex images is heavy.
    # Instead: generate all 3x3 signed permutation matrices AND general rotations via
    # matching: use pairs of adjacent vertices to build candidate maps.
    # Simpler robust approach: find all rotations R with R@V.T a permutation of V.T,
    # searching over maps of one vertex + one neighbor + one second neighbor.
    from numpy.linalg import det, norm
    Vt = {tuple(np.round(v,6)) for v in V}
    adj = {i:set() for i in range(n)}
    for a,b in EDGES: adj[a].add(b); adj[b].add(a)
    perms = set()
    v0 = 0; n1 = min(adj[v0]); n2 = min(adj[n1]-{v0})
    B = np.array([V[v0],V[n1],V[n2]]).T   # 3x3 (assume nondegenerate)
    if abs(det(B))<1e-9:
        n2 = max(adj[n1]-{v0}); B = np.array([V[v0],V[n1],V[n2]]).T
    Binv = np.linalg.inv(B)
    for i in range(n):
        for j in adj[i]:
            for k in adj[j]:
                if k==i: continue
                C = np.array([V[i],V[j],V[k]]).T
                R = C @ Binv
                if norm(R@R.T-np.eye(3))>1e-6: continue
                if det(R)<0: continue
                W = (R@V.T).T
                pm = []
                ok = True
                for v in W:
                    key = tuple(np.round(v,6))
                    # find index
                    d = norm(V-v, axis=1)
                    m = d.argmin()
                    if d[m]>1e-6: ok=False; break
                    pm.append(m)
                if ok and len(set(pm))==n:
                    perms.add(tuple(pm))
    return sorted(perms)

def edge_perms(vperms, EDGES):
    EIDX = {e:i for i,e in enumerate(EDGES)}
    eps = []
    for vp in vperms:
        ep = []
        for (a,b) in EDGES:
            x,y = vp[a],vp[b]
            ep.append(EIDX[(min(x,y),max(x,y))])
        eps.append(ep)
    return eps

def enumerate_incomplete(V, EDGES, name):
    NE = len(EDGES)
    vperms = rot_group_from_verts(V, EDGES)
    eps = edge_perms(vperms, EDGES)
    print(f"{name}: |rot group| = {len(vperms)}")
    V = np.array(V, float)
    def connected(mask):
        es = [EDGES[e] for e in range(NE) if mask>>e&1]
        if not es: return False
        parent = {}
        def find(x):
            while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
            return x
        for a,b in es:
            parent.setdefault(a,a); parent.setdefault(b,b)
            ra,rb = find(a),find(b)
            if ra!=rb: parent[ra]=rb
        return len({find(x) for x in parent})==1
    def nonplanar(mask):
        vs = sorted({v for e in range(NE) if mask>>e&1 for v in EDGES[e]})
        if len(vs)<4: return False
        P = V[vs] - V[vs].mean(0)
        return np.linalg.matrix_rank(P, tol=1e-8)==3
    def canon(mask):
        best = mask
        for ep in eps:
            m=0
            for e in range(NE):
                if mask>>e&1: m |= 1<<ep[e]
            if m<best: best=m
        return best
    classes = set()
    FULLM = (1<<NE)-1
    for m in range(1, FULLM):
        if not nonplanar(m): continue
        if not connected(m): continue
        classes.add(canon(m))
    from collections import Counter
    cnt = Counter(bin(r).count('1') for r in classes)
    print(f"{name}: incomplete open count = {len(classes)}  by k: {dict(sorted(cnt.items()))}")
    return sorted(classes), vperms

TET_V = [(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)]
TET_E = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
OCT_V = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
OCT_E = [(a,b) for a in range(6) for b in range(a+1,6)
         if abs(np.dot(OCT_V[a],OCT_V[b]))<0.5]
if __name__=="__main__":
    import json
    tet, tperm = enumerate_incomplete(TET_V, TET_E, "tetrahedron")   # expect 6
    octa, operm = enumerate_incomplete(OCT_V, OCT_E, "octahedron")   # expect 185
    json.dump({'tet':tet,'oct':octa}, open('platonic.json','w'))
