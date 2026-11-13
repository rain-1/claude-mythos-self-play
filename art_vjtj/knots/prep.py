"""pick one representative per knot type, fatten it (anneal), choose a view; write crests.json"""
import json, glob, numpy as np
from alex import anneal, thickness, fingerprint, crossings, FP, TABLE, alexander
want = [('3_1', 6), ('4_1', 7), ('5_1', 8), ('5_2', 8), ('6_1', 8), ('6_2', 8), ('6_3', 8), ('8_19', 8), ('3_1#3_1 / 8_20', 8)]
runs = [json.load(open(f)) for f in sorted(glob.glob('census_n*.json'))]
rng = np.random.default_rng(7)
out = []
for name, n in want:
    cands = []; tot = 0; samp = 0; unconf = None; press = None
    for r in runs:
        if r['n'] != n: continue
        for e in r['res']:
            if e['name'] == name:
                cands.append(np.array(e['V']))
                if r['R'] == 0: unconf = (e['count'], r['samples'])
                elif press is None or r['R'] < press[2]: press = (e['count'], r['samples'], r['R'])
        if r['R'] == 0 and unconf is None: unconf = (0, r['samples'])
    if not cands:
        out.append(dict(name=name, n=n, found=False, unconf=unconf)); print(name, 'NOT FOUND'); continue
    best = None
    for V0 in cands:
        for seed in range(3):
            V = V0.copy()
            th = anneal(V, 1500000, seed + 1, 0.3)
            if best is None or th > best[0]: best = (th, V.copy())
    th, V = best
    assert FP[tuple(int(x) for x in fingerprint(V))] == name
    # the full polynomial, in five random projections
    for t in range(5):
        Q, _ = np.linalg.qr(rng.standard_normal((3, 3)))
        co = alexander(V @ Q)
        assert co == TABLE[name] or co == TABLE[name][::-1], (name, co)
    L = np.linalg.norm(np.roll(V, -1, 0) - V, axis=1)
    assert np.allclose(L, 1, atol=1e-9), L
    # view: fewest crossings, then the most open projection
    V = V - V.mean(0)
    bestv = None
    for t in range(6000):
        Q, _ = np.linalg.qr(rng.standard_normal((3, 3)))
        W = V @ Q
        X = crossings(W)
        P = W[:, :2]
        proj = np.linalg.norm(np.roll(P, -1, 0) - P, axis=1).min()
        # crossing points away from stick ends
        m = 1.0
        for row in X:
            m = min(m, row[1], 1 - row[1], row[3], 1 - row[3])
        dv = min(np.linalg.norm(P[i] - P[j]) for i in range(n) for j in range(i))
        score = (-len(X), min(proj, 2.5 * m, dv))
        if bestv is None or score > bestv[0]: bestv = (score, W.copy())
    (sc, W) = bestv
    out.append(dict(name=name, n=n, found=True, thick=float(th), crossings=int(-sc[0]), V=W.tolist(), unconf=unconf, press=press))
    print(name, n, 'thickness %.3f' % th, 'crossings', -sc[0], 'open %.3f' % sc[1], 'unconfined count', unconf, 'pressure', press, 'Alexander', co)
json.dump(out, open('crests.json', 'w'))
