#!/usr/bin/env python3
"""MO 514722: exhaustive census of circles through >=3 lattice points with
circumradius <= R_MAX.  Exact integer arithmetic throughout.

Every circle through >=3 lattice points, translated so one of its lattice
points is the origin, satisfies  A(x^2+y^2) + Gx + Fy = 0  with integers
A>0, G, F, gcd(A,G,F)=1.  Center (-G/2A, -F/2A), r^2 = (G^2+F^2)/4A^2.
Two anchored circles are plane-translates iff (A, -G mod 2A, -F mod 2A,
r^2) agree, since re-anchoring at another lattice point shifts the center
by integers.

Rigor for the minimum-interior question (exactly 5 on-points):
  closed-disk lattice count >= ceil(pi (r - 1/sqrt2)^2)   [centered unit
  squares covering the shrunk disk], so interior >= pi(r-0.7072)^2 - 5.
  interior <= 105 forces r <= 6.63.  We search r <= R_MAX >= 7.3, which
  also covers the coarser bound pi(r-sqrt2)^2 <= 106 (r <= 7.23).
"""
import sys, math, json
from math import gcd, isqrt
import numpy as np
from collections import defaultdict

R_MAX = float(sys.argv[1]) if len(sys.argv) > 1 else 7.3
OUT = sys.argv[2] if len(sys.argv) > 2 else f"census_r{R_MAX:g}.json"
R2CAP_NUM = None  # r^2 <= R_MAX^2 exact via cross-multiplied ints below
D = 2 * R_MAX     # chord bound
DI = int(math.floor(D))

pts = [(x, y) for x in range(-DI, DI + 1) for y in range(-DI, DI + 1)
       if x * x + y * y <= D * D and (x, y) != (0, 0)]
pts.sort()
n = len(pts)
print(f"R_MAX={R_MAX}  candidate points={n}  pairs~{n*(n-1)//2}")

R2q = R_MAX * R_MAX
seen = set()
circles = []          # (A,G,F) anchored, normalized
for i in range(n):
    bx, by = pts[i]
    nb = bx * bx + by * by
    for j in range(i + 1, n):
        cx, cy = pts[j]
        dx, dy = cx - bx, cy - by
        if dx * dx + dy * dy > D * D:
            continue
        det = bx * cy - by * cx
        if det == 0:
            continue
        nc = cx * cx + cy * cy
        A = det
        G = -nb * cy + nc * by
        F = nb * cx - nc * bx
        if A < 0:
            A, G, F = -A, -G, -F
        g = gcd(gcd(A, abs(G)), abs(F))
        A //= g; G //= g; F //= g
        # r^2 = (G^2+F^2)/(4A^2) <= R2q ?
        num = G * G + F * F
        if num > R2q * 4 * A * A:
            continue
        key = (A, (-G) % (2 * A), (-F) % (2 * A), num)
        # num/(4A^2) with gcd(A,G,F)=1 is already a translation invariant
        # paired with A; (num, A) determines r^2.
        if key in seen:
            continue
        seen.add(key)
        circles.append((A, G, F))
print(f"unique circles (translation classes): {len(circles)}")

# exact counting per circle
by_k = defaultdict(list)   # on-count -> list of (interior, num, A, G, F)
for (A, G, F) in circles:
    cxf = -G / (2 * A); cyf = -F / (2 * A)
    r = math.sqrt(G * G + F * F) / (2 * A)
    x0, x1 = math.ceil(cxf - r - 1e-9), math.floor(cxf + r + 1e-9)
    y0, y1 = math.ceil(cyf - r - 1e-9), math.floor(cyf + r + 1e-9)
    xs = np.arange(x0, x1 + 1, dtype=np.int64)
    ys = np.arange(y0, y1 + 1, dtype=np.int64)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    val = A * (X * X + Y * Y) + G * X + F * Y
    on = int((val == 0).sum())
    inside = int((val < 0).sum())
    by_k[on].append((inside, G * G + F * F, A, G, F))

summary = {}
for k in sorted(by_k):
    lst = sorted(by_k[k])
    best = lst[0]
    # min radius representative too
    byr = min(lst, key=lambda t: t[1] / (4 * t[2] * t[2]))
    summary[k] = dict(
        count=len(lst),
        min_interior=best[0],
        min_interior_circle=dict(A=best[2], G=best[3], F=best[4],
                                 r=math.sqrt(best[1]) / (2 * best[2])),
        min_radius=math.sqrt(byr[1]) / (2 * byr[2]),
        min_radius_interior=byr[0],
        min_radius_circle=dict(A=byr[2], G=byr[3], F=byr[4]),
    )
    print(f"k={k:3d}  circles={len(lst):7d}  min_interior={best[0]:5d} "
          f"(r={math.sqrt(best[1])/(2*best[2]):.4f})  "
          f"min_radius={summary[k]['min_radius']:.4f}")

# dump full census for the art (k, r2num, A, interior) per circle
art = {str(k): [[t[0], t[1], t[2], t[3], t[4]] for t in sorted(by_k[k])]
       for k in by_k}
with open(OUT, "w") as f:
    json.dump(dict(R_MAX=R_MAX, summary=summary, census=art), f)
print("wrote", OUT)
