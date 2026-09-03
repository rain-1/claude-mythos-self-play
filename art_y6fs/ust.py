"""The Tree and Its Path — a uniform spanning tree of the N x N grid (Wilson's algorithm,
loop-erased random walks) and the Peano curve that winds between the tree and its dual.

Certificates: Burton–Pemantle exact degree probabilities of the UST on Z^2
  P(deg 1) = 8/pi^2 (1 - 2/pi), P(deg 2) = 4/pi (1-2/pi)(... ) etc. (we use the known values
  0.29454, 0.44699, 0.22239, 0.03608) against the census on the bulk of the grid.

usage: python3 ust.py SIZE N [seed] [out]
"""
import sys, math, time
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from skimage import measure
from pastel import *


def wilson(N, seed):
    rng = np.random.default_rng(seed)
    n = N * N
    intree = np.zeros(n, bool)
    parent = -np.ones(n, np.int64)
    root = rng.integers(n)
    intree[root] = True
    nxt = -np.ones(n, np.int64)   # loop-erased successor during a walk
    order = rng.permutation(n)
    dirs = np.array([1, -1, N, -N])
    for start in order:
        if intree[start]:
            continue
        u = start
        while not intree[u]:
            # random neighbour with boundary handling
            while True:
                d = rng.integers(4)
                if d == 0 and (u % N) == N - 1: continue
                if d == 1 and (u % N) == 0: continue
                if d == 2 and u >= n - N: continue
                if d == 3 and u < N: continue
                break
            v = u + dirs[d]
            nxt[u] = v
            u = v
        u = start
        while not intree[u]:
            intree[u] = True
            parent[u] = nxt[u]
            u = nxt[u]
    return parent, root


def degree_census(parent, N):
    n = N * N
    deg = np.zeros(n, int)
    ch = parent >= 0
    np.add.at(deg, parent[ch], 1)
    deg += ch
    # bulk only: at least 8 cells from the boundary
    ii, jj = np.divmod(np.arange(n), N)
    bulk = (ii >= 8) & (ii < N - 8) & (jj >= 8) & (jj < N - 8)
    counts = np.bincount(deg[bulk], minlength=5)[1:5] / bulk.sum()
    return counts, deg


def depth_from_root(parent, root, N):
    n = N * N
    # children lists via sorting
    ch = np.nonzero(parent >= 0)[0]
    order = np.argsort(parent[ch], kind='stable')
    ch = ch[order]
    starts = np.searchsorted(parent[ch], np.arange(n))
    ends = np.searchsorted(parent[ch], np.arange(n), side='right')
    depth = -np.ones(n, np.int64)
    depth[root] = 0
    frontier = [root]
    while frontier:
        nf = []
        for u in frontier:
            for v in ch[starts[u]:ends[u]]:
                depth[v] = depth[u] + 1
                nf.append(v)
        frontier = nf
    return depth


def render(SIZE, N, seed, out):
    SS = 2
    W = H = SIZE * SS
    t0 = time.time()
    parent, root = wilson(N, seed)
    print('wilson %.0fs' % (time.time() - t0))
    counts, deg = degree_census(parent, N)
    BP = np.array([8 / math.pi ** 2 * (1 - 2 / math.pi), 0.0, 0.0, 0.0])
    # Burton–Pemantle (1993) exact values for Z^2
    BP = np.array([0.294535, 0.446988, 0.222394, 0.036082])
    print('degree fractions measured', np.round(counts, 5), ' Burton–Pemantle', BP, ' max |diff| %.4f' % np.abs(counts - BP).max())
    depth = depth_from_root(parent, root, N)
    print('tree depth max', depth.max(), 'mean %.1f' % depth.mean())
    # --- geometry: cell size in px; tree vertices at (cell*(j+0.5), cell*(i+0.5))
    cell = W / (N + 1)
    ii, jj = np.divmod(np.arange(N * N), N)
    vx = cell * (jj + 1.0); vy = cell * (ii + 1.0)
    # thick tree bitmap for the Peano contour
    tree_im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(tree_im)
    ch = np.nonzero(parent >= 0)[0]
    tw = max(2, int(round(cell * 0.30)))
    for u in ch:
        p = parent[u]
        dr.line([(vx[u], vy[u]), (vx[p], vy[p])], fill=255, width=tw)
    tree = np.asarray(tree_im, np.float32) / 255
    # Peano curve = the contour of the thickened tree
    t1 = time.time()
    cs = measure.find_contours(tree, 0.5)
    cs.sort(key=len, reverse=True)
    peano = cs[0]   # (rows, cols)
    print('contours', len(cs), 'longest', len(peano), 'others', [len(c) for c in cs[1:4]], '%.0fs' % (time.time() - t1))
    py, px = peano[:, 0], peano[:, 1]
    L = len(px)
    # arc-length parameter -> cyclic pastel hue, slowly (3 cycles around the whole curve)
    s = np.arange(L) / L
    # --- colour field: each pixel takes the hue of the nearest curve point: nearest via a
    # rasterised label image + EDT indices
    lab = np.full((H, W), -1, np.int64)
    ix = np.clip(np.round(px).astype(int), 0, W - 1); iy = np.clip(np.round(py).astype(int), 0, H - 1)
    lab[iy, ix] = np.arange(L)
    _, inds = distance_transform_edt(lab < 0, return_indices=True)
    near = lab[inds[0], inds[1]]
    hue = np.mod(3.0 * near / L, 1.0)
    sheet = Sheet(W, H, seed=9)
    # the tree's depth as lightness: shallow (near root) = deeper pigment, leaves = pale
    # per-pixel: depth of the nearest tree vertex (cell-blocky is fine: 'growth from one point')
    dep_img = np.zeros((N, N), np.float32)
    dep_img[ii, jj] = depth
    dep_img = dep_img / dep_img.max()
    dep_field = np.asarray(Image.fromarray((dep_img * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    dep_field = gaussian_filter(dep_field, cell)
    dens = 0.92 * (0.42 + 0.58 * (1 - dep_field))
    i0, i1, t = hue_to_pigments(hue)
    for p in range(len(CYCLE)):
        w = np.where(i0 == p, 1 - t, 0) + np.where(i1 == p, t, 0)
        if w.max() <= 0:
            continue
        sheet.wash(w * dens, CYCLE[p], granulate=0.30, seed=31 + p)
    # ink: the tree drawn with branch width and ink ∝ subtree mass (a root system, not a maze)
    mass = np.ones(N * N, np.int64)
    order = np.argsort(-depth)
    for u in order:
        if parent[u] >= 0:
            mass[parent[u]] += mass[u]
    lm = np.log(mass)
    # bent threads: two Laplacian passes on node positions along the tree (parent + children mean)
    sx, sy = vx.astype(np.float64).copy(), vy.astype(np.float64).copy()
    nchild = np.bincount(parent[ch], minlength=N * N).astype(np.float64)
    for _ in range(2):
        csx = np.bincount(parent[ch], weights=sx[ch], minlength=N * N)
        csy = np.bincount(parent[ch], weights=sy[ch], minlength=N * N)
        mx = np.where(nchild > 0, csx / np.maximum(nchild, 1), sx)
        my = np.where(nchild > 0, csy / np.maximum(nchild, 1), sy)
        pxp = np.where(parent >= 0, sx[np.maximum(parent, 0)], sx)
        pyp = np.where(parent >= 0, sy[np.maximum(parent, 0)], sy)
        sx = 0.5 * sx + 0.25 * pxp + 0.25 * mx
        sy = 0.5 * sy + 0.25 * pyp + 0.25 * my
    vx, vy = sx, sy
    wid = 0.08 * cell + 1.5 * cell * (lm / lm.max()) ** 1.7
    ink = 0.10 + 1.05 * (lm / lm.max()) ** 1.0
    # draw in width classes into an 'F' image (max-composite via separate layers is overkill: additive then clip)
    tree_f = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(tree_f)
    for u in ch:
        p = parent[u]
        w = int(max(1, round(0.5 * (wid[u] + wid[p]))))
        dr.line([(vx[u], vy[u]), (vx[p], vy[p])], fill=float(ink[u]), width=w)
        if w >= 3:
            dr.ellipse([vx[u] - w / 2, vy[u] - w / 2, vx[u] + w / 2, vy[u] + w / 2], fill=float(ink[u]))
    Tk = gaussian_filter(np.asarray(tree_f, np.float32), 0.45 * SS)
    Tk = np.clip(Tk, 0, 1.1)
    sheet.wash(Tk * 0.85, 'ink')
    # the Peano curve itself as a pale thread (the path)
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    dr.line(list(zip(px.tolist(), py.tolist())), fill=1.0, width=max(1, int(round(0.08 * cell))))
    Pk = gaussian_filter(np.asarray(im, np.float32), 0.4 * SS)
    sheet.wash(Pk / (Pk.max() + 1e-9) * 0.16, 'sepia')
    # root star
    S = discs_density(W, H, [vx[root]], [vy[root]], [cell * 2.2], [1.0], sigma=cell * 1.2)
    sheet.wash(S / (S.max() + 1e-9) * 0.9, 'coral')
    S = discs_density(W, H, [vx[root]], [vy[root]], [cell * 0.7], [1.0], sigma=cell * 0.3)
    sheet.wash(S / (S.max() + 1e-9) * 0.8, 'ink')
    sheet.caption_strip(0.905, 0.985)
    items = [("The Tree and Its Path", 0.05 * W, 0.935 * H, 0.030 * W, 'serif_bold', 'ls'),
             ("one tree grown by loop-erased wandering, uniform among all %d^%d; leaves %.4f of it (Burton–Pemantle: 0.2945)" % (
                 N, N, counts[0]), 0.05 * W, 0.962 * H, 0.0135 * W, 'italic', 'ls')]
    T = text_density(W, H, items)
    sheet.wash(T * 0.85, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), out)
    return dict(counts=counts.tolist(), BP=BP.tolist(), depth_max=int(depth.max()), L=int(L))


if __name__ == '__main__':
    SIZE = int(sys.argv[1]); N = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    out = sys.argv[4] if len(sys.argv) > 4 else 'ust_%d.png' % SIZE
    print(render(SIZE, N, seed, out))
