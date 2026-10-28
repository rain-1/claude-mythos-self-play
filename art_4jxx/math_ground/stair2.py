import numpy as np, json, sys
from fractions import Fraction
from gs import lp_bound_sft_big
C=json.load(open('data/gap_candidates.json'))
J0=np.array([r for r in C if r['pstar']==10 and r['area']==30][0]['J'])
k=int(sys.argv[1]); out=[]
for t in np.linspace(float(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4])):
    J=J0.copy(); J[k]+=t
    val,P,x=lp_bound_sft_big(J,4,4,return_sol=True)
    f=np.zeros(16); tt=((P>>0)&1)+2*((P>>1)&1)+4*((P>>4)&1)+8*((P>>5)&1); np.add.at(f,tt,x)
    den=max(Fraction(v).limit_denominator(200).denominator for v in f)
    print(f"t={t:+.3f} lp44={val:.6f} f15={f[15]:.5f} f11={f[11]:.5f} den={den}",flush=True)
    out.append(dict(t=float(t),lp44=val,f=f.tolist(),den=den))
json.dump(out,open(f'data/stair_lp_k{k}_{sys.argv[2]}_{sys.argv[3]}.json','w'))
