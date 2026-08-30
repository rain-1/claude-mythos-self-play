#!/usr/bin/env python3
"""Apply the pre-committed verdict rules (atlas48_precommit.md) to the final
analyze48 results.  Writes atlas48_verdict.json (ledger lines for the panel)
and atlas48_verdict.txt (prose verdict)."""
import json

R = json.load(open("atlas48_results.json"))
frac = R["frac_of_window"]
scale = frac                      # expectations were stated for the full window
N25 = len(R["fences25"]["starts"])
N24 = R["fences24"]["count"]
N23 = R["fences23"]["count"]
n4 = R["l4g25"]["count"]
fert = R["l4g25"]["fertile"]
ff = R["l4g25"]["fertile_frac"]
sx = R["sextets"]["starts"]
viol = len(R["l4g25"]["violations"])
gate25ok = R["fences25"]["all_94"]
sxok = R["sextets"]["gate_ok"]
S = R["S_count"]

lines = []
# gates first (override)
gates_ok = (viol == 0) and gate25ok and sxok and \
           R["l4g25"]["mod5_zero"] == R["l4g25"]["mod25_zero"]
if not gates_ok:
    lines.append("A GATE BROKE — see results json; this overrides everything.")
else:
    lines.append(f"VERDICT ({frac*100:.1f}% of window scanned, judged vs atlas48_precommit.md): every gate held — "
                 f"4-run classes {n4}/{n4} in {{94,103,110,119}}, fences {N25}/{N25} ≡ 94, "
                 f"sextet gate ✓, 5-adic {R['l4g25']['mod5_zero']}/{R['l4g25']['mod25_zero']} all ≡ 0 (mod 25).")
# ch-25 rule
if N25 <= 1: v25 = "N25 ≤ 1: piece 47's “warm again” call was weather; the cold long-run rate stands."
elif N25 <= 3: v25 = f"N25 = {N25}: in the long-run band (E≈2.1); the warm call of piece 47 is unsupported."
elif N25 <= 6: v25 = f"N25 = {N25}: the WARM STREAK IS REAL — two consecutive warm windows (warm E≈4.7)."
else: v25 = f"N25 = {N25}: loudening beyond even the warm model."
r45f = R["r45_25_fertile"]
lines.append(f"ch-25: {v25}  r45|94 = {r45f:.2e} (vs 1.18e-2 piece 46, 2.4e-2 piece 47).")
# ch-23 rule
if N23 <= 4: v23 = f"N23 = {N23}: COLD SHIFT CONFIRMED — two consecutive lows; the 08-27 “loudening” is dead."
elif N23 <= 10: v23 = f"N23 = {N23}: base weather."
elif N23 >= 13: v23 = f"N23 = {N23}: the loud window was real after all; 08-28's quiet quarter was the fluke."
else: v23 = f"N23 = {N23}: indeterminate."
lines.append(f"ch-23: {v23}   ch-24: N24 = {N24} (band 105–135 full-window).")
lines.append(f"fertile share {ff:.3f} (band 0.17±0.03)  ·  |S∩window| = {S:,}  ·  "
             f"sextets: {len(sx)} {sx if sx else ''}")
json.dump({"ledger": lines}, open("atlas48_verdict.json", "w"))
open("atlas48_verdict.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
