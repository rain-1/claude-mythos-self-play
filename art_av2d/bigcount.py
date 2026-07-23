"""Independently verify Vejdemo-Johansson's incomplete-open counts for ALL Platonic solids.

Method:
  N_conn (connected edge-subgraphs, exact) via the exponential formula in the
  subset-convolution algebra over vertex supports: g = log f, where
  f(S) = 2^{e(S)}  (all subgraphs on support-contained-in S).
  Computed mod p = 2^31-1 (final counts < p, so exact).
  Planar connected subsets: bounded enumeration (planarity = affine rank <= 2).
  Classes up to rotation: Burnside; Fix(identity) = N_conn - planar - full;
  Fix(g!=e) by direct enumeration over unions of g's edge-orbits.
"""
import numpy as np
from itertools import combinations

P = (1<<31)-1

def popcount_arr(a):
    # numpy >=2 has bitwise_count
    return np.bitwise_count(a) if hasattr(np,'bitwise_count') else np.vectorize(lambda x: bin(x).count('1'))(a)

def connected_count(nv, edges):
    """number of nonempty connected edge-subgraphs, mod P (exact if < P)"""
    NE = len(edges)
    full = 1<<nv
    # e[S]: edges inside S
    adjmask = [0]*nv
    for a,b in edges:
        adjmask[a] |= 1<<b; adjmask[b] |= 1<<a
    e = np.zeros(full, dtype=np.int64)
    S = np.arange(full, dtype=np.int64)
    low = (S & -S)
    lowbit = np.zeros(full, dtype=np.int64)
    lowbit[1:] = np.round(np.log2(low[1:])).astype(np.int64)
    rest = S & (S-1)
    adj = np.array(adjmask, dtype=np.int64)
    # sequential DP but vectorizable in index order chunks? rest[S] < S so plain loop over python is 1M — use numpy trick:
    # process in increasing S; gather e[rest] requires e already filled for smaller idx.
    # do it in pure numpy via sorting? simplest: iterate over bits instead:
    # e(S) = sum over edges (both endpoints in S) — direct: for each edge, add 1 to all S containing both bits.
    # That's 30 * (full/4) additions via broadcasting on reshaped views.
    ee = np.zeros(full, dtype=np.int64)
    v = ee.reshape([2]*nv)
    for a,b in edges:
        idx = [slice(None)]*nv
        idx[nv-1-a] = 1; idx[nv-1-b] = 1
        v[tuple(idx)] += 1
    e = ee
    f = np.array([pow(2,int(x),P) for x in range(int(e.max())+1)], dtype=np.int64)[e]
    pc = popcount_arr(S).astype(np.int64)
    # ranked slices, zeta transform along each bit axis
    R = nv+1
    F = np.zeros((R, full), dtype=np.int64)
    F[pc, S] = f
    for r in range(R):
        vr = F[r].reshape([2]*nv)
        for ax in range(nv):
            sl1 = [slice(None)]*nv; sl0 = [slice(None)]*nv
            sl1[ax] = 1; sl0[ax] = 0
            vr[tuple(sl1)] += vr[tuple(sl0)]
            vr[tuple(sl1)] %= P
    # per-S log series: l_r via r*l_r = r*p_r - sum_{j=1}^{r-1} j*l_j*p_{r-j}, p_0 = 1 (rank-0 slice = f(empty)=1)
    assert int(F[0].min())==1 and int(F[0].max())==1
    L = np.zeros((R, full), dtype=np.int64)
    inv = [0]+[pow(k, P-2, P) for k in range(1,R)]
    for r in range(1, R):
        acc = (r * F[r]) % P
        for j in range(1, r):
            acc = (acc - j * ((L[j]*F[r-j]) % P)) % P
        L[r] = (acc * inv[r]) % P
    # Moebius invert each rank slice
    for r in range(R):
        vr = L[r].reshape([2]*nv)
        for ax in range(nv):
            sl1 = [slice(None)]*nv; sl0 = [slice(None)]*nv
            sl1[ax] = 1; sl0[ax] = 0
            vr[tuple(sl1)] -= vr[tuple(sl0)]
            vr[tuple(sl1)] %= P
    g = L[pc, S] % P
    return int(g.sum() % P)

def planar_connected_count(V, edges, kmax=7):
    """enumerate connected subsets with <= kmax edges; count planar ones; assert none at kmax"""
    V = np.array(V, float)
    NE = len(edges)
    cnt = 0
    maxk_planar = 0
    # grow connected subsets via BFS on subsets (canonical: enumerate combinations, filter connected) — NE choose k
    for k in range(1, kmax+1):
        for comb in combinations(range(NE), k):
            es = [edges[i] for i in comb]
            # connectivity
            parent = {}
            def find(x):
                while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
                return x
            for a,b in es:
                parent.setdefault(a,a); parent.setdefault(b,b)
                ra,rb=find(a),find(b)
                if ra!=rb: parent[ra]=rb
            if len({find(x) for x in parent})!=1: continue
            vs = sorted({v for e2 in es for v in e2})
            Pm = V[vs]-V[vs].mean(0)
            if np.linalg.matrix_rank(Pm, tol=1e-8) <= 2:
                cnt += 1
                maxk_planar = max(maxk_planar, k)
    assert maxk_planar < kmax, f"planar subset found at kmax={kmax}; raise bound"
    return cnt

def burnside(V, edges, vperms, N_conn, N_planar, name, expected):
    NE = len(edges)
    EIDX = {e:i for i,e in enumerate(edges)}
    V = np.array(V,float)
    def connected_mask(mask):
        es=[edges[i] for i in range(NE) if mask>>i&1]
        if not es: return False
        parent={}
        def find(x):
            while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
            return x
        for a,b in es:
            parent.setdefault(a,a); parent.setdefault(b,b)
            ra,rb=find(a),find(b)
            if ra!=rb: parent[ra]=rb
        return len({find(x) for x in parent})==1
    def nonplanar_mask(mask):
        vs=sorted({v for i in range(NE) if mask>>i&1 for v in edges[i]})
        if len(vs)<4: return False
        Pm=V[vs]-V[vs].mean(0)
        return np.linalg.matrix_rank(Pm,tol=1e-8)==3
    FULL = (1<<NE)-1
    total = 0
    for vp in vperms:
        ep = [EIDX[(min(vp[a],vp[b]),max(vp[a],vp[b]))] for a,b in edges]
        if all(ep[i]==i for i in range(NE)):
            fix = N_conn - N_planar - 1   # nonempty connected, minus planar-connected, minus full set
        else:
            # edge orbits of ep
            seen=[False]*NE; orbits=[]
            for i in range(NE):
                if seen[i]: continue
                o=[]; j=i
                while not seen[j]:
                    seen[j]=True; o.append(j); j=ep[j]
                orbits.append(o)
            fix=0
            for u in range(1, 1<<len(orbits)):
                mask=0
                for oi in range(len(orbits)):
                    if u>>oi&1:
                        for i2 in orbits[oi]: mask |= 1<<i2
                if mask==FULL: continue
                if connected_mask(mask) and nonplanar_mask(mask): fix+=1
        total += fix
    classes = total // len(vperms)
    print(f"{name}: N_conn={N_conn}  planar={N_planar}  |G|={len(vperms)}  classes={classes}  expected={expected}  {'OK' if classes==expected else 'MISMATCH'}")
    return classes

if __name__ == "__main__":
    from platonic import TET_V, TET_E, OCT_V, OCT_E, rot_group_from_verts
    # cube
    CUBE_V = [(x,y,z) for x in (0,1) for y in (0,1) for z in (0,1)]
    CUBE_E = [(i,j) for i in range(8) for j in range(i+1,8)
              if sum(abs(CUBE_V[i][k]-CUBE_V[j][k]) for k in range(3))==1]
    for V,E,name,exp_ in [(TET_V,TET_E,'tetrahedron',6), (CUBE_V,CUBE_E,'cube',122), (OCT_V,OCT_E,'octahedron',185)]:
        V = list(np.array(V,float) - np.array(V,float).mean(0))
        nv=len(V)
        vperms = rot_group_from_verts(V,E)
        nc = connected_count(nv, E)
        pl = planar_connected_count(V,E,kmax=7)
        burnside(V,E,vperms,nc,pl,name,exp_)
