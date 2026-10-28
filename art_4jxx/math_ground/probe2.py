import numpy as np, json, sys
from fractions import Fraction
from gs import *
C=json.load(open('data/gap_candidates.json'))
J=np.array(C[int(sys.argv[1])]['J'])
val,P,x=lp_bound_sft_big(J,4,4,return_sol=True)
f=np.zeros(16)
t=((P>>0)&1)+2*((P>>1)&1)+4*((P>>4)&1)+8*((P>>5)&1)
np.add.at(f,t,x)
print(val, np.round(f,6).tolist())
print([str(Fraction(v).limit_denominator(60)) for v in f])
print('allowed',[i for i in range(16) if J[i]<9])
perm=[ (t&1) + 2*((t>>2)&1) + 4*((t>>1)&1) + 8*((t>>3)&1) for t in range(16)]
Jt=J[perm]
for p in range(1,int(sys.argv[2])):
    e,g,m=strip_opt_sft(Jt,p); print('T',p,e,None if g is None else g.shape,flush=True)
