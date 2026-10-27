import numpy as np,geom,sys
seed=int(sys.argv[1]); rng=np.random.default_rng(seed)
def S(x):
    P=x[:9].reshape(3,3); a=np.sort(x[9:12]); b=np.sort(x[12:15])
    s,nu=geom.score(P,a,b); return s if nu==18 else -9
best=(-9,None)
for it in range(8000):
    x=rng.normal(size=15); s=S(x)
    if s>best[0]: best=(s,x)
s0,x=best
for it in range(12000):
    y=x+rng.normal(size=15)*0.06*(1-it/12000); s=S(y)
    if s>s0: s0,x=s,y
print(seed,s0); np.save(f'X{seed}.npy',x)
