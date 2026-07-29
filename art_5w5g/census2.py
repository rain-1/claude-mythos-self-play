"""
census2.py — COMPLETE rim-ring census for curvatures 2..9 via the
radical-class-reduced alphabet.

From class_relations.py (Galois classes + Niven + PSLQ + two exact identities
    2*arccos(13/14) + arccos(47/49) = pi/3        (class sqrt3, the 5-8-8 law)
    4*arccos(3/4)   + arccos(31/32) = pi          (class sqrt7, the 2-9 law)
the only adjacencies that can appear in an exact closed rim ring are:

    2-2, 2-3, 2-4, 2-5, 2-6, 3-3, 3-6, 4-4   (K<=7 alphabet)
    5-8, 8-8                                  (new at K=8)
    2-9, 9-9                                  (new at K=9)

with counting conditions  m24 = 2*m44,  m58 = 2*m88,  m29 = 4*m99,
(m25+m33+m88) = 0 mod 3,  m26 = m36.  Curvature 7 has NO usable adjacency.
Every candidate is then certified exactly by the quadratic-tower product,
checked for embeddability, and rigidity-tested.
"""

import math
import json
import numpy as np
from engine import (theta, ring_closure_certificate, ring_positions,
                    ring_embeddable, is_rigid)

ALLOWED = {(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 3), (3, 6), (4, 4),
           (5, 8), (8, 8), (2, 9), (9, 9)}
NBR = {}
for a, b in ALLOWED:
    NBR.setdefault(a, set()).add(b)
    NBR.setdefault(b, set()).add(a)

TH = {}
for a, b in ALLOWED:
    TH[(a, b)] = TH[(b, a)] = theta(a, b)
THMIN = min(TH.values())
TOL = 1e-7


def dfs_census(maxlen=26):
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
        last = seq[-1]
        if len(seq) >= 3 and seq[0] in NBR[last]:
            closing = ang + TH[(last, seq[0])]
            if abs(closing - 2 * math.pi) < TOL:
                key = canon(seq)
                if key not in seen:
                    seen.add(key)
                    results.append(list(key))
        if len(seq) >= maxlen:
            return
        if ang + 2 * THMIN > 2 * math.pi + TOL:
            return
        for nxt in NBR[last]:
            a2 = ang + TH[(last, nxt)]
            if a2 + THMIN > 2 * math.pi + TOL:
                continue
            seq.append(nxt)
            dfs(seq, a2)
            seq.pop()

    for start in sorted(NBR):
        dfs([start], 0.0)
    # the 2-coin special ring (radii sum 1)
    results.append([2, 2])
    return results


def main():
    rings = dfs_census()
    print(f"candidates (numeric closure): {len(rings)}")
    certified, ghosts, flexes = [], [], []
    for ring in sorted(rings, key=lambda r: (len(r), r)):
        ok, tot = ring_closure_certificate(ring)
        if not ok:
            print(f"  NOT exact (near miss): {ring} {tot-2*math.pi:+.2e}")
            continue
        emb, extra = ring_embeddable(ring)
        if not emb:
            ghosts.append(ring)
            print(f"  exact, NOT embeddable: {ring}")
            continue
        pos = ring_positions(ring)
        centers = np.array([[x, y] for x, y, r in pos])
        radii = np.array([r for x, y, r in pos])
        rigid, rep = is_rigid(centers, radii)
        (certified if rigid else flexes).append(
            {"ring": ring, "rigid": bool(rigid), "verdict": rep["verdict"],
             "extra": extra, "sizes": sorted(set(ring))})
        print(f"  EXACT {'RIGID ' if rigid else 'flex  '}{ring} sizes={sorted(set(ring))} "
              f"contacts={rep['n_contacts']}")
    print(f"\nK=9 census: {len(certified)} rigid rings, {len(flexes)} exact-but-flexible, "
          f"{len(ghosts)} ghosts")
    print("curvatures appearing in rigid rings:",
          sorted({p for c in certified for p in c['ring']}))
    json.dump({"rigid": certified, "flexible": flexes, "ghosts": ghosts},
              open("rings_census_K9.json", "w"), indent=1)


if __name__ == "__main__":
    main()
