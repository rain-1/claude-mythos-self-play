"""Galois orbits of the n<=6 tree dessins.

Polish each numeric Shabat solution to 50 digits (mpmath Newton, gauge pinned
by freezing the first robust weighted power-sum to its float64 value), compute
the scale-invariant J = s2^3/s3^2 (fallbacks if degenerate), then for each
passport form prod(x - J_s) over its dessins: coefficients must be RATIONAL
(the passport set is Galois-closed).  Rationalize by continued fractions and
factor over Q -> factors = Galois orbits.  Mirror pairs with complex J are
conjugate <=> chirality is a Galois phenomenon here.
"""
import json, itertools
import numpy as np
import mpmath as mp
from fractions import Fraction

mp.mp.dps = 60

def poly_from_roots_mp(roots, mults):
    p = [mp.mpc(1)]
    for r, m in zip(roots, mults):
        for _ in range(m):
            q = [mp.mpc(0)] * (len(p) + 1)
            for i, c in enumerate(p):
                q[i] += c
                q[i + 1] -= c * r
            p = q
    return p

def polish(a0, b0, lam, mu, n):
    """Newton at high precision.  Unknowns: a[1:], b[:] (a0 from centroid),
    equations: mid coeffs of A-B (=0) plus gauge: s_k pinned (k robust)."""
    a0 = [mp.mpc(z) for z in a0]; b0 = [mp.mpc(z) for z in b0]
    def s_k(a, b, k):
        return (sum(l * z**k for l, z in zip(lam, a)) +
                sum(m * z**k for m, z in zip(mu, b)))
    kpin, spin = None, None
    for k in (2, 3, 4, 5):
        v = s_k(a0, b0, k)
        if abs(v) > 0.05:
            kpin, spin = k, v
            break
    if kpin is None:
        return None
    VB, VW = len(lam), len(mu)
    def pack(a, b): return a[1:] + b
    def unpack(u):
        a_rest = u[:VB - 1]; b = u[VB - 1:]
        a1 = -sum(l * z for l, z in zip(lam[1:], a_rest)) / lam[0] if VB > 1 else mp.mpc(0)
        return [a1] + list(a_rest), list(b)
    def F(u):
        a, b = unpack(u)
        A = poly_from_roots_mp(a, lam); B = poly_from_roots_mp(b, mu)
        R = [A[i] - B[i] for i in range(1, n)]       # z^{n-1}..z^1
        R.append(s_k(a, b, kpin) - spin)             # gauge pin
        return R
    u = pack(a0, b0)
    m = len(u)
    for it in range(80):
        Fv = F(u)
        # numeric Jacobian
        J = mp.matrix(m, m)
        h = mp.mpf(10) ** (-mp.mp.dps // 2)
        for j in range(m):
            up = list(u); up[j] = up[j] + h
            Fp = F(up)
            for i in range(m):
                J[i, j] = (Fp[i] - Fv[i]) / h
        rhs = mp.matrix([-f for f in Fv])
        try:
            du = mp.lu_solve(J, rhs)
        except Exception:
            return None
        u = [u[j] + du[j] for j in range(m)]
        if max(abs(x) for x in du) < mp.mpf(10) ** (-mp.mp.dps + 8):
            break
    res = max(abs(f) for f in F(u))
    if res > mp.mpf(10) ** (-mp.mp.dps + 12):
        return None
    a, b = unpack(u)
    return a, b

def invariant(a, b, lam, mu):
    def s_k(k):
        return (sum(l * z**k for l, z in zip(lam, a)) +
                sum(m * z**k for m, z in zip(mu, b)))
    cands = []
    s2, s3, s4, s5, s6 = (s_k(k) for k in (2, 3, 4, 5, 6))
    if abs(s3) > 1e-25: cands.append(('J23', s2**3 / s3**2))
    if abs(s4) > 1e-25: cands.append(('J24', s2**2 / s4))
    if abs(s4) > 1e-25: cands.append(('J34', s3**4 / s4**3))
    if abs(s5) > 1e-25 and abs(s2) > 1e-25: cands.append(('J25', s5**2 / s2**5))
    if abs(s6) > 1e-25 and abs(s2) > 1e-25: cands.append(('J26', s6 / s2**3))
    if abs(s6) > 1e-25 and abs(s3) > 1e-25: cands.append(('J36', s6 / s3**2))
    return cands

def rationalize(x, maxden=10**14):
    """High-precision continued fraction on an mpf."""
    x = mp.mpf(x)
    p0, q0, p1, q1 = 0, 1, 1, 0
    v = x
    for _ in range(64):
        a = mp.floor(v)
        p0, q0, p1, q1 = p1, q1, int(a) * p1 + p0, int(a) * q1 + q0
        if q1 > maxden:
            break
        if abs(mp.mpf(p1) / q1 - x) < mp.mpf(10) ** (-mp.mp.dps + 10):
            fr = Fraction(p1, q1)
            return fr, abs(mp.mpf(fr.numerator) / fr.denominator - x)
        fv = v - a
        if fv == 0:
            break
        v = 1 / fv
    fr = Fraction(p1, q1)
    return fr, abs(mp.mpf(fr.numerator) / fr.denominator - x)

def main():
    sols = json.load(open('shabat_solutions_6.json'))
    orbits_out = {}
    report = []
    for n in range(1, 7):
        # group by passport
        bypass = {}
        for s in sols[str(n)]:
            key = (tuple(s['lam']), tuple(s['mu']))
            bypass.setdefault(key, []).append(s)
        for key, group in sorted(bypass.items()):
            lam, mu = list(key[0]), list(key[1])
            if len(group) == 1:
                # a passport with ONE dessin is Galois-fixed => defined over Q;
                # certificate is cardinality itself, no invariant needed
                orbits_out[group[0]['cls']] = 0
                report.append(dict(n=n, passport=[lam, mu], inv='singleton',
                                   certified=True, maxerr=0.0, maximag=0.0,
                                   orbit_sizes=[1], factors='(defined over Q)'))
                continue
            polished = []
            for s in group:
                a0 = [complex(*z) for z in s['a']]
                b0 = [complex(*z) for z in s['b']]
                r = polish(a0, b0, lam, mu, n)
                if r is None:
                    print(f"POLISH FAIL n={n} {key} cls={s['cls'][:30]}")
                    polished.append(None); continue
                polished.append(r)
            if any(p is None for p in polished):
                continue
            # pick first invariant defined & pairwise distinct across group
            chosen = None
            for name in ('J23', 'J24', 'J34', 'J25', 'J26', 'J36'):
                vals = []
                okc = True
                for p in polished:
                    cands = dict(invariant(p[0], p[1], lam, mu))
                    if name not in cands or not abs(cands[name]) < 1e12:
                        okc = False; break
                    vals.append(cands[name])
                if not okc: continue
                if len(vals) > 1:
                    md = min(abs(v - w) for v, w in itertools.combinations(vals, 2))
                    if md < 1e-20: continue
                chosen = (name, vals); break
            if chosen is None:
                print(f"NO INVARIANT n={n} {key}"); continue
            name, vals = chosen
            # product polynomial over the group: must be rational
            import sympy as sp
            x = sp.symbols('x')
            poly = mp.mpc(1)
            coeffs = [mp.mpc(1)]
            for v in vals:
                nc = [mp.mpc(0)] * (len(coeffs) + 1)
                for i, c in enumerate(coeffs):
                    nc[i] += c; nc[i + 1] -= c * v
                coeffs = nc
            rat, maxerr, maximag = [], 0.0, 0.0
            for c in coeffs:
                maximag = max(maximag, float(abs(mp.im(c))))
                fr, err = rationalize(mp.re(c))
                rat.append(fr); maxerr = max(maxerr, float(err))
            certified = maximag < 1e-25 and maxerr < 1e-22
            P = sum(sp.Rational(f.numerator, f.denominator) * x**(len(rat) - 1 - i)
                    for i, f in enumerate(rat))
            fac = sp.factor_list(P)
            # assign each dessin to the factor that annihilates its J
            groups = {}
            for gi, (fpol, mult) in enumerate(fac[1]):
                f = sp.lambdify(x, fpol, 'mpmath')
                for si, v in enumerate(vals):
                    if abs(f(v)) < 1e-18 * (1 + abs(v)) ** sp.degree(fpol, x):
                        groups.setdefault(gi, []).append(si)
            # orbit index per dessin (order by first member)
            assigned = {}
            for gi, mem in sorted(groups.items(), key=lambda kv: min(kv[1])):
                for si in mem:
                    assigned[si] = gi
            sizes = sorted(len(m) for m in groups.values())
            report.append(dict(n=n, passport=[lam, mu], inv=name,
                               certified=bool(certified), maxerr=maxerr,
                               maximag=maximag,
                               orbit_sizes=sizes,
                               factors=str(fac)))
            print(f"n={n} {key}: |group|={len(group)} inv={name} "
                  f"certified={certified} orbit sizes={sizes}", flush=True)
            for si, s in enumerate(group):
                if si in assigned:
                    orbits_out[s['cls']] = assigned[si]
    json.dump(orbits_out, open('galois_orbits.json', 'w'))
    json.dump(report, open('galois_report.json', 'w'))

if __name__ == '__main__':
    main()
