"""
engine.py — exact machinery for MO 513668:
"For what n can coins of radius 1/2..1/n be held rigidly in a circular tray of radius 1?"

Coins have integer curvature p (radius 1/p), tray curvature -1.
A rim coin of radius a=1/p sits with center at distance 1-a from the tray center.
Two tangent rim coins of radii a,b subtend a central angle with RATIONAL cosine:

    cos theta(a,b) = ((1-a)^2 + (1-b)^2 - (a+b)^2) / (2 (1-a)(1-b))

A rim ring [p_1..p_k] closes exactly  iff  sum theta = 2*pi
iff the product of unit complex numbers (c_j + i s_j), s_j = sqrt(1-c_j^2),
equals 1 EXACTLY — which we verify in the field Q(sqrt(d_1),...,sqrt(d_m)).

Rigidity: prestress stability for the unilateral contact system
    tray:  g_i  = (1-r_i)^2 - |x_i|^2          >= 0   (concave -> helps rigidity)
    pair:  g_ij = |x_i-x_j|^2 - (r_i+r_j)^2    >= 0   (convex  -> hurts)
Rigid (mod global rotation) iff no strict first-order flex and a strict
self-stress omega>0 exists with the stress-corrected second-order form
positive definite on the first-order flex space.
"""

from fractions import Fraction
import math
import numpy as np


# ---------------------------------------------------------------- exact angles
def cos_theta(p, q):
    """Rational cosine of the central angle between tangent rim coins 1/p, 1/q."""
    a, b = Fraction(1, p), Fraction(1, q)
    return ((1-a)**2 + (1-b)**2 - (a+b)**2) / (2*(1-a)*(1-b))


def theta(p, q):
    return math.acos(float(cos_theta(p, q)))


# ------------------------------------------------- quadratic tower arithmetic
def _squarefree_split(n):
    """n = k^2 * d with d squarefree; return (k, d). n > 0."""
    k, d, i = 1, 1, 2
    while i * i <= n:
        e = 0
        while n % i == 0:
            n //= i
            e += 1
        k *= i ** (e // 2)
        d *= i ** (e % 2)
        i += 1
    return k, d * n


class TowerElt:
    """Element of Q(sqrt(d1),...,sqrt(dm)): dict {squarefree int d: Fraction coeff},
    meaning sum coeff_d * sqrt(d). Key 1 = rational part."""

    __slots__ = ("c",)

    def __init__(self, c=None):
        self.c = dict(c or {})

    @staticmethod
    def rat(x):
        return TowerElt({1: Fraction(x)})

    @staticmethod
    def sqrt_of(fr):
        """sqrt of a positive rational as a TowerElt."""
        fr = Fraction(fr)
        assert fr >= 0
        if fr == 0:
            return TowerElt({})
        num, den = fr.numerator, fr.denominator
        k, d = _squarefree_split(num * den)
        return TowerElt({d: Fraction(k, den)})

    def __add__(self, o):
        c = dict(self.c)
        for d, v in o.c.items():
            c[d] = c.get(d, Fraction(0)) + v
            if c[d] == 0:
                del c[d]
        return TowerElt(c)

    def __sub__(self, o):
        return self + TowerElt({d: -v for d, v in o.c.items()})

    def __mul__(self, o):
        c = {}
        for d1, v1 in self.c.items():
            for d2, v2 in o.c.items():
                g = math.gcd(d1, d2)
                d3 = (d1 // g) * (d2 // g)      # sqrt(d1)sqrt(d2) = g*sqrt(d3)
                v = v1 * v2 * g
                c[d3] = c.get(d3, Fraction(0)) + v
                if c[d3] == 0:
                    del c[d3]
        return TowerElt(c)

    def is_rat(self, x):
        x = Fraction(x)
        if x == 0:
            return not self.c
        return self.c == {1: x}

    def __float__(self):
        return sum(float(v) * math.sqrt(d) for d, v in self.c.items())

    def __repr__(self):
        return " + ".join(f"{v}*sqrt({d})" for d, v in sorted(self.c.items())) or "0"


class TowerComplex:
    """a + b*i with a,b TowerElt."""

    __slots__ = ("re", "im")

    def __init__(self, re, im):
        self.re, self.im = re, im

    def __mul__(self, o):
        return TowerComplex(self.re * o.re - self.im * o.im,
                            self.re * o.im + self.im * o.re)

    def is_one(self):
        return self.re.is_rat(1) and self.im.is_rat(0)


def ring_closure_certificate(ring):
    """ring = list of curvatures [p1..pk]. Returns (exact_close: bool, angle_sum: float).
    exact_close True means sum of consecutive rim angles == 2*pi EXACTLY (certified:
    the product of exact unit complexes equals 1, and the float sum is near 2*pi)."""
    k = len(ring)
    z = TowerComplex(TowerElt.rat(1), TowerElt.rat(0))
    tot = 0.0
    for j in range(k):
        c = cos_theta(ring[j], ring[(j + 1) % k])
        s2 = 1 - c * c
        zc = TowerComplex(TowerElt.rat(c), TowerElt.sqrt_of(s2))
        z = z * zc
        tot += math.acos(float(c))
    return z.is_one() and abs(tot - 2 * math.pi) < 1e-6, tot


# ---------------------------------------------------------------- embeddings
def ring_positions(ring):
    """Centers of rim coins of a (numerically) closed ring, first coin at angle 0.
    Returns list of (x, y, r)."""
    ang = 0.0
    out = []
    for j, p in enumerate(ring):
        r = 1.0 / p
        out.append((math.cos(ang) * (1 - r), math.sin(ang) * (1 - r), r))
        ang += theta(p, ring[(j + 1) % len(ring)])
    return out


def ring_embeddable(ring, tol=1e-9):
    """No two non-adjacent coins overlap. Returns (ok, extra_tangencies)
    where extra_tangencies are non-adjacent pairs at exact touch (within tol)."""
    pos = ring_positions(ring)
    k = len(pos)
    extra = []
    for i in range(k):
        for j in range(i + 1, k):
            if j == i + 1 or (i == 0 and j == k - 1):
                continue
            xi, yi, ri = pos[i]
            xj, yj, rj = pos[j]
            d = math.hypot(xi - xj, yi - yj) - (ri + rj)
            if d < -tol:
                return False, []
            if abs(d) <= tol:
                extra.append((i, j))
    return True, extra


# ------------------------------------------------------------ rigidity tester
def contact_data(centers, radii, tol=1e-8):
    """Active contacts at configuration. centers (N,2). Returns list of
    ('tray', i) and ('pair', i, j)."""
    N = len(radii)
    cts = []
    for i in range(N):
        if abs(np.hypot(*centers[i]) - (1 - radii[i])) < tol:
            cts.append(("tray", i))
    for i in range(N):
        for j in range(i + 1, N):
            d = np.hypot(*(centers[i] - centers[j]))
            if abs(d - (radii[i] + radii[j])) < tol:
                cts.append(("pair", i, j))
    return cts


def _grad_rows(centers, radii, cts):
    """Gradient rows of g (scaled): tray: -x_i ; pair: (x_i-x_j) on i, -(x_i-x_j) on j.
    (Dropping factors of 2; signs so that g>=0 means row.v>=0 allowed.)"""
    N = len(radii)
    rows = np.zeros((len(cts), 2 * N))
    for k, c in enumerate(cts):
        if c[0] == "tray":
            i = c[1]
            rows[k, 2*i:2*i+2] = -centers[i]
        else:
            _, i, j = c
            d = centers[i] - centers[j]
            rows[k, 2*i:2*i+2] = d
            rows[k, 2*j:2*j+2] = -d
    return rows


def _rotation_flex(centers):
    v = np.zeros(2 * len(centers))
    for i, (x, y) in enumerate(centers):
        v[2*i], v[2*i+1] = -y, x
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def first_order_flex(centers, radii, cts):
    """LP: maximize t s.t. G v >= t, |v|<=1, v . rot = 0.
    Returns (t_max, v). t_max > 0 => strict flex => NOT rigid."""
    from scipy.optimize import linprog
    N = len(radii)
    G = _grad_rows(centers, radii, cts)
    rot = _rotation_flex(centers)
    n = 2 * N
    # vars: v (n), t (1). maximize t -> minimize -t
    cobj = np.zeros(n + 1)
    cobj[-1] = -1
    A_ub = np.hstack([-G, np.ones((len(cts), 1))])     # t - G v <= 0
    b_ub = np.zeros(len(cts))
    A_eq = np.hstack([rot[None, :], [[0.0]]])
    b_eq = [0.0]
    bounds = [(-1, 1)] * n + [(-1, 1)]
    res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")
    if not res.success:
        return 0.0, None
    return res.x[-1], res.x[:n]


def strict_self_stress(centers, radii, cts):
    """LP: find omega >= eps, sum_c omega_c grad_c = 0 (force balance), max min omega.
    Returns omega (normalized max=1) or None."""
    from scipy.optimize import linprog
    G = _grad_rows(centers, radii, cts)          # m x n
    m, n = G.shape
    # vars: omega (m), s (1). maximize s ; omega_c >= s ; G^T omega = 0 ; omega <= 1
    cobj = np.zeros(m + 1)
    cobj[-1] = -1
    A_ub = np.hstack([-np.eye(m), np.ones((m, 1))])   # s - omega_c <= 0
    b_ub = np.zeros(m)
    A_eq = np.hstack([G.T, np.zeros((n, 1))])
    b_eq = np.zeros(n)
    bounds = [(0, 1)] * m + [(0, 1)]
    res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")
    if not res.success or res.x[-1] < 1e-9:
        return None
    return res.x[:m]


def prestress_stable(centers, radii, cts, omega):
    """Second-order/prestress test. Flex space V = {v: G v = 0, v.rot=0}.
    Energy Q(v) = -sum_c omega_c v^T H_c v  (H scaled like grads: tray H=-I, pair +[I,-I;-I,I])
    Rigid if Q positive definite on V. Returns (stable, min_eig, dimV)."""
    N = len(radii)
    n = 2 * N
    G = _grad_rows(centers, radii, cts)
    rot = _rotation_flex(centers)
    A = np.vstack([G, rot[None, :]])
    # nullspace
    u, s, vt = np.linalg.svd(A)
    ns = vt[np.sum(s > 1e-10):].T                    # n x dimV
    if ns.shape[1] == 0:
        return True, np.inf, 0                       # first-order rigid outright
    # Q matrix
    Q = np.zeros((n, n))
    for k, c in enumerate(cts):
        w = omega[k]
        if c[0] == "tray":
            i = c[1]
            Q[2*i:2*i+2, 2*i:2*i+2] += w * np.eye(2)          # -(-I)*w
        else:
            _, i, j = c
            blk = w * np.eye(2)
            Q[2*i:2*i+2, 2*i:2*i+2] -= blk
            Q[2*j:2*j+2, 2*j:2*j+2] -= blk
            Q[2*i:2*i+2, 2*j:2*j+2] += blk
            Q[2*j:2*j+2, 2*i:2*i+2] += blk
    Qp = ns.T @ Q @ ns
    ev = np.linalg.eigvalsh(Qp)
    return ev.min() > 1e-10, ev.min(), ns.shape[1]


def stress_support(centers, radii, cts):
    """Which contacts can carry force in a nonneg self-stress?
    Returns (support_mask, omega) where omega is strictly positive on the support."""
    from scipy.optimize import linprog
    G = _grad_rows(centers, radii, cts)
    m, n = G.shape
    supp = np.zeros(m, bool)
    acc = np.zeros(m)
    for c in range(m):
        if supp[c]:
            continue
        cobj = np.zeros(m)
        cobj[c] = -1.0
        res = linprog(cobj, A_eq=G.T, b_eq=np.zeros(n),
                      bounds=[(0, 1)] * m, method="highs")
        if res.success and res.x[c] > 1e-9:
            supp |= res.x > 1e-11
            acc += res.x
    if acc.max() > 0:
        acc /= acc.max()
    return supp, acc


def _core_prestress(centers, radii, cts, supp, omega):
    """Prestress test restricted to the stressed core (coins incident to supp)."""
    core_coins = sorted({i for k, c in enumerate(cts) if supp[k]
                         for i in (c[1:] if c[0] == "pair" else (c[1],))})
    if not core_coins:
        return False, core_coins
    idx = {i: k for k, i in enumerate(core_coins)}
    n = 2 * len(core_coins)
    core_cts = [c for k, c in enumerate(cts) if supp[k]]
    core_om = [omega[k] for k, c in enumerate(cts) if supp[k]]
    G = np.zeros((len(core_cts), n))
    Q = np.zeros((n, n))
    for k, c in enumerate(core_cts):
        w = core_om[k]
        if c[0] == "tray":
            i = idx[c[1]]
            G[k, 2*i:2*i+2] = -centers[c[1]]
            Q[2*i:2*i+2, 2*i:2*i+2] += w * np.eye(2)
        else:
            _, a, b = c
            i, j = idx[a], idx[b]
            d = centers[a] - centers[b]
            G[k, 2*i:2*i+2] = d
            G[k, 2*j:2*j+2] = -d
            blk = w * np.eye(2)
            Q[2*i:2*i+2, 2*i:2*i+2] -= blk
            Q[2*j:2*j+2, 2*j:2*j+2] -= blk
            Q[2*i:2*i+2, 2*j:2*j+2] += blk
            Q[2*j:2*j+2, 2*i:2*i+2] += blk
    rot = np.zeros(n)
    for i0 in core_coins:
        i = idx[i0]
        rot[2*i], rot[2*i+1] = -centers[i0][1], centers[i0][0]
    nr = np.linalg.norm(rot)
    if nr > 1e-12:
        rot /= nr
    A = np.vstack([G, rot[None, :]])
    u, s, vt = np.linalg.svd(A)
    ns = vt[np.sum(s > 1e-10):].T
    if ns.shape[1] == 0:
        return True, core_coins
    ev = np.linalg.eigvalsh(ns.T @ Q @ ns)
    return ev.min() > 1e-10, core_coins


def _positively_spans(normals):
    """Do the 2-D vectors positively span R^2 (i.e. {v: v.n>=0 all n} == {0})?"""
    if len(normals) < 3:
        return False
    angs = np.sort(np.arctan2([n[1] for n in normals], [n[0] for n in normals]))
    gaps = np.diff(np.concatenate([angs, [angs[0] + 2*np.pi]]))
    return gaps.max() < np.pi - 1e-9


def is_rigid(centers, radii, tol=1e-8, verbose=False):
    """Full test: (rigid?, report dict).
    Certificate structure: strict first-order LP == 0, then arch-core prestress
    stability + iterative wedge-pinning of unloaded coins."""
    centers = np.asarray(centers, float)
    radii = np.asarray(radii, float)
    N = len(radii)
    cts = contact_data(centers, radii, tol)
    t, v = first_order_flex(centers, radii, cts)
    rep = {"contacts": cts, "n_contacts": len(cts), "flex_lp": t}
    if t > 1e-7:
        rep["verdict"] = "FLEXIBLE (strict first-order flex)"
        return False, rep
    supp, omega = stress_support(centers, radii, cts)
    rep["n_stressed"] = int(supp.sum())
    stable, core = _core_prestress(centers, radii, cts, supp, omega)
    rep["core"] = core
    rep["stress"] = omega
    if not stable:
        rep["verdict"] = "UNDETERMINED (core not prestress stable)"
        return False, rep
    pinned = set(core)
    changed = True
    while changed:
        changed = False
        for i in range(N):
            if i in pinned:
                continue
            normals = []
            for c in cts:
                if c[0] == "tray" and c[1] == i:
                    normals.append(-centers[i] / np.linalg.norm(centers[i]))
                elif c[0] == "pair" and i in c[1:]:
                    j = c[2] if c[1] == i else c[1]
                    if j in pinned:
                        d = centers[i] - centers[j]
                        normals.append(d / np.linalg.norm(d))
            if _positively_spans(normals):
                pinned.add(i)
                changed = True
    rep["pinned"] = sorted(pinned)
    if len(pinned) == N:
        rep["verdict"] = "RIGID (core prestress stable + wedged fills)"
        return True, rep
    rep["verdict"] = f"UNDETERMINED (coins {sorted(set(range(N))-pinned)} not pinned)"
    return False, rep


# ------------------------------------------------------- feasibility checking
def feasible(centers, radii, tol=1e-9):
    """No overlaps, all inside tray (within tol)."""
    centers = np.asarray(centers, float)
    N = len(radii)
    for i in range(N):
        if np.hypot(*centers[i]) > 1 - radii[i] + tol:
            return False
    for i in range(N):
        for j in range(i + 1, N):
            if np.hypot(*(centers[i] - centers[j])) < radii[i] + radii[j] - tol:
                return False
    return True


if __name__ == "__main__":
    # --- certificates for the poster's known configs ---
    print("exact angle table (cos):")
    for p in range(2, 8):
        print(" ", [f"{p},{q}:{cos_theta(p,q)}" for q in range(p, 8)])

    tests = {
        "n=2 pair [2,2]": [2, 2],
        "n=3 ring [2,3,3,3,3]": [2, 3, 3, 3, 3],
        "n=3 alt ring [2,3,2,3]": [2, 3, 2, 3],
        "n=3 ring [2,2,3]": [2, 2, 3],
        "n=4 ring [2,3,2,4,4]": [2, 3, 2, 4, 4],
        "hexaflower ring [3]*6": [3, 3, 3, 3, 3, 3],
    }
    for name, ring in tests.items():
        ok, tot = ring_closure_certificate(ring)
        emb, extra = ring_embeddable(ring) if ok else (None, None)
        print(f"{name}: closure exact={ok} (sum={tot:.15f}) embeddable={emb} extra_tangencies={extra}")
        if ok and emb:
            pos = ring_positions(ring)
            centers = np.array([[x, y] for x, y, r in pos])
            radii = np.array([r for x, y, r in pos])
            rigid, rep = is_rigid(centers, radii)
            print(f"   RIGID={rigid}  [{rep['verdict']}] contacts={rep['n_contacts']} "
                  f"flexLP={rep['flex_lp']:.2e} dimV={rep.get('dim_flex')} minEig={rep.get('min_eig', float('nan')):.2e}")
