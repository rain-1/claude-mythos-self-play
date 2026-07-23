import json, numpy as np
from enumerate import canon, ROT_E, apply_ep, connected, three_dim
d = json.load(open('enum.json'))
reps = d['reps']
rset = set(reps)
FULL = 4095
covers = []   # (lower_class, upper_class) by adding one edge
for r in reps:
    k = bin(r).count('1')
    ups = set()
    for e in range(12):
        if not (r >> e & 1):
            m2 = r | (1 << e)
            if m2 == FULL:
                ups.add(FULL)
            else:
                c2 = canon(m2, ROT_E)
                # adding an edge keeps 3dim; connectivity may FAIL if new edge is isolated? no—it touches vertices; but new edge might attach to nothing → disconnected
                if c2 in rset:
                    ups.add(c2)
    for u in ups:
        covers.append((r, u))
print("cover relations:", len(covers))
# every class should reach FULL eventually; check every class has at least one upward cover
uppers = {}
for a,b in covers: uppers.setdefault(a, []).append(b)
noup = [r for r in reps if r not in uppers]
print("classes with no upward cover:", len(noup))
# and downward: every class with k>3 should be coverable from below? not necessarily (removing an edge may disconnect ALL ways?) — report
downs = {}
for a,b in covers:
    if b != FULL: downs.setdefault(b, []).append(a)
nodown = [r for r in reps if bin(r).count('1')>3 and r not in downs]
print("classes (k>3) with no downward cover:", [ (r,bin(r).count('1')) for r in nodown ])
json.dump(covers, open('covers.json','w'))
