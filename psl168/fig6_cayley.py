"""Figure 6 — the Cayley graph of PSL(2,7) (the group itself, 168 nodes).
Generators: a = z->z+1 (order 7) and b = z->-1/z (order 2). The order-7
generator carves the 168 elements into 24 heptagons (the cosets); the order-2
generator is the matching that laces them together — 168 = 24 x 7."""
import numpy as np, sys, math
sys.path.insert(0,'psl168'); sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import p168, figkit
from tdraw import Canvas

def perm_from(a,b,c,d):
    return tuple(p168.mobius(a,b,c,d,x) for x in [0,1,2,3,4,5,6,p168.INF])
def comp(p,q): return tuple(p[q[i]] for i in range(8))   # apply q then p

def build_group():
    A=perm_from(1,1,0,1)          # z -> z+1
    B=perm_from(0,6,1,0)          # z -> -1/z  (-1 = 6 mod 7)
    I=tuple(range(8))
    seen={I}; frontier=[I]
    while frontier:
        nf=[]
        for g in frontier:
            for s in (A,B):
                h=comp(g,s)
                if h not in seen: seen.add(h); nf.append(h)
        frontier=nf
    return list(seen), A, B

def render(W=1600):
    elts,A,B=build_group()
    idx={g:i for i,g in enumerate(elts)}
    N=len(elts)                                   # 168
    # right multiplication
    rA=[idx[comp(g,A)] for g in elts]
    rB=[idx[comp(g,B)] for g in elts]
    # cosets = orbits under right-mult by A  (7-cycles)
    cosets=[]; placed=[False]*N
    for i in range(N):
        if placed[i]: continue
        cyc=[]; j=i
        for _ in range(7):
            cyc.append(j); placed[j]=True; j=rA[j]
        cosets.append(cyc)
    nc=len(cosets)                                # 24
    coset_of=[0]*N
    for ci,cy in enumerate(cosets):
        for n in cy: coset_of[n]=ci
    # order cosets by BFS over B-adjacency so linked heptagons sit near each other
    adj={c:set() for c in range(nc)}
    for n in range(N):
        adj[coset_of[n]].add(coset_of[rB[n]])
    order=[]; seen={0}; q=[0]
    while q:
        c=q.pop(0); order.append(c)
        for d in sorted(adj[c]):
            if d not in seen: seen.add(d); q.append(d)
    for c in range(nc):
        if c not in seen: order.append(c)
    ring_pos={c:k for k,c in enumerate(order)}
    # geometry
    cx=cy=W/2; R0=W*0.40; r0=W*0.052
    pos=[None]*N
    for ci,cy_list in enumerate(cosets):
        k=ring_pos[ci]; ang=2*math.pi*k/nc - math.pi/2
        hx=cx+R0*math.cos(ang); hy=cy+R0*math.sin(ang)
        for t,n in enumerate(cy_list):
            aa=2*math.pi*t/7 - math.pi/2 + ang
            pos[n]=(hx+r0*math.cos(aa), hy+r0*math.sin(aa))
    cv=Canvas(W,bg=(0.012,0.013,0.024))
    GOLD=np.array([1.0,0.78,0.32]); CYAN=np.array([0.4,0.8,1.0])
    drawnB=set()
    # B-edges (matching) first, behind
    for n in range(N):
        m=rB[n]; e=frozenset((n,m))
        if e in drawnB or n==m: continue
        drawnB.add(e)
        cv.line(pos[n],pos[m],CYAN,CYAN,width=1.5,bright=0.16)
    # A-edges (heptagon rims)
    for cyc in cosets:
        for t in range(7):
            cv.line(pos[cyc[t]],pos[cyc[(t+1)%7]],GOLD,GOLD,width=2.2,bright=0.34)
    for n in range(N):
        cv.splat(pos[n],(0.92,0.95,1.0),radius=W*0.0055,bright=1.3)
    return cv.finish(W,bloom=(W*0.0006+0.6,W*0.005),gloss=(0.45,0.28),expo=1.18)

if __name__=="__main__":
    viz=render(1600)
    body=("Here is the entire group, all 168 elements, drawn as a Cayley graph: each dot is one "
          "symmetry, and you move between dots by applying a generator. The two generators are the "
          "translation a: z→z+1 (order 7, gold) and the inversion b: z→−1/z (order 2, cyan). "
          "Because a has order 7, repeatedly applying it traces out a 7-gon, and the 168 elements "
          "fall into exactly 24 such heptagons (168 = 24 × 7) — the 24 cosets, the very same count "
          "as the 24 heptagons tiling the Klein quartic. The cyan involution b is a perfect "
          "matching that laces the heptagons together into one connected, indivisible whole: the "
          "graph cannot be cut into smaller invariant pieces, which is what it means for PSL(2,7) "
          "to be a SIMPLE group. This single object is the Fano plane's symmetries, the Klein "
          "quartic's symmetries, and the projective line's symmetries, all at once.")
    fig=figkit.caption(viz,"FIGURE 6 · THE GROUP ITSELF","The Cayley graph of PSL(2,7) — 24 heptagons, laced",
                       body,accent=(255,200,110))
    figkit.save(fig,"psl168/06_cayley_graph.png")
    print("done",fig.size)
