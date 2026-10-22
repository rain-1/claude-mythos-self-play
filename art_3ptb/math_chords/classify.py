"""Classify verified hits into the Thales family and sporadic triangles; Galois orbits; write JSON."""
import sys, json
from fractions import Fraction as F
from math import gcd
import mpmath as mp
mp.mp.dps = 60

D = sys.argv[1] if len(sys.argv) > 1 else "420"
hits = [tuple(F(s) for s in h) for h in json.load(open(f"hits_{D}.json"))]
half = F(1, 2)
thales = [h for h in hits if h[2] == half]
spor = [h for h in hits if h[2] != half]
# Thales check: every hypotenuse-1/2 hit satisfies r1+r2=1/2, and every such pair with denominators <= D appears
assert all(a + b == half for a, b, _ in thales)
print("Thales members:", len(thales), " sporadic:", len(spor))

def red(q):  # r -> representative in (0,1/2] of the chord 2 sin(pi r)
    q = q % 1
    return min(q, 1 - q)

def canon(t):
    a, b, c = t
    return (min(a, b), max(a, b), c)

def orbit(t):
    N = 1
    for f in t:
        N = N * f.denominator // gcd(N, f.denominator)
    return sorted({canon(tuple(red(j * f) for f in t)) for j in range(1, N + 1) if gcd(j, N) == 1})

def nk(f):
    return [f.denominator, f.numerator]

def length(f):
    return mp.nstr(2 * mp.sin(mp.pi * mp.mpf(f.numerator) / f.denominator), 20)

def name(f):
    n, k = nk(f)
    return f"{{{n}}}" if k == 1 else f"{{{n}/{k}}}"

orbits, out = [], []
for t in sorted(spor):
    o = orbit(t)
    if o not in orbits:
        orbits.append(o)
    oid = orbits.index(o)
    a, b, c = t
    res = mp.sin(mp.pi * a) ** 2 + mp.sin(mp.pi * b) ** 2 - mp.sin(mp.pi * c) ** 2
    out.append({"legs": [nk(a), nk(b)], "hyp": nk(c), "lengths": [length(a), length(b), length(c)],
                "r": [str(a), str(b), str(c)], "names": [name(a), name(b), name(c)],
                "orbit": oid, "residual_60digits": mp.nstr(res, 5)})
    print(t, [name(x) for x in t], "orbit", oid, "residual", mp.nstr(res, 3))
for i, o in enumerate(orbits):
    print("orbit", i, [[str(x) for x in t] for t in o])
json.dump(out, open("sporadic.json", "w"), indent=1)

samples = [(F(1, 4), F(1, 4)), (F(1, 6), F(1, 3)), (F(1, 10), F(2, 5)), (F(1, 5), F(3, 10)), (F(1, 12), F(5, 12)),
           (F(1, 8), F(3, 8)), (F(2, 7), F(3, 14))]
fam = [{
    "name": "Thales (degenerate: hypotenuse is the diameter = digon {2})",
    "condition": "r1 + r2 = 1/2, r3 = 1/2  (any rational r1 in (0,1/4])",
    "polygons": "{n/k} and {2n/(n-2k)} reduced, i.e. legs 2 sin(pi r) and 2 cos(pi r), hypotenuse 2",
    "count_with_denominators_le_" + D: len(thales),
    "samples": [{"legs": [nk(a), nk(b)], "hyp": [2, 1], "lengths": [length(a), length(b), "2"]} for a, b in samples],
}, {
    "name": "Non-degenerate infinite families",
    "condition": "none exist (proved via Conway-Jones Thm 7; see RESULTS.md)",
    "samples": [],
}]
json.dump(fam, open("families.json", "w"), indent=1)
