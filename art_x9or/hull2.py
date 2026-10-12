import numpy as np
from hullrun import run
print('disc', [np.round(run(1, 1, 0, R, m=30), 4).tolist() for R in (1e4, 1e5)], flush=True)
for th in (0.0, 0.3, 1.1):
    print('4:1 th', th, [np.round(run(1, 0.25, th, R, m=30), 4).tolist() for R in (1e4, 1e5)], flush=True)
print('2:1 th 0 R=1e6', np.round(run(1, 0.5, 0, 1e6, m=12), 4).tolist(), flush=True)
print('2:1 th .6 R=1e6', np.round(run(1, 0.5, 0.618, 1e6, m=12), 4).tolist(), flush=True)
