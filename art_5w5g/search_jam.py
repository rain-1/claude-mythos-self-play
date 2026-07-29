"""
search_jam.py — general (not just rim-ring) search for perfect fits.

For a fixed multiset of coin radii, maximize the inflation factor s such that
coins of radius s*r_i fit in the unit tray:

    maximize s
    s.t.  |x_i|  <= 1 - s*r_i
          |x_i - x_j| >= s*(r_i + r_j)

Local maxima of s are jammed configurations of the s-scaled coins.
A PERFECT FIT of the actual coin set exists iff some local max has s == 1
exactly (then verify rigidity there with engine.is_rigid).

Sweep: all multisets for the n=5 question (sizes {1/2,1/3,1/4,1/5}, each >= 1),
plus reproduction runs for the poster's configurations.

Usage: search_jam.py <mode>   mode in {n5, n4, n3, poster}
"""

import sys
import math
import json
import numpy as np
from itertools import product
from multiprocessing import Pool
from scipy.optimize import minimize

rng_global = np.random.default_rng(20260729)


def maximize_s(radii, x0=None, seed=0, s0=0.7):
    """One local maximization of s. radii: array (N,). Returns (s, centers)."""
    radii = np.asarray(radii, float)
    N = len(radii)
    rng = np.random.default_rng(seed)
    if x0 is None:
        # random init: sunflower-ish with noise, biased big coins outward
        u = rng.random(N)
        ang = rng.random(N) * 2 * np.pi
        rad = np.sqrt(u) * (1 - radii * s0)
        x0 = np.stack([rad * np.cos(ang), rad * np.sin(ang)], 1)
    z0 = np.concatenate([x0.ravel(), [s0]])

    def unpack(z):
        return z[:-1].reshape(N, 2), z[-1]

    def obj(z):
        return -z[-1]

    def obj_grad(z):
        g = np.zeros_like(z)
        g[-1] = -1.0
        return g

    cons = []

    def tray_c(z):
        x, s = unpack(z)
        return (1 - s * radii) ** 2 - (x ** 2).sum(1)

    def tray_j(z):
        x, s = unpack(z)
        J = np.zeros((N, 2 * N + 1))
        for i in range(N):
            J[i, 2*i:2*i+2] = -2 * x[i]
            J[i, -1] = -2 * (1 - s * radii[i]) * radii[i]
        return J

    pairs = [(i, j) for i in range(N) for j in range(i + 1, N)]

    def pair_c(z):
        x, s = unpack(z)
        d = x[[i for i, j in pairs]] - x[[j for i, j in pairs]]
        rr = np.array([radii[i] + radii[j] for i, j in pairs])
        return (d ** 2).sum(1) - (s * rr) ** 2

    def pair_j(z):
        x, s = unpack(z)
        J = np.zeros((len(pairs), 2 * N + 1))
        for k, (i, j) in enumerate(pairs):
            d = x[i] - x[j]
            J[k, 2*i:2*i+2] = 2 * d
            J[k, 2*j:2*j+2] = -2 * d
            J[k, -1] = -2 * s * (radii[i] + radii[j]) ** 2
        return J

    cons = [{"type": "ineq", "fun": tray_c, "jac": tray_j},
            {"type": "ineq", "fun": pair_c, "jac": pair_j}]
    res = minimize(obj, z0, jac=obj_grad, constraints=cons, method="SLSQP",
                   options={"maxiter": 400, "ftol": 1e-14})
    x, s = unpack(res.x)
    # validate feasibility at reported s
    viol = min(tray_c(res.x).min(initial=np.inf), pair_c(res.x).min(initial=np.inf))
    if viol < -1e-9:
        return -1.0, x
    return s, x


def best_s(radii, restarts=60, seed=0):
    """Global-ish max s + list of distinct local maxima."""
    best = (-1.0, None)
    locs = []
    for k in range(restarts):
        s, x = maximize_s(radii, seed=seed * 100003 + k)
        if s < 0:
            continue
        locs.append(s)
        if s > best[0]:
            best = (s, x)
    return best[0], best[1], sorted(locs, reverse=True)


def enum_multisets_n5(area_cap=0.94, max_coins=14):
    """Multisets over curvatures {2,3,4,5}, each >= 1."""
    out = []
    for m2 in range(1, 4):
        for m3 in range(1, 9):
            for m4 in range(1, 13):
                for m5 in range(1, 17):
                    area = m2 / 4 + m3 / 9 + m4 / 16 + m5 / 25
                    n = m2 + m3 + m4 + m5
                    if area <= area_cap and n <= max_coins:
                        out.append((m2, m3, m4, m5))
    return out


def radii_of(ms, curvs=(2, 3, 4, 5)):
    r = []
    for m, p in zip(ms, curvs):
        r += [1.0 / p] * m
    return np.array(sorted(r, reverse=True))


def run_one(args):
    ms, restarts = args
    radii = radii_of(ms)
    s, x, locs = best_s(radii, restarts=restarts, seed=hash(ms) % (2**31))
    return ms, s, (x.tolist() if x is not None else None), locs[:8]


def sweep_n5():
    multis = enum_multisets_n5()
    print(f"n=5 sweep: {len(multis)} multisets")
    jobs = [(ms, 48) for ms in multis]
    results = []
    with Pool(4) as pool:
        for k, res in enumerate(pool.imap_unordered(run_one, jobs)):
            results.append(res)
            ms, s, x, locs = res
            flag = ""
            if s > 0.997:
                flag = "  <<<<< NEAR/OVER 1" if s < 1.0 else "  (fits with slack)"
            if k % 25 == 0 or (0.997 < s < 1.0005):
                print(f"[{k+1}/{len(jobs)}] m={ms} best_s={s:.6f}{flag}", flush=True)
    results.sort(key=lambda t: -t[1])
    with open("jam_n5.json", "w") as f:
        json.dump([{"multiset": list(ms), "best_s": s, "x": x, "local_maxima": locs}
                   for ms, s, x, locs in results], f)
    print("\n=== top of the shore (best_s closest to 1 from below) ===")
    shore = sorted([r for r in results if r[1] <= 1.0000005], key=lambda t: 1 - t[1])
    for ms, s, x, locs in shore[:15]:
        print(f"  m={ms}: best_s = {s:.9f}   deficit {1-s:.3e}")
    over = [r for r in results if r[1] > 1.0000005]
    print(f"\n{len(over)} multisets fit with slack (floppy at s=1); "
          f"closest-to-jammed slack:")
    for ms, s, x, locs in sorted(over, key=lambda t: t[1])[:10]:
        print(f"  m={ms}: best_s = {s:.9f}   slack {s-1:.3e}")


def polish_perfect(radii, x, target_s=1.0):
    """Try to converge a candidate to an exact perfect fit at s=1 via
    repeated local maximization from the found config."""
    s, x2 = maximize_s(np.asarray(radii), x0=np.asarray(x), s0=target_s * 0.999)
    return s, x2


def reproduce_poster():
    """(a) the {2,3,4,6,7} perfect fit; (b) the near-miss {2,3,3,4,4,5,5}."""
    print("== poster's perfect fit multiset {2,2,3,4,4,6,6,7}? "
          "(from image: 1/2,1/2,1/3,1/4,1/4,1/6,1/6,1/7) ==")
    radii = np.array([1/2, 1/2, 1/3, 1/4, 1/4, 1/6, 1/6, 1/7])
    s, x, locs = best_s(radii, restarts=400, seed=7)
    print(f"best_s = {s:.12f}   top local maxima: {[f'{v:.9f}' for v in locs[:6]]}")

    print("== poster's near-miss multiset {2,3,3,4,4,5,5} ==")
    radii = np.array([1/2, 1/3, 1/3, 1/4, 1/4, 1/5, 1/5])
    s, x, locs = best_s(radii, restarts=400, seed=11)
    print(f"best_s = {s:.12f}   (poster found the 1/4 must shrink to 0.99991/4)")
    np.save("nearmiss_x.npy", x)
    np.save("nearmiss_r.npy", radii)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "n5"
    if mode == "n5":
        sweep_n5()
    elif mode == "poster":
        reproduce_poster()
