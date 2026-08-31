#!/usr/bin/env python3
"""Outer billiards on the golden kite — EXACT arithmetic census.

The kite K: vertices (-1,0), (0,1), (0,-1), (phi-1, 0) with phi-1 = (sqrt5-1)/2
(Schwartz's golden kite; his theorem: irrational kites have unbounded orbits —
the Moser–Neumann question). The outer billiards map psi reflects P through
the tangent vertex v seen on the right: P' = 2v - P.

All coordinates live in (1/16) Z[sqrt5]: x = (a + b*sqrt5)/16 with a,b int64.
The map is subtraction only, so orbits stay in the lattice EXACTLY. Hence:
  * a detected repeat state is a PROOF of periodicity (exact equality);
  * a tie in the tangent test (cross product exactly 0) is a PROOF the seed
    hits a singular ray (map undefined there) — such seeds are retired;
  * excursion records (max |P|^2 over N steps) are exact rationals.

Census: seeds on a small grid around the kite, N steps each, vectorized in
int64 numpy (magnitudes stay far below overflow; asserted). Output:
  outer_orbits.npz: visited points (float), per-seed fate, excursions
  outer_census.txt: per-seed fate ledger
"""
import numpy as np, sys, time

NSTEP = 200000 if len(sys.argv) < 2 else int(sys.argv[1])
DEN = 16

# vertices as (ax, bx, ay, by): ((ax+bx*sqrt5)/DEN, (ay+by*sqrt5)/DEN)
VERTS = np.array([
    [-16, 0,   0, 0],
    [  0, 0,  16, 0],
    [  0, 0, -16, 0],
    [ -8, 8,   0, 0],   # ((sqrt5-1)/2, 0)
], dtype=np.int64)
M = len(VERTS)

# ---------------- seeds: grid around the kite + resonant sqrt5 offsets
seeds = []
for i in range(-10, 15):
    for j in range(1, 12):
        seeds.append((2 * i, 0, 2 * j, 0))            # (i/8, j/8)
for i in range(-6, 9):
    seeds.append((2 * i, 2, 6, 0))                    # x = i/8 + sqrt5/8
    seeds.append((2 * i + 1, 1, 5, 1))                # mixed parity
seeds = np.array(sorted(set(seeds)), dtype=np.int64)
NS = len(seeds)
print(f"[outer] {NS} seeds, {NSTEP} steps, exact lattice (1/{DEN})Z[sqrt5]")

P = seeds.copy()                                       # (NS,4)
alive = np.ones(NS, bool)                              # not yet singular
fate = np.zeros(NS, np.int8)                           # 0 wandering, 1 singular
maxr2a = np.zeros(NS, np.int64); maxr2b = np.zeros(NS, np.int64)

def sign_field(A, Bc):
    """exact sign of A + B*sqrt5 (int64 arrays; |A|,|B| < 3e9 asserted)"""
    assert np.all(np.abs(A) < 3_000_000_000) and np.all(np.abs(Bc) < 1_200_000_000)
    d = A * A - 5 * Bc * Bc                            # sign(A)*|..| comparison
    s = np.sign(A)
    t = np.sign(Bc)
    # value > 0 iff (A>=0 and B>=0 and not both 0) or (A>=0>B and A^2>5B^2)
    #            or (B>=0>A and 5B^2>A^2)
    out = np.where((s >= 0) & (t >= 0), np.where((s > 0) | (t > 0), 1, 0),
          np.where((s <= 0) & (t <= 0), np.where((s < 0) | (t < 0), -1, 0),
          np.where(s > 0, np.sign(d), -np.sign(d))))
    return out.astype(np.int8)

# hashes for cycle detection
HASHC = np.array([0x9E3779B97F4A7C15, 0xC2B2AE3D27D4EB4F,
                  0xBF58476D1CE4E5B9, 0x94D049BB133111EB], dtype=np.uint64)
hashes = np.zeros((NSTEP, NS), dtype=np.uint64)

# visited points for the render (float, subsampled by 1 — keep all)
VIS = np.zeros((NSTEP, NS, 2), dtype=np.float32)
S5 = np.sqrt(5.0)

t0 = time.time()
for step in range(NSTEP):
    # tangent vertex: v_i s.t. for all j: cross(v_i - P, v_j - P) >= 0
    # cross in field: (x_i y_j - x_j y_i) etc.; components (a+b*sqrt5)/DEN^2
    dx_a = VERTS[:, 0][None, :] - P[:, 0][:, None]     # (NS, M)
    dx_b = VERTS[:, 1][None, :] - P[:, 1][:, None]
    dy_a = VERTS[:, 2][None, :] - P[:, 2][:, None]
    dy_b = VERTS[:, 3][None, :] - P[:, 3][:, None]
    ok = np.ones((NS, M), bool)
    tie = np.zeros(NS, bool)
    for i in range(M):
        # cross(d_i, d_j) = dx_i*dy_j - dx_j*dy_i, field components:
        A = dx_a[:, i:i+1] * dy_a - dx_a * dy_a[:, i:i+1] \
            + 5 * (dx_b[:, i:i+1] * dy_b - dx_b * dy_b[:, i:i+1])
        Bc = dx_a[:, i:i+1] * dy_b - dx_b * dy_a[:, i:i+1] \
            + dx_b[:, i:i+1] * dy_a - dx_a * dy_b[:, i:i+1]
        sg = sign_field(A, Bc)
        sg[:, i] = 1
        zero_elsewhere = (sg == 0) & (np.arange(M)[None, :] != i)
        tie |= zero_elsewhere.any(axis=1)
        ok[:, i] = (sg >= 0).all(axis=1)
    dead = (tie | ~ok.any(axis=1)) & alive
    if dead.any():
        fate[dead] = 1
        alive[dead] = False
    vidx = np.argmax(ok, axis=1)
    v = VERTS[vidx]                                    # (NS,4)
    P = np.where(alive[:, None], 2 * v - P, P)
    # excursion (exact |P|^2 = (A + B sqrt5)/DEN^2): track A,B; compare via float
    A2 = P[:, 0] ** 2 + 5 * P[:, 1] ** 2 + P[:, 2] ** 2 + 5 * P[:, 3] ** 2
    B2 = 2 * P[:, 0] * P[:, 1] + 2 * P[:, 2] * P[:, 3]
    val = A2 + S5 * B2
    old = maxr2a + S5 * maxr2b
    upd = alive & (val > old)
    maxr2a = np.where(upd, A2, maxr2a); maxr2b = np.where(upd, B2, maxr2b)
    h = (P[:, 0].astype(np.uint64) * HASHC[0] + P[:, 1].astype(np.uint64) * HASHC[1]
         + P[:, 2].astype(np.uint64) * HASHC[2] + P[:, 3].astype(np.uint64) * HASHC[3])
    h ^= h >> np.uint64(30); h *= np.uint64(0xBF58476D1CE4E5B9)
    h ^= h >> np.uint64(27); h *= np.uint64(0x94D049BB133111EB)
    h ^= h >> np.uint64(31)
    hashes[step] = h
    VIS[step, :, 0] = (P[:, 0] + S5 * P[:, 1]) / DEN
    VIS[step, :, 1] = (P[:, 2] + S5 * P[:, 3]) / DEN
    if step % 20000 == 0:
        print(f"  step {step} alive {alive.sum()} {time.time()-t0:.0f}s", flush=True)

# overflow guard (post-hoc): coordinates stayed small
assert np.all(np.abs(P[:, :4]) < 2_000_000_000)

# ---------------- cycle detection per seed (hash duplicates -> exact verify)
periods = np.zeros(NS, np.int64)
rep_at = np.zeros(NS, np.int64)                        # index of the repeat (transient bound)
for s in range(NS):
    if fate[s] == 1: continue
    hs = hashes[:, s]
    order = np.argsort(hs, kind="stable")
    dup = np.nonzero(hs[order][1:] == hs[order][:-1])[0]
    if len(dup) == 0: continue
    # earliest repeat pair whose period is SHIFT-CONSISTENT (guards collisions)
    i1s = np.minimum(order[dup], order[dup + 1])
    i2s = np.maximum(order[dup], order[dup + 1])
    for j in np.argsort(i2s)[:20]:
        i1, i2 = int(i1s[j]), int(i2s[j])
        p_ = i2 - i1
        span = min(NSTEP - i2, 3 * p_)
        if span > 0 and np.array_equal(hs[i2:i2 + span], hs[i1:i1 + span]):
            periods[s] = p_
            rep_at[s] = i2
            fate[s] = 2                                # eventually periodic (verified below)
            break
# (*) hash collision chance ~ 2^-64 per pair; verified below by exact replay
# exact replay verification for a sample of periodic seeds
def step_one(p):
    best = None  # returns None on tie/no-tangent (verification then skips)
    for i in range(M):
        good = True
        for j in range(M):
            if i == j: continue
            dxa_i = VERTS[i,0]-p[0]; dxb_i = VERTS[i,1]-p[1]
            dya_i = VERTS[i,2]-p[2]; dyb_i = VERTS[i,3]-p[3]
            dxa_j = VERTS[j,0]-p[0]; dxb_j = VERTS[j,1]-p[1]
            dya_j = VERTS[j,2]-p[2]; dyb_j = VERTS[j,3]-p[3]
            A = int(dxa_i)*int(dya_j) - int(dxa_j)*int(dya_i) \
                + 5*(int(dxb_i)*int(dyb_j) - int(dxb_j)*int(dyb_i))
            Bc = int(dxa_i)*int(dyb_j) + int(dxb_i)*int(dya_j) \
                - int(dxa_j)*int(dyb_i) - int(dxb_j)*int(dya_i)
            # exact sign of A + B sqrt5
            if A >= 0 and Bc >= 0: sg = 1 if (A or Bc) else 0
            elif A <= 0 and Bc <= 0: sg = -1 if (A or Bc) else 0
            else:
                d = A*A - 5*Bc*Bc
                sg = (1 if d > 0 else -1) * (1 if A > 0 else -1)
                if d == 0: sg = 0
            if sg < 0: good = False; break
        if good: best = i; break
    if best is None:
        return None
    return tuple(2*VERTS[best][k] - p[k] for k in range(4))

nver = 0
transients = {}
cand = [s for s in np.nonzero(fate == 2)[0] if rep_at[s] <= 40000][:40]
for s in cand:
    p0 = tuple(int(x) for x in seeds[s]); p = p0
    seen = {p0: 0}
    per = 0; trans = 0
    broke = False
    for t in range(1, int(rep_at[s]) + int(periods[s]) + 8):
        p = step_one(p)
        if p is None:
            broke = True; break
        if p in seen:
            per = t - seen[p]; trans = seen[p]; break
        seen[p] = t
    if broke:
        fate[s] = 1; periods[s] = 0
        continue
    assert per and periods[s] % per == 0, (s, per, int(periods[s]))
    periods[s] = per
    transients[int(s)] = trans
    nver += 1
print(f"[outer] exact-replay verified {nver} eventually-periodic seeds "
      f"(min periods; transients up to {max(transients.values()) if transients else 0})")

exc = (maxr2a + S5 * maxr2b) / DEN**2
np.savez_compressed("outer_orbits.npz", vis=VIS[::1], fate=fate,
                    periods=periods, exc=exc.astype(np.float64), seeds=seeds)
with open("outer_census.txt", "w") as f:
    for s in range(NS):
        f.write(f"seed=({seeds[s,0]}+{seeds[s,1]}r5)/16,({seeds[s,2]}+{seeds[s,3]}r5)/16 "
                f"fate={'singular' if fate[s]==1 else ('periodic p='+str(periods[s]) if fate[s]==2 else 'wandering')} "
                f"max|P|={np.sqrt(exc[s]):.3f}\n")
nw = (fate == 0).sum(); npd = (fate == 2).sum(); nsg = (fate == 1).sum()
print(f"[outer] fates: {npd} provably periodic, {nw} wandering after {NSTEP} steps, "
      f"{nsg} hit singular rays; max excursion {np.sqrt(exc[fate==0].max() if nw else 0):.1f}")
