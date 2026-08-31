#!/usr/bin/env python3
"""Apply the pre-committed verdict rules (atlas49_precommit.md) to the final
analyze48 results.  Writes atlas49_verdict.json (ledger lines for the panel)
and atlas49_verdict.txt (prose verdict)."""
import json

R = json.load(open("atlas49_results.json"))
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
    lines.append(f"VERDICT ({frac*100:.1f}% of window scanned, judged vs atlas49_precommit.md): every gate held — "
                 f"4-run classes {n4}/{n4} in {{94,103,110,119}}, fences {N25}/{N25} ≡ 94, "
                 f"sextet gate ✓, 5-adic {R['l4g25']['mod5_zero']}/{R['l4g25']['mod25_zero']} all ≡ 0 (mod 25).")
# ch-25 rule (atlas49_precommit: E≈0.92 per 2e11; 0 is modal)
if N25 <= 2: v25 = f"N25 = {N25}: long-run band (E≈0.92 for this half-window); nothing to report but the count."
else: v25 = f"N25 = {N25}: warm streak worth a note (≥3σ over E≈0.92)."
r45f = R["r45_25_fertile"]
r45s = f"{r45f:.2e}" if r45f else f"0/{fert}"
lines.append(f"ch-25: {v25}  r45|94 4th point = {r45s} (series 1.18e-2 / 2.4e-2 / 1.22e-2).")
# ch-23 rule (atlas49_precommit: cold E 0.8–2, base 2.4–4)
if N23 <= 2: v23 = f"N23 = {N23}: cold shift SETTLED — third consecutive low window."
elif N23 <= 5: v23 = f"N23 = {N23}: back to base weather; the cold shift was two windows of weather."
else: v23 = f"N23 = {N23}: REHEAT — flag for next run."
lines.append(f"ch-23: {v23}   ch-24: N24 = {N24} (band 34–52 for this half-window).")
lines.append(f"fertile share {ff:.3f} (band 0.17±0.04)  ·  |S∩window| = {S:,}  ·  "
             f"sextets: {len(sx)} {sx if sx else ''}")
json.dump({"ledger": lines}, open("atlas49_verdict.json", "w"))
open("atlas49_verdict.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
