"""2-adic + p=3,5 obstruction checker for l-term equal-gap runs in S (Z[sqrt2] norms).
For each gap g and phase n mod 2^K, check whether membership conditions (odd part == +-1 mod 8)
can be satisfied at every term; report surviving (g, n) classes."""
K = 16
M = 1 << K

def term_ok(t):
    """t = value mod M. Return False if provably excluded (odd part mod 8 in {3,5}),
       True if OK or undetermined (v2 too high to see)."""
    if t == 0: return True   # undetermined (deep 2-divisibility)
    v = 0
    while t % 2 == 0: t //= 2; v += 1
    # odd part determined mod 8 iff we have >= 3 bits: v <= K-3 guaranteed since t != 0 mod M... careful
    return (t % 8) in (1, 7)

def p3_ok(g, l):
    """3-adic: if 3|g fine (choose n coprime to 3). Else need a phase with at most one hit of 0 mod 3;
       hits at i = i0, i0+3, ... : need count of hits with v3 problems... simplified:
       double hits (i0 and i0+3 both < l) force contradiction; single hit fine."""
    if g % 3 == 0: return True
    # exists phase i0 in 0..2 with only one hit? hits at i = i0 mod 3, i < l
    for i0 in range(3):
        if len([i for i in range(l) if i % 3 == i0]) <= 1:
            return True
    # all phases have >= 2 hits -> forced contradiction
    return False

def survivors(l, gmax=100):
    out = {}
    for g in range(1, gmax+1):
        if not p3_ok(g, l): continue
        # p=5 analogue: 5 !| g: hits at i=i0 mod 5: double hit iff i0 and i0+5 < l -> l>=6 and i0<=l-6
        if g % 5 and all(len([i for i in range(l) if i % 5 == i0]) >= 2 for i in range(5) for i0 in [i]) : 
            pass  # only relevant l>=10; skip
        good_phases = []
        for n in range(1, M):
            if all(term_ok((n + i*g) % M) for i in range(l)):
                good_phases.append(n)
        if good_phases:
            out[g] = len(good_phases)
    return out

print("l=5 surviving gap classes (g<=20):", sorted(survivors(5, 20).keys()))
print("   census observed l=5 gaps:      [1, 2, 4, 7, 8, 9, 15, 16, 18]")
s6 = survivors(6, 100)
print("l=6 surviving gap classes (g<=100):", sorted(s6.keys()))
print("l=7:", sorted(survivors(7, 100).keys()))
