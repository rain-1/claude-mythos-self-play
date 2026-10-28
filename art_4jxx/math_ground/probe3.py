import numpy as np, json, sys, time
from gs import *
C=json.load(open('data/gap_candidates.json'))
J=np.array(C[int(sys.argv[1])]['J'])
perm=[ (t&1) + 2*((t>>2)&1) + 4*((t>>1)&1) + 8*((t>>3)&1) for t in range(16)]
for name,JJ in [('orig',J),('transp',J[perm])]:
  for p in range(int(sys.argv[2]),int(sys.argv[3])):
    t=time.time(); e,col,s=shear_search(JJ,p); print(name,p,e,s,round(time.time()-t,1),flush=True)
