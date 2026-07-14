"""Exact Steffen flexible-polyhedron flex + topology (self-contained).

Anchor coords + flex rule from Alexandrov & Volokitin, arXiv:2508.02392:
  v1=(0,-17/2, sqrt166/2)  v2=(0,17/2, sqrt166/2)
  v3=(-11/2,0,0)  v4=(11/2,0,0)  v9=(0,0,-3 sqrt31/2)
Flex: v1..v4 FIXED; v9(t)=R_x(t) v9 rides the circle gamma; v5..v8 re-trilaterated
each t from three anchors (root chosen by continuity).  All 21 edge lengths stay
constant; the enclosed volume stays constant (Sabitov's Bellows theorem).

Exposes: config(t, prev), EDGES (21), FACES (14, consistently oriented),
         volume(V), elens(V).
"""
import numpy as np, itertools
from collections import defaultdict

s166=np.sqrt(166.0); s31=np.sqrt(31.0)

def anchors_at(t):
    V1=np.array([0.0,-8.5,s166/2]); V2=np.array([0.0,8.5,s166/2])
    V3=np.array([-5.5,0,0]); V4=np.array([5.5,0,0])
    r=3*s31/2; c,sn=np.cos(t),np.sin(t)
    V9=np.array([0.0, r*sn, -r*c])            # oriented angle t about +x on gamma
    return {1:V1,2:V2,3:V3,4:V4,9:V9}

STRUCT={5:[(1,10),(3,5),(9,12)],6:[(1,10),(4,5),(9,12)],
        7:[(2,10),(3,5),(9,12)],8:[(2,10),(4,5),(9,12)]}
approx={5:np.array([-1.98248,0.834943,3.45397]),6:np.array([6.89559,-4.79631,0.218428]),
        7:np.array([-6.89559,4.79631,0.218428]),8:np.array([1.98248,-0.834943,3.45397])}

def trilaterate(P1,P2,P3,r1,r2,r3):
    ex=(P2-P1); ex=ex/np.linalg.norm(ex)
    i=np.dot(ex,P3-P1); temp=(P3-P1)-i*ex; ey=temp/np.linalg.norm(temp)
    ez=np.cross(ex,ey); d=np.linalg.norm(P2-P1); j=np.dot(ey,P3-P1)
    x=(r1*r1-r2*r2+d*d)/(2*d); y=(r1*r1-r3*r3+i*i+j*j)/(2*j)-i/j*x
    z2=r1*r1-x*x-y*y
    if z2<-1e-9: return None
    z=np.sqrt(max(z2,0.0)); base=P1+x*ex+y*ey
    return base+z*ez, base-z*ez

def moving_at(t, prev=None):
    A=anchors_at(t); out={}
    for j,lst in STRUCT.items():
        (k1,r1),(k2,r2),(k3,r3)=lst
        sol=trilaterate(A[k1],A[k2],A[k3],r1,r2,r3)
        ref=prev[j] if prev is not None else approx[j]
        out[j]=min([sol[0],sol[1]],key=lambda c:np.linalg.norm(c-ref))
    return out

def config(t,prev=None):
    A=anchors_at(t); M=moving_at(t,prev); V=np.zeros((9,3))
    for k,p in A.items(): V[k-1]=p
    for k,p in M.items(): V[k-1]=p
    return V

# ---- topology, derived once from the rest configuration ---------------------
def _topology():
    V0=config(0.0); EDGELEN={5,10,11,12,17}; edges=[]
    for a in range(9):
        for b in range(a+1,9):
            d=np.linalg.norm(V0[a]-V0[b])
            if any(abs(d-L)<1e-6 for L in EDGELEN) and (a,b)!=(2,3):  # v3-v4 is a coincidence, not an edge
                edges.append((a,b))
    E=set(edges); adj={i:set() for i in range(9)}
    for a,b in E: adj[a].add(b); adj[b].add(a)
    tris=[t for t in itertools.combinations(range(9),3)
          if t[1] in adj[t[0]] and t[2] in adj[t[0]] and t[2] in adj[t[1]]]
    def eof(t): a,b,c=t; return [tuple(sorted(x)) for x in [(a,b),(b,c),(a,c)]]
    ce=defaultdict(list)
    for i,t in enumerate(tris):
        for e in eof(t): ce[e].append(i)
    tris_e=[set(eof(t)) for t in tris]
    def solve(sel,cnt):
        for e in E:
            if cnt[e]<2:
                for i in ce[e]:
                    if i in sel: continue
                    if any(cnt[ee]+1>2 for ee in tris_e[i]): continue
                    sel.add(i)
                    for ee in tris_e[i]: cnt[ee]+=1
                    r=solve(sel,cnt)
                    if r: return r
                    sel.discard(i)
                    for ee in tris_e[i]: cnt[ee]-=1
                return None
        return set(sel)
    faces=[tris[i] for i in solve(set(),{e:0 for e in E})]
    return sorted(E), faces

def _orient(faces):
    faces=[list(f) for f in faces]; e2f=defaultdict(list)
    for i,f in enumerate(faces):
        for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]: e2f[frozenset((a,b))].append(i)
    orient=[None]*len(faces); orient[0]=tuple(faces[0]); seen={0}; stack=[0]
    de=lambda f:[(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]
    while stack:
        i=stack.pop()
        for (a,b) in de(orient[i]):
            for j in e2f[frozenset((a,b))]:
                if j==i or j in seen: continue
                fj=faces[j]
                for rot in range(3):
                    g=fj[rot:]+fj[:rot]
                    if (b,a) in de(g): orient[j]=tuple(g); break
                    if (a,b) in de(g): orient[j]=(g[0],g[2],g[1]); break
                seen.add(j); stack.append(j)
    return orient

EDGES, _FACES0 = _topology()
FACES = _orient(_FACES0)

def volume(V):
    return sum(np.dot(V[a],np.cross(V[b],V[c]))/6.0 for a,b,c in FACES)
def elens(V):
    return np.array([np.linalg.norm(V[a]-V[b]) for a,b in EDGES])
