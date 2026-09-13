"""render_far.py — THE PATTERN IS IN THE DISTANCE.  A stealthy hyperuniform point pattern and a Poisson
pattern of the same density, each seen from ever farther away toward the right of the sheet.

Two bands, one period of each periodic box.  Left: coins (soft discs) tinted by Voronoi degree with the
Voronoi web in ink.  Toward the right the density is smoothed at a growing scale (a geometric ramp of
Gaussian widths) — the hyperuniform band goes perfectly flat once the smoothing exceeds 2π/K, the Poisson
band stays cloudy at every scale (its variance only falls like 1/σ²).  Coral circles of one radius carry
their exact point counts.  Insets: the structure factor of each (the paper hole is the order).

usage: python3 render_far.py FW FH points.npy cert.json out_prefix
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.spatial import Voronoi, cKDTree
from PIL import Image, ImageDraw
import pastel as P
from stealthy import Stealthy, poisson

FW, FH = int(sys.argv[1]), int(sys.argv[2]); PTS = sys.argv[3]; CERT = json.load(open(sys.argv[4])); OUT = sys.argv[5]
SS = 2; W, H = FW * SS, FH * SS; rs = FW / 1024.0 * SS
t0 = time.time()
r_st = np.load(PTS); box = np.array(CERT['box']); N = len(r_st); K = CERT['K']
r_po = poisson(N, box, seed=5)

sheet = P.Sheet(W, H, seed=17)
bw = 0.92 * W; bh = bw / (box[0] / box[1])
bx0 = (W - bw) / 2
band_y = [0.03 * H, 0.03 * H + bh + 0.05 * H]
ppu = bw / box[0]                       # pixels per unit length (unit density: mean spacing 1)
print('band', bw, bh, 'px per unit', ppu, flush=True)

SIG_MIN, SIG_MAX = 0.16, 3.2            # smoothing widths in units, left → right
def ramp(xfrac):
    return np.clip((xfrac - 0.10) / 0.88, 0, 1) ** 1.35

def voronoi_degree_and_edges(r):
    """periodic Voronoi: tile 3×3, keep cells of the central copy"""
    shifts = np.array([[i, j] for i in (-1, 0, 1) for j in (-1, 0, 1)], float) * box
    big = np.concatenate([r + s for s in shifts])
    vor = Voronoi(big)
    centre = np.arange(4 * N, 5 * N)          # the (0,0) shift is index 4 in shifts
    deg = np.zeros(N, int)
    segs = []
    for (p, q), (a, b) in zip(vor.ridge_points, vor.ridge_vertices):
        if a < 0 or b < 0:
            continue
        pin, qin = 4 * N <= p < 5 * N, 4 * N <= q < 5 * N
        if pin: deg[p - 4 * N] += 1
        if qin: deg[q - 4 * N] += 1
        if pin or qin:
            segs.append(np.concatenate([vor.vertices[a], vor.vertices[b]]))
    return deg, np.array(segs)

def band(r, y0, pigs, label, seed):
    """pigs: dict degree-class -> pigment: 'lo' (≤5), 'mid' (6), 'hi' (≥7)"""
    deg, segs = voronoi_degree_and_edges(r)
    cls = np.where(deg <= 5, 0, np.where(deg == 6, 1, 2))
    Hb, Wb = int(round(bh)), int(round(bw))
    px = r[:, 0] * ppu; py = r[:, 1] * ppu
    fields = []
    for c in range(3):
        m = cls == c
        f = np.zeros((Hb, Wb), np.float32)
        np.add.at(f, (np.clip(py[m].astype(int), 0, Hb - 1), np.clip(px[m].astype(int), 0, Wb - 1)), 1.0)
        fields.append(f)
    # multi-scale ladder (periodic blur = 'wrap' since the band is one period)
    xfrac = (np.arange(Wb) + 0.5) / Wb
    lev = np.log2(SIG_MAX / SIG_MIN) * ramp(xfrac)            # fractional level per column
    nlev = int(np.ceil(lev.max())) + 1
    out = [np.zeros((Hb, Wb), np.float32) for _ in range(3)]
    total = np.zeros((Hb, Wb), np.float32)
    for k in range(nlev):
        sig = SIG_MIN * 2 ** k * ppu
        wgt = np.clip(1 - np.abs(lev - k), 0, 1)[None, :]       # tent weights between levels
        if not (wgt > 0).any():
            continue
        for c in range(3):
            g = gaussian_filter(fields[c], sig, mode='wrap')
            out[c] += wgt * g
    mean_density = N / (Hb * Wb)
    for c in range(3):
        out[c] /= mean_density                                   # 1 = uniform paper-tone reference
    tot = out[0] + out[1] + out[2]
    # constant-gain mapping around the mean (the same for both bands): a uniform field is an even wash of 0.55,
    # deviations from the mean are shown with gain 1.4 and a soft knee for the coins
    dev = tot - 1.0
    dens = 0.55 + 1.4 * np.where(dev > 0, dev / (1 + dev / 1.6) * 1.0, dev)
    dens = np.clip(dens, 0, None)
    ybnd = int(round(y0))
    for c, key in enumerate(('lo', 'mid', 'hi')):
        d = dens * out[c] / np.maximum(tot, 1e-6)
        full = np.zeros((H, W), np.float32); full[ybnd:ybnd + Hb, int(bx0):int(bx0) + Wb] = d
        sheet.wash(full, pigs[key], granulate=0.10, seed=seed + c)
    # Voronoi web in ink, fading with the ramp
    im = Image.new('F', (Wb, Hb), 0.0); dr = ImageDraw.Draw(im)
    wv = max(1, int(round(0.55 * rs)))
    for (x0, y0_, x1, y1) in segs * ppu:
        dr.line([(x0, y0_), (x1, y1)], fill=1.0, width=wv)
    web = gaussian_filter(np.asarray(im, np.float32), 0.35 * rs)
    web *= ((1 - ramp(xfrac)) ** 2.2)[None, :]
    full = np.zeros((H, W), np.float32); full[ybnd:ybnd + Hb, int(bx0):int(bx0) + Wb] = np.clip(web, 0, 1)
    sheet.wash(0.55 * full, 'ink')
    # coral windows with exact counts
    tree = cKDTree(r, boxsize=box)
    R = 2.5
    yy, xx = np.mgrid[:Hb, :Wb]
    ring = np.zeros((Hb, Wb), np.float32); labels = []
    for k, xf in enumerate((0.09, 0.27, 0.45, 0.63, 0.81)):
        cx, cy = xf * box[0], (0.32 + 0.36 * (k % 2)) * box[1]
        cnt = len(tree.query_ball_point([cx, cy], R))
        rr = np.hypot(xx - cx * ppu, yy - cy * ppu)
        ring += np.exp(-((rr - R * ppu) / (0.9 * rs)) ** 2)
        labels.append((str(cnt), bx0 + cx * ppu, y0 + cy * ppu - R * ppu - 0.006 * H, int(0.0115 * H), 'italic', 'ms'))
    full = np.zeros((H, W), np.float32); full[ybnd:ybnd + Hb, int(bx0):int(bx0) + Wb] = ring
    sheet.wash(1.1 * full, 'coral')
    sheet.wash(0.9 * P.text_density(W, H, labels), 'ink')
    # band label
    sheet.wash(0.9 * P.text_density(W, H, [(label, bx0, y0 + Hb + 0.016 * H, int(0.0125 * H), 'italic', 'ls')]), 'ink')
    print('band done', label[:30], 'degree classes', np.bincount(cls, minlength=3), '[%.0fs]' % (time.time() - t0), flush=True)
    return deg

deg_st = band(r_st, band_y[0], dict(lo='aqua', mid='cornflower', hi='lavender'),
              'stealthy hyperuniform — optimised so that no wave longer than 2π/K fits the pattern; from afar it is flat', 50)
deg_po = band(r_po, band_y[1], dict(lo='lemon', mid='apricot', hi='blush'),
              'Poisson — the same 5,000 points thrown at random; from afar it is still weather', 60)

# ---- structure-factor insets (bottom strip) ----
st = Stealthy(N, aspect=box[0] / box[1], chi=CERT['chi'], seed=0)
ins = 0.10 * H; iy = band_y[1] + bh + 0.04 * H
for j, (r, x0i, lab) in enumerate(((r_st, 0.30 * W - ins / 2, 'S(k) of the upper pattern: zero inside the disc |k| < K'),
                                    (r_po, 0.70 * W - ins / 2, 'S(k) of the lower pattern: no hole, noise at every k'))):
    kx, ky, Sg = st.structure_factor_grid(r, kmax_factor=2.6)
    # resample the S(k) grid to a square inset (kx, ky are different lattices: Lx = 4 Ly) by nearest lookup
    n_i = int(round(ins))
    u = (np.arange(n_i) + 0.5) / n_i * 2 - 1
    KX, KY = np.meshgrid(u * 2.6 * K, u * 2.6 * K)
    ix = np.clip(np.round(KX * box[0] / (2 * np.pi)).astype(int) + len(kx) // 2, 0, len(kx) - 1)
    iyy = np.clip(np.round(KY * box[1] / (2 * np.pi)).astype(int) + len(ky) // 2, 0, len(ky) - 1)
    Sq = Sg[iyy, ix]
    d = 1.3 * Sq / (Sq + 1.0)
    d *= (np.hypot(KX, KY) <= 2.6 * K)
    full = np.zeros((H, W), np.float32); full[int(iy):int(iy) + n_i, int(x0i):int(x0i) + n_i] = d
    sheet.wash(full, 'cornflower' if j == 0 else 'apricot', granulate=0.1)
    # coral circle at |k| = K
    yy, xx = np.mgrid[:n_i, :n_i]
    rr = np.hypot(xx - n_i / 2, yy - n_i / 2) / (n_i / 2) * 2.6 * K
    ring = np.exp(-((rr - K) / (0.9 * rs * 2.6 * K / (n_i / 2))) ** 2)
    full = np.zeros((H, W), np.float32); full[int(iy):int(iy) + n_i, int(x0i):int(x0i) + n_i] = ring
    sheet.wash(1.2 * full, 'coral')
    sheet.wash(0.9 * P.text_density(W, H, [(lab, x0i + n_i / 2, iy + n_i + 0.014 * H, int(0.0105 * H), 'italic', 'ms')]), 'ink')
print('insets [%.0fs]' % (time.time() - t0), flush=True)

sv = np.array(CERT['stealthy_mean_var']); pv = np.array(CERT['poisson_mean_var']); radii = CERT['radii']
title = 'The Pattern Is in the Distance'
sub = (f'Two scatterings of {N:,} points at one density, looked at from ever farther away toward the right. Up close both are '
       f'disorder; only one of them was made so that no long wave fits, and from afar it is calm. Each coral circle holds the count beside it.')
fs_t = int(0.034 * H); fs_s = int(0.0128 * H)
items = [(title, 0.04 * W, 0.948 * H, fs_t, 'serif_bold', 'ls'), (sub, 0.04 * W, 0.974 * H, fs_s, 'italic', 'ls')]
print('caption width', P.text_width(sub, fs_s, 'italic') / W, flush=True)
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FW, FH), OUT + f'_{FW}x{FH}.png')
json.dump(dict(N=N, K=K, chi=CERT['chi'], phi_over_N=CERT['phi_over_N'], degree_hist_stealthy=np.bincount(deg_st).tolist(),
               degree_hist_poisson=np.bincount(deg_po).tolist(), radii=radii, stealthy_mean_var=sv.tolist(),
               poisson_mean_var=pv.tolist(), sig_min=SIG_MIN, sig_max=SIG_MAX, seconds=time.time() - t0),
          open(OUT + f'_{FW}x{FH}_cert.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
