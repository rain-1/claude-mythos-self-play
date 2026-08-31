import numpy as np
D = np.load("lorenz_orbits.npz", allow_pickle=True)
words = [str(w) for w in D["words"]]
NO = len(words)
paths = [D[f"path_{i}"] for i in range(NO)]

def basis(v):
    v = v / np.linalg.norm(v)
    e1 = np.cross(v, [0, 0, 1.0]); e1 /= np.linalg.norm(e1)
    return e1, np.cross(v, e1), v

def linking(P, Q, e1, e2, v):
    def pr(X): return X @ e1, X @ e2, X @ v
    x1, y1, d1 = pr(P); x2, y2, d2 = pr(Q)
    a0 = np.stack([x1[:-1], y1[:-1]], 1); a1 = np.stack([x1[1:], y1[1:]], 1)
    b0 = np.stack([x2[:-1], y2[:-1]], 1); b1 = np.stack([x2[1:], y2[1:]], 1)
    da = a1 - a0; db = b1 - b0
    DA = da[:, None, :]; DB = db[None, :, :]
    denom = DA[..., 0] * DB[..., 1] - DA[..., 1] * DB[..., 0]
    rel = b0[None, :, :] - a0[:, None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (rel[..., 0] * DB[..., 1] - rel[..., 1] * DB[..., 0]) / denom
        s = (rel[..., 0] * DA[..., 1] - rel[..., 1] * DA[..., 0]) / denom
    hit = (np.abs(denom) > 1e-14) & (t > 0) & (t < 1) & (s > 0) & (s < 1)
    if not hit.any(): return 0.0
    ti, si = t[hit], s[hit]
    ia, ib = np.nonzero(hit)
    da_ = d1[:-1][ia] + ti * (d1[1:] - d1[:-1])[ia]
    db_ = d2[:-1][ib] + si * (d2[1:] - d2[:-1])[ib]
    return 0.5 * np.sum(np.sign(denom[hit]) * np.sign(da_ - db_))

# close each loop explicitly
cp = [np.vstack([p, p[:1]]) for p in paths]
V1 = basis(np.array([0.317, 0.871, 0.394]))
V2 = basis(np.array([-0.412, 0.766, 0.492]))
LK = np.zeros((NO, NO)); bad = 0
for i in range(NO):
    for j in range(i + 1, NO):
        l1 = linking(cp[i][::2], cp[j][::2], *V1)
        l2 = linking(cp[i][::2], cp[j][::2], *V2)
        r1, r2 = round(l1), round(l2)
        if abs(l1 - r1) > 0.01 or abs(l2 - r2) > 0.01 or r1 != r2:
            # third tiebreak projection, full sampling
            V3 = basis(np.array([0.201, -0.655, 0.728]))
            l3 = linking(cp[i], cp[j], *V3)
            r3 = round(l3)
            cands = [r for r, l in ((r1, l1), (r2, l2), (r3, l3)) if abs(l - r) < 0.01]
            assert cands and all(c == cands[0] for c in cands), (words[i], words[j], l1, l2, l3)
            LK[i, j] = LK[j, i] = cands[0]
            bad += 1
        else:
            LK[i, j] = LK[j, i] = r1
    print("row", i, flush=True)
off = LK[np.triu_indices(NO, 1)]
print(f"[relink] pairs needing tiebreak: {bad}; min lk={off.min():.0f} max={off.max():.0f} all positive: {(off>0).all()}")
d = dict(D)
d["LK"] = LK
np.savez_compressed("lorenz_orbits.npz", **d)
open("lorenz_census.txt", "a").write(
    f"relink 2-projection agreement: min={off.min():.0f} max={off.max():.0f} allpos={(off>0).all()} tiebreaks={bad}\n")
