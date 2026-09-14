"""render_stereo.py — THE DEPTH THAT ISN'T ON THE PAGE.
A single-image random-dot stereogram (Thimbleby–Inglis–Witten 1994) whose texture is a field of pastel coins.  Cross
your eyes (or look through the page) until two neighbouring coins fuse, and a shape rises out of the paper: the hero's
seven-sided plateau with a dome beside it.  Neither eye's image contains it; it exists only in the relation between them.

Rendered at final resolution with no supersampling: the picture IS its pixels.
usage: python3 render_stereo.py FINAL out_prefix [E_px_fraction] [mu]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import pastel as P

FINAL = int(sys.argv[1]); OUT = sys.argv[2]
EF = float(sys.argv[3]) if len(sys.argv) > 3 else 0.14         # eye separation as a fraction of width; the far-plane repeat is E/2
MU = float(sys.argv[4]) if len(sys.argv) > 4 else 0.33         # depth of field
W = H = FINAL; rs = FINAL / 1024.0
E = int(round(EF * W)); E += E % 2; SF = E // 2; t0 = time.time()
rng = np.random.default_rng(12)

# ---- depth map: heptagonal plateau (soft edge) + a dome; 0 = far (paper), 1 = near
yy, xx = np.mgrid[:H, :W].astype(np.float32)
def heptagon(cx, cy, R, rot):
    ang = np.arctan2(yy - cy, xx - cx) - rot
    # signed distance to a regular heptagon: max over the 7 half-planes
    d = -np.inf * np.ones_like(xx)
    for i in range(7):
        a = 2 * np.pi * i / 7 + rot
        d = np.maximum(d, (xx - cx) * np.cos(a) + (yy - cy) * np.sin(a) - R * np.cos(np.pi / 7))
    return d
d7 = heptagon(0.42 * W, 0.46 * H, 0.24 * W, -np.pi / 2)
plateau = np.clip(0.5 - d7 / (0.05 * W), 0, 1) ** 1.6 * 0.72
rd = np.hypot(xx - 0.72 * W, yy - 0.64 * H) / (0.12 * W)
dome = np.sqrt(np.clip(1 - rd ** 2, 0, 1)) * 0.9
Z = np.maximum(plateau, dome).astype(np.float32)
Image.fromarray((Z * 255).astype(np.uint8)).resize((512, 512)).save(OUT + '_depth_key_512.png')

# ---- texture: pastel coins, random pigments, as per-pixel absorbance
sheet = P.Sheet(W, H, seed=41)
# a strip of dense small coins, periodic with the far-plane separation E/2 (drawn three times, shifted by -E, 0, +E, so the seam is invisible), tiled across
pigs = ['aqua', 'blush', 'lemon', 'mint', 'lavender', 'apricot', 'cornflower', 'orchid', 'pistachio']
strip = np.zeros((H, SF, 3), np.float32)
ncoin = int(0.028 * SF * H / (rs * rs))          # ~ the same coin count per area at every size
r_coin = 0.0045 * W
for name in pigs:
    n_ = int(ncoin / len(pigs))
    cxs = rng.uniform(0, SF, n_); cys = rng.uniform(0, H, n_); rr_ = rng.uniform(0.6, 1.0, n_) * r_coin
    d = np.zeros((H, SF), np.float32)
    for sh in (-SF, 0, SF):
        d += P.discs_density(SF, H, cxs + sh, cys, rr_, np.ones(n_), sigma=None)
    d = gaussian_filter(np.clip(d, 0, 1), 0.5 * rs)
    strip += d[..., None] * P.absorb(P.PIG[name])[None, None, :] * 0.9
tex = np.tile(strip, (1, W // SF + 2, 1))[:, :W]
ncoin = ncoin * 1
print('texture done [%.0fs]' % (time.time() - t0), flush=True)

# ---- the stereogram: per row, link pixel pairs whose separation is set by depth (union-find), then propagate absorbance
A = np.zeros_like(tex)
for y in range(H):
    z = Z[y]
    same = np.arange(W)
    def root(x):
        while same[x] != x:
            x = same[x]
        return x
    for x in range(W):
        s = int(round((1 - MU * z[x]) * E / (2 - MU * z[x])))
        left = x - (s + (s & (y & 1))) // 2; right = left + s
        if 0 <= left and right < W:
            l, r = root(left), root(right)
            if l != r:
                if l < r: same[r] = l
                else: same[l] = r
    # propagate: each pixel takes the absorbance of its root's texture pixel
    roots = np.array([root(x) for x in range(W)])
    A[y] = tex[y, roots]
    if y % 400 == 0:
        print('row', y, '[%.0fs]' % (time.time() - t0), flush=True)
sheet.A = A
# soft vignette so the field floats in paper
rr = np.hypot((xx - W / 2) / (0.5 * W), (yy - 0.47 * H) / (0.5 * H))
edge = np.clip((1.05 - rr) / 0.18, 0, 1) ** 1.3
sheet.A *= edge[..., None]

title = "The Depth That Isn't on the Page"
sub = ('A field of pastel coins that repeats, almost, every few centimetres. Let your eyes drift until two coins become one, and a '
       'seven-sided plateau rises from the paper with a dome beside it. Neither eye sees it; it is in the relation between what the '
       'two of them see. Every coin is on the page; the shape is not.')
fs_t = int(0.036 * H); fs_s = int(0.0125 * H)
sheet.caption_strip(0.905, 0.995, 0.6)
items = [(title, 0.05 * W, 0.935 * H, fs_t, 'serif_bold', 'ls')]
for j_, line in enumerate(P.wrap(sub, fs_s, 'italic', 0.90 * W)):
    items.append((line, 0.05 * W, (0.958 + 0.018 * j_) * H, fs_s, 'italic', 'ls'))
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(E_px=E, far_sep_px=SF, mu=MU, ncoins=ncoin * 1, seconds=time.time() - t0), open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
