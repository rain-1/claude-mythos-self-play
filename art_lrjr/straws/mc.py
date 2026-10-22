import numpy as np, sys
from scipy.spatial import ConvexHull
from knot import determinant, ham_cycles
rng=np.random.default_rng(int(sys.argv[1])); M=int(sys.argv[2])
cyc=ham_cycles(); reg=0; tref_in_reg=[]; hits=0; trials=0
rot=np.linalg.qr(rng.standard_normal((3,3)))[0]
for it in range(M):
    P=rng.standard_normal((6,3)); P/=np.linalg.norm(P,axis=1)[:,None]
    h=ConvexHull(P); deg=np.zeros(6,int)
    E=set()
    for s in h.simplices:
        for a in range(3):
            e=tuple(sorted((s[a],s[(a+1)%3]))); E.add(e)
    for a,b in E: deg[a]+=1; deg[b]+=1
    regular = all(deg==4)
    # random ordering (the question's random knot)
    trials+=1
    if regular:
        reg+=1
        if it<300:
            t=sum(determinant(P[list(c)],rot)==3 for c in cyc); tref_in_reg.append(t)
        d=determinant(P,rot); hits+=(d==3)
print('P(regular)=',reg/trials,'vs 15/(4pi^2)=',15/(4*np.pi**2))
print('trefoils per regular octahedron:',set(tref_in_reg))
print('P(trefoil)=',hits/trials,'vs 1/(16pi^2)=',1/(16*np.pi**2))
