import numpy as np, pickle, time
from dwell_engine import *
d = pickle.load(open("dwell_data.pkl","rb"))
P, D = d['P'], d['D']
rng = np.random.default_rng(99)
best, bl = d['tour'].copy(), d['L']
n = len(P); t0 = time.time()
k = 0
while time.time() - t0 < 900:
    k += 1
    t = best.copy()
    cuts = np.sort(rng.choice(np.arange(1, n), 3, replace=False))
    a, b, c = cuts
    t = np.concatenate([t[:a], t[b:c], t[a:b], t[c:]])
    t = two_opt(D, t)
    if k % 3 == 0: t = or_opt(D, t); t = two_opt(D, t)
    L = tour_len(D, t)
    if L < bl - 1e-12:
        bl, best = L, t.copy()
        print(f"kick {k}: {bl:.5f}")
d['tour'], d['L'] = best, bl
pickle.dump(d, open("dwell_data.pkl","wb"))
print("final best", bl, "kicks", k)
