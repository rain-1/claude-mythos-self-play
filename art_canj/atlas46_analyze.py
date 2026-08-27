"""Atlas 46 analysis: relay [1.6e12, 2.0e12) of the Z[sqrt2]-norm-form set S
(n whose primes ≡ 3,5 mod 8 appear to even powers).
- verdict vs atlas46_precommit.md
- 4->5 hazard per channel from OCC l=4 / l=5 starts
- 5-adic classification of ch-25 4-run starts (the WHY question)
"""
import numpy as np, json, re
from collections import defaultdict

X0, X1 = 1600000000000, 2000000000000
alarms = open(f'hunt_alarms_{X0}_{X1}.txt').read().strip().split('\n')

occ = defaultdict(set)      # (l, g) -> set of starts
for line in alarms:
    m = re.match(r'(?:OCC|FIRST|L6\+!) l=(\d+) g(?:ap)?=(\d+) start=(\d+)', line)
    if m:
        l, g, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
        occ[(l, g)].add(s)

print("=== event counts (distinct starts) ===")
for (l, g) in sorted(occ):
    print(f"l={l} g={g}: {len(occ[(l,g)])}")

print("\n=== 4->5 hazard per hot channel ===")
res = {}
for g in (23, 24, 25):
    n4 = occ.get((4, g), set())
    n5 = occ.get((5, g), set())
    # every run reaching 5 logged l=4 at the same start
    assert n5 <= n4 or not n5, (g, n5 - n4)
    r = len(n5) / len(n4) if n4 else float('nan')
    res[g] = dict(n4=len(n4), n5=len(n5), r45=r)
    print(f"g={g}: 4-runs={len(n4)}  5-runs={len(n5)}  r45={r:.2e}")

print("\n=== ch-25 quintets (fences) ===")
for s in sorted(occ.get((5, 25), set())):
    print(f"  start={s}  mod144={s % 144}  mod5={s % 5}  mod25={s % 25}")

print("\n=== sextets (l>=6) ===")
for (l, g) in sorted(occ):
    if l >= 6:
        for s in sorted(occ[(l, g)]):
            print(f"  l={l} g={g} start={s}  mod8={s%8} mod3={s%3}")

print("\n=== 5-adic mix of ch-25 4-run starts ===")
starts25 = np.array(sorted(occ.get((4, 25), set())), dtype=np.int64)
mod5 = starts25 % 5
for r in range(5):
    print(f"  start ≡ {r} (mod 5): {(mod5 == r).sum()}")
z25 = starts25[mod5 == 0]
if len(z25):
    print(f"  of the ≡0 class, ≡0 mod 25: {(z25 % 25 == 0).sum()} / {len(z25)}")
print("  (a 5-adic throttle at the 5th post can only act on the ≡0-mod-25 class)")

# height drift: quarters of the window
print("\n=== height quarters: ch-25 4-run count + hazard ===")
q = np.linspace(X0, X1, 5).astype(np.int64)
n5set = occ.get((5, 25), set())
for i in range(4):
    m = (starts25 >= q[i]) & (starts25 < q[i+1])
    k4 = int(m.sum())
    k5 = sum(1 for s in n5set if q[i] <= s < q[i+1])
    print(f"  [{q[i]},{q[i+1]}): 4-runs={k4} 5-runs={k5} r45={k5/max(k4,1):.2e}")

# same for ch-24 as control
starts24 = np.array(sorted(occ.get((4, 24), set())), dtype=np.int64)
n5s24 = occ.get((5, 24), set())
print("\n=== ch-24 control, quarters ===")
for i in range(4):
    m = (starts24 >= q[i]) & (starts24 < q[i+1])
    k4 = int(m.sum())
    k5 = sum(1 for s in n5s24 if q[i] <= s < q[i+1])
    print(f"  [{q[i]},{q[i+1]}): 4-runs={k4} 5-runs={k5} r45={k5/max(k4,1):.2e}")

# mod-144 structure of 4-run starts (gate feeder classes)
print("\n=== ch-25 4-run starts mod 144 (top classes) ===")
vals, cnts = np.unique(starts25 % 144, return_counts=True)
order = np.argsort(-cnts)
for j in order[:8]:
    print(f"  ≡ {vals[j]:3d} (mod 144): {cnts[j]}")

# density checkpoint
dens = np.loadtxt(f'hunt_density_{X0}_{X1}.txt')
print(f"\n|S ∩ [X0, {dens[-1,0]:.0f})| = {dens[-1,1]:.0f}")

json.dump({str(k): sorted(int(x) for x in v) for k, v in occ.items()},
          open('atlas46_occ.json', 'w'))
print("saved atlas46_occ.json")

# ---- fertile vs sterile classes (gate anatomy) ----
# l=5 gate: start ≡ 94 (mod 144).  A maximal-or-growing 4-run logged at
# start s was already blocked backward (s-25 ∉ S), so its only hope is the
# forward post s+100, giving a 5-run with the SAME start: fertile ⟺ s ≡ 94.
# The 4-run gate itself allows {94, 103, 110, 119}; the other three classes
# are sterile by arithmetic alone — their fifth bell can never ring.
print("\n=== fertile/sterile anatomy of ch-25 4-runs ===")
fert = starts25[(starts25 % 144 == 94)]
ster = starts25[(starts25 % 144 == 103) | (starts25 % 144 == 110) | (starts25 % 144 == 119)]
other = len(starts25) - len(fert) - len(ster)
print(f"fertile (94): {len(fert)}  sterile (103,110,119): {len(ster)}  other: {other}")
n5 = sorted(occ.get((5, 25), set()))
print(f"quintets: {len(n5)}  -> conditional hazard r45|fertile = "
      f"{len(n5)/max(len(fert),1):.2e}  (vs raw {len(n5)/max(len(starts25),1):.2e})")
for i in range(4):
    mf = ((fert >= q[i]) & (fert < q[i+1])).sum()
    ms = ((ster >= q[i]) & (ster < q[i+1])).sum()
    print(f"  quarter {i+1}: fertile={mf} sterile={ms} fertile_frac={mf/max(mf+ms,1):.3f}")
# ch-24 comparison: gate classes for l=4 g=24?
print("\n=== ch-24 4-run starts mod 144 (top classes) ===")
vals4, cnts4 = np.unique(starts24 % 144, return_counts=True)
order4 = np.argsort(-cnts4)
for j in order4[:10]:
    print(f"  ≡ {vals4[j]:3d} (mod 144): {cnts4[j]}")
