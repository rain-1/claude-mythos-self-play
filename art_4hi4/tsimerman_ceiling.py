"""THE CEILING OF SMALL PRIMES — for Jacob Tsimerman, Fields Medal 2026.

Tsimerman's medal is for taming special points: o-minimality imported into
arithmetic geometry (Pila-Zannier, André-Oort, Griffiths' conjecture).  The
oldest special points are the singular moduli: j-invariants of CM elliptic
curves, algebraic integers of degree h(D).  Gross and Zagier (1985) proved
that the difference of two singular moduli is astonishingly smooth: for
coprime fundamental discriminants, every prime p dividing the norm

    J(D1, D2)^(...) = prod (j(tau_1) - j(tau_2)) = +-Res(H_D1, H_D2)

divides some (D1 D2 - x^2)/4; in particular  4p <= D1 D2.  Two special values
may only meet below a hard ceiling.

The picture: each coprime pair (D1, D2) is a column of prime-stars at
abscissa log(D1 D2/4), one star at height log p per prime p | Res, brightness
by exact multiplicity.  The diagonal p = D1 D2/4 blazes; above it -- nothing.
The empty sky is the theorem.

Computed from scratch, exactly:
  * H_D by high-precision j-values (q-series E4^3/Delta) over reduced forms,
    rounded to integers; integrality residual checked (< 1e-6);
  * class numbers independently checked against Dirichlet's formula;
  * resultants as exact big integers (sympy, domain ZZ);
  * complete factorization by primes <= D1 D2/4; leftover cofactor MUST be
    +-1 (asserted) -- Gross-Zagier verified pair by pair;
  * for every prime found: existence of x with x^2 = D1 D2 mod 4p (asserted).
"""
import numpy as np
import sys, os, json, time
from math import gcd, isqrt, log
from mpmath import mp, mpc, mpf
import sympy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import filmic, bloom, save_png, ramp, bilinear_splat, splat_lines
from scipy.ndimage import gaussian_filter

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
DMAX = int(os.environ.get("DMAX", "250"))


def squarefree(m):
    d = 2
    while d * d <= m:
        if m % (d * d) == 0:
            return False
        d += 1
    return True


def is_fundamental(D):
    if D >= -2:
        return False
    if D % 4 == 1 or D % 4 == -3:
        return squarefree(-D)
    if D % 4 == 0:
        m = -D // 4
        return squarefree(m) and (m % 4 in (1, 2))
    return False


def reduced_forms(D):
    """Reduced primitive forms (a,b,c), b^2-4ac=D<0: |b|<=a<=c, b>=0 if
    |b|=a or a=c, gcd(a,b,c)=1."""
    out = []
    amax = isqrt(-D // 3) + 1
    for a in range(1, amax + 1):
        for b in range(-a, a + 1):
            if (b * b - D) % (4 * a) != 0:
                continue
            c = (b * b - D) // (4 * a)
            if c < a:
                continue
            if (abs(b) == a or a == c) and b < 0:
                continue
            if gcd(gcd(a, abs(b)), c) != 1:
                continue
            out.append((a, b, c))
    return out


def dirichlet_h(D, nmax=200000):
    """Class number via Dirichlet's formula (independent check)."""
    w = 6 if D == -3 else (4 if D == -4 else 2)
    ks = np.arange(1, nmax)
    chi = np.array([kronecker(D, int(n)) for n in range(1, nmax)])
    L = (chi / ks).sum()
    return w * np.sqrt(-D) * L / (2 * np.pi)


def kronecker(a, n):
    return int(sympy.ntheory.residue_ntheory.jacobi_symbol(a % n if n % 2 == 1 else a, n)) if False else kron(a, n)


def kron(a, n):
    """Kronecker symbol (a|n) for n>0."""
    if n == 0:
        return 1 if abs(a) == 1 else 0
    result = 1
    if n < 0:
        n = -n
        if a < 0:
            result = -result
    # factor out 2s
    while n % 2 == 0:
        n //= 2
        if a % 2 == 0:
            return 0
        if a % 8 in (3, 5):
            result = -result
    a %= n
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def j_tau(a, b, D, prec):
    """j((-b+sqrt(D))/(2a)) via q-series, working precision prec bits."""
    mp.prec = prec + 20
    tau = mpc(mpf(-b) / (2 * a), mp.sqrt(mpf(-D)) / (2 * a))
    q = mp.exp(2j * mp.pi * tau)
    qa = abs(q)
    nterms = int(mp.ceil((prec + 30) * mp.log(2) / (-mp.log(qa)))) + 2
    E4 = mp.mpc(1)
    qn = mp.mpc(1)
    for n in range(1, nterms + 1):
        qn *= q
        E4 += 240 * n ** 3 * qn / (1 - qn)
    Dl = mp.mpc(1)
    qn = mp.mpc(1)
    for n in range(1, nterms + 1):
        qn *= q
        Dl *= (1 - qn) ** 24
    Dl *= q
    return E4 ** 3 / Dl


def hilbert_class_poly(D):
    forms = reduced_forms(D)
    h = len(forms)
    bits = int(sum(np.pi * np.sqrt(-D) / a for (a, b, c) in forms)
               / np.log(2)) + 96 + 12 * h
    js = [j_tau(a, b, D, bits) for (a, b, c) in forms]
    mp.prec = bits + 20
    coeffs = [mp.mpc(1)]
    for jv in js:
        new = [mp.mpc(0)] * (len(coeffs) + 1)
        for k, ck in enumerate(coeffs):
            new[k] += ck * 1
            new[k + 1] -= ck * jv
        coeffs = new
    ints = []
    resid = 0.0
    for ck in coeffs:
        cr = mp.nint(ck.real)
        resid = max(resid, float(abs(ck.real - cr)), float(abs(ck.imag)))
        ints.append(int(cr))
    return ints, resid, h, forms


# ------------------------------------------------------------- compute polys
Ds = [D for D in range(-3, -DMAX - 1, -1) if is_fundamental(D)]
print(f"{len(Ds)} fundamental discriminants down to -{DMAX}")
polys = {}
meta = {}
for D in Ds:
    ints, resid, h, forms = hilbert_class_poly(D)
    hd = dirichlet_h(D)
    ok = abs(hd - h) < 0.15
    if not ok:
        raise RuntimeError(f"class number mismatch D={D}: forms {h} vs L {hd:.3f}")
    if resid > 1e-6:
        raise RuntimeError(f"integrality residual too big D={D}: {resid}")
    polys[D] = ints
    meta[D] = dict(h=h, resid=resid, h_dirichlet=float(hd))
print(f"class polys done, max h = {max(m['h'] for m in meta.values())}, "
      f"max resid = {max(m['resid'] for m in meta.values()):.2e} "
      f"({time.time()-t0:.0f}s)", flush=True)

# ------------------------------------------------------- resultants + factor
from sympy import Poly, Symbol, ZZ
X = Symbol('x')


def primes_upto(n):
    sieve = np.ones(n + 1, bool)
    sieve[:2] = False
    for p in range(2, isqrt(n) + 1):
        if sieve[p]:
            sieve[p * p:: p] = False
    return np.nonzero(sieve)[0]


PMAX = DMAX * DMAX // 4 + 1
PRIMES = [int(p) for p in primes_upto(PMAX)]
print(f"{len(PRIMES)} primes up to {PMAX}")

pairs = []
stars = []          # (x=log(D1 D2/4), y=log p, mass=multiplicity)
threads = []        # (x, ymin, ymax)
checked = 0
gz_x_checked = 0
t_last = time.time()
for i1 in range(len(Ds)):
    for i2 in range(i1 + 1, len(Ds)):
        D1, D2 = Ds[i1], Ds[i2]
        if gcd(D1, D2) != 1:
            continue
        P1 = Poly(polys[D1], X, domain=ZZ)
        P2 = Poly(polys[D2], X, domain=ZZ)
        R = int(P1.resultant(P2))
        if R == 0:
            raise RuntimeError("zero resultant?!")
        n = abs(R)
        ceiling = D1 * D2 // 4
        facs = {}
        for p in PRIMES:
            if p > ceiling:
                break
            if n % p == 0:
                m = 0
                while n % p == 0:
                    n //= p
                    m += 1
                facs[p] = m
            if n == 1:
                break
        if n != 1:
            raise RuntimeError(
                f"GROSS-ZAGIER VIOLATION?! pair ({D1},{D2}): cofactor {n}")
        checked += 1
        xx = log(D1 * D2 / 4)
        ys = []
        for p, m in facs.items():
            # sharper check: x^2 = D1 D2 mod 4p must be solvable
            M = 4 * p
            ok = any((x * x) % M == (D1 * D2) % M for x in range(0, M // 2 + 1))
            if not ok:
                raise RuntimeError(f"no x for p={p}, pair ({D1},{D2})")
            gz_x_checked += 1
            stars.append((xx, log(p), m))
            ys.append(log(p))
        if ys:
            threads.append((xx, min(ys), max(ys)))
        pairs.append((D1, D2, len(facs)))
    if time.time() - t_last > 30:
        t_last = time.time()
        print(f"  D1={Ds[i1]}: {checked} pairs, {len(stars)} stars "
              f"({time.time()-t0:.0f}s)", flush=True)

print(f"pairs verified: {checked}; stars: {len(stars)}; "
      f"x-solvability checks: {gz_x_checked}  ({time.time()-t0:.0f}s)")
json.dump(dict(pairs=checked, stars=len(stars), xchecks=gz_x_checked,
               dmax=DMAX, max_h=max(m['h'] for m in meta.values()),
               max_resid=max(m['resid'] for m in meta.values())),
          open(os.path.join(HERE, "ceiling_verify.json"), "w"), indent=1)
np.save(os.path.join(HERE, "ceiling_stars.npy"), np.array(stars))

# ------------------------------------------------------------------- render
SIZE = int(os.environ.get("SIZE", "2560"))
SS = 2
W = H = SIZE * SS
stars = np.array(stars)
threads = np.array(threads)

xlo, xhi = 2.2, log(DMAX * DMAX / 4) + 0.15
ylo, yhi = log(2) - 0.25, log(DMAX * DMAX / 4) + 0.15


def px(x):
    return (x - xlo) / (xhi - xlo) * 0.90 * W + 0.055 * W


def py(y):
    return H - ((y - ylo) / (yhi - ylo) * 0.90 * H + 0.055 * H)


acc = np.zeros((H, W), np.float64)
accm = np.zeros((H, W), np.float64)

# threads: dim vertical curtains per pair
splat_lines(acc, px(threads[:, 0]), py(threads[:, 1]),
            px(threads[:, 0]), py(threads[:, 2]),
            np.full(len(threads), 0.07), samples_per_px=0.9)

# stars: mass = multiplicity^0.7
sx = px(stars[:, 0]); sy = py(stars[:, 1])
mass = stars[:, 2] ** 0.7
star_field = np.zeros((H, W), np.float64)
bilinear_splat(star_field, sx, sy, mass)
# soften stars into small gaussian glints
star_soft = gaussian_filter(star_field, 1.6)
acc += star_soft * 4.6
accm += gaussian_filter(star_field * stars[:, 1][0], 0.0) * 0  # placeholder

# height-fraction moment for coloring: y relative to each star's own ceiling
frac = stars[:, 1] / stars[:, 0]           # log p / log ceiling in (0,1]
fracf = np.zeros((H, W), np.float64)
bilinear_splat(fracf, sx, sy, mass * frac)
fracf = gaussian_filter(fracf, 1.6)
mean_frac = np.where(star_soft > 1e-12, fracf / np.maximum(star_soft, 1e-12), 0)

# the ceiling: blazing diagonal y = x
tt = np.linspace(max(xlo, ylo), xhi, 4000)
ceil_acc = np.zeros((H, W), np.float64)
splat_lines(ceil_acc, px(tt[:-1]), py(tt[:-1]), px(tt[1:]), py(tt[1:]),
            np.full(len(tt) - 1, 2.2), samples_per_px=1.3)
ceil_soft = gaussian_filter(ceil_acc, 2.0)

# fold
Hf = Wf = SIZE
def fold(a):
    return a.reshape(Hf, SS, Wf, SS).mean(axis=(1, 3))

acc_f = fold(acc)
mean_frac_f = fold(mean_frac * acc) / np.maximum(fold(acc), 1e-12)
ceil_f = fold(ceil_soft)

lum = filmic(acc_f, k=1.05, gamma=0.8)
stops = [
    (0.00, (0.045, 0.14, 0.22)),
    (0.35, (0.06, 0.36, 0.42)),    # teal: low primes
    (0.60, (0.42, 0.60, 0.52)),
    (0.80, (0.95, 0.70, 0.28)),    # amber: high in the column
    (1.00, (1.00, 0.90, 0.55)),    # near-ceiling gold
]
rgb = ramp(np.clip(mean_frac_f, 0, 1), stops) * lum[..., None]
hot = filmic(acc_f, k=0.10, gamma=1.0) ** 2.6
rgb += hot[..., None] * np.array([1.0, 0.96, 0.88]) * 0.7

# ceiling: white-gold blade with warm halo
cl = filmic(ceil_f, k=1.5, gamma=0.9)
rgb += cl[..., None] * np.array([1.0, 0.88, 0.55]) * 1.1

rgb = bloom(rgb, mask_lo=0.70, sigma=4.0, strength=0.45, tint=(1.0, 0.88, 0.6))
rgb = bloom(rgb, mask_lo=0.28, sigma=22.0, strength=0.13, tint=(0.55, 0.8, 0.9))
save_png(rgb, os.path.join(HERE, "ceiling_of_small_primes.png"))
print(f"total {time.time()-t0:.0f}s")
