#!/usr/bin/env python3
"""Engineered families: nested reversals; waist-window designs; compare at n=256..2048."""
import numpy as np, json
from cloth_lib import area_grid, sigma_rev, sigma_blockrev

def compose(a, b):  # (a o b)(i) = a[b[i]]
    return a[b]

def nested_rev(n, scales):
    """reverse at several block scales, coarsest last (global rev if n in scales)"""
    s = np.arange(n)
    for B in scales:
        s = compose(sigma_blockrev(n, B), s)
    return s

def waist_sigma(n, W, y0, y1, rng, mode="stagger"):
    """Each line forced through x = c + o_i at height h_i; o in [-W/2,W/2] n-units."""
    c = n / 2
    i = np.arange(n)
    if mode == "stagger":
        h = y0 + (y1 - y0) * ((i * 0.61803398875) % 1.0)
        o = W * (((i * 0.7548776662) % 1.0) - 0.5)
    else:
        h = rng.uniform(y0, y1, n)
        o = rng.uniform(-W/2, W/2, n)
    xw = c + o
    x1 = i + (xw - i) / h          # position at y=1
    return np.argsort(np.argsort(x1)).astype(np.int64)  # ranks -> permutation

if __name__ == "__main__":
    rng = np.random.default_rng(5)
    out = {}
    for n in (256, 512, 1024, 2048):
        M = 4096
        rows = {}
        rows["rev"] = area_grid(sigma_rev(n), M)
        # nested reversal cascades
        for scales in ([n, 4], [n, 8], [n, 16], [n, 32], [n, 8, 64] if n >= 512 else [n, 8],
                       [4, n], [8, n], [16, n]):
            key = "nest" + "-".join(map(str, scales))
            rows[key] = area_grid(nested_rev(n, scales), M)
        # waist designs
        for W in (n//16, n//8, n//4):
            for (y0, y1) in ((0.3, 0.7), (0.2, 0.8), (0.4, 0.6)):
                key = f"waist_W{W}_y{y0}-{y1}"
                rows[key] = area_grid(waist_sigma(n, W, y0, y1, rng), M)
        best = min(rows, key=rows.get)
        out[n] = rows
        print(f"n={n}: best {best} = {rows[best]:.5f}  (rev {rows['rev']:.5f})")
        for k, v in sorted(rows.items(), key=lambda kv: kv[1])[:6]:
            print(f"    {k:24s} {v:.5f}")
    json.dump(out, open("cloth_families2.json", "w"), indent=1)
