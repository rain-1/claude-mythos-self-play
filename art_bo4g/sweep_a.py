"""sweep the squeeze a: does the dumbbell pinch (surgery) or round off and die as one sphere?"""
import sys, json, time
import numpy as np
from ricci import run_flow
out = {}
for a in [float(x) for x in sys.argv[1:]]:
    t0 = time.time()
    rec, cert = run_flow(a=a, N=600, verbose=False, record_dt=0.01)
    ev = cert['events']
    kinds = [e[0] for e in ev]
    out[a] = dict(events=ev, pinch=('surgery' in kinds), time=time.time() - t0)
    print(a, 'PINCH' if 'surgery' in kinds else 'no pinch', ev, '%.0f s' % (time.time() - t0), flush=True)
json.dump(out, open('cache/sweep_%s.json' % sys.argv[1], 'w'), indent=1, default=float)
