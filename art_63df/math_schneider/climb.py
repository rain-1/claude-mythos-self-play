"""Continue hill-climbing from the best points of search2 (n = 2): can the line be crossed?"""
import sys, json, glob, time, numpy as np
from convex_union import a_seq
n = 2; which = int(sys.argv[1]); secs = float(sys.argv[2])
R = []
for f in glob.glob("s2_n2_s*.jsonl"): R += [json.loads(l) for l in open(f)]
R.sort(key=lambda r: -r["J"]); r = R[which]
T = np.array(r["T"]); tl = np.array(r["tl"]); tr = np.array(r["tr"]); I = [np.array(s) for s in r["I"]]
rng = np.random.default_rng(100 + which); t0 = time.time()
def pieces(T, tl, tr, I):
    N = len(T); P = []
    for i in range(N):
        A, B = T[i], T[(i+1) % N]
        if tl[i] + tr[i] >= 1: P.append(np.array([A, B]))
        else:
            if tl[i] > 1e-9: P.append(np.array([A, A + tl[i]*(B-A)]))
            else: P.append(A[None])
            if tr[i] > 1e-9: P.append(np.array([B, B + tr[i]*(A-B)]))
    return P + list(I)
def ev(*par):
    try: a, _ = a_seq(pieces(*par), 3, res=150, ncand=6, iters=18)
    except Exception: return None
    return a
obj = lambda a: 5*a[1] - 2 - 4*a[2]
a = ev(T, tl, tr, I); J = obj(a); sig = 0.05
print("start", J, a, flush=True)
while time.time() - t0 < secs:
    T2, tl2, tr2, I2 = T.copy(), tl.copy(), tr.copy(), [s.copy() for s in I]
    u = rng.random(); N = len(T)
    if u < 0.35: i = rng.integers(N); tl2[i] = np.clip(tl2[i] + rng.normal(scale=sig), 0, 0.6)
    elif u < 0.7: i = rng.integers(N); tr2[i] = np.clip(tr2[i] + rng.normal(scale=sig), 0, 0.6)
    elif u < 0.9 or not I2: i = rng.integers(N); T2[i] += rng.normal(scale=sig*0.5, size=2)
    else: i = rng.integers(len(I2)); I2[i] = I2[i] + rng.normal(scale=sig*0.5, size=I2[i].shape)
    b = ev(T2, tl2, tr2, I2)
    if b is None: continue
    if obj(b) > J + 1e-10:
        T, tl, tr, I, a, J = T2, tl2, tr2, I2, b, obj(b)
        print(round(J, 6), np.round(a, 5), "tl", np.round(tl, 3), "tr", np.round(tr, 3), flush=True)
        json.dump(dict(J=J, a=list(map(float, a)), T=T.tolist(), tl=tl.tolist(), tr=tr.tolist(), I=[s.tolist() for s in I]), open(f"climb_{which}.json", "w"))
    else: sig = max(sig*0.99, 0.002)
