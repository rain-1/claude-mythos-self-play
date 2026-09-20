"""lattice_circle.py — the lattice points on x^2 + y^2 = n and the Gaussian-prime turns between them.

n = prod p_i^{e_i} over primes p = 1 mod 4 with p = pi * conj(pi) in Z[i].  Every point of norm n is
u * prod pi^{k} conj(pi)^{e-k}, u a unit: 4 * prod (e_i + 1) points.  For each prime, multiplying by
pi/conj(pi) (a rotation by 2 arg pi) carries a point with k < e to another point of the same circle;
the chords of that turn all subtend the same angle and so envelope the circle of radius r cos(arg pi).
"""
import numpy as np
from itertools import product
from math import gcd


def gaussian_prime(p):
    """a + bi with a^2 + b^2 = p, a > b > 0"""
    for b in range(1, int(p ** 0.5) + 1):
        a2 = p - b * b
        a = int(round(a2 ** 0.5))
        if a * a == a2 and a > b:
            return complex(a, b)
    raise ValueError(p)


def points_on_circle(primes, exps):
    """exact integer points (x, y) with x^2 + y^2 = n, keyed by their exponent vector and unit."""
    pis = [gaussian_prime(p) for p in primes]
    pts = {}
    for ks in product(*[range(e + 1) for e in exps]):
        z = 1 + 0j
        # exact integer arithmetic via Python ints on (re, im)
        zr, zi = 1, 0
        for pi, k, e in zip(pis, ks, exps):
            a, b = int(pi.real), int(pi.imag)
            for _ in range(k):
                zr, zi = zr * a - zi * b, zr * b + zi * a
            for _ in range(e - k):
                zr, zi = zr * a + zi * b, -zr * b + zi * a
        for u in range(4):
            ur, ui = zr, zi
            for _ in range(u):
                ur, ui = -ui, ur
            pts[(ks, u)] = (ur, ui)
    n = 1
    for p, e in zip(primes, exps):
        n *= p ** e
    for (x, y) in pts.values():
        assert x * x + y * y == n
    return pts, n, pis


def chord_families(pts, primes, exps):
    """for each prime index j: list of (z, z') with z' = z * pi_j / conj(pi_j)"""
    fams = []
    for j, e in enumerate(exps):
        f = []
        for (ks, u), (x, y) in pts.items():
            if ks[j] < e:
                ks2 = list(ks); ks2[j] += 1
                x2, y2 = pts[(tuple(ks2), u)]
                f.append(((x, y), (x2, y2)))
        fams.append(f)
    return fams


def discrepancy(angles):
    """star discrepancy of angles/(2 pi) on [0,1)"""
    a = np.sort(np.mod(angles, 2 * np.pi) / (2 * np.pi))
    N = len(a); i = np.arange(1, N + 1)
    return float(max((i / N - a).max(), (a - (i - 1) / N).max()))


if __name__ == '__main__':
    import json
    primes, exps = [41, 13, 5, 17], [3, 3, 2, 2]
    pts, n, pis = points_on_circle(primes, exps)
    xy = np.array(list(pts.values()), float)
    ang = np.arctan2(xy[:, 1], xy[:, 0])
    fams = chord_families(pts, primes, exps)
    r = np.sqrt(n)
    out = dict(n=n, primes=primes, exps=exps, count=len(pts), discrepancy=discrepancy(ang),
               poisson_scale=1.0 / np.sqrt(len(pts)))
    for j, (p, f) in enumerate(zip(primes, fams)):
        A = np.array([a for a, b in f], float); B = np.array([b for a, b in f], float)
        # distance of each chord line to the origin
        d = np.abs(A[:, 0] * B[:, 1] - A[:, 1] * B[:, 0]) / np.linalg.norm(B - A, axis=1)
        th = np.angle(pis[j])
        out[f'family_{p}'] = dict(chords=len(f), env_ratio_min=float(d.min() / r), env_ratio_max=float(d.max() / r),
                                  cos_arg_pi=float(np.cos(th)), turn_deg=float(np.degrees(2 * th)))
    print(json.dumps(out, indent=1))
