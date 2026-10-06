"""packing.py — 3-D Apollonian sphere packing (Soddy–Gosset).  Five mutually tangent spheres
(curvatures k, centres c) satisfy (Σk)² = 3Σk²; replacing sphere i by its partner is LINEAR:
    k_i' = Σ_{j≠i} k_j − k_i ,     (k c)_i' = Σ_{j≠i} (k c)_j − (k c)_i .
Root: outer unit sphere (k = −1) + four equal inner spheres in a tetrahedron, one vertex DOWN.
Search over QUINTUPLES (deduped as sets of five sphere keys); a sphere borders many gaps, so
deduping spheres instead loses branches.   usage: packing.py rmin out.npy -> rows (x,y,z,r,depth)"""
import sys, numpy as np
rmin = float(sys.argv[1]); out = sys.argv[2]
r0 = 1 / (1 + np.sqrt(1.5))
T = np.array([[0, 0, -1], [np.sqrt(8 / 9), 0, 1 / 3], [-np.sqrt(2 / 9), np.sqrt(2 / 3), 1 / 3], [-np.sqrt(2 / 9), -np.sqrt(2 / 3), 1 / 3]])
K = np.array([-1.0] + [1 / r0] * 4)
KC = np.vstack([np.zeros(3), T * (1 - r0) / r0])
def key(k, kc):
    if k < 0: return ('outer',)
    return tuple(np.round(np.r_[kc / k, 1 / k] * 1e8).astype(np.int64))
spheres = {}
for i in range(1, 5): spheres[key(K[i], KC[i])] = (*(KC[i] / K[i]), 1 / K[i], 0)
q0 = frozenset(key(K[i], KC[i]) for i in range(5))
seenq = {q0}; stack = [(K, KC, 0)]; maxerr = 0.0
while stack:
    K, KC, dep = stack.pop()
    keys = [key(K[j], KC[j]) for j in range(5)]
    for i in range(5):
        k2 = K.sum() - 2 * K[i]
        if k2 <= 0 or 1 / k2 < rmin: continue
        kc2 = KC.sum(0) - 2 * KC[i]
        kk = key(k2, kc2)
        q = frozenset(keys[:i] + keys[i + 1:] + [kk])
        if q in seenq: continue
        seenq.add(q)
        if kk not in spheres:
            c2 = kc2 / k2; r2 = 1 / k2
            if len(spheres) % 499 == 0:
                for j in range(5):
                    if j == i: continue
                    err = abs(np.linalg.norm(c2) - (1 - r2)) if K[j] < 0 else abs(np.linalg.norm(c2 - KC[j] / K[j]) - (r2 + 1 / K[j]))
                    maxerr = max(maxerr, err)
            spheres[kk] = (*c2, r2, dep + 1)
        K2, KC2 = K.copy(), KC.copy(); K2[i] = k2; KC2[i] = kc2
        stack.append((K2, KC2, dep + 1))
A = np.array(list(spheres.values()))
print('spheres', len(A), 'quintuples', len(seenq), 'max tangency err', maxerr, 'gap volume', 1 - (A[:, 3] ** 3).sum())
np.save(out, A)
