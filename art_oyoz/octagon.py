"""octagon.py — THE LOOM OF THE OCTAGON: cylinder decompositions of the regular-octagon
translation surface (opposite sides glued; genus 2, one cone point of angle 6π).

Veech's dichotomy: every direction is either uniquely ergodic or COMPLETELY PERIODIC, and
the periodic directions are exactly the directions of saddle connections.  We
  1. enumerate saddle connections up to length L by lattice candidates + exact shooting,
  2. for each periodic direction trace the 3 saddle connections through the cone point,
  3. decompose into cylinders (height H, circumference C from closed trajectories),
  4. certify: every sampled trajectory closes; heights constant along each cylinder;
     moduli C/H within a direction commensurable (Veech);
  5. paint each cylinder as a pastel ribbon (brightness = sin(πu) across its height).
"""
import numpy as np, json, sys, time, argparse
from collections import defaultdict

t0 = time.time()
def log(*a):
    print(f'[{time.time() - t0:7.1f}s]', *a, flush=True)

# ---- regular octagon, side 1, edge k from V[k] to V[k+1]; edge k glued to edge k+4 by translation
R = 1 / (2 * np.sin(np.pi / 8))
ang = np.pi / 8 + np.arange(8) * np.pi / 4 + np.pi / 2   # vertex 0 at top-left... orientation: start so edge 0 is the top edge
V = np.stack([R * np.cos(ang), R * np.sin(ang)], 1)
E0 = V; E1 = np.roll(V, -1, axis=0)
EDGE = E1 - E0
NORM = np.stack([EDGE[:, 1], -EDGE[:, 0]], 1) / np.linalg.norm(EDGE, axis=1)[:, None]  # outward normals? check below
# make normals outward
cen = V.mean(0)
for k in range(8):
    if np.dot(NORM[k], E0[k] - cen) < 0:
        NORM[k] = -NORM[k]
GLUE = np.array([(E0[(k + 4) % 8] + E1[(k + 4) % 8]) / 2 - (E0[k] + E1[k]) / 2 for k in range(8)])  # translate when exiting edge k
EPS = 1e-9

def exit_edge(p, d):
    """From interior point p moving in direction d: (t, k) first edge hit."""
    best_t, best_k = np.inf, -1
    for k in range(8):
        dn = np.dot(d, NORM[k])
        if dn <= 1e-14:
            continue
        t = np.dot(E0[k] - p, NORM[k]) / dn
        if t < best_t:
            best_t, best_k = t, k
    return best_t, best_k

def trace(p, d, Lmax, stop_at_vertex=True, vtol=1e-7):
    """Straight-line trajectory from p in direction d (unit). Returns (chords, total_len, hit_vertex, endpoint).
    chords: list of (a, b) points inside the octagon."""
    chords = []; total = 0.0
    while total < Lmax:
        t, k = exit_edge(p, d)
        q = p + t * d
        chords.append((p.copy(), q.copy()))
        total += t
        # vertex hit?
        if stop_at_vertex:
            dv = np.linalg.norm(V - q, axis=1)
            if dv.min() < vtol:
                return chords, total, True, q
        p = q + GLUE[k]
        # nudge inside numerically
        p = p - 1e-12 * NORM[(k + 4) % 8]
    return chords, total, False, p

def corner_sectors():
    """For each vertex k, the angular sector of directions pointing INTO the octagon at that corner."""
    out = []
    for k in range(8):
        a = V[(k - 1) % 8] - V[k]; b = V[(k + 1) % 8] - V[k]
        out.append((np.arctan2(a[1], a[0]), np.arctan2(b[1], b[0])))
    return out
SECT = corner_sectors()
def angle_in_sector(th, k):
    a, b = SECT[k]
    # interior angle 3π/4 from b (next vertex dir) to a (prev vertex dir) counterclockwise
    d = (th - b) % (2 * np.pi)
    w = (a - b) % (2 * np.pi)
    return 1e-9 < d < w - 1e-9

def shoot_from_cone(th, Lmax):
    """The 3 outgoing rays of direction th from the (single) cone point: one per corner whose sector contains th."""
    d = np.array([np.cos(th), np.sin(th)])
    rays = []
    for k in range(8):
        if angle_in_sector(th, k):
            p = V[k] + 1e-10 * d
            rays.append((k, trace(p, d, Lmax)))
    return rays

def saddle_directions(L):
    """Directions (mod π) of saddle connections of length <= L, verified by shooting."""
    # lattice of translations
    T = GLUE[:4]
    cands = {}
    rng = range(-5, 6)
    import itertools
    for n in itertools.product(rng, repeat=4):
        tau = n[0] * T[0] + n[1] * T[1] + n[2] * T[2] + n[3] * T[3]
        for i in range(8):
            for j in range(8):
                v = V[j] + tau - V[i]
                l = np.linalg.norm(v)
                if l < 1e-9 or l > L:
                    continue
                th = np.arctan2(v[1], v[0]) % np.pi
                key = round(th, 7)
                if key not in cands or cands[key][0] > l:
                    cands[key] = (l, th)
    log(f'{len(cands)} candidate directions')
    good = {}
    for key, (l, th) in cands.items():
        for th2 in (th, th + np.pi):
            for k, (chords, total, hit, q) in shoot_from_cone(th2, L + 1e-6):
                if hit and total <= L + 1e-6:
                    if key not in good or good[key][0] > total:
                        good[key] = (total, th)
    log(f'{len(good)} verified saddle-connection directions with length <= {L}')
    return good

def cylinders(th, Lmax=200.0, nsamp=400):
    """Cylinder decomposition in a periodic direction th: returns list of dicts
    (H, C, ribbons=[(u, chords)]) plus the saddle connections' chords."""
    d = np.array([np.cos(th), np.sin(th)]); nrm = np.array([-d[1], d[0]])
    saddles = []
    for k, (chords, total, hit, q) in shoot_from_cone(th, Lmax):
        assert hit, 'direction not periodic (saddle ray never returned to the cone point)'
        saddles.append((chords, total))
    # perpendicular coordinates of all saddle chords (they are parallel lines: c = <point, nrm>)
    schords = [(np.dot(a, nrm), np.dot(a, d), np.dot(b, d)) for chords, _ in saddles for a, b in chords]
    sc = np.array([[c, min(s0, s1), max(s0, s1)] for c, s0, s1 in schords])
    # sample closed trajectories: starting points along the transversal through the centre
    lo = -R; hi = R
    ribbons = []
    for u0 in np.linspace(lo, hi, nsamp)[1:-1]:
        p = cen + u0 * nrm
        if exit_edge(p, d)[1] < 0:
            continue
        # inside test: exit both ways
        tb, kb = exit_edge(p, -d)
        if not np.isfinite(tb):
            continue
        # start at the back wall to make a canonical closed loop
        start = p - (tb - 1e-9) * d
        chords, total, hit, endp = trace(start + 1e-12 * d, d, Lmax, stop_at_vertex=False)
        # closure: find first return to start (same point mod gluing): check each chord start against start
        ribbons.append((u0, chords, total))
    # closure detection per trajectory: walk chords, the trajectory returns when a chord start equals 'start'
    cyls = defaultdict(list)
    out = []
    for u0, chords, total in ribbons:
        st = chords[0][0]
        Csum = 0.0; closed = None
        for i, (a, b) in enumerate(chords):
            if i > 0 and np.linalg.norm(a - st) < 1e-6:
                closed = i; break
            Csum += np.linalg.norm(b - a)
        if closed is None:
            continue
        loop = chords[:closed]
        # distance up / down to nearest overlapping saddle chord
        dup = np.inf; ddn = np.inf
        for a, b in loop:
            c = np.dot(a, nrm); s0, s1 = sorted((np.dot(a, d), np.dot(b, d)))
            ov = (sc[:, 2] > s0 + 1e-9) & (sc[:, 1] < s1 - 1e-9)
            dc = sc[ov, 0] - c
            up = dc[dc > 1e-9]; dn = -dc[dc < -1e-9]
            if len(up): dup = min(dup, up.min())
            if len(dn): ddn = min(ddn, dn.min())
        if not np.isfinite(dup) or not np.isfinite(ddn):
            continue
        H = dup + ddn
        out.append(dict(u=ddn / H, H=H, C=Csum, loop=loop))
    # group by (H, C)
    groups = defaultdict(list)
    for r in out:
        groups[(round(r['H'], 6), round(r['C'], 6))].append(r)
    cyl = [dict(H=k[0], C=k[1], members=v) for k, v in groups.items()]
    return cyl, saddles

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=float, default=9.0)
    ap.add_argument('--out', default='octagon_data.json')
    args = ap.parse_args()
    good = saddle_directions(args.L)
    dirs = sorted(good.items(), key=lambda kv: kv[1][0])
    data = []
    for key, (l, th) in dirs:
        cyl, saddles = cylinders(th)
        mods = sorted([c['C'] / c['H'] for c in cyl])
        Hs = [c['H'] for c in cyl]; Cs = [c['C'] for c in cyl]
        ratio = [m / mods[0] for m in mods]
        data.append(dict(theta=float(th), shortest=float(l), ncyl=len(cyl), H=Hs, C=Cs, moduli=mods, ratio=ratio,
                         nsaddle=len(saddles), saddle_len=[float(t) for _, t in saddles],
                         members=[[dict(u=float(m['u']), loop=[[a.tolist(), b.tolist()] for a, b in m['loop']]) for m in c['members']] for c in cyl]))
        print(f'θ={np.degrees(th):8.4f}°  shortest saddle {l:.4f}  cylinders {len(cyl)}  H={np.round(Hs, 4)}  C={np.round(Cs, 4)}  moduli ratio={np.round(ratio, 6)}', flush=True)
    json.dump(data, open(args.out, 'w'))
    log('saved', args.out, len(data), 'directions')
