"""
class_relations.py — rule out integer relations between same-class rim angles.

For a closed rim ring, the Galois argument forces, for each radical class d>1:
    sum of that class's angles == 0 (mod pi).
A class consisting of a single angle value theta with theta/pi irrational
(cos theta not in {0, +-1/2, +-1}: Niven) can then never appear.
A class with several DISTINCT angle values theta_1..theta_k could only appear
through an integer relation  sum m_i theta_i == 0 (mod pi), m_i >= 0, not all 0.
This script searches for such relations with PSLQ over [theta_1/pi, ..., 1]
at 100 dps with coefficient bound 10^6; finding none (and the thetas being
Niven-irrational) certifies-with-evidence that the class is unusable.

Classes whose angles are all rational multiples of pi (d=1 and the pi/3 class)
are handled exactly in the text.
"""

from fractions import Fraction
from mpmath import mp, mpf, acos, pi, pslq, nstr
from engine import cos_theta, _squarefree_split

mp.dps = 100
K = 9

classes = {}
for p in range(2, K + 1):
    for q in range(p, K + 1):
        c = cos_theta(p, q)
        s2 = 1 - c * c
        if s2 == 0:
            d = 1
        else:
            _, d = _squarefree_split(s2.numerator * s2.denominator)
        classes.setdefault(d, {}).setdefault(c, []).append((p, q))

NIVEN = {Fraction(0), Fraction(1, 2), Fraction(-1, 2), Fraction(1), Fraction(-1)}

print(f"=== radical classes, curvatures 2..{K} ===")
for d in sorted(classes):
    vals = classes[d]
    names = {c: v for c, v in vals.items()}
    print(f"\nclass sqrt({d}): {sum(len(v) for v in vals.values())} pairs, "
          f"{len(vals)} distinct angles")
    for c, prs in sorted(vals.items()):
        tag = "RATIONAL-PI" if c in NIVEN else "irrational multiple of pi (Niven)"
        print(f"   cos={c}  pairs={prs}  [{tag}]")
    if d == 1:
        print("   -> class 1: exact analysis in Q(i) (see verification.md)")
        continue
    irr = [c for c in vals if c not in NIVEN]
    if len(irr) == 0:
        print("   -> all angles rational multiples of pi: usable with counting condition")
        continue
    if len(irr) == 1 and len(vals) == 1:
        print("   -> single Niven-irrational angle: sum m*theta = 0 mod pi forces m=0."
              "  CLASS UNUSABLE in any exact ring.")
        continue
    # distinct angles: PSLQ for relations among [theta_i/pi, 1]
    thetas = [acos(mpf(c.numerator) / mpf(c.denominator)) for c in sorted(irr)]
    vec = [t / pi for t in thetas] + [mpf(1)]
    rel = pslq(vec, maxcoeff=10**6, maxsteps=10**6)
    if rel is None:
        print("   -> PSLQ finds NO integer relation (coeffs <= 1e6, 100 dps):"
              " no combination of these angles is a multiple of pi."
              "  CLASS UNUSABLE (evidence-grade).")
    else:
        # check whether the relation is realizable with all-nonnegative counts
        print(f"   -> PSLQ RELATION FOUND: {rel}  — check realizability!")
        val = sum(r * v for r, v in zip(rel, vec))
        print(f"      residual {nstr(abs(val), 4)}")
        same = all(abs(thetas[i] - thetas[0]) < mpf(10) ** -90
                   for i in range(1, len(thetas)))
        if same:
            print("      (equal angles: relation is m+n=0 -> unusable with m,n>=0)")
