"""Statistics over all valid polygons found + even near-misses."""
import json, glob, re
import numpy as np
from poly import orient_ccw, turns, canon, interior_angles, exact_check


def w_winding(V):
    """w_k = (-1)^k u_k ; consecutive w's satisfy w_k.w_{k+1} >= 0 (as u_k.u_{k+1} <= 0).
    Return total rotation of the w-sequence (closing w_n = (-1)^n w_0) in units of 360 deg."""
    V = orient_ccw(np.asarray(V)); n = len(V)
    U = np.roll(V, -1, axis=0) - V
    W = U * ((-1) ** np.arange(n))[:, None]
    tot = 0.0
    for k in range(n):
        a = W[k]; b = W[k + 1] if k + 1 < n else W[0] * (-1) ** n
        tot += np.arctan2(a[0] * b[1] - a[1] * b[0], a @ b)
    return tot / (2 * np.pi), float(np.min([U[k] @ U[(k + 1) % n] for k in range(n)])), float(np.max([U[k] @ U[(k + 1) % n] for k in range(n)]))


def zig(c):
    k = (len(c) - 5) // 2
    return len(c) == 3 and c == "LLL" or (len(c) >= 5 and c == "LLLL" + "RL" * k + "R")


out = {}
for f in sorted(glob.glob("runs/g*.json"), key=lambda f: int(re.findall(r"\d+", f)[-1])):
    d = json.load(open(f)); n = d["n"]
    pats = {}; wind = {}; maxdot = -9; rc = {}; maxconv = 0; minref = 360
    for p in d["found"]:
        V = np.array(p["verts"]); c = canon(turns(V))
        pats[c] = pats.get(c, 0) + 1
        w, lo, hi = w_winding(V); wind[round(w, 3)] = wind.get(round(w, 3), 0) + 1
        maxdot = max(maxdot, hi)
        r = c.count("R"); rc[r] = rc.get(r, 0) + 1
        ia = interior_angles(V)
        maxconv = max(maxconv, ia[ia < 180].max()); minref = min(minref, ia[ia > 180].min()) if (ia > 180).any() else minref
    out[n] = dict(valid=len(d["found"]), tries=d["tries"], patterns=pats,
                  all_zigzag_word=all(zig(c) for c in pats), reflex_counts=rc,
                  w_winding=wind, max_consecutive_edge_dot=maxdot,
                  max_convex_interior_angle=float(maxconv), min_reflex_interior_angle=float(minref))
    print(n, out[n])
ev = {}
for f in sorted(glob.glob("runs/even*.json"), key=lambda f: int(re.findall(r"\d+", f)[-1])):
    d = json.load(open(f)); n = d["n"]
    rows = []
    for b in d["best"][:5]:
        V = np.array(b["verts"])
        rows.append(dict(viol=b["viol"], breakdown=b["breakdown"], turns=canon(b["turns"]),
                         w_winding=round(w_winding(V)[0], 3)))
    ev[n] = dict(tries=d["tries"], delta=d["delta"], best=rows)
    print("even", n, d["tries"], rows[0])
json.dump(dict(odd=out, even=ev), open("analysis.json", "w"), indent=1)
nm = {}
for f in glob.glob("runs/even*.json"):
    d = json.load(open(f))
    nm[d["n"]] = dict(delta=d["delta"], tries=d["tries"],
                      note="sides exactly 1 by construction; viol = max(closure gap, box excess, delta-clearance, delta-fold)",
                      best=[dict(viol=b["viol"], breakdown=b["breakdown"], verts=b["verts"], turns=b["turns"],
                                 exact_check=b["exact"]) for b in d["best"]])
json.dump(nm, open("near_misses.json", "w"))
