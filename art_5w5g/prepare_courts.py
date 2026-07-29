"""
prepare_courts.py — assemble the full catalogue of certified courts for the hero.
Ring courts (from census) + special non-ring courts (hexaflower+center,
poster's 8-coin perfect fit) with positions, stress, rigidity verdicts.
"""

import json
import math
import numpy as np
from engine import (ring_positions, ring_closure_certificate, ring_embeddable,
                    is_rigid, contact_data)
from search_jam import best_s, maximize_s


def court_from_config(centers, radii, name, kind, note=""):
    centers = np.asarray(centers, float)
    radii = np.asarray(radii, float)
    rigid, rep = is_rigid(centers, radii)
    stress = []
    if "stress" in rep:
        for k, c in enumerate(rep["contacts"]):
            stress.append([c[0], int(c[1]),
                           (int(c[2]) if c[0] == "pair" else None),
                           float(rep["stress"][k])])
    return {"name": name, "kind": kind, "note": note,
            "centers": centers.tolist(), "radii": radii.tolist(),
            "rigid": bool(rigid), "verdict": rep["verdict"],
            "n_contacts": rep["n_contacts"], "stress": stress}


def ring_court(ring, name=None):
    pos = ring_positions(ring)
    centers = [[x, y] for x, y, r in pos]
    radii = [r for x, y, r in pos]
    ok, tot = ring_closure_certificate(ring)
    assert ok, ring
    return court_from_config(centers, radii,
                             name or "ring " + "".join(map(str, ring)),
                             "ring", note=f"ring {ring}")


def orient(court, angle):
    """Rotate court so its composition reads well (e.g. hero coin up)."""
    c = np.array(court["centers"])
    ca, sa = math.cos(angle), math.sin(angle)
    court["centers"] = (c @ np.array([[ca, sa], [-sa, ca]])).tolist()
    return court


def main():
    courts = []

    # ---- the true courts of the question ----
    courts.append(ring_court([2, 2], name="n=2 · [2,2]"))
    courts.append(ring_court([2, 2, 3], name="n=3 · [2,2,3]"))
    courts.append(ring_court([2, 3, 2, 3], name="[2,3,2,3]"))
    courts.append(ring_court([2, 3, 3, 3, 3], name="n=3 · [2,3,3,3,3]"))
    courts.append(ring_court([2, 3, 2, 4, 4], name="n=4 · [2,3,2,4,4]"))

    # ---- jewels from the census ----
    for ring, nm in [
        ([3, 3, 3, 3, 3, 3], "[3]x6"),
        ([2, 4, 4, 2, 4, 4], "[2,4,4]x2"),
        ([2, 2, 3, 6], "[2,2,3,6]"),
        ([2, 3, 2, 3, 6], "[2,3,2,3,6]"),
        ([2, 3, 3, 3, 3, 6], "[2,3,3,3,3,6]"),
        ([2, 6, 3, 6, 2, 6, 3, 6], "[2,6,3,6]x2"),
        ([2, 4, 4, 2, 6, 3, 6], "[2,4,4,2,6,3,6]"),
        ([2, 3, 6, 2, 4, 4], "[2,3,6,2,4,4]"),
    ]:
        courts.append(ring_court(ring, name=nm))

    # ---- hexaflower + center (7 thirds) ----
    pos = [[math.cos(k * math.pi / 3) * 2 / 3,
            math.sin(k * math.pi / 3) * 2 / 3] for k in range(6)] + [[0, 0]]
    courts.append(court_from_config(pos, [1 / 3] * 7, "seven thirds", "flower",
                                    note="6-ring + exact center pocket"))

    # ---- the flexible perfect closure [2,2,4,4] (closure exact, NOT rigid) ----
    pos = ring_positions([2, 2, 4, 4])
    courts.append(court_from_config([[x, y] for x, y, r in pos],
                                    [r for x, y, r in pos],
                                    "[2,2,4,4] · closes but rattles", "ring-flex",
                                    note="exact closure, strict flex exists"))

    # ---- poster's 8-coin perfect fit {2,2,3,4,4,6,6,7} ----
    radii = np.array([1/2, 1/2, 1/3, 1/4, 1/4, 1/6, 1/6, 1/7])
    best = (0, None)
    for seed in range(40):
        s, x, locs = best_s(radii, restarts=25, seed=999 + seed)
        if s > best[0]:
            best = (s, x)
        if abs(s - 1) < 1e-10:
            break
    s, x = best
    print(f"poster 8-coin: s = {s:.14f}")
    assert abs(s - 1) < 1e-8
    # polish: re-run local from found config at s target
    s2, x2 = maximize_s(radii, x0=x, s0=0.9995)
    print(f"polished     : s = {s2:.14f}")
    if abs(s2 - 1) < abs(s - 1):
        x = x2
    c = court_from_config(x, radii, "the court that skipped five",
                          "jam", note="{2,2,3,4,4,6,6,7} · poster's perfect fit")
    print("8-coin verdict:", c["verdict"], "contacts:", c["n_contacts"])
    courts.append(c)

    with open("courts.json", "w") as f:
        json.dump(courts, f)
    print(f"\n{len(courts)} courts saved")
    for c in courts:
        print(f"  {c['name']:30s} rigid={c['rigid']} {c['verdict']}")


if __name__ == "__main__":
    main()
