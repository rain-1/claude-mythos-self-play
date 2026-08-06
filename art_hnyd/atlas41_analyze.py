"""Atlas piece 41 analysis: compare 1e11 census run tables vs 3.2e10 (piece 40).
Channel-17 verdict + per-channel growth + l=6 check + records."""
import re, json

def parse_rungap(path):
    out = {}
    for line in open(path):
        m = re.match(r"l=(\d+) g=(\d+) maximal_runs=(\d+) first_start=(\d+)", line)
        if m:
            l, g, c, f = map(int, m.groups())
            out[(l, g)] = (c, f)
    return out

new = parse_rungap("deep_rungap.txt")
old = parse_rungap("prev_deep_rungap.txt")

stdout = open("census_1e11_stdout.txt").read()
m = re.search(r"X=(\d+) \|S\|=(\d+)", stdout)
X, Scount = int(m.group(1)), int(m.group(2))
print(f"X = {X:.3e}  |S| = {Scount:,}  density = {Scount/X:.4f}")

# l>=5 per gap: counts are 'maximal runs of exactly l'; a run of 6 would appear as l=6.
print("\nl=5 fences (maximal runs) per gap: old(3.2e10) -> new(1e11), first occurrence")
gaps = sorted({g for (l, g) in set(new) | set(old) if l >= 5})
tot_old = tot_new = 0
for g in gaps:
    co, fo = old.get((5, g), (0, 0))
    cn, fn = new.get((5, g), (0, 0))
    tot_old += co; tot_new += cn
    print(f"  g={g:3d}: {co:6d} -> {cn:6d}   first at {fn:,}" + ("  (NEW CHANNEL!)" if co == 0 and cn > 0 else ""))
print(f"  total: {tot_old} -> {tot_new}  (growth x{tot_new/max(tot_old,1):.2f})")

# channel 17 verdict
c17 = new.get((5, 17), (0, 0))[0]
print(f"\nCHANNEL 17: {'SPOKE! ' + str(new[(5,17)]) if c17 else 'STILL SILENT at 1e11'}")
c14 = new.get((5, 14), (0, 0))
print(f"CHANNEL 14: {c14[0]} fences, first at {c14[1]:,}")
for g in (23, 24, 25):
    c = new.get((5, g), (0, 0))
    print(f"CHANNEL {g}: {c[0]} fences" + (f", first at {c[1]:,}" if c[0] else " (silent)"))

# growth-calibrated debt of channel 17:
# E17(1e11) = E17(3.2e10) * (observed total growth of speaking channels)
grow = tot_new / max(tot_old, 1)
E17_32 = 5.5   # piece-40 calibration: E[W5(17)] ~ 5-6 below 3.2e10
E17 = E17_32 * grow
import math
print(f"\nDEBT: E[W5(17)](1e11) ~ {E17_32} x {grow:.2f} = {E17:.1f}"
      f"  -> P(silence) ~ exp(-{E17:.1f}) = {math.exp(-E17):.2e}" if c17 == 0 else "")

# l = 6
l6 = [(g, c) for (l, g), (c, f) in new.items() if l >= 6]
print("\nl>=6 runs:", l6 if l6 else "NONE (theorem 24|g + iid est >1e13 stand)")

# l=4 counts for the far-channel record
print("\nl=4 counts (selected gaps):")
for g in sorted({g for (l, g) in new if l == 4}):
    co = old.get((4, g), (0, 0))[0]
    cn, fn = new[(4, g)]
    print(f"  g={g:3d}: {co:8d} -> {cn:8d}  first {fn:,}")

# records
print("\nrecords file:")
print(open("deep_records.txt").read())
print("g14/17 events:")
print(open("deep_g14_17.txt").read())

json.dump({"X": X, "S": Scount,
           "l5": {str(g): dict(old=old.get((5, g), (0, 0)), new=new.get((5, g), (0, 0))) for g in gaps},
           "growth": grow, "E17": E17},
          open("atlas41_data.json", "w"), indent=1)
