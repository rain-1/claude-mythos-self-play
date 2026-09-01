#!/usr/bin/env python3
"""Atlas 50 verdict per atlas50_precommit.md (rules written BEFORE the scan).
Reads atlas50_results.json; writes atlas50_verdict.json / .txt"""
import json

R = json.load(open("atlas50_results.json"))
frac = R["frac_of_window"]
led = []

g = R["l4g25"]
viol = len(g["violations"])
gate_line = (f"every gate held — 4-run classes {g['count']-viol}/{g['count']} in "
             f"{{94,103,110,119}}, fences {len(R['fences25']['starts'])}/"
             f"{len(R['fences25']['starts'])} ≡ 94, sextet gate "
             f"{'✓' if R['sextets']['gate_ok'] else 'VIOLATED'}, "
             f"5-adic {g['mod25_zero']}/{g['mod5_zero']} all ≡ 0 (mod 25).")
if viol or not R["fences25"]["all_94"] or not R["sextets"]["gate_ok"]:
    gate_line = "GATE VIOLATION — see results json; treat as engine bug until proven (precommit rule)."
led.append(f"VERDICT ({frac*100:.1f}% of window scanned, judged vs atlas50_precommit.md): {gate_line}")

n25 = len(R["fences25"]["starts"])
if n25 <= 2:
    s25 = f"ch-25: N25 = {n25}: long-run band (E≈0.93·{frac:.2f}); the count is the report."
else:
    s25 = f"ch-25: N25 = {n25}: warm streak (≥3σ over E≈0.93) — noted for piece 51."
r45f = R["r45_25_fertile"]
series = "1.18e-2 / 2.4e-2 / 1.22e-2 / 1.04e-2"
if r45f is not None:
    last4 = [2.4e-2, 1.22e-2, 1.04e-2, r45f]
    mono = all(a > b for a, b in zip(last4, last4[1:])) or all(a < b for a, b in zip(last4, last4[1:]))
    trend = "monotone over the last four — trend note earned" if mono else "scatter, no trend"
    s25 += f"  r45|94 5th point = {r45f:.2e} (series {series}; {trend})."
led.append(s25)

n23 = R["fences23"]["count"]
if n23 <= 1:
    s23 = f"ch-23: N23 = {n23}: quiet — consistent with either reading; still weather until a run of lows."
elif n23 <= 4:
    s23 = f"ch-23: N23 = {n23}: base weather CONFIRMED; the cold-shift chapter is closed."
else:
    s23 = f"ch-23: N23 = {n23}: warm swing — the channel is noisy at this width; widen next window."
led.append(s23 + f"   ch-24: N24 = {R['fences24']['count']} (band 34–56).")

sx = R["sextets"]["starts"]
if sx:
    s6 = f"SEXTET #{5+len(sx)}: {', '.join(f'{s:,}' for s in sx)} — the drought ends."
else:
    s6 = "sextets: 0 — drought now 3 windows (9e11); Poisson P(0)≈0.26 at E≈0.45/window: a note, not a shift."
led.append(f"fertile share {g['fertile_frac']:.3f} (band 0.17±0.04)  ·  "
           f"|S∩window| = {R['S_count']:,}  ·  {s6}")

rare = [f for f in R["firsts"] if "g=14" in f or "g=17" in f]
if rare:
    led.append("rare-channel firsts in-window: " +
               " · ".join(f.replace("FIRST l=5 ", "ch-").replace(" start=", " fence ")
                          .replace("g=", "") for f in rare))

json.dump({"ledger": led}, open("atlas50_verdict.json", "w"))
open("atlas50_verdict.txt", "w").write("\n".join(led) + "\n")
print("\n".join(led))
