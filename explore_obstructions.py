"""
explore_obstructions.py  --  verify the AP good-step obstruction across the
four class-number-one imaginary quadratic rings done so far in this project:

    Heegner -1 : Z[i]              N(a,b) = a^2 + b^2
    Heegner -2 : Z[sqrt(-2)]       N(a,b) = a^2 + 2 b^2          <- the new ring
    Heegner -3 : Z[omega]          N(a,b) = a^2 - a b + b^2
    Heegner -7 : Z[(1+sqrt-7)/2]   N(a,b) = a^2 + a b + 2 b^2

"Prime point" = lattice point (a,b) whose norm is a rational prime.
"Good step" (da,db) = a step with nonzero PAIR CORRELATION: many (a,b) with
both (a,b) and (a+da, b+db) prime. The set of good steps is the AP obstruction
structure; it is dictated by the ramified prime of each ring.
"""
import numpy as np

# --- a prime sieve over the norms we will see -------------------------------
def sieve(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i*i::i] = False
    return s

RINGS = {
    "Z[i]  (-1)":            lambda a, b: a*a + b*b,
    "Z[sqrt-2]  (-2)":       lambda a, b: a*a + 2*b*b,
    "Z[omega]  (-3)":        lambda a, b: a*a - a*b + b*b,
    "Z[(1+sqrt-7)/2] (-7)":  lambda a, b: a*a + a*b + 2*b*b,
}

W = 220                       # half-window for the (a,b) lattice
R = 8                         # step window [-R..R]^2
aa, bb = np.mgrid[-W:W+1, -W:W+1]
NMAX = int((2*W)**2 * 3) + 10
isp = sieve(NMAX)

for name, Nf in RINGS.items():
    norm = Nf(aa, bb)
    prime = (norm >= 2) & (norm <= NMAX) & isp[np.clip(norm, 0, NMAX)]
    # pair-correlation C(da,db) over the step window
    C = np.zeros((2*R+1, 2*R+1), float)
    for i, da in enumerate(range(-R, R+1)):
        for j, db in enumerate(range(-R, R+1)):
            sh = np.roll(np.roll(prime, -da, 0), -db, 1)
            # zero the wrapped border so rolled-in points are not counted
            m = prime & sh
            if da > 0:   m[-da:, :] = False
            elif da < 0: m[:-da, :] = False
            if db > 0:   m[:, -db:] = False
            elif db < 0: m[:, :-db] = False
            C[i, j] = m.sum()
    good = C > (0.05 * C.max())          # steps with real pair correlation
    # characterise the good-step sublattice by parity / mod-3 membership
    das, dbs = np.where(good)
    das = das - R; dbs = dbs - R
    pset = {(int(x) % 2, int(y) % 2) for x, y in zip(das, dbs)}
    p3 = {(int(x) % 3, int(y) % 3) for x, y in zip(das, dbs)}
    print(f"\n=== {name} ===")
    print(f"  prime points in window: {prime.sum()}")
    print(f"  good-step (da,db) parities present (da%2,db%2): {sorted(pset)}")
    # decide condition
    if pset == {(0, 0)}:
        cond = "da == 0 AND db == 0  (mod 2)   [strictest, 2Z x 2Z]"
    elif pset == {(0, 0), (1, 1)}:
        cond = "da == db (mod 2)              [diagonal checkerboard]"
    elif all(x == 0 for x, y in pset) and {y for x, y in pset} == {0, 1}:
        cond = "da == 0 (mod 2), db free       [vertical stripes]"
    else:
        cond = f"(see mod-3 set) parities={sorted(pset)}  mod3={sorted(p3)}"
    print(f"  => GOOD-STEP CONDITION: {cond}")
