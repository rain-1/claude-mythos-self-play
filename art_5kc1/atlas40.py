#!/usr/bin/env python3
"""Piece 40 analysis: combine census statistics into the channel model.
Model:  W5(g) = C5(g) * q(g),  q = P(4 inter-post windows empty | 5 posts in S).
Fit log q(g) = a - b*(g-1) + c*[g odd]  on gaps with W5 > 0 at 4e9, then predict
W5(14), W5(17) and expected first-occurrence depth.  Writes atlas40_data.json."""
import json, numpy as np
from density40 import R_factor

OBS_GAPS = [1, 2, 4, 7, 8, 9, 15, 16, 18]
TARGETS = [14, 17]

# ---- load census stats ----
cap = {}
for line in open("capcount_out.txt"):
    kv = dict(p.split("=") for p in line.split())
    g = int(kv["g"])
    cap[g] = {k: int(v) for k, v in kv.items()}

# ---- R(g) singular series ----
print("computing R(g) 1..26 ...")
R = {}
for g in range(1, 27):
    R[g], _ = R_factor(g, 5, K=22)
    print(f"  R({g}) = {R[g]:.5g}", flush=True)

# ---- fit emptiness ----
gs = np.array([g for g in OBS_GAPS if cap[g]["W5"] > 0 and cap[g]["C5"] > 0])
q = np.array([cap[g]["W5"] / cap[g]["C5"] for g in gs])
X = np.stack([np.ones_like(gs, float), -(gs - 1.0), (gs % 2 == 1).astype(float)], 1)
coef, res, *_ = np.linalg.lstsq(X, np.log(q), rcond=None)
a, b, c = coef
pred_lnq = X @ coef
print("fit: ln q = %.3f - %.4f*(g-1) + %.3f*odd" % (a, b, c))
for g, lq, lqh in zip(gs, np.log(q), pred_lnq):
    print(f"  g={g:2d}  ln q obs {lq:7.3f}  fit {lqh:7.3f}")

out = {"R": R, "cap": cap, "fit": [float(a), float(b), float(c)]}
for g in TARGETS:
    lnqh = a - b * (g - 1) + c * (g % 2 == 1)
    W5h = cap[g]["C5"] * np.exp(lnqh)
    out[f"pred_W5_{g}"] = float(W5h)
    print(f"g={g}: C5(4e9) = {cap[g]['C5']}, predicted W5(4e9) = {W5h:.3g}  "
          f"(observed 0) -> first fence expected near X ~ {4e9 / max(W5h, 1e-12):.3g}"
          if W5h < 1 else
          f"g={g}: C5 = {cap[g]['C5']}, predicted W5(4e9) = {W5h:.3g} but observed 0 (!)")

# per-gap deep counts from the 3.2e10 run
deep = {}
for line in open("deep_rungap.txt"):
    kv = dict(p.split("=") for p in line.split())
    l, g = int(kv["l"]), int(kv["g"])
    if l == 5:
        deep[g] = {"count": int(kv["maximal_runs"]), "first": int(kv["first_start"])}
out["deep_l5"] = deep
json.dump(out, open("atlas40_data.json", "w"), indent=1)
print("wrote atlas40_data.json")
