"""Parse this run's hunt output files -> atlas44_results.md + checks."""
import glob, re

out = ["# Atlas 44 — scan results (generated post-hunt)\n"]
for rg in sorted(glob.glob('hunt_rungap_8*txt')) + sorted(glob.glob('hunt_rungap_1*txt')):
    m = re.match(r'hunt_rungap_(\d+)_(\d+)\.txt', rg)
    lo, hi = int(m.group(1)), int(m.group(2))
    lines = open(rg).read().splitlines()
    head = lines[0]
    want = [l for l in lines if re.match(r'l=[3456] g=(24|25|48) ', l)]
    out.append(f"## window [{lo:.3g}, {hi:.3g})\n{head}\n" + "\n".join(want) + "\n")
    d = {}
    for l in want:
        mm = re.match(r'l=(\d) g=(\d+) maximal_runs=(\d+)', l)
        if mm: d[(int(mm.group(1)), int(mm.group(2)))] = int(mm.group(3))
    if (3,25) in d and (4,25) in d:
        out.append(f"drift r34(25) this window: {d[(4,25)]/d[(3,25)]:.3e}\n")
for al in sorted(glob.glob('hunt_alarms_8*txt')) + sorted(glob.glob('hunt_alarms_1*txt')):
    out.append(f"## {al}\n")
    for line in open(al):
        line = line.strip()
        out.append(line)
        mm = re.search(r'l=(\d+) g=?(?:ap)?=?(\d+) start=(\d+)', line)
        if mm:
            l_, g_, s_ = int(mm.group(1)), int(mm.group(2)), int(mm.group(3))
            if g_ == 25 and l_ >= 5:
                out.append(f"   -> mod 144 = {s_ % 144} (gate demands 94)")
            if l_ >= 6:
                out.append(f"   -> SEXTET/beyond: mod 16 = {s_%16}, mod 9 = {s_%9} (gate: ±1 mod 8, ≢0 mod 3)")
    out.append("")
open('atlas44_results.md','w').write("\n".join(out))
print("\n".join(out))
