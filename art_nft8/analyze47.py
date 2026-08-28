#!/usr/bin/env python3
"""Atlas 47 analysis from the live alarm + density streams.
Usage: python3 analyze47.py   (reads hunt_alarms_*, hunt_density_*)
Writes atlas47_results.json and prints the human summary."""
import json, glob, sys

AL = 'hunt_alarms_2000000000000_2400000000000.txt'
DE = 'hunt_density_2000000000000_2400000000000.txt'

occ4 = {23: [], 24: [], 25: []}
occ5 = {23: [], 24: [], 25: []}
occ6 = {23: [], 24: [], 25: []}
firsts = []
for line in open(AL):
    p = line.split()
    if p[0] in ('OCC', 'FIRST', 'L6+!'):
        if p[0] == 'FIRST':
            firsts.append(line.strip())
            continue
        l = int(p[1].split('=')[1]); g = int(p[2].split('=')[1])
        s = int(p[3].split('=')[1])
        if g in occ4:
            if l == 4: occ4[g].append(s)
            elif l == 5: occ5[g].append(s)
            elif l >= 6: occ6[g].append(s)

lastX, lastS = 0, 0
for line in open(DE):
    a = line.split()
    if len(a) >= 2 and a[0].isdigit():
        lastX, lastS = int(a[0]), int(a[1])

res = {'scanned_to': lastX, 'S_count': lastS,
       'frac_of_window': (lastX-2.0e12)/4e11}

# ch-25 gate census on l=4 occurrences
g25 = occ4[25]
mods = [s % 144 for s in g25]
gate = {94, 103, 110, 119}
viol = [s for s, m in zip(g25, mods) if m not in gate]
cls = {c: mods.count(c) for c in sorted(set(mods))}
fertile = mods.count(94)
res['l4g25'] = {'count': len(g25), 'classes': cls, 'violations': viol,
                'fertile': fertile,
                'fertile_frac': fertile/len(g25) if g25 else None}
# 5-adic depletion
m5 = [s for s in g25 if s % 5 == 0]
res['l4g25']['mod5_zero'] = len(m5)
res['l4g25']['mod25_zero'] = len([s for s in m5 if s % 25 == 0])

# fences
f25 = occ5[25]
res['fences25'] = {'starts': f25, 'mod144': [s % 144 for s in f25],
                   'all_94': all(s % 144 == 94 for s in f25)}
res['fences24'] = {'count': len(occ5[24])}
res['fences23'] = {'count': len(occ5[23]), 'starts': occ5[23]}
# r45
res['r45_25'] = len(f25)/len(g25) if g25 else None
res['r45_25_fertile'] = len(f25)/fertile if fertile else None
res['r45_24'] = len(occ5[24])/len(occ4[24]) if occ4[24] else None
res['r45_23'] = len(occ5[23])/len(occ4[23]) if occ4[23] else None
res['l4_counts'] = {g: len(occ4[g]) for g in occ4}

# sextets (l>=6 g=24)
sx = sorted(set(occ6[24]))
res['sextets'] = {'starts': sx,
                  'gate_ok': all(s % 8 in (1, 7) and s % 3 != 0 for s in sx)}
res['firsts'] = firsts

json.dump(res, open('atlas47_results.json', 'w'), indent=1)
f = res
print(f"scanned to {lastX:,} ({res['frac_of_window']*100:.1f}% of window), |S∩[2e12,X)| = {lastS:,}")
print(f"l=4 g=25: {len(g25)} occurrences; classes {cls}; violations: {len(viol)}")
print(f"  fertile(94): {fertile} ({res['l4g25']['fertile_frac']:.3f}); mod5=0: {len(m5)} (mod25: {res['l4g25']['mod25_zero']})")
print(f"ch-25 fences: {len(f25)} at {f25} mod144={res['fences25']['mod144']}")
print(f"r45(25) = {res['r45_25']:.2e}" if f25 else "r45(25) = 0")
print(f"r45|94 = {res['r45_25_fertile']:.3e}" if fertile and f25 else f"r45|94 = 0/{fertile}")
print(f"ch-24 fences {len(occ5[24])} (l4: {len(occ4[24])}), ch-23 fences {len(occ5[23])} (l4: {len(occ4[23])})")
print(f"sextets: {sx} gate_ok={res['sextets']['gate_ok']}")
