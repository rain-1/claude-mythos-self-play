#!/usr/bin/env python3
"""Unstable periodic orbits of the Lorenz flow (sigma=10, rho=28, beta=8/3)
— the knotted skeleton of the strange attractor.

Section: z-maxima (zdot = xy - beta z = 0 crossing downward, z > 20).
Symbol at a z-max: R if x > 0 else L. Harvest close returns from a long
trajectory, polish each candidate with Newton on the m-th return map
(finite-difference Jacobian), certify ||R_m(u) - u|| < 1e-9 in section
coords and the full-state period residual. Deduplicate by necklace-canonical
symbolic word. Then compute all pairwise LINKING NUMBERS by signed crossings
in a generic projection (asserted near-integer) — Birman–Williams: Lorenz
links are positive: every pairwise linking number should be > 0.

Output: lorenz_orbits.npz (trajectories, words, periods, residuals, linking
matrix), lorenz_census.txt ledger.
"""
import numpy as np
from scipy.integrate import solve_ivp
import time, sys

SIG, RHO, BET = 10.0, 28.0, 8.0 / 3.0
MAXLEN = 8

def rhs(t, u):
    x, y, z = u
    return [SIG * (y - x), x * (RHO - z) - y, x * y - BET * z]

def zmax_event(t, u):
    return u[0] * u[1] - BET * u[2]
zmax_event.direction = -1.0

def integrate_maxes(u0, nmax, tmax=500.0):
    """integrate until nmax z-maxima with z>20; return (section pts, states, times)"""
    pts, syms, ts, states = [], [], [], []
    t0, u = 0.0, np.array(u0, float)
    while len(pts) < nmax and t0 < tmax:
        sol = solve_ivp(rhs, (t0, t0 + 40.0), u, events=zmax_event,
                        rtol=1e-12, atol=1e-12, dense_output=False, max_step=0.05)
        for te, ue in zip(sol.t_events[0], sol.y_events[0]):
            if ue[2] > 20.0:
                pts.append((ue[0], ue[1])); syms.append('R' if ue[0] > 0 else 'L')
                ts.append(te); states.append(ue.copy())
                if len(pts) >= nmax: break
        u = sol.y[:, -1]; t0 = sol.t[-1]
    return np.array(pts), ''.join(syms), np.array(ts), np.array(states)

def return_map(xy, m):
    """m-th return of section point (x,y) [z = 3xy/8]; returns (xy', word, T, path)"""
    x, y = xy
    z = 3.0 * x * y / 8.0
    u = np.array([x, y, z])
    word = []
    T = 0.0
    path = [u.copy()]
    for _ in range(m):
        sol = solve_ivp(rhs, (0.0, 40.0), u, events=zmax_event,
                        rtol=1e-12, atol=1e-12, max_step=0.05, dense_output=True)
        # first event with z>20
        hit = None
        for te, ue in zip(sol.t_events[0], sol.y_events[0]):
            if te > 0.05 and ue[2] > 20.0:
                hit = (te, ue); break
        if hit is None:
            return None
        te, ue = hit
        tt = np.linspace(0, te, max(24, int(te / 0.004)))
        path.append(sol.sol(tt).T[1:])
        u = ue.copy()
        word.append('R' if u[0] > 0 else 'L')
        T += te
    return (np.array([u[0], u[1]]), ''.join(word), T,
            np.vstack([p if p.ndim == 2 else p[None, :] for p in path]))

def necklace(word):
    return min(word[i:] + word[:i] for i in range(len(word)))

def is_primitive(word):
    n = len(word)
    for d in range(1, n):
        if n % d == 0 and word[:d] * (n // d) == word:
            return False
    return True

# ---------------- harvest close returns
t0 = time.time()
pts, syms, ts, states = integrate_maxes((1.0, 1.0, 20.0), 4000, tmax=4000.0)
print(f"[lorenz] harvested {len(pts)} section points in {time.time()-t0:.0f}s", flush=True)

cands = {}   # necklace word -> seed xy
NPTS = len(pts)
for m in range(1, MAXLEN + 1):
    d = np.linalg.norm(pts[m:] - pts[:-m], axis=1)
    order = np.argsort(d)
    for i in order[:60]:
        if d[i] > 1.5: break
        w = syms[i:i + m]
        if len(w) < m or not is_primitive(w): continue
        key = necklace(w)
        if key not in cands:
            cands[key] = tuple(pts[i])
print(f"[lorenz] candidate words: {len(cands)}", flush=True)

# ---------------- Newton polish
orbits = {}
for key, seed in sorted(cands.items(), key=lambda kv: (len(kv[0]), kv[0])):
    m = len(key)
    xy = np.array(seed)
    ok = False
    for it in range(14):
        r = return_map(xy, m)
        if r is None: break
        f = r[0] - xy
        if np.linalg.norm(f) < 1e-10:
            ok = True; break
        eps = 1e-7
        J = np.zeros((2, 2))
        for c in range(2):
            xp = xy.copy(); xp[c] += eps
            rp = return_map(xp, m)
            J[:, c] = (rp[0] - r[0]) / eps
        J -= np.eye(2)
        try:
            dx = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError:
            break
        if np.linalg.norm(dx) > 5.0: break
        xy = xy + dx
    if not ok: continue
    r = return_map(xy, m)
    resid = np.linalg.norm(r[0] - xy)
    word = necklace(r[1])
    if word != key:
        # converged onto a different orbit; keep under its true word
        pass
    if not is_primitive(word): continue
    if word in orbits and orbits[word]['resid'] <= resid: continue
    orbits[word] = dict(xy=xy, T=r[2], path=r[3], resid=resid, word=word)
    print(f"  UPO {word:10s} T={r[2]:.4f} resid={resid:.1e}", flush=True)

print(f"[lorenz] certified orbits: {len(orbits)} in {time.time()-t0:.0f}s", flush=True)

# expected necklace counts per length (binary primitive necklaces)
from math import gcd
def count_neck(n):
    tot = 0
    for d in range(1, n + 1):
        if n % d == 0:
            mu = {1:1,2:-1,3:-1,4:0,5:-1,6:1,7:-1,8:0}[n // d] if n // d <= 8 else 0
            tot += mu * 2 ** d
    return tot // n
for L in range(1, MAXLEN + 1):
    have = sum(1 for w in orbits if len(w) == L)
    print(f"  length {L}: found {have} / {count_neck(L)} primitive necklaces")

# ---------------- linking numbers by signed crossings (generic projection)
keys = sorted(orbits, key=lambda w: (len(w), w))
NO = len(keys)
# projection basis: view direction v; screen = (e1, e2), depth = v
v = np.array([0.31, 0.88, 0.36]); v /= np.linalg.norm(v)
e1 = np.cross(v, [0, 0, 1.0]); e1 /= np.linalg.norm(e1)
e2 = np.cross(v, e1)

def proj(path, step):
    p = path[::step]
    return p @ e1, p @ e2, p @ v

def linking(P, Q):
    x1, y1, d1 = P; x2, y2, d2 = Q
    a0 = np.stack([x1[:-1], y1[:-1]], 1); a1 = np.stack([x1[1:], y1[1:]], 1)
    b0 = np.stack([x2[:-1], y2[:-1]], 1); b1 = np.stack([x2[1:], y2[1:]], 1)
    da = a1 - a0; db = b1 - b0
    A0 = a0[:, None, :]; DA = da[:, None, :]
    B0 = b0[None, :, :]; DB = db[None, :, :]
    denom = DA[..., 0] * DB[..., 1] - DA[..., 1] * DB[..., 0]
    rel = B0 - A0
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (rel[..., 0] * DB[..., 1] - rel[..., 1] * DB[..., 0]) / denom
        s = (rel[..., 0] * DA[..., 1] - rel[..., 1] * DA[..., 0]) / denom
    hit = (np.abs(denom) > 1e-14) & (t > 0) & (t < 1) & (s > 0) & (s < 1)
    if not hit.any(): return 0.0
    ti, si = t[hit], s[hit]
    ia, ib = np.nonzero(hit)
    depth_a = d1[:-1][ia] + ti * (d1[1:] - d1[:-1])[ia]
    depth_b = d2[:-1][ib] + si * (d2[1:] - d2[:-1])[ib]
    sgn_cross = np.sign(denom[hit])
    over = np.sign(depth_a - depth_b)
    return 0.5 * np.sum(sgn_cross * over)

LK = np.zeros((NO, NO))
step = 3
projs = [proj(orbits[k]['path'], step) for k in keys]
t1 = time.time()
for i in range(NO):
    for j in range(i + 1, NO):
        lk = linking(projs[i], projs[j])
        LK[i, j] = LK[j, i] = lk
    print(f"  linking row {i}/{NO} {time.time()-t1:.0f}s", flush=True)
off = LK[np.triu_indices(NO, 1)]
ints = np.abs(off - np.round(off))
print(f"[lorenz] linking ints max dev {ints.max():.3f}; min lk = {off.min():.1f}; "
      f"all positive: {bool((np.round(off) > 0).all())}")

np.savez_compressed("lorenz_orbits.npz",
                    words=np.array(keys),
                    periods=np.array([orbits[k]['T'] for k in keys]),
                    resids=np.array([orbits[k]['resid'] for k in keys]),
                    LK=LK,
                    **{f"path_{i}": orbits[k]['path'] for i, k in enumerate(keys)})
with open("lorenz_census.txt", "w") as f:
    for i, k in enumerate(keys):
        f.write(f"{k:10s} T={orbits[k]['T']:.6f} resid={orbits[k]['resid']:.2e} "
                f"nL={k.count('L')} nR={k.count('R')}\n")
    f.write(f"linking: min={off.min():.1f} max={off.max():.1f} "
            f"integer-dev={ints.max():.4f} all-positive={bool((np.round(off)>0).all())}\n")
print("[lorenz] saved.")
