"""Every Cell Remembers Its Grandmother — a tissue grown by cell division.
Cells are Voronoi regions of seeds in a growing disc. Each round, each cell divides with
probability p along its short axis (Errera's rule: the new wall is the shortest one through the
centroid, i.e. perpendicular to the long axis) with angular noise; then a few Lloyd steps relax
the tissue. Lineage is recorded; the palette is the lineage: pigment = ancestor at generation 3,
lightness = ancestor at generation 6.
Certificates: mean sides -> 6 (Euler), Lewis's law (area linear in sides), Aboav–Weaire
m(n) = (6 - a) + (6a + mu2)/n.

usage: python3 tissue.py SIZE [target_cells] [seed] [out]
"""
import sys, math, time, json
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image
from pastel import *


def label_raster(seeds, R, res):
    """nearest-seed labels on a res x res raster of the disc of radius R; -1 outside"""
    ax = np.linspace(-R, R, res)
    X, Y = np.meshgrid(ax, ax)
    inside = X * X + Y * Y <= R * R
    pts = np.c_[X[inside], Y[inside]]
    _, lab = cKDTree(seeds).query(pts)
    L = np.full((res, res), -1, np.int64)
    L[inside] = lab
    return L, X, Y, inside


def cell_stats(L, X, Y, nseeds):
    ids = L.ravel(); m = ids >= 0
    cnt = np.bincount(ids[m], minlength=nseeds).astype(float)
    sx = np.bincount(ids[m], weights=X.ravel()[m], minlength=nseeds)
    sy = np.bincount(ids[m], weights=Y.ravel()[m], minlength=nseeds)
    cxs = sx / np.maximum(cnt, 1); cys = sy / np.maximum(cnt, 1)
    # covariance for the long axis
    dx = X.ravel()[m] - cxs[ids[m]]; dy = Y.ravel()[m] - cys[ids[m]]
    sxx = np.bincount(ids[m], weights=dx * dx, minlength=nseeds) / np.maximum(cnt, 1)
    syy = np.bincount(ids[m], weights=dy * dy, minlength=nseeds) / np.maximum(cnt, 1)
    sxy = np.bincount(ids[m], weights=dx * dy, minlength=nseeds) / np.maximum(cnt, 1)
    ang = 0.5 * np.arctan2(2 * sxy, sxx - syy)   # long-axis angle
    return cnt, cxs, cys, ang


def neighbours(L, nseeds):
    """adjacency from the raster (4-neighbour label changes); boundary cells flagged"""
    pairs = set()
    a, b = L[:, :-1], L[:, 1:]
    m = (a != b) & (a >= 0) & (b >= 0)
    pairs.update(zip(a[m].tolist(), b[m].tolist()))
    a, b = L[:-1, :], L[1:, :]
    m = (a != b) & (a >= 0) & (b >= 0)
    pairs.update(zip(a[m].tolist(), b[m].tolist()))
    nb = [set() for _ in range(nseeds)]
    for i, j in pairs:
        nb[i].add(j); nb[j].add(i)
    # boundary: touches the outside
    bd = np.zeros(nseeds, bool)
    for a, b in ((L[:, :-1], L[:, 1:]), (L[:-1, :], L[1:, :])):
        m = (a >= 0) & (b < 0); bd[a[m]] = True
        m = (b >= 0) & (a < 0); bd[b[m]] = True
    return nb, bd


def grow(target, seed, res=700, p_div=0.6):
    rng = np.random.default_rng(seed)
    seeds = np.array([[0.0, 0.0]])
    lineage = [[]]           # list of ancestor indices path (binary string as list of 0/1)
    R = 1.0
    rounds = 0
    while len(seeds) < target:
        n = len(seeds)
        R = math.sqrt(n) * 1.0    # keep mean cell area ~ pi
        L, X, Y, inside = label_raster(seeds, R, res)
        cnt, cxs, cys, ang = cell_stats(L, X, Y, n)
        new_seeds, new_lin = [], []
        for i in range(n):
            area = cnt[i]
            if rng.random() < p_div * min(1.0, area / cnt.mean()) and len(seeds) + len(new_seeds) - i < target * 1.05:
                th = ang[i] + rng.normal(0, 0.25)      # daughters along the long axis (wall across it)
                r = 0.28 * math.sqrt(max(area, 1) / cnt.mean())
                new_seeds.append([cxs[i] + r * math.cos(th), cys[i] + r * math.sin(th)]); new_lin.append(lineage[i] + [0])
                new_seeds.append([cxs[i] - r * math.cos(th), cys[i] - r * math.sin(th)]); new_lin.append(lineage[i] + [1])
            else:
                new_seeds.append([cxs[i], cys[i]]); new_lin.append(lineage[i])
        seeds = np.array(new_seeds); lineage = new_lin
        # growth = uniform dilation of the whole tissue (mean cell area stays ~pi)
        seeds *= math.sqrt(len(seeds)) / R
        R = math.sqrt(len(seeds))
        # partial Lloyd relaxation (a tissue is not a centroidal tessellation: young cells stay small)
        for _ in range(2):
            L, X, Y, inside = label_raster(seeds, R, res)
            cnt, cxs, cys, ang = cell_stats(L, X, Y, len(seeds))
            seeds = 0.6 * seeds + 0.4 * np.c_[cxs, cys]
        rounds += 1
        print('round %d: %d cells' % (rounds, len(seeds)))
    return seeds, lineage, R


def laws(L, X, Y, seeds):
    n = len(seeds)
    cnt, cxs, cys, ang = cell_stats(L, X, Y, n)
    nb, bd = neighbours(L, n)
    sides = np.array([len(s) for s in nb])
    interior = ~bd
    ms = sides[interior].mean()
    out = dict(cells=n, interior=int(interior.sum()), mean_sides=float(ms))
    # Lewis: mean area vs sides
    lewis = {}
    for k in range(4, 10):
        m = interior & (sides == k)
        if m.sum() >= 5:
            lewis[k] = float(cnt[m].mean() / cnt[interior].mean())
    ks = np.array(sorted(lewis)); vals = np.array([lewis[k] for k in ks])
    sl, ic = np.polyfit(ks, vals, 1)
    out['lewis'] = {int(k): round(v, 3) for k, v in lewis.items()}
    out['lewis_fit'] = dict(slope=float(sl), intercept=float(ic), area_at_6=float(sl * 6 + ic))
    # Aboav–Weaire: m(n) = mean sides of neighbours of n-sided cells; n m(n) = (6-a) n + (6a + mu2)
    aw = {}
    for k in range(4, 10):
        m = np.nonzero(interior & (sides == k))[0]
        if len(m) >= 5:
            aw[k] = float(np.mean([np.mean([sides[j] for j in nb[i]]) for i in m]))
    ks = np.array(sorted(aw)); vals = np.array([aw[k] * k for k in ks])
    s2, i2 = np.polyfit(ks, vals, 1)
    mu2 = float(np.var(sides[interior]))
    a = 6 - s2
    out['aboav'] = {int(k): round(v, 3) for k, v in aw.items()}
    out['aboav_fit'] = dict(a=float(a), intercept=float(i2), predicted_intercept_6a_plus_mu2=float(6 * a + mu2), mu2=mu2)
    out['sides_hist'] = {int(k): int(v) for k, v in zip(*np.unique(sides[interior], return_counts=True))}
    return out, sides, bd, nb


def render(SIZE, target, seed, out):
    SS = 2
    W = H = SIZE * SS
    t0 = time.time()
    seeds, lineage, R = grow(target, seed)
    print('grown %d cells in %.0fs' % (len(seeds), time.time() - t0))
    # statistics on a fine raster
    L, X, Y, inside = label_raster(seeds, R, 1400)
    stats, sides, bd, nb = laws(L, X, Y, seeds)
    print(json.dumps(stats, indent=1))
    # render raster
    Rw = 0.45 * W
    ax = np.linspace(-R * (W / 2) / Rw, R * (W / 2) / Rw, W)
    Xr, Yr = np.meshgrid(ax, ax)
    ins = Xr * Xr + Yr * Yr <= R * R
    # organic outline: the disc boundary wobbles
    th = np.arctan2(Yr, Xr)
    wob = R * (1 + 0.035 * np.sin(3 * th + 0.7) + 0.02 * np.sin(7 * th + 2.1))
    ins = Xr * Xr + Yr * Yr <= wob * wob
    pts = np.c_[Xr[ins], Yr[ins]]
    _, lab = cKDTree(seeds).query(pts)
    Lr = np.full((H, W), -1, np.int64); Lr[ins] = lab
    # hierarchy palette: pigment = ancestor at generation 3, lightness = ancestor at generation 6
    pigs = ['coral', 'apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']
    def anc(lin, g):
        return tuple(lin[:g])
    clones = sorted(set(anc(l, 3) for l in lineage))
    rng = np.random.default_rng(seed + 5)
    clone_pig = {c: pigs[k % len(pigs)] for k, c in enumerate(clones)}
    sub = sorted(set(anc(l, 6) for l in lineage))
    sub_light = {s: float(rng.uniform(0.55, 1.0)) for s in sub}
    cell_pig = np.array([pigs.index(clone_pig[anc(l, 3)]) for l in lineage])
    cell_light = np.array([sub_light[anc(l, 6)] for l in lineage])
    # walls: EDT of label boundaries
    bnd = np.zeros((H, W), bool)
    bnd[:, 1:] |= (Lr[:, 1:] != Lr[:, :-1]); bnd[1:, :] |= (Lr[1:, :] != Lr[:-1, :])
    bnd &= (Lr >= 0)
    dwall = distance_transform_edt(~bnd)
    sheet = Sheet(W, H, seed=23)
    cellsize = Rw / math.sqrt(len(seeds)) * 1.8
    pool = 0.45 + 0.55 * np.exp(-dwall / (0.22 * cellsize))   # watercolour pooling toward the walls
    light_map = np.where(Lr >= 0, cell_light[np.maximum(Lr, 0)], 0)
    for k, name in enumerate(pigs):
        m = (Lr >= 0) & (cell_pig[np.maximum(Lr, 0)] == k)
        if not m.any(): continue
        D = m.astype(np.float32) * light_map * pool * 0.85
        D = gaussian_filter(D, 0.6 * SS)
        sheet.wash(D, name, granulate=0.3, seed=80 + k)
    # walls in ink
    ink = ink_from_distance(dwall, 0.9 * SS) * (Lr >= 0)
    sheet.wash(ink * 0.75, 'ink')
    # outer membrane: thicker
    dout = distance_transform_edt(ins)
    sheet.wash(np.exp(-(dout / (1.6 * SS)) ** 2) * ins * 0.7, 'ink')
    # the first cell (origin) remembered: a coral dot where it all began
    Dc = discs_density(W, H, [W / 2], [H / 2], [0.012 * W], [1.0], sigma=1.5 * SS)
    sheet.wash(Dc / (Dc.max() + 1e-9) * 0.9, 'coral')
    sheet.caption_strip(0.905, 0.985)
    af = stats['aboav_fit']; lf = stats['lewis_fit']
    items = [("Every Cell Remembers Its Grandmother", 0.05 * W, 0.935 * H, 0.030 * W, 'serif_bold', 'ls'),
             ("%d cells from one, colour = the clone at generation 3, shade = generation 6; mean sides %.3f, Lewis slope %.2f, Aboav a = %.2f" % (
                 len(seeds), stats['mean_sides'], lf['slope'], af['a']),
              0.05 * W, 0.962 * H, 0.0135 * W, 'italic', 'ls')]
    T = text_density(W, H, items)
    sheet.wash(T * 0.85, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), out)
    return stats


if __name__ == '__main__':
    SIZE = int(sys.argv[1])
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    out = sys.argv[4] if len(sys.argv) > 4 else 'tissue_%d.png' % SIZE
    stats = render(SIZE, target, seed, out)
    json.dump(stats, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
