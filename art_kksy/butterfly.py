#!/usr/bin/env python3
"""
Panel A (hero): The Hofstadter butterfly with Diophantine gap labels.

Almost-Mathieu / Harper operator at critical coupling:
    (H u)_n = u_{n+1} + u_{n-1} + 2 cos(2 pi alpha n + theta) u_n
At rational flux alpha = p/q the spectrum is q bands; by Chambers' relation
the band edges are the eigenvalues of the q x q Bloch matrix at the two
corners (kappa, phi) = (0,0) and (pi, pi/q).  In gap r (IDS = r/q) the
gap-labelling theorem gives IDS = s + t*alpha with the unique integer
|t| <= q/2 solving  t*p == r (mod q):  t is the Chern number / quantized
Hall conductance of that gap.  We paint every gap by t.

Per image row: alpha-interval -> minimal-denominator rational via
Stern-Brocot descent; batch eigensolves by q.
"""
import numpy as np, sys, time
from fractions import Fraction

# ---------------------------------------------------------------- fractions
def _simplest(lo, hi):
    """Simplest fraction in the closed interval [lo, hi] (both Fractions >=0)."""
    if lo == hi:
        return lo
    cl = -((-lo.numerator) // lo.denominator)   # ceil(lo)
    if cl <= hi:                                # an integer lies inside
        return Fraction(cl)
    a = lo.numerator // lo.denominator          # common integer part
    return a + 1 / _simplest(1 / (hi - a), 1 / (lo - a))

def min_denominator_fraction(lo, hi):
    """Smallest-denominator fraction in [lo, hi]; returns (p, q)."""
    f = _simplest(Fraction(lo), Fraction(hi))
    return f.numerator, f.denominator

def best_frac_capped(x, qcap):
    """Best rational approximation to Fraction x with denominator <= qcap
    (continued-fraction convergents + semiconvergents)."""
    f = Fraction(x)
    p0, q0, p1, q1 = 1, 0, f.numerator // f.denominator, 1
    frac = f - (f.numerator // f.denominator)
    best = (p1, q1)
    while frac != 0:
        frac = 1 / frac
        a = frac.numerator // frac.denominator
        frac -= a
        # semiconvergents p1*k+p0 / q1*k+q0 for k=1..a
        kmax = (qcap - q0) // q1 if q1 else 0
        if kmax <= 0:
            break
        k = min(a, kmax)
        p0, q0, p1, q1 = p1, q1, k * p1 + p0, k * q1 + q0
        best = (p1, q1)
        if k < a:
            break
    p, q = best
    from math import gcd
    g = gcd(p, q) or 1
    return p // g, q // g

def row_fraction(i, H, qcap):
    """Fraction used to render row i of H (alpha in [i/H,(i+1)/H])."""
    p, q = min_denominator_fraction(Fraction(i, H), Fraction(i + 1, H))
    if q <= qcap:
        return p, q
    return best_frac_capped(Fraction(2 * i + 1, 2 * H), qcap)

# ---------------------------------------------------------------- spectrum
def band_edges(p, q):
    """Return sorted array of 2q band-edge energies for flux p/q (lambda=1)."""
    if q == 1:
        return np.array([-4.0, 4.0])
    j = np.arange(q)
    d0 = 2.0 * np.cos(2 * np.pi * p * j / q)            # (kappa,phi)=(0,0)
    d1 = 2.0 * np.cos(2 * np.pi * p * j / q + np.pi / q) # (pi, pi/q)
    def eigs(diag, corner):
        M = np.zeros((q, q))
        M[np.arange(q), np.arange(q)] = diag
        idx = np.arange(q - 1)
        M[idx, idx + 1] = 1.0
        M[idx + 1, idx] = 1.0
        M[0, q - 1] += corner
        M[q - 1, 0] += corner
        return np.linalg.eigvalsh(M)
    e0 = eigs(d0, 1.0)     # Delta = +4 side
    e1 = eigs(d1, -1.0)    # Delta = -4 side
    return np.sort(np.concatenate([e0, e1]))

def gap_label(p, q, r):
    """Chern number t of gap r at flux p/q: t*p == r (mod q), |t|<=q/2."""
    t = (r * pow(p, -1, q)) % q
    if t > q // 2:
        t -= q
    return t

# ---------------------------------------------------------------- verify
def verify():
    # q=2: edges +-2*sqrt(2) with central touching at 0
    e = band_edges(1, 2)
    assert np.allclose(sorted(np.abs(e)), [0, 0, 2**1.5, 2**1.5], atol=1e-9), e
    # E -> -E symmetry for a few fluxes
    for (p, q) in [(1, 3), (2, 5), (3, 7), (5, 12)]:
        e = band_edges(p, q)
        assert np.allclose(e, -e[::-1], atol=1e-9), (p, q)
    # gap labels: IDS = s + t*alpha must lie in [0,1] and reproduce r/q
    for (p, q) in [(1, 3), (2, 5), (3, 7), (5, 12), (7, 16)]:
        for r in range(1, q):
            t = gap_label(p, q, r)
            s = Fraction(r, q) - Fraction(t * p, q)
            assert s.denominator == 1, (p, q, r, t)
            assert 0 <= s + Fraction(t) * Fraction(p, q) <= 1
            assert abs(t) <= q // 2
    # symmetry t(r) = -t(q-r)
    p, q = 3, 11
    for r in range(1, q):
        assert gap_label(p, q, r) == -gap_label(p, q, q - r)
    # total bandwidth decreases with q (Thouless ~ c/q)
    w = []
    for (p, q) in [(1, 5), (1, 25), (1, 125)]:
        e = band_edges(p, q)
        w.append(np.sum(e[1::2] - e[0::2]))
    assert w[0] > w[1] > w[2], w
    print("verify: all checks passed;  bandwidth(1/5,1/25,1/125) =",
          [f"{x:.3f}" for x in w])

# ---------------------------------------------------------------- render maps
def compute_maps(H, W, emax=4.0, qcap=600, alo=Fraction(0), ahi=Fraction(1)):
    """Return (label, band-coverage, dist, qs); alpha spans [alo, ahi]."""
    t0 = time.time()
    # 1) row -> fraction
    span = ahi - alo
    def rf(i):
        lo = alo + span * Fraction(i, H)
        hi = alo + span * Fraction(i + 1, H)
        p, q = min_denominator_fraction(lo, hi)
        if q <= qcap:
            return p, q
        return best_frac_capped((lo + hi) / 2, qcap)
    fracs = [rf(i) for i in range(H)]
    qs = np.array([f[1] for f in fracs])
    print(f"rows={H} distinct fracs={len(set(fracs))} qmax={qs.max()} "
          f"({time.time()-t0:.1f}s)")
    # 2) eigensolves, batched by q for BLAS efficiency
    cache = {}
    byq = {}
    for f in set(fracs):
        byq.setdefault(f[1], []).append(f[0])
    for q in sorted(byq):
        ps = byq[q]
        if q == 1:
            for p in ps:
                cache[(p, q)] = band_edges(p, q)
            continue
        j = np.arange(q)
        M = np.zeros((2 * len(ps), q, q))
        idx = np.arange(q - 1)
        M[:, idx, idx + 1] = 1.0
        M[:, idx + 1, idx] = 1.0
        for k, p in enumerate(ps):
            M[2 * k, j, j] = 2.0 * np.cos(2 * np.pi * p * j / q)
            M[2 * k, 0, q - 1] += 1.0; M[2 * k, q - 1, 0] += 1.0
            M[2 * k + 1, j, j] = 2.0 * np.cos(2 * np.pi * p * j / q + np.pi / q)
            M[2 * k + 1, 0, q - 1] -= 1.0; M[2 * k + 1, q - 1, 0] -= 1.0
        ev = np.linalg.eigvalsh(M)
        for k, p in enumerate(ps):
            cache[(p, q)] = np.sort(np.concatenate([ev[2 * k], ev[2 * k + 1]]))
    print(f"eigensolves done ({time.time()-t0:.1f}s)")
    # 3) paint rows
    label = np.full((H, W), -32768, np.int16)   # sentinel = outside spectrum hull
    cov = np.zeros((H, W), np.float32)
    dist = np.zeros((H, W), np.float32)         # px distance to nearest band edge
    scale = W / (2 * emax)
    for i in range(H):
        p, q = fracs[i]
        e = cache[(p, q)]
        # bands e[0::2]..e[1::2]; gaps between e[2r-1], e[2r]
        # gap fill (integer pixel spans, cheap)
        for r in range(1, q):
            a, b = e[2 * r - 1], e[2 * r]
            if b - a <= 1e-12:
                continue
            fa, fb = (a + emax) * scale, (b + emax) * scale
            ia, ib = int(np.ceil(fa)), int(np.floor(fb))
            if ib > ia:
                label[i, ia:ib] = gap_label(p, q, r)
                x = np.arange(ia, ib) + 0.5
                dist[i, ia:ib] = np.minimum(x - fa, fb - x)
        # band coverage, antialiased
        for r in range(q):
            a, b = e[2 * r] , e[2 * r + 1]
            fa, fb = (a + emax) * scale, (b + emax) * scale
            ia, ib = int(np.floor(fa)), int(np.floor(fb))
            ia = max(ia, 0); ib = min(ib, W - 1)
            if ia == ib:
                cov[i, ia] += (fb - fa)
            else:
                cov[i, ia] += (ia + 1 - fa)
                cov[i, ib] += (fb - ib)
                if ib > ia + 1:
                    cov[i, ia + 1:ib] = 1.0
        # inside-hull background label 0 regions: below first band s=0,t=0 not
        # painted (outside spectrum hull keeps sentinel)
        if i % 1024 == 0:
            print(f"  row {i} ({time.time()-t0:.1f}s)")
    print(f"paint done ({time.time()-t0:.1f}s)")
    return label, cov, dist, qs

if __name__ == "__main__":
    verify()
