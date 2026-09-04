"""scan.py — hunt actual zeros of Z(s) up to height T near several lines; stream to zeros_<tag>.txt"""
import sys, time
import numpy as np
from zeta_g import gseq, scan_zeros

T = float(sys.argv[1]); tag = sys.argv[2]
lines = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0.5, 0.8, 0.95]
DT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
T0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
g = gseq(400)
seen = {}
t0 = time.time()
with open(f'zeros_{tag}.txt', 'w') as f:
    # chunked so the file grows live
    step = 5000.0
    a = T0
    while a < T:
        b = min(T, a + step)
        for sig in lines:
            for (x, y) in scan_zeros(sig, b, dt=DT, g=g, thresh=0.15, t0=a):
                key = (round(x, 7), round(y, 7))
                if key not in seen:
                    seen[key] = 1
                    f.write(f'{x:.12f} {y:.12f}\n')
        f.flush()
        print(f'height {b:.0f}: {len(seen)} zeros, max Re = {max(k[0] for k in seen) if seen else 0:.5f}  ({time.time()-t0:.0f}s)')
        sys.stdout.flush()
        a = b
