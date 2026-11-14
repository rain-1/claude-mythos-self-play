"""Structured search for violations of the simplex-family line
       (n+2) a_{n+1} >= (n+3) a_n - 2        (d = 2)
among sets  M = (pieces of the boundary of a convex polygon) + (interior segments/points)."""
import sys, json, time, numpy as np
from convex_union import a_seq
seed = int(sys.argv[1]); n = int(sys.argv[2]); secs = float(sys.argv[3])
rng = np.random.default_rng(seed); t0 = time.time()
log = open(f"s2_n{n}_s{seed}.jsonl", "a")

def pieces(par):
    T, tl, tr, I = par
    N = len(T); P = []
    for i in range(N):
        A, B = T[i], T[(i+1) % N]
        if tl[i] + tr[i] >= 1: P.append(np.array([A, B]))
        else:
            P.append(np.array([A, A + tl[i]*(B-A)])); P.append(np.array([B, B + tr[i]*(A-B)]))
    for s in I: P.append(s)
    return P

def ev(par):
    try: a, _ = a_seq(pieces(par), n + 1, res=80, ncand=4, iters=14)
    except Exception: return None
    return a

def obj(a): return (n+3)*a[n-1] - 2 - (n+2)*a[n]

best = -9
while time.time() - t0 < secs:
    N = int(rng.integers(3, 6))
    th = np.sort(rng.uniform(0, 2*np.pi, N)) if rng.random() < 0.5 else np.linspace(0, 2*np.pi, N+1)[:-1]
    T = np.stack([np.cos(th), np.sin(th)], 1)
    if np.linalg.matrix_rank(T[1:]-T[0]) < 2: continue
    tl = rng.uniform(0, 0.6, N); tr = rng.uniform(0, 0.6, N)
    k = int(rng.integers(0, 3))
    I = [T.mean(0) + rng.normal(scale=0.25, size=(int(rng.integers(1, 3)), 2)) for _ in range(k)]
    par = (T, tl, tr, I); a = ev(par)
    if a is None: continue
    J = obj(a); sig = 0.1
    for it in range(50):
        T2, tl2, tr2, I2 = T.copy(), tl.copy(), tr.copy(), [s.copy() for s in I]
        r = rng.random()
        if r < 0.45: i = rng.integers(N); tl2[i] = np.clip(tl2[i] + rng.normal(scale=sig), 0, 0.6)
        elif r < 0.9: i = rng.integers(N); tr2[i] = np.clip(tr2[i] + rng.normal(scale=sig), 0, 0.6)
        elif I2: i = rng.integers(len(I2)); I2[i] = I2[i] + rng.normal(scale=sig*0.5, size=I2[i].shape)
        b = ev((T2, tl2, tr2, I2))
        if b is None: continue
        Jb = obj(b)
        if Jb > J + 1e-9: T, tl, tr, I, a, J = T2, tl2, tr2, I2, b, Jb
        else: sig = max(sig*0.98, 0.004)
        if time.time() - t0 > secs: break
    log.write(json.dumps(dict(J=float(J), a=[float(x) for x in a], T=T.tolist(), tl=tl.tolist(), tr=tr.tolist(), I=[s.tolist() for s in I])) + "\n"); log.flush()
