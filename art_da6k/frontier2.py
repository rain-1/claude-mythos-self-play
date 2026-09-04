"""frontier2.py — precise zero frontier: leftmost reach of the value set, N terms, batched ascent."""
import numpy as np, json, sys
from math import log, pi
from zeta_g import gseq, torus_setup
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
g = gseq(N); primes, V = torus_setup(N, g); lg = np.array([log(x) for x in g[:N]])
rng = np.random.default_rng(0); P = V.shape[1]
res = {}
for sigma in [0.990, 1.000, 1.005, 1.010, 1.015, 1.020]:
    r = np.exp(-sigma * lg)
    B = 40
    th = np.mod(np.pi + rng.normal(0, 0.8, (B, P)), 2 * pi); th[0] = np.pi
    th[:, :3] = np.pi + rng.normal(0, 0.1, (B, 3))
    lr = 0.1; m1 = np.zeros_like(th); m2 = np.zeros_like(th)
    for it in range(1200):
        e = np.exp(-1j * (th @ V.T)); z = e @ r
        dz = -1j * (e * r[None, :]) @ V
        grad = -(dz.real)                      # maximise -Re z  == minimise Re z
        m1 = 0.9 * m1 + 0.1 * grad; m2 = 0.99 * m2 + 0.01 * grad ** 2
        th += lr * m1 / (np.sqrt(m2) + 1e-9)
        if it in (700, 1000): lr *= 0.3
    e = np.exp(-1j * (th @ V.T)); z = e @ r
    k = np.argmin(z.real)
    res[sigma] = (float(z.real[k]), float(z.imag[k]))
    world = {str(p): round(float(np.mod(th[k, i], 2*pi)), 3) for i, p in enumerate(primes[:10])}
    print(f'sigma={sigma:.3f}  leftmost Re = {z.real[k]:+.5f} (Im {z.imag[k]:+.4f})  world {world}'); sys.stdout.flush()
# interpolate the crossing
sg = sorted(res); vals = [res[s][0] for s in sg]
for i in range(len(sg) - 1):
    if vals[i] < 0 <= vals[i + 1]:
        s_star = sg[i] - vals[i] * (sg[i + 1] - sg[i]) / (vals[i + 1] - vals[i])
        print(f'sigma* (linear interpolation) = {s_star:.5f}')
        res['sigma_star'] = s_star
json.dump(dict(N=N, primes=len(primes), res={str(k): v for k, v in res.items()}), open(f'frontier2_N{N}.json', 'w'), indent=1)
