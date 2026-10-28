import numpy as np, json, time, sys
from gs import *
C=json.load(open('data/gap_candidates.json'))
J=np.array(C[int(sys.argv[1])]['J'])
print('lp33',lp_bound_sft(J,3,3),lp_bound_sft_big(J,3,3))
for (m,n) in [(4,4),(4,5),(5,5),(5,6),(6,6),(6,7),(7,7)]:
    t=time.time(); N=len(valid_windows(J,m,n)); lb=lp_bound_sft_big(J,m,n); print(m,n,N,lb,round(time.time()-t,1),flush=True)
