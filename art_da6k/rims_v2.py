import json, numpy as np
from cloud import rims_fast
sig = [0.6, 0.7, 0.8, 0.9054, 0.95, 1.0, 1.0086, 1.02, 1.05, 1.10, 1.20, 1.30, 1.50, 1.60, 2.00]
R = rims_fast(sig, ndirs=240, N=120, starts=8, iters=900, seed=3)
json.dump({str(k): [[p.real, p.imag] for p in v] for k, v in R.items()}, open('rims_v2.json', 'w'))
