import numpy as np,geom,sys
seed=int(sys.argv[1]); rng=np.random.default_rng(seed)
def S(x):
    P=x[:9].reshape(3,3); a=np.sort(x[9:12]); b=np.sort(x[12:15])
    s,nu=geom.score(P,a,b)
    if nu!=18: return -9
    lines,A,B,C=geom.config(P,a,b)
    c=np.array([v[:2]/(1+v[2]) for v in C.values()])
    dc=min(np.linalg.norm(c[i]-c[j]) for i in range(3) for j in range(i+1,3))
    return s-1.0*max(0,0.5-dc)
best=(-9,None)
for it in range(10000):
    x=rng.normal(size=15); s=S(x)
    if s>best[0]: best=(s,x)
s0,x=best
for it in range(15000):
    y=x+rng.normal(size=15)*0.06*(1-it/15000); s=S(y)
    if s>s0: s0,x=s,y
print(seed,s0); np.save(f'Y{seed}.npy',x)
