import json, sys, numpy as np, time
from gs import strip_opt, lp_bound, period_lattice
C = json.load(open(sys.argv[1]))
out=[]
for r in C:
    J = np.array(r["J"])
    t=time.time()
    e12 = [strip_opt(J, p)[0] for p in range(11, 14)]
    l34 = lp_bound(J, 3, 4); l43 = lp_bound(J, 4, 3)
    l44 = lp_bound(J, 4, 4) if len(sys.argv)>2 else None
    allowed = [t for t in range(16) if J[t] < 9]
    print(r["fam"], "allowed", allowed, "J_allowed", np.round(J[allowed],3).tolist())
    print("  e*(p<=10)", r["estar"], "e11..13", e12, "LP33", r["lp33"], "LP34", l34, "LP43", l43, "LP44", l44, round(time.time()-t,1), flush=True)
    r.update(e11_13=e12, lp34=l34, lp43=l43, lp44=l44); out.append(r)
json.dump(out, open(sys.argv[1].replace('.json','_checked.json'),'w'))
