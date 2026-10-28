import numpy as np, json, time
from gs import *
C=json.load(open('data/gap_candidates.json'))
perm=[ (t&1) + 2*((t>>2)&1) + 4*((t>>1)&1) + 8*((t>>3)&1) for t in range(16)]
out=[]
for i,r in enumerate(C):
    J=np.array(r['J']); t=time.time()
    lb44 = lp_bound_sft_big(J,4,4)
    lb45 = lp_bound_sft_big(J,4,5) if (J<9).sum()<16 else None
    best=(r['estar'],'strip',r['pstar'])
    for name,JJ in [('orig',J),('transp',J[perm])]:
        for p in range(1,22):
            e,col,s=shear_search(JJ,p)
            if e < best[0]-1e-9: best=(e,name,p,s)
    # hard-constraint version of best periodic (forbidden avoided?)
    r.update(lp44=lb44, lp45=lb45, best_shear=best)
    print(i, r['fam'], 'estar', r['estar'], 'lp33', r['lp33'], 'lp44', lb44, 'lp45', lb45, 'best', best, round(time.time()-t,1), flush=True)
    out.append(r)
json.dump(out, open('data/gap_candidates_checked.json','w'))
