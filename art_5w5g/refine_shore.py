"""
refine_shore.py — strengthen the n=5 evidence on the shortlist.
For every multiset whose first-pass best_s came within 0.02 of 1, re-run with
400 restarts, keep all local maxima within [0.995, 1.005], polish each, and
rigidity-test any that land within 1e-7 of s=1 (full-config rigidity —
rattlers disqualify). Writes shore.json.
"""

import json
import numpy as np
from multiprocessing import Pool
from search_jam import maximize_s, radii_of
from engine import is_rigid

data = json.load(open("jam_n5.json"))
short = [d for d in data if abs(d["best_s"] - 1) < 0.02]
print(f"shortlist: {len(short)} multisets")


def refine(entry):
    ms = tuple(entry["multiset"])
    radii = radii_of(ms)
    results = []
    best = -1.0
    bx = None
    for k in range(400):
        s, x = maximize_s(radii, seed=61_000_003 * hash(ms) % (2**31) + k)
        if s < 0:
            continue
        if s > best:
            best, bx = s, x
        if 0.995 < s < 1.005:
            results.append((s, x))
    verdicts = []
    for s, x in results:
        if abs(s - 1) < 1e-7:
            s2, x2 = maximize_s(radii, x0=x, s0=0.9998)
            rigid, rep = is_rigid(x2, radii * min(s2, 1.0), tol=1e-6)
            verdicts.append({"s": float(s2), "rigid": bool(rigid),
                             "verdict": rep["verdict"],
                             "x": x2.tolist()})
    return {"multiset": list(ms), "best_s": float(best),
            "x_best": bx.tolist() if bx is not None else None,
            "near_one_tested": verdicts,
            "n_near_one": len(verdicts)}


if __name__ == "__main__":
    with Pool(4) as pool:
        out = list(pool.imap_unordered(refine, short))
    out.sort(key=lambda d: abs(d["best_s"] - 1))
    json.dump(out, open("shore.json", "w"))
    print("\n=== refined shore ===")
    any_rigid = False
    for d in out:
        v = d["near_one_tested"]
        rig = [w for w in v if w["rigid"]]
        any_rigid |= bool(rig)
        print(f"m={tuple(d['multiset'])}  best_s={d['best_s']:.9f}  "
              f"near-1 maxima tested: {len(v)}  RIGID: {len(rig)}")
        for w in v:
            if w["rigid"]:
                print("   *** RIGID PERFECT FIT:", w)
    print("\nANY RIGID n=5 PERFECT FIT FOUND:", any_rigid)
