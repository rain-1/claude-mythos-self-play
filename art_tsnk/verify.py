"""Verification battery for the triptych WHAT RETURNS IN FIVE.

Three worlds, one recurrence  y_{i+1} = (1 + y_i) / y_{i-1}  (Lyness / cluster A2):
  1. Lyness map on the plane: EVERY orbit has exact period 5 (Zamolodchikov).
  2. Conway-Coxeter friezes: diamond rule ad-bc=1, glide symmetry, positivity.
  3. Gauss pentagramma mirificum: polar-arc construction closes after 5 steps,
     and the tan^2 of the five arcs satisfy the Lyness recurrence.
"""
from fractions import Fraction
import random, math
import numpy as np

random.seed(5)
ok = lambda name, cond: print(("PASS " if cond else "FAIL ") + name) or cond

ALL = True

# ---------------------------------------------------------------- 1. LYNESS
def lyness(p):
    x, y = p
    return (y, (y + 1) / x)

# exact rational 5-periodicity, 2000 random seeds incl. negatives
fails = 0
for _ in range(2000):
    x = Fraction(random.randint(-10**6, 10**6), random.randint(1, 10**6))
    y = Fraction(random.randint(-10**6, 10**6), random.randint(1, 10**6))
    if x == 0 or y == 0 or y == -1 or x + y + 1 == 0 or x == y:  # avoid singular set & fixed pts
        continue
    p0 = (x, y)
    p = p0
    period1 = False
    try:
        for k in range(5):
            p = lyness(p)
            if k < 4 and p == p0:
                period1 = True
    except ZeroDivisionError:
        continue  # orbit passed through the singular set (measure zero)
    if p != p0 or period1:
        fails += 1
ALL &= ok(f"Lyness: exact period 5 (Fraction arithmetic), fails={fails}", fails == 0)

# invariant K = (x+1)(y+1)(x+y+1)/(xy) constant along orbits (exact)
def K(p):
    x, y = p
    return (x + 1) * (y + 1) * (x + y + 1) / (x * y)

bad = 0
for _ in range(300):
    x = Fraction(random.randint(1, 10**4), random.randint(1, 10**4))
    y = Fraction(random.randint(1, 10**4), random.randint(1, 10**4))
    p = (x, y); k0 = K(p)
    for _ in range(5):
        p = lyness(p)
        if K(p) != k0:
            bad += 1
ALL &= ok(f"Lyness: invariant (x+1)(y+1)(x+y+1)/(xy) exactly constant, bad={bad}", bad == 0)

# fixed point is the golden ratio; rotation number of the linearization
phi = (1 + 5**0.5) / 2
fp_res = abs((phi + 1) / phi - phi)
ALL &= ok(f"fixed point (φ,φ): residual {fp_res:.2e}", fp_res < 1e-15)
# Jacobian of (x,y)->(y,(y+1)/x) at (φ,φ): [[0,1],[-(y+1)/x^2, 1/x]]
J = np.array([[0.0, 1.0], [-(phi + 1) / phi**2, 1 / phi]])
ev = np.linalg.eigvals(J)
theta = math.atan2(ev[0].imag, ev[0].real)
rot = abs(theta) / (2 * math.pi)
ALL &= ok(f"rotation number at φ: {rot:.6f} (=1/5? {abs(rot-0.2)<1e-9})", abs(rot - 0.2) < 1e-9)
Kphi = (phi + 1) ** 2 * (2 * phi + 1) / phi**2
print(f"      K at the golden point = {Kphi:.6f}  (min of K on the positive quadrant)")

# ---------------------------------------------------------------- 2. FRIEZE
def random_triangulation(n):
    """Random triangulation of an n-gon as a list of triangles (recursive split)."""
    tris = []
    def rec(poly):
        if len(poly) < 3: return
        if len(poly) == 3:
            tris.append(tuple(poly)); return
        i = 0; j = random.randint(2, len(poly) - 1) if len(poly) > 3 else 2
        # pick random ear split: choose vertex k strictly between ends of edge (0, len-1)?
        # simpler: fan split at random diagonal from vertex 0
        k = random.randint(1, len(poly) - 2)
        # triangle (poly[0], poly[k], poly[-1]) splits polygon edge (0,-1)
        tris.append((poly[0], poly[k], poly[-1]))
        rec(poly[:k + 1])
        rec(poly[k:])
    rec(list(range(n)))
    return tris

def quiddity(n, tris):
    q = [0] * n
    for t in tris:
        for v in t:
            q[v] += 1
    return q

def build_frieze(q, rows_extra=None):
    """Frieze from quiddity row. Row 0 = 1s, row 1 = quiddity,
    row r+1[i] = (row r[i]*row r[i+1] - 1)/row r-1[i+1]  (SE-diamond rule).
    Returns list of rows (each length n, periodic index)."""
    n = len(q)
    width = n - 3  # nontrivial rows between the two rows of 1s
    rows = [[Fraction(1)] * n, [Fraction(x) for x in q]]
    for r in range(1, width + 1):
        prev, cur = rows[r - 1], rows[r]
        nxt = []
        for i in range(n):
            nxt.append((cur[i] * cur[(i + 1) % n] - 1) / prev[(i + 1) % n])
        rows.append(nxt)
    return rows

n = 24
tris = random_triangulation(n)
q = quiddity(n, tris)
rows = build_frieze(q)
# checks: last row all 1s; every entry positive integer; diamond rule everywhere
last_ok = all(v == 1 for v in rows[-1])
int_ok = all(v.denominator == 1 and v > 0 for row in rows for v in row)
dia = True
for r in range(1, len(rows) - 1):
    for i in range(n):
        a = rows[r][i]; b = rows[r][(i + 1) % n]
        u = rows[r - 1][(i + 1) % n]; d = rows[r + 1][i]
        if a * b - u * d != 1:
            dia = False
ALL &= ok(f"Frieze n={n}: closes with a row of 1s", last_ok)
ALL &= ok("Frieze: all entries positive integers (Conway–Coxeter)", int_ok)
ALL &= ok("Frieze: every diamond satisfies ad-bc=1", dia)
# glide symmetry: row r shifted relates to row width+1-r  (frieze period n, glide)
w = len(rows) - 1
glide = all(rows[r][i] == rows[w - r][(i + r + 1 - 0) % n] for r in range(len(rows)) for i in range(n))
# try the standard glide: F[r][i] = F[w-r][i + r? ] -- test a few shifts to find the right one
found_shift = None
for s in range(n):
    if all(rows[r][i] == rows[w - r][(i + s + r) % n] for r in range(len(rows)) for i in range(n)):
        found_shift = ('r-dependent', s); break
if found_shift is None:
    for s in range(n):
        if all(rows[r][i] == rows[w - r][(i + s) % n] for r in range(len(rows)) for i in range(n)):
            found_shift = ('constant', s); break
ALL &= ok(f"Frieze: glide symmetry found: {found_shift}", found_shift is not None)

# frieze row-pair Lyness connection: adjacent entries along a diagonal follow
# the SAME recurrence family (cluster A_{n-3}); verify the n=5 pentagon frieze IS Lyness:
x, y = Fraction(3, 2), Fraction(7, 3)
five = [x, y]
for _ in range(6):
    five.append((five[-1] + 1) / five[-2])
ALL &= ok(f"n=5 frieze/Lyness sequence period 5: {[str(v) for v in five[:7]]}",
          five[5] == five[0] and five[6] == five[1])

# ---------------------------------------------------------------- 3. PENTAGRAMMA
def normalize(v): return v / np.linalg.norm(v)

def pentagramma(seed_a, seed_b, t=0.7):
    """Gauss pentagramma mirificum, star-walk order.

    Self-polarity says each vertex is the pole of the great circle through the
    two vertices 'across' the star:  P_i . P_{i+2} = 0  for all i (mod 5).
    Hence P_{k+3} is orthogonal to both P_k and P_{k+1}, i.e.
        P_{k+3} = +- normalize(P_k x P_{k+1}).
    Seeds: P0, P1 free; P2 = any unit vector orthogonal to P0 (parameter t).
    Closure after 5 is then an identity:  P5 = P2 x (P0 x P1) = P0 (P2.P1).
    """
    P0 = normalize(np.array(seed_a, float))
    P1 = normalize(np.array(seed_b, float))
    # basis of the plane orthogonal to P0
    u = normalize(np.cross(P0, P1)); v = np.cross(P0, u)
    P2 = normalize(math.cos(t) * v + math.sin(t) * u)
    P = [P0, P1, P2]
    for k in range(7):
        P.append(normalize(np.cross(P[-3], P[-2])))
    return P

P = pentagramma([1, 0.2, 0.1], [0.05, 1, 0.3])
# closure: P[k+5] parallel to P[k]
clo = max(min(np.linalg.norm(P[k + 5] - P[k]), np.linalg.norm(P[k + 5] + P[k])) for k in range(5))
ALL &= ok(f"Pentagramma: closes after 5 steps (up to sign): {clo:.2e}", clo < 1e-12)
# self-polarity P_i . P_{i+2} = 0 for all i
sp = max(abs(np.dot(P[i], P[(i + 2) % 5])) for i in range(5))
ALL &= ok(f"Pentagramma: self-polar (P_i . P_i+2 = 0): {sp:.2e}", sp < 1e-12)
# arcs a_k = angle(P_k, P_{k+1}) (projective: fold to <= pi/2);
# y_k = tan^2(a_k) should satisfy the Lyness recurrence in some index direction
def arcs(P):
    out = []
    for k in range(5):
        c = abs(np.dot(P[k % 5], P[(k + 1) % 5]))
        out.append(math.acos(np.clip(c, -1, 1)))
    return out
a = arcs(P)
yv = [math.tan(x) ** 2 for x in a]
def lyness_res(y):
    return max(abs(y[(k + 1) % 5] - (1 + y[k % 5]) / y[(k - 1) % 5]) / max(1, abs(y[(k + 1) % 5]))
               for k in range(5))
# star-walk arcs, read in DOUBLED order (pentagon order i -> 2i mod 5), are a Lyness 5-cycle
yd = [yv[(2 * k) % 5] for k in range(5)]
res = lyness_res(yd)
ALL &= ok(f"Pentagramma: tan²(arcs) in pentagon order (i->2i mod 5) satisfy Lyness: {res:.2e}",
          res < 1e-10)
# Gauss's product identity: prod y_k = 3 + sum y_k
lhs = math.prod(yv); rhs = 3 + sum(yv)
ALL &= ok(f"Pentagramma: Gauss identity Πy = 3+Σy  ({lhs:.10f} vs {rhs:.10f})", abs(lhs - rhs) < 1e-8)

print()
print("ALL PASS" if ALL else "SOME FAILURES")
