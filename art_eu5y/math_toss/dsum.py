"""dsum.py n groupsfile : the GENERAL move.  If the corner set S of a stair is a direct sum T (+) U
(every corner is t+u in exactly one way; equivalently P_w = P_T * P_U with 0/1 polynomials) and
(-T) (+) U is again the corner set of a stair w', then w and w' have the same tossprint.
Finds ALL direct-sum decompositions of a stair by the smallest-uncovered-corner rule (the smallest
corner not yet written as t+u must be a new element of T or a new element of U), flips T, and
checks that brute-force tossprint classes are exactly the closures under these flips."""
import sys
def corners(w):
    p=[(0,0)]
    for c in w: p.append((p[-1][0]+(c=='0'), p[-1][1]+(c=='1')))
    return p
def word(pts):
    pts=sorted(pts, key=lambda p:(p[0]+p[1]))
    out=[]
    for a,b in zip(pts,pts[1:]):
        d=(b[0]-a[0], b[1]-a[1])
        if d==(1,0): out.append('0')
        elif d==(0,1): out.append('1')
        else: return None
    return ''.join(out)
def decompositions(w):
    S=corners(w); n=len(S); idx={p:i for i,p in enumerate(S)}; res=[]
    def rec(T,U,cov):
        # smallest uncovered
        i=0
        while i<n and cov[i]: i+=1
        if i==n:
            if len(T)>1 and len(U)>1: res.append((tuple(T),tuple(U)))
            return
        s=S[i]
        for which in (0,1):
            A,B=(T,U) if which==0 else (U,T)
            if n % (len(A)+1) and False: pass
            new=[]; ok=True
            for b in B:
                q=(s[0]+b[0], s[1]+b[1]); j=idx.get(q)
                if j is None or cov[j] or j in new: ok=False; break
                new.append(j)
            if not ok: continue
            if n % 1: continue
            for j in new: cov[j]=True
            A.append(s)
            if n % len(A)==0 or True: rec(T,U,cov)
            A.pop()
            for j in new: cov[j]=False
    cov=[False]*n; cov[0]=True
    rec([(0,0)],[(0,0)],cov)
    return res
def neighbours(w):
    out={w[::-1]}
    for T,U in decompositions(w):
        if len(S_:=T)*len(U)!=len(w)+1: continue
        pts=[(u[0]-t[0], u[1]-t[1]) for t in T for u in U]
        m=(min(p[0] for p in pts), min(p[1] for p in pts))
        v=word([(p[0]-m[0], p[1]-m[1]) for p in pts])
        if v is not None and len(v)==len(w): out.add(v)
    return out
def closure(w):
    seen={w}; st=[w]
    while st:
        u=st.pop()
        for v in neighbours(u):
            if v not in seen: seen.add(v); st.append(v)
    return seen
if __name__=='__main__':
    n=int(sys.argv[1]); bad=0; tot=0
    for line in open(sys.argv[2]):
        G=line.split(); tot+=1
        full=set(G)|set(g[::-1] for g in G)
        if closure(G[0])!=full:
            bad+=1
            if bad<4: print('NOT EXPLAINED', sorted(full))
    print(f'n={n}: {tot} nontrivial tossprint classes, {bad} not explained by direct-sum flips')
