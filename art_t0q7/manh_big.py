#!/usr/bin/env python3
"""Exhaustive census n=10, 11 + distribution dump for the art piece.

Saves per-n: histogram of log(|det|/floor), min/max, #argmin, violations,
gcd of all values, second-smallest, and for n=10 the full sorted value list
(unique values + counts) for rendering.
"""
import numpy as np, itertools, json, time
from math import gcd

def run(n, chunk=250000):
    A = np.abs(np.subtract.outer(np.arange(n), np.arange(n))).astype(np.float64)
    floor_ = (n-1) * 4.0**(n-1)
    it = itertools.permutations(range(n))
    total = 0; viol = 0; g_all = 0
    minv = np.inf; nmin = 0; maxv = -np.inf; maxperm = None
    # histogram of r = |det|/floor in log2, range [0, 20), 2000 bins
    H = np.zeros(2000, np.int64)
    uniq = {}
    t0 = time.time()
    while True:
        block = list(itertools.islice(it, chunk))
        if not block: break
        P = np.array(block, dtype=np.int16)
        B = np.abs(P[:, :, None] - P[:, None, :]).astype(np.float64)
        D = A[None] + B
        del B
        adets = np.abs(np.linalg.det(D))
        del D
        viol += int(np.sum(adets < floor_ * (1 - 1e-9)))
        nmin += int(np.sum(np.abs(adets - floor_) < 1e-7 * floor_))
        i = int(np.argmax(adets))
        if adets[i] > maxv: maxv = float(adets[i]); maxperm = [int(x) for x in block[i]]
        minv = min(minv, float(np.min(adets)))
        r = np.log2(adets / floor_)
        H += np.histogram(r, bins=2000, range=(0, 20))[0]
        iv = np.round(adets).astype(np.int64)
        vv, cc = np.unique(iv, return_counts=True)
        if n <= 10:
            for v, c in zip(vv[:2000], cc[:2000]):
                uniq[int(v)] = uniq.get(int(v), 0) + int(c)
        for v in vv[:50]: g_all = gcd(g_all, int(v))
        g_all = gcd(g_all, int(vv[-1]))
        total += len(block)
        if total % 4000000 < chunk:
            print(f"n={n} {total} done {time.time()-t0:.0f}s", flush=True)
    out = dict(n=n, total=total, floor=floor_, viol=viol, nmin=nmin,
               minv=minv, maxv=maxv, maxperm=maxperm, gcd=g_all,
               hist=H.tolist(), secs=round(time.time()-t0, 1))
    if n <= 10:
        sv = sorted(uniq)
        out["bottom_vals"] = [(v, uniq[v]) for v in sv[:24]]
    json.dump(out, open(f"manh_big_{n}.json", "w"))
    print(f"n={n} DONE total={total} viol={viol} nmin={nmin} min={minv:.0f} "
          f"floor={floor_:.0f} max={maxv:.0f} gcd={g_all} ({time.time()-t0:.0f}s)",
          flush=True)

if __name__ == "__main__":
    run(10)
    run(11)
    print("ALLDONE")
