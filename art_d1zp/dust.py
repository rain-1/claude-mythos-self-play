"""FIFTEEN PLACES TO BE UNEQUAL — sun print (cyanotype), four exposures.

A hand of four heights (X1..X4) is one grain of sand at the point of a tetrahedron whose four distances
to the faces are the four shares X_i / (X1+X2+X3+X4).  Sand blocks the sun: where hands pile up the
paper stays white.  White thread: the tetrahedron, and inside it the small upside-down one whose corners
are the four face centres.  A hand has NO share above a third exactly when its grain is inside the small
one.  Four panels = the nested law at eps = 1/2, 1/10, 1/1000, 1e-9: the sand walks to the 15 centres
(4 corners, 6 edge middles, 4 face middles, 1 centre), slowly.
usage: dust.py W out.png [hands_per_panel]"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
W = int(sys.argv[1]); OUT = sys.argv[2]; NH = int(float(sys.argv[3])) if len(sys.argv) > 3 else 20_000_000
S = W / 2048.0; PSTAR = 0.47434645545490369
def noise(shape, sig, seed):
    r = np.random.default_rng(seed).standard_normal(shape).astype(np.float32); r = gaussian_filter(r, sig, mode='wrap'); return r / r.std()
# ---- the tetrahedron, turned a little so that all fifteen centres are seen apart ----
V = np.array([[1, 1, 1.0], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]])
def rot(ax, t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]) if ax == 'z' else np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
roty = lambda t: np.array([[np.cos(t), 0, np.sin(t)], [0, 1, 0], [-np.sin(t), 0, np.cos(t)]])
Rm = rot('z', np.radians(52)) @ rot('x', np.radians(24)) @ roty(np.radians(15))
V = V @ Rm.T
P2 = np.stack([V[:, 0], -V[:, 1]], 1)                 # looking down the z axis: a kite with both diagonals
P2 -= (P2.max(0) + P2.min(0)) / 2; P2 /= np.abs(P2).max() * 2 / 0.93      # fit in a unit box with margin
EPSS = [0.5, 0.1, 1e-3, 1e-9]; TONE = float(sys.argv[4]) if len(sys.argv) > 4 else 1.6
pad = int(24 * S); PW = int(760 * S); gap = int(64 * S)
ox = (W - 2 * PW - gap) // 2; oy = int(92 * S)
rng = np.random.default_rng(1511)
paper = np.array([0.957, 0.937, 0.878]); img = np.ones((W, W, 3)) * paper
img *= (1 + 0.016 * noise((W, W), 0.9 * S, 1)[..., None] + 0.012 * noise((W, W), 50 * S, 2)[..., None])
blue_lo = np.array([0.40, 0.60, 0.77]); blue_hi = np.array([0.030, 0.105, 0.275])
stats = []
def thread(mask, a, b, w, dash=None):
    n = int(np.hypot(*(b - a)) * 2) + 2; t = np.linspace(0, 1, n)
    pts = a[None] + (b - a)[None] * t[:, None]
    wob = np.stack([np.interp(t, np.linspace(0, 1, 9), rng.normal(0, 1.3 * S, 9)), np.interp(t, np.linspace(0, 1, 9), rng.normal(0, 1.3 * S, 9))], 1)
    wob *= np.sin(np.pi * t)[:, None]; pts = pts + wob
    if dash is not None:
        L = np.hypot(*(b - a)) * t; keep = (L % dash) < dash * 0.58; pts = pts[keep]
    xi = np.clip(pts[:, 0].round().astype(int), 0, mask.shape[1] - 1); yi = np.clip(pts[:, 1].round().astype(int), 0, mask.shape[0] - 1)
    tmp = np.zeros_like(mask); tmp[yi, xi] = 1
    tmp = gaussian_filter(tmp, w); tmp /= max(tmp.max(), 1e-9) / 1.25
    np.maximum(mask, np.clip(tmp, 0, 1), out=mask)
for k, eps in enumerate(EPSS):
    H = np.zeros((PW, PW), np.float64); lions = np.zeros(5); CH = 2_000_000
    for c in range(NH // CH):
        G = rng.geometric(1 - PSTAR, (CH, 4)) - 1; G -= G.min(1, keepdims=True)       # only the differences of level matter
        U = rng.random((CH, 4))
        X = np.exp(np.log(eps) * G) * (1 - np.exp(np.log(eps) * U))
        sh = X / X.sum(1, keepdims=True)
        lions += np.bincount((sh > 1 / 3).sum(1), minlength=5)
        q = sh @ P2
        px = ((q[:, 0] + 0.5) * PW + rng.uniform(-0.5, 0.5, CH)).astype(int); py = ((q[:, 1] + 0.5) * PW + rng.uniform(-0.5, 0.5, CH)).astype(int)
        np.add.at(H, (np.clip(py, 0, PW - 1), np.clip(px, 0, PW - 1)), 1)
    lions /= lions.sum(); Pv = float((lions * np.arange(5)).sum() / 4)
    stats.append(dict(eps=eps, P=Pv, none=float(lions[0]), one=float(lions[1]), two=float(lions[2])))
    print(stats[-1], flush=True)
    Hs = gaussian_filter(H, 0.6 * S); inside = Hs > 0
    dn = Hs / (NH / (0.30 * PW * PW))                                  # density relative to an even spread over the kite
    sand = 1 - np.exp(-(dn / TONE) ** 0.62)                            # coverage of the paper by sand
    pen = gaussian_filter(sand, 5 * S) * 0.25                          # light creeps under the heaps
    obj = np.clip(sand * 0.985 + pen * (1 - sand), 0, 1)
    # threads
    th = np.zeros((PW, PW), np.float32); th2 = np.zeros((PW, PW), np.float32)
    C = (P2 + 0.5) * PW
    for i in range(4):
        for j in range(i + 1, 4): thread(th, C[i], C[j], 1.15 * S)
    FC = np.array([(C.sum(0) - C[i]) / 3 for i in range(4)])
    for i in range(4):
        for j in range(i + 1, 4): thread(th2, FC[i], FC[j], 0.8 * S)
    obj = np.maximum(obj, np.maximum(th * 0.93, th2 * 0.80))
    # exposure: uneven sun, brushed coat with ragged ends
    Q = PW + 2 * pad
    expo = 1.0 + 0.05 * noise((Q, Q), 120 * S, 10 + k) + 0.03 * noise((Q, Q), 12 * S, 20 + k)
    full = np.zeros((Q, Q), np.float32); full[pad:pad + PW, pad:pad + PW] = obj
    b = np.clip(expo * (1 - full), 0, 1) ** 0.85
    y2, x2 = np.mgrid[0:Q, 0:Q].astype(np.float32)
    br = noise((Q, Q), (1.2 * S, 60 * S), 30 + k)                      # brush streaks run across
    b = np.clip(b * (1 + 0.035 * br), 0, 1)
    tb = pad * 0.45 * (1 + 0.8 * noise((Q,), 9 * S, 40 + k)); tb2 = pad * 0.45 * (1 + 0.8 * noise((Q,), 9 * S, 50 + k))
    coat = np.clip((x2 - tb[:, None] * 0.6 - 3 * S) / (2.5 * S), 0, 1) * np.clip((Q - tb2[:, None] * 0.6 - 3 * S - x2) / (2.5 * S), 0, 1)
    coat *= np.clip((y2 - 4 * S - 0.25 * tb[None, :]) / (2.5 * S), 0, 1) * np.clip((Q - 4 * S - 0.25 * tb2[None, :] - y2) / (2.5 * S), 0, 1)
    col = blue_lo[None, None, :] * (1 - b[..., None]) + blue_hi[None, None, :] * b[..., None]
    t = np.clip(b * 2.4, 0, 1)[..., None]; unexp = paper * np.array([0.975, 0.985, 0.99])
    col = unexp * (1 - t) + col * t
    col *= (1 + 0.03 * noise((Q, Q), 0.8 * S, 70 + k)[..., None])
    px0 = ox + (k % 2) * (PW + gap) - pad; py0 = oy + (k // 2) * (PW + gap + int(36 * S)) - pad
    sl = (slice(py0, py0 + Q), slice(px0, px0 + Q)); a_ = coat[..., None]
    img[sl] = img[sl] * (1 - a_) + col * a_
    stats[-1]['origin'] = (px0 + pad, py0 + pad); stats[-1]['C'] = C.tolist(); stats[-1]['FC'] = FC.tolist()
im = Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)); dr = ImageDraw.Draw(im)
F = lambda nm, sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf', int(sz * S))
pc = (78, 78, 90); rc = (205, 52, 42)
names = ['ε = 1/2', 'ε = 1/10', 'ε = 1/1000', 'ε = 1/10⁹']
for k, st in enumerate(stats):
    x_, y_ = st['origin']
    dr.text((x_ - pad + int(4 * S), y_ + PW + pad + int(6 * S)), names[k], font=F('Italic', 25), fill=pc)
    tx = f"a share above a third: {100 * st['P']:.2f}% of the time   ·   none in {100 * st['none']:.1f}% of hands, two in {100 * st['two']:.1f}%"
    dr.text((x_ + PW + pad - int(4 * S), y_ + PW + pad + int(9 * S)), tx, font=F('Regular', 19), fill=pc, anchor='ra')
# the one red: a ring round a face middle in the last panel
st = stats[-1]; x_, y_ = st['origin']; fc = np.array(st['FC'][3]); rr = 19 * S
cx, cy = x_ + fc[0], y_ + fc[1]
for w_ in range(int(3 * S)):
    dr.ellipse([cx - rr - w_, cy - rr - w_, cx + rr + w_, cy + rr + w_], outline=rc)
dr.text((cx + rr + 8 * S, cy - 3 * S), 'three near-thirds:', font=F('Italic', 19), fill=rc, anchor='lb')
dr.text((cx + rr + 8 * S, cy + 1 * S), 'the larger two count', font=F('Italic', 19), fill=rc, anchor='lt')
by = oy + 2 * PW + gap + int(36 * S) + pad + int(48 * S)
dr.text((ox - pad, by), 'Fifteen Places to Be Unequal', font=F('Regular', 54), fill=pc)
L = ['Each grain of sand is one hand of four, laid where its four distances to the faces of the tetrahedron are the four shares of the total.',
     'Inside the small thread tetrahedron nobody holds more than a third. As the bridges move apart the sand walks to the fifteen centres:',
     '4 corners (one holds everything), 6 edge middles (two halves), 4 face middles (three near-thirds), and the very centre (four quarters).']
for i, l in enumerate(L): dr.text((ox - pad, by + int((72 + 34 * i) * S)), l, font=F('Italic', 26), fill=pc)
q = 1 - PSTAR; z = 1 - PSTAR ** 4
lim = [4 * q * PSTAR ** 3 / z, 6 * q * q * PSTAR ** 2 / z, 4 * q ** 3 * PSTAR / z, q ** 4 / z]
dr.text((ox - pad, by + int(186 * S)), f'{NH:,} hands per exposure (sand blocks the sun; doses add). In the limit the heaps weigh {100 * lim[0]:.1f}%, {100 * lim[1]:.1f}%, {100 * lim[2]:.1f}%, {100 * lim[3]:.1f}% '
        f'and the first number is (1·{100 * lim[0]:.1f} + 2·{100 * lim[1]:.1f} + 2·{100 * lim[2]:.1f})/4 = 40.07%.',
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(16.2 * S)), fill=pc)
im.save(OUT); json.dump(stats, open(OUT.replace('.png', '.json'), 'w'), indent=1); print('saved', OUT)
