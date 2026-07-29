"""
search_rings.py — complete census of exact rim-ring perfect fits.

A rim ring = coins all tangent to the tray, consecutively tangent, central
angles summing to EXACTLY 2*pi. Census over curvatures 2..K.

Also: the radical-class analysis. For each unordered pair (p,q) the unit
complex z = c + i*sqrt(1-c^2) lives over the squarefree kernel d of 1-c^2.
Closure product = 1 must survive every Galois flip sqrt(d) -> -sqrt(d),
forcing  sum of angles within each class d  ==  0 mod pi.
Classes whose angles are irrational multiples of pi and admit no integer
relation then cannot appear at all.
"""

import math
import sys
from fractions import Fraction
from collections import Counter
from engine import (cos_theta, theta, ring_closure_certificate,
                    ring_positions, ring_embeddable, is_rigid,
                    _squarefree_split)
import numpy as np

K = int(sys.argv[1]) if len(sys.argv) > 1 else 9
TOL = 1e-7


def radical_class(p, q):
    c = cos_theta(p, q)
    s2 = 1 - c * c
    if s2 == 0:
        return 1
    num, den = s2.numerator, s2.denominator
    _, d = _squarefree_split(num * den)
    return d


def class_table():
    classes = {}
    for p in range(2, K + 1):
        for q in range(p, K + 1):
            d = radical_class(p, q)
            classes.setdefault(d, []).append((p, q, cos_theta(p, q), theta(p, q)))
    return classes


def print_class_analysis():
    classes = class_table()
    print(f"=== radical classes for curvatures 2..{K} ===")
    for d in sorted(classes):
        entries = classes[d]
        print(f"class sqrt({d}):")
        for (p, q, c, th) in entries:
            ratpi = th / math.pi
            print(f"   theta({p},{q}) = arccos({c})  = {ratpi:.6f}*pi")
    return classes


def dfs_census():
    """All cyclic sequences (up to rotation+reflection) of curvatures in 2..K
    with exact angle-sum closure 2*pi. DFS with angle budget pruning."""
    curvs = list(range(2, K + 1))
    th = {(p, q): theta(p, q) for p in curvs for q in curvs}
    thmin = min(th.values())
    maxlen = int(2 * math.pi / thmin) + 1
    results = []
    seen = set()

    def canon(seq):
        best = None
        for s in (seq, seq[::-1]):
            for r in range(len(s)):
                cand = tuple(s[r:] + s[:r])
                if best is None or cand < best:
                    best = cand
        return best

    def dfs(seq, ang):
        # try to close
        if len(seq) >= 3:
            closing = ang + th[(seq[-1], seq[0])]
            if abs(closing - 2 * math.pi) < TOL:
                key = canon(seq)
                if key not in seen:
                    seen.add(key)
                    results.append(list(key))
        if len(seq) >= maxlen:
            return
        # prune: even one more coin then closing needs ang + 2*thmin <= 2pi
        if ang + 2 * thmin > 2 * math.pi + TOL:
            return
        last = seq[-1]
        for nxt in curvs:
            a2 = ang + th[(last, nxt)]
            if a2 + thmin > 2 * math.pi + TOL:
                continue
            seq.append(nxt)
            dfs(seq, a2)
            seq.pop()

    for start in curvs:
        dfs([start], 0.0)

    # length-2 special: 2*theta(p,q) = 2pi  <=>  radii sum to 1
    for p in curvs:
        for q in range(p, K + 1):
            if Fraction(1, p) + Fraction(1, q) == 1:
                results.append([p, q])
    return results


def main():
    classes = print_class_analysis()
    print()
    print("=== DFS census of closed rings ===")
    rings = dfs_census()
    print(f"raw candidates (numeric closure, deduped): {len(rings)}")
    certified = []
    ghosts = []
    for ring in sorted(rings, key=len):
        ok, tot = ring_closure_certificate(ring)
        if not ok:
            print(f"  NEAR-MISS (not exact): {ring}  sum-2pi = {tot-2*math.pi:+.3e}")
            continue
        emb, extra = ring_embeddable(ring)
        if not emb:
            ghosts.append(ring)
            print(f"  exact but NOT embeddable: {ring}")
            continue
        pos = ring_positions(ring)
        centers = np.array([[x, y] for x, y, r in pos])
        radii = np.array([r for x, y, r in pos])
        rigid, rep = is_rigid(centers, radii)
        sizes = sorted(set(ring))
        certified.append((ring, rigid, rep["verdict"], extra, sizes))
        print(f"  EXACT ring {ring}  sizes={sizes}  rigid={rigid}  "
              f"contacts={rep['n_contacts']}  extra_tang={extra}")
    print()
    print(f"=== {len(certified)} exact embeddable rings ===")
    print("which curvatures appear in ANY exact embeddable ring:",
          sorted({p for ring, *_ in certified for p in ring}))
    import json
    with open(f"rings_census_K{K}.json", "w") as f:
        json.dump({"rings": [{"ring": r, "rigid": bool(g), "verdict": v,
                              "extra": e, "sizes": s} for r, g, v, e, s in certified],
                   "ghosts": ghosts}, f, indent=1)
    return certified


if __name__ == "__main__":
    main()
