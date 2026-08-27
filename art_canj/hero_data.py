"""Hero data prep: window-clearance triangles for the zigzag Z_p.
clearance(i,L) = distance of (window sum)/L from the nearest integer, in [0, 1/2].
Theorem (this run): interior odd windows have clearance exactly 1/L,
interior even windows exactly 1/2, prefixes carry the arithmetic of p:
odd prefix L: ((-p) mod L)/L scaled;  zero exactly at divisors L | p.
"""
import numpy as np

def constr(p):
    a = [1]
    x = p - 1
    while x >= 2:
        a += [x, x + 1]
        x -= 2
    return a

def triangle(p):
    a = constr(p)
    pre = np.concatenate([[0], np.cumsum(a)])
    rows = []
    for L in range(2, p):
        for i in range(0, p - L + 1):
            S = pre[i + L] - pre[i]
            r = S % L
            c = min(r, L - r) / L          # clearance in [0, 1/2]
            rows.append((i, L, c, 1 if i == 0 else 0))
    return np.array(rows)

if __name__ == '__main__':
    for p in (127, 63):
        T = triangle(p)
        np.savez_compressed(f'hero_tri_{p}.npz', T=T)
        wounds = T[(T[:, 2] == 0)]
        print(f"p={p}: cells={len(T)}, wounds at (i,L):",
              [(int(i), int(L)) for i, L, c, pf in wounds])
        # sanity vs theorem
        inter = T[T[:, 3] == 0]
        oddL = inter[inter[:, 1] % 2 == 1]
        evenL = inter[inter[:, 1] % 2 == 0]
        assert np.allclose(oddL[:, 2], 1.0 / oddL[:, 1])
        assert np.allclose(evenL[:, 2], 0.5)
        print("   interior clearances match theorem exactly")
