#!/usr/bin/env python3
"""Verify t(x,y,z) = min(x+y, y+z, z+x, floor((x+y+z)/2)) against the DP,
and machine-check lemma (ii): from every P, every v < f(P) is reachable."""
import numpy as np, sys, time
from mesh_small import solve

def formula(N):
    i = np.arange(N)
    x = i[:, None, None]; y = i[None, :, None]; z = i[None, None, :]
    s = x + y + z
    return np.minimum.reduce([x+y+0*z, y+z+0*x, z+x+0*y, s//2])

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    t0 = time.time()
    g = solve(N)
    f = formula(N)
    ok = np.array_equal(g, f)
    print(f"N={N}: formula == DP grundy: {ok}  ({time.time()-t0:.1f}s)")
    if not ok:
        d = np.argwhere(g != f)[:10]
        for x, y, z in d: print(" mismatch", x, y, z, g[x,y,z], f[x,y,z])
        sys.exit(1)
    # lemma (ii) machine check, small range: from each P and each v < f(P),
    # exists a two-pile reduction with f(P') = v  (uses formula only)
    M = min(N, 30)
    fm = formula(N)
    bad = 0
    for x in range(M):
        for y in range(M):
            for z in range(M):
                fv = fm[x, y, z]
                need = set(range(fv))
                for a in range(1, x+1):
                    for b in range(1, y+1): need.discard(fm[x-a, y-b, z])
                for a in range(1, x+1):
                    for c in range(1, z+1): need.discard(fm[x-a, y, z-c])
                for b in range(1, y+1):
                    for c in range(1, z+1): need.discard(fm[x, y-b, z-c])
                if need:
                    bad += 1
                    if bad < 5: print("lemma(ii) FAILS at", x, y, z, "missing", sorted(need)[:5])
    print(f"lemma(ii) exhaustive to {M}: {'PASS' if bad==0 else f'{bad} failures'}")
    # lemma (i): every move strictly decreases f — spot proof via random moves
    rng = np.random.default_rng(0)
    bad1 = 0
    for _ in range(200000):
        x, y, z = rng.integers(0, N, 3)
        which = rng.integers(0, 3)
        if which == 0 and x > 0 and y > 0:
            a = rng.integers(1, x+1); b = rng.integers(1, y+1)
            if fm[x-a, y-b, z] >= fm[x, y, z]: bad1 += 1
        elif which == 1 and x > 0 and z > 0:
            a = rng.integers(1, x+1); c = rng.integers(1, z+1)
            if fm[x-a, y, z-c] >= fm[x, y, z]: bad1 += 1
        elif which == 2 and y > 0 and z > 0:
            b = rng.integers(1, y+1); c = rng.integers(1, z+1)
            if fm[x, y-b, z-c] >= fm[x, y, z]: bad1 += 1
    print(f"lemma(i) random moves: {'PASS' if bad1==0 else f'{bad1} failures'}")
