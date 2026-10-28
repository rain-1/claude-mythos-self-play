"""1-parameter family J(t) = J0 + t*D through the period-21 example: track optimal shear-slope s/p and LP certification."""
import numpy as np, json, sys
from gs import shear_search, lp_bound_sft_big, strip_opt_sft
C=json.load(open('data/gap_candidates.json'))
J0=np.array([r for r in C if r['pstar']==10 and r['area']==30][0]['J'])
k=int(sys.argv[1]); PM=int(sys.argv[2])
res=[]
for t in np.linspace(float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])):
    J=J0.copy(); J[k]+=t
    best=(1e9,None,None)
    for p in range(1,PM+1):
        e,col,s=shear_search(J,p)
        if e<best[0]-1e-10: best=(e,p,s)
    lb=lp_bound_sft_big(J,4,4)
    gap=best[0]-lb
    print(f"t={t:+.4f} e={best[0]:.6f} p={best[1]} s={best[2]} lp44={lb:.6f} gap={gap:.2e}",flush=True)
    res.append(dict(t=float(t),e=best[0],p=best[1],s=best[2],lp44=lb,gap=gap))
json.dump(res,open(f'data/staircase_k{k}.json','w'))
