import numpy as np, json, time
from gs import *
rng=np.random.default_rng(5)
bad=0
for trial in range(150):
    k=rng.integers(8,14); al=rng.choice(16,k,replace=False)
    J=np.full(16,1000.0); J[al]=rng.normal(size=k)
    for p in range(1,8):
        e1,g1=strip_opt(J,p); e2,g2,m=strip_opt_sft(J,p)
        if e1<500 and abs(e1-e2)>1e-9: bad+=1; print('BAD',trial,p,e1,e2)
        if e1>=500 and e2<np.inf: bad+=1; print('BAD2',trial,p,e1,e2)
print('bad',bad)
C=json.load(open('data/gap_candidates.json'))
J=np.array(C[-1]['J'])
for p in range(1,17):
    t=time.time(); e,g,m=strip_opt_sft(J,p); print(p,e,None if g is None else g.shape,m,round(time.time()-t,2),flush=True)
print('lp33 sft',lp_bound_sft(J,3,3),'lp34',lp_bound_sft(J,3,4),'lp43',lp_bound_sft(J,4,3))
