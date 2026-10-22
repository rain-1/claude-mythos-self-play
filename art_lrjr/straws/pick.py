import numpy as np, itertools, json
from scipy.spatial import ConvexHull
def segdist(p1,q1,p2,q2):
    # min distance between segments (sampled fine enough + exact-ish)
    best=1e9
    for s in np.linspace(0,1,41):
        a=p1+s*(q1-p1); d=q2-p2; t=np.clip(np.dot(a-p2,d)/np.dot(d,d),0,1)
        best=min(best,np.linalg.norm(a-(p2+t*d)))
    return best
rng=np.random.default_rng(5); best=(0,None)
for it in range(4000):
    P=rng.standard_normal((6,3)); P/=np.linalg.norm(P,axis=1)[:,None]
    h=ConvexHull(P); deg=np.zeros(6,int); E=set()
    for s in h.simplices:
        for a in range(3): E.add(tuple(sorted((s[a],s[(a+1)%3]))))
    for a,b in E: deg[a]+=1; deg[b]+=1
    if not all(deg==4): continue
    # min vertex separation too
    vs=min(np.linalg.norm(P[i]-P[j]) for i,j in itertools.combinations(range(6),2))
    m=1e9
    for (a,b),(c,d) in itertools.combinations(itertools.combinations(range(6),2),2):
        if len({a,b,c,d})<4: continue
        m=min(m,segdist(P[a],P[b],P[c],P[d]))
    sc=min(m,vs/4)
    if sc>best[0]: best=(sc,P.copy(),m,vs)
print(best[0],best[2],best[3]); json.dump(best[1].tolist(),open('octa.json','w'))
