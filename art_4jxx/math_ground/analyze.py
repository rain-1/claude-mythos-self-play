import json, glob, collections, sys
import numpy as np

recs = []
for f in sorted(glob.glob("data/sweep*.jsonl")):
    for l in open(f):
        recs.append(json.loads(l))
print("total", len(recs))
fams = sorted(set(r["fam"] for r in recs))
print(f"{'family':10s} {'N':>5s} {'cert33':>7s} {'gap>1e-6':>8s} {'max gap':>8s}  pstar distribution (p*:count)        area>=8")
for fam in fams:
    R = [r for r in recs if r["fam"] == fam]
    cert = sum(r["gap"] < 1e-7 for r in R)
    big = sum(r["gap"] > 1e-6 for r in R)
    ps = collections.Counter(r["pstar"] for r in R)
    ar = sum(r["area"] >= 8 for r in R)
    print(f"{fam:10s} {len(R):5d} {cert/len(R):7.3f} {big:8d} {max(r['gap'] for r in R):8.4f}  "
          + " ".join(f"{k}:{ps[k]}" for k in sorted(ps)) + f"   {ar}")
area = collections.Counter(r["area"] for r in recs)
print("fundamental-domain area distribution:", sorted(area.items()))
# 'late improvers': optimum first reached at p >= 6
late = [r for r in recs if r["pstar"] >= 6]
print("pstar>=6:", len(late))
for r in sorted(late, key=lambda r: -r["pstar"])[:15]:
    print(r["fam"], r["pstar"], r["area"], (r["pv"], r["h"], r["s"]), "gap", round(r["gap"], 6))
gaps = sorted(recs, key=lambda r: -r["gap"])
print("largest gaps:")
for r in gaps[:15]:
    print(r["fam"], r["pstar"], r["area"], round(r["gap"], 6), np.round(r["e"], 4).tolist())
json.dump([r for r in recs if r["gap"] > 1e-6], open("data/gap_candidates.json", "w"))
