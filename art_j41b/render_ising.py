"""render_ising.py — 'Zero Is Not Nothing': a critical Ising configuration on the triangular lattice.

Two pigment families by spin (warm for +, cool for -), the pigment within a family chosen by the
nesting depth of the site's cluster (seas pale, islands deeper and darker), ink on every domain
wall (a loop of CLE_3), thicker for bigger loops.  Coral: the deepest islands — the ones the
theorem counts (mean depth grows like ln L / (4 sqrt3 pi)).  Rendered in true triangular geometry
(x = j + i/2, y = i sqrt3/2) by one affine transform of the lattice fields.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, affine_transform, label
sys.path.insert(0, '.')
import ising as isg
from pastel import Sheet, PIG, text_density, ink_from_distance, finish, text_width

WARM = ['blush', 'apricot', 'lemon', 'apricot', 'lemon']
COOL = ['aqua', 'mint', 'cornflower', 'lavender', 'orchid']


def render(FINAL=1024, SS=2, spins='big_spins.npy', tag='proto_ising', caption=True, px_per_site=2.0,
           origin=None, dens=(0.36, 0.78, 1.05, 1.3, 1.4), small_boost=0.35, ink_w=0.55, ink_k=0.10,
           gran=0.14, coral_depth=3, fade_edge=True, warm=WARM, cool=COOL, seed=0, min_loop=4):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    a = px_per_site * SS          # pixels per lattice unit at supersample
    s = np.load(spins)
    R, C = s.shape
    d, lab, parent, dep, N = isg.depth_field(s, return_tree=True)
    sizes = np.bincount(lab.ravel(), minlength=N + 1)
    print(f'depth {time.time()-t0:.0f}s  max depth {d.max()}  clusters {N}')
    # window: rows needed = H/(a sqrt3/2), cols = W/a + rows/2
    rows = int(np.ceil(H / (a * np.sqrt(3) / 2))) + 2
    cols = int(np.ceil(W / a + rows / 2)) + 2
    if origin is None:
        origin = ((R - rows) // 2, (C - cols) // 2)
    i0, j0 = origin
    cert_origin = [int(i0), int(j0)]
    assert i0 + rows <= R and j0 + cols <= C, f'window {rows}x{cols} exceeds lattice {R}x{C}'
    win = (slice(i0, i0 + rows), slice(j0, j0 + cols))
    cert = dict(lattice=[R, C], window_rows=rows, window_cols=cols, px_per_site=px_per_site, origin=cert_origin,
                max_depth=int(d.max()), n_clusters=int(N), bond_corr=float(isg.bond_energy(s)),
                magnetisation=float(s.mean()), mean_depth_window=float(d[win].mean()),
                depth_histogram=[int(x) for x in np.bincount(d[win].ravel())])
    # affine: output (y, x) -> input (i, j): i = y/(a*sqrt3/2), j = x/a - i/2   (input window offset at 0)
    k = a * np.sqrt(3) / 2
    mat = np.array([[1 / k, 0.0], [-0.5 / k, 1 / a]])
    off = np.array([0.0, rows / 2.0])      # j = x/a - i/2 + rows/2 keeps the sheared window inside the array

    def warp(f, order):
        return affine_transform(f.astype(np.float32), mat, offset=off, output_shape=(H, W), order=order, mode='nearest')

    sm = warp(s[win].astype(np.float32), 3)
    sm = gaussian_filter(sm, 0.35 * a)                 # smooth domain walls
    gy, gx = np.gradient(sm)
    grad = np.hypot(gx, gy) + 1e-6
    dist = np.abs(sm) / grad                           # px distance to the wall
    del gx, gy, grad
    sign = sm > 0
    # per-site fields
    dsite = np.minimum(d[win], len(dens) - 1)
    sz = sizes[lab].astype(np.float32)
    lsz = np.log(sz[win])
    # the smaller of the two clusters across each domain wall: min over the six neighbours
    msz = sz.copy()
    for di, dj in ((0, 1), (0, -1), (1, 0), (-1, 0), (-1, 1), (1, -1)):
        nb = np.roll(np.roll(sz, -di, 0), -dj, 1)
        msz = np.minimum(msz, nb)
    lmsz = np.log(msz[win])
    dep_w = warp(dsite.astype(np.float32), 0).astype(np.int8)
    lsz_w = warp(lsz, 1)
    lmsz_w = warp(lmsz, 1)
    # ink width by the smaller adjacent cluster; loops around fewer than min_loop sites get no ink
    wfield = ink_w * rs * (1 + ink_k * np.clip(lmsz_w - 3, 0, 12))
    ink = ink_from_distance(dist, wfield) * np.clip((lmsz_w - np.log(min_loop)) / 0.7 + 0.5, 0, 1)
    sheet = Sheet(W, H, seed=41 + seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if fade_edge:
        # painter's unfinished edge: fade toward the lower-right corner
        u = ((xx / W) + (yy / H)) / 2
        fade = np.clip(1 - (u - 0.72) / 0.30, 0, 1) ** 1.5
    else:
        fade = np.ones((H, W), np.float32)
    dens = np.array(dens, np.float32)
    small = small_boost * np.clip((7.5 - lsz_w) / 4.5, 0, 1)      # tiny islands get a little extra
    for fam, sgn in ((warm, True), (cool, False)):
        for dd in range(len(dens)):
            m = (sign == sgn) & (dep_w == dd)
            if not m.any(): continue
            dfield = m.astype(np.float32) * (dens[dd] + small) * fade
            dfield = gaussian_filter(dfield, 0.8)
            sheet.wash(dfield, fam[dd], granulate=gran, seed=80 + dd + 10 * sgn)
    # coral: deepest islands
    deep = (dep_w >= coral_depth)
    if deep.any():
        sheet.wash(gaussian_filter(deep.astype(np.float32), 0.8) * 1.1 * fade, 'coral')
    cert.update(n_sites_at_or_over_coral_depth=int((d[win] >= coral_depth).sum()))
    sheet.wash(np.clip(ink, 0, 1) * 0.85 * (0.35 + 0.65 * fade), 'ink')
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'Zero Is Not Nothing'
        sub = ("Ising exactly at its critical point: the mean spin is zero, and every wall is a loop inside a loop. "
               "Warm up, cool down; islands darker with depth; coral: two loops deep.")
        fs = 0.0135 * H
        fs = min(fs, fs * 0.90 * W / max(1, text_width(sub, fs, 'italic')))
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, fs, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')
    return cert


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, val = a.split('=', 1)
        try:
            val = eval(val)
        except Exception:
            pass
        kw[k] = val
    render(**kw)
