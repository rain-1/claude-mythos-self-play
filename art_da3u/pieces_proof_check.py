"""Check of the proof that E[pieces] = e/pi + 1/2 + B(e), with 0 <= B(e) = O(1/e).
S = {y in [-1,1] : 0 <= y/sin(M+e y) <= 1}  (rows where the needle is seen; R = 1).
Pieces = 1 + A+ + A-  (hub component + the components of S+ and S- that do not touch y = 0)."""
import numpy as np
def pieces_grid(e, M, n):
    y = np.linspace(-1, 1, n); s = np.sin(M + e*y)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = y/s
    ok = (r >= 0) & (r <= 1); ok[n//2] = True
    return int(np.sum(ok[1:] & ~ok[:-1]) + ok[0])
def pieces_formula(e, M):
    """count from the proof: peaks + boundary humps, decided exactly (per hump, maximise the concave h)."""
    tot = 1
    for MM in (M, -M):                       # S+ with phase M, S- is S+ with phase -M
        th0, th1 = MM, MM + e
        m0 = int(np.floor(th0/(2*np.pi))) - 1
        for m in range(m0, m0 + int(e/(2*np.pi)) + 4):
            a, b = 2*np.pi*m, 2*np.pi*m + np.pi          # positive hump in theta
            lo, hi = max(a, th0), min(b, th1)
            if lo >= hi: continue
            if a <= th0 <= b and np.sin(th0) > 0: continue   # the hump touching y = 0 joins the hub piece
            # h(theta) = sin(theta) - (theta - th0)/e is concave on the hump: maximise on [lo, hi]
            t = np.clip(np.arccos(1/e) + a, lo, hi) if e > 1 else lo
            cand = [lo, hi, t]
            if max(np.sin(x) - (x - th0)/e for x in cand) >= 0: tot += 1
    return tot
rng = np.random.default_rng(5)
for e in (3.0, 7.0, 20.0, 40.0, 80.0):
    Ms = rng.uniform(0, 2*np.pi, 200000)
    f = np.array([pieces_formula(e, M) for M in Ms])
    g = np.array([pieces_grid(e, M, 200001) for M in Ms[:300]])
    agree = np.mean(g == f[:300])
    print(f'e={e:5.1f}  E[pieces]={f.mean():.4f} +- {f.std()/np.sqrt(len(f)):.4f}   e/pi+1/2={e/np.pi+0.5:.4f}   '
          f'B(e)={f.mean()-e/np.pi-0.5:+.4f}   e*B={e*(f.mean()-e/np.pi-0.5):+.3f}   grid agrees on {agree:.3f}')
