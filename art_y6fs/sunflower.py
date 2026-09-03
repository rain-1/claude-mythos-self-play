"""The Sunflower of Fifths — Vogel spiral with divergence angle log2(3) (a perfect fifth
per step, reduced to the octave) instead of the golden angle.

Bead k sits at angle 2*pi*frac(k*alpha), radius c*sqrt(k), alpha = log2 3.
Its nearest neighbours are k +- m where m minimises
    d(m,k)^2 = c^2 [ (2 pi sqrt(k) ||m alpha||)^2 + m^2/(4k) ]
so the visible spiral families (parastichies) are the m with record-small ||m alpha||:
the convergents of log2 3 — 1, 2, 5, 12, 41, 53, 306, 665, 15601 — i.e. exactly the equal
temperaments whose fifth is a record approximation. The flower draws the ladder of tunings.

usage: python3 sunflower.py SIZE N [out]
"""
import sys, json, math, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter
from pastel import *

ALPHA = math.log2(3.0)


def cf(x, n=20):
    a = []
    for _ in range(n):
        q = math.floor(x); a.append(q); x -= q
        if x < 1e-12: break
        x = 1 / x
    return a


def convergents(a):
    p0, q0, p1, q1 = 1, 0, a[0], 1
    out = [(p1, q1)]
    for ai in a[1:]:
        p0, q0, p1, q1 = p1, q1, ai * p1 + p0, ai * q1 + q0
        out.append((p1, q1))
    return out


def intermediates(a):
    """all intermediate fractions (semiconvergents) denominators in order"""
    p0, q0, p1, q1 = 1, 0, a[0], 1
    out = [q1]
    for ai in a[1:]:
        for j in range(1, ai + 1):
            out.append(j * q1 + q0)
        p0, q0, p1, q1 = p1, q1, ai * p1 + p0, ai * q1 + q0
    return out


def frac_dist(x):
    return abs(x - round(x))


def predicted_nn(k, mmax=20000):
    """m minimising the analytic neighbour distance at index k (both neighbours k+m,k-m)."""
    best = None
    for m in range(1, min(mmax, k) + 1):
        d2 = (2 * math.pi * math.sqrt(k) * frac_dist(m * ALPHA)) ** 2 + m * m / (4 * k)
        if best is None or d2 < best[0]:
            best = (d2, m)
    return best[1]


def census(N):
    """KD-tree nearest-neighbour index differences vs analytic prediction, per radial band."""
    k = np.arange(N)
    th = 2 * np.pi * np.mod(k * ALPHA, 1.0)
    r = np.sqrt(k)
    xy = np.c_[r * np.cos(th), r * np.sin(th)]
    tree = cKDTree(xy)
    d, idx = tree.query(xy, k=4)
    dk1 = np.abs(idx[:, 1] - k)   # nearest
    dk2 = np.abs(idx[:, 2] - k)
    dk3 = np.abs(idx[:, 3] - k)
    rows = []
    edges = np.unique(np.round(np.geomspace(4, N, 40)).astype(int))
    for lo, hi in zip(edges[:-1], edges[1:]):
        sl = slice(lo, hi)
        fam = {}
        for arr in (dk1[sl], dk2[sl], dk3[sl]):
            u, c = np.unique(arr, return_counts=True)
            for uu, cc in zip(u, c):
                fam[int(uu)] = fam.get(int(uu), 0) + int(cc)
        top = sorted(fam.items(), key=lambda t: -t[1])[:3]
        u1, c1 = np.unique(dk1[sl], return_counts=True)
        nn_meas = int(u1[np.argmax(c1)])
        kmid = int(math.sqrt(lo * hi))
        rows.append(dict(k_lo=int(lo), k_hi=int(hi), r_lo=float(math.sqrt(lo)), r_hi=float(math.sqrt(hi)),
                         nn_measured=nn_meas, nn_predicted=predicted_nn(kmid), families=top))
    # transitions of the nearest family (measured) as k increases
    trans = []
    prev = None
    for kk in range(1, N):
        v = int(dk1[kk])
        if v != prev:
            trans.append((kk, v)); prev = v
    # compress: keep first index where each value takes over for a stretch >= 50
    return rows, dk1, dk2, dk3, trans


def render(SIZE, N, out):
    SS = 2
    W = H = SIZE * SS
    t0 = time.time()
    k = np.arange(N)
    th = 2 * np.pi * np.mod(k * ALPHA, 1.0)
    rr = np.sqrt(k)
    R = 0.455 * W
    c = R / math.sqrt(N)          # px per unit
    cx, cy = W / 2, H / 2
    xs = cx + c * rr * np.cos(th)
    ys = cy + c * rr * np.sin(th)
    rows, dk1, dk2, dk3, trans = census(N)

    sheet = Sheet(W, H, seed=3)
    # family palette: nearest-neighbour family -> pigment (the temperament ladder)
    fam_pig = {1: 'blush', 2: 'blush', 3: 'blush', 5: 'orchid', 7: 'orchid', 12: 'coral', 17: 'coral', 29: 'apricot', 41: 'apricot',
               53: 'apricot', 94: 'pistachio', 147: 'pistachio', 200: 'mint', 253: 'mint', 306: 'aqua', 359: 'cornflower', 665: 'cornflower', 971: 'orchid'}
    # pigment index per bead from nearest family; second family lightens/darkens
    pig_names = sorted(set(fam_pig.values()), key=CYCLE.index)
    fam1 = np.array([fam_pig.get(int(v), 'blush') for v in dk1])
    bead_r = 0.40 * c * np.ones(N)   # bead radius in px (spacing ~ c units)
    # slight size modulation: the pitch's distance from its 12-TET note (comma drift) as a breathing
    pc = np.mod(k * ALPHA, 1.0)
    dev = np.abs(pc * 12 - np.round(pc * 12))  # 0..0.5 in semitone units
    bead_r *= (0.80 + 0.45 * (1 - 2 * dev))
    # florets: dense at the heart, lighter toward the rim
    dens = 1.0 * (1.0 - 0.42 * (rr / rr.max()) ** 1.3)
    # rim: the flower head ends on an irregular front (painter's unfinished edge)
    rim = 1.0 - 0.025 * (1 + np.sin(5 * th + 1.0)) * 0.5 - 0.02 * (1 + np.sin(13 * th + 2.0)) * 0.5
    edge_t = np.clip((rr / rr.max() - 0.90 * rim) / (0.10 * rim + 1e-9), 0, 1)
    dens *= (1 - edge_t) ** 1.2
    # soft hand-over: pigment shares blend across each ring boundary (no archery target)
    # family share per bead = smoothed indicator over k (window ~8% of k)
    shares = {}
    for name in pig_names:
        ind = (fam1 == name).astype(np.float32)
        # smooth in k with a window proportional to k (log-scale smoothing)
        sm = np.zeros(N, np.float32)
        lk = np.log(np.maximum(k, 1))
        # bin by log k
        nb = 400
        bins = np.clip(((lk - lk.min()) / (lk.max() - lk.min() + 1e-9) * nb).astype(int), 0, nb - 1)
        cnt = np.bincount(bins, minlength=nb).astype(np.float32)
        tot = np.bincount(bins, weights=ind, minlength=nb)
        prof = tot / np.maximum(cnt, 1)
        prof = gaussian_filter(prof, 6.0)
        shares[name] = prof[bins]
    tot = sum(shares.values()) + 1e-9
    # per pigment: draw discs, blur, wash
    for name in pig_names:
        w = shares[name] / tot
        m = w > 0.02
        if not m.any():
            continue
        D = discs_density(W, H, xs[m], ys[m], bead_r[m], (dens * w)[m], sigma=0.35 * c)
        D = D / (D.max() + 1e-9) * 0.95
        sheet.wash(D, name, granulate=0.25, seed=11 + CYCLE.index(name))
    # --- the parastichy threads: nearest family in ink, opposed family in the ring pigment
    segs1, segs2, w2 = [], [], []
    kk = np.arange(N)
    tgt1 = kk + dk1
    ok = tgt1 < N
    segs1 = np.c_[xs[ok], ys[ok], xs[tgt1[ok]], ys[tgt1[ok]]]
    # opposed family: second neighbour unless it is a multiple of the first (same spiral, two steps)
    d2 = np.where(dk2 % np.maximum(dk1, 1) == 0, dk3, dk2)
    tgt2 = kk + d2
    ok2 = (tgt2 < N) & (d2 % np.maximum(dk1, 1) != 0)
    segs2 = np.c_[xs[ok2], ys[ok2], xs[tgt2[ok2]], ys[tgt2[ok2]]]
    Dthread = draw_lines_density(W, H, segs1, 0.18 * c, weights=dens[ok], sigma=0.10 * c)
    Dthread = Dthread / (Dthread.max() + 1e-9)
    sheet.wash(Dthread * 1.25, 'ink')
    # opposed-family threads, coloured by the ring they cross (use the bead's dominant pigment)
    dom = np.array([max(shares, key=lambda nm: shares[nm][i]) for i in range(N)]) if N <= 200000 else fam1
    for name in pig_names:
        mm = ok2 & (dom == name)
        if mm.sum() < 5:
            continue
        S = np.c_[xs[mm], ys[mm], xs[tgt2[mm]], ys[tgt2[mm]]]
        Dt = draw_lines_density(W, H, S, 0.22 * c, weights=dens[mm], sigma=0.14 * c)
        Dt = Dt / (Dt.max() + 1e-9)
        sheet.wash(Dt * 1.1, name)
    # ink: a tiny centre dot per bead (the seed)
    Dk = discs_density(W, H, xs, ys, 0.17 * c * np.ones(N), 0.55 * dens, sigma=0.12 * c)
    Dk = Dk / (Dk.max() + 1e-9) * 0.75
    sheet.wash(Dk, 'ink')
    # the founding gesture: seed 0 (the fundamental) as a coral bloom at the heart
    Sb = discs_density(W, H, [cx], [cy], [2.2 * c], [1.0], sigma=1.3 * c)
    sheet.wash(Sb / (Sb.max() + 1e-9) * 0.9, 'coral')
    Sb2 = discs_density(W, H, [cx], [cy], [0.6 * c], [1.0], sigma=0.3 * c)
    sheet.wash(Sb2 / (Sb2.max() + 1e-9) * 0.8, 'ink')
    # ring annotations: the temperament at each hand-over, along one spoke (angle -100deg)
    items = []
    ang = math.radians(-100)
    seen = set()
    for kk, v in trans:
        if v in seen or kk < 3:
            continue
        # keep only takeovers that last: check dominance over next 200 beads
        if kk + 200 < N and np.mean(dk1[kk:kk + 200] == v) < 0.6:
            continue
        seen.add(v)
        rad = c * math.sqrt(kk)
        x = cx + rad * math.cos(ang); y = cy + rad * math.sin(ang)
        items.append((str(v), x + 0.012 * W, y, 0.0115 * W, 'serif', 'lm'))
        print('takeover', v, 'at k=', kk, 'r=%.1f' % math.sqrt(kk))
    # title
    items.append(("The Sunflower of Fifths", 0.05 * W, 0.935 * H, 0.030 * W, 'serif_bold', 'ls'))
    items.append(("a seed every perfect fifth: the spirals you can count are the temperaments whose fifth is a record — 12, 53, 306, 665",
                  0.05 * W, 0.962 * H, 0.0135 * W, 'italic', 'ls'))
    T = text_density(W, H, items)
    sheet.wash(T * 0.85, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), out)
    print('render %.0fs' % (time.time() - t0))
    return rows, trans


if __name__ == '__main__':
    SIZE = int(sys.argv[1]); N = int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else 'sunflower_%d.png' % SIZE
    a = cf(ALPHA - 1, 16)
    print('cf(log2 3 - 1) =', a)
    print('convergent denominators:', [q for p, q in convergents(a)])
    print('intermediate denominators:', intermediates(a))
    rows, trans = render(SIZE, N, out)
    for r in rows:
        print('k %7d..%7d  r %6.1f..%6.1f  nn meas %5d pred %5d  families %s' % (
            r['k_lo'], r['k_hi'], r['r_lo'], r['r_hi'], r['nn_measured'], r['nn_predicted'], r['families']))
    json.dump(dict(rows=rows, N=N), open(out.replace('.png', '_census.json'), 'w'), indent=1)
