"""render_moire.py — THE LATTICE IN NEITHER LAYER.
Two identical triangular lattices of soft pastel coins, one aqua and one blush, twisted against each other by a
small angle theta.  Neither layer has any structure larger than its own spacing a; together they show a
superlattice of period a / (2 sin(theta/2)) — the moiré — which lives in the RELATION between the layers.
Ink: the exact moiré superlattice (its Wigner–Seitz hexagons), computed from the difference of the two
reciprocal lattices.  Coral: the AA sites, where the two layers coincide.

usage: python3 render_moire.py FINAL theta_deg out_prefix [pitch_px_at_1024] [mode] [twist_power]
mode: coins | honeycomb | registry   (registry: upper coins tinted by the vector to the nearest lower coin)
twist_power > 0: the twist grows with radius as theta * (r/R)^power (layer 2 is then not a lattice; no ink web)
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
import pastel as P

FINAL = int(sys.argv[1]); THETA = float(sys.argv[2]); OUT = sys.argv[3]
PITCH = float(sys.argv[4]) if len(sys.argv) > 4 else 11.0
MODE = sys.argv[5] if len(sys.argv) > 5 else 'coins'
TWP = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
a = PITCH * rs                      # lattice constant in canvas px
th = np.radians(THETA)
t0 = time.time()

def lattice_points(a, rot, cx, cy, W, H, margin):
    """triangular lattice of constant a rotated by rot about (cx, cy), all points inside the canvas + margin"""
    a1 = a * np.array([1.0, 0.0]); a2 = a * np.array([0.5, np.sqrt(3) / 2])
    R = np.array([[np.cos(rot), -np.sin(rot)], [np.sin(rot), np.cos(rot)]])
    a1, a2 = R @ a1, R @ a2
    n = int(np.hypot(W, H) / a) + 3
    i, j = np.mgrid[-n:n + 1, -n:n + 1]
    pts = np.stack([cx + i * a1[0] + j * a2[0], cy + i * a1[1] + j * a2[1]], -1).reshape(-1, 2)
    m = (pts[:, 0] > -margin) & (pts[:, 0] < W + margin) & (pts[:, 1] > -margin) & (pts[:, 1] < H + margin)
    return pts[m], a1, a2

cx, cy = W / 2, H / 2
p1, a1, a2 = lattice_points(a, -th / 2, cx, cy, W, H, a)
p2, b1, b2 = lattice_points(a, +th / 2, cx, cy, W, H, a)
if TWP > 0:
    # radial twist: rotate every layer-2 point about the centre by th * (r/R)^TWP (layer 1 stays put)
    p2, _, _ = lattice_points(a, 0.0, cx, cy, W, H, a)
    p1, a1, a2 = lattice_points(a, 0.0, cx, cy, W, H, a)
    rr2 = np.hypot(p2[:, 0] - cx, p2[:, 1] - cy); Rmax = 0.5 * W
    phi = th * (rr2 / Rmax) ** TWP
    x, y = p2[:, 0] - cx, p2[:, 1] - cy
    p2 = np.stack([cx + x * np.cos(phi) - y * np.sin(phi), cy + x * np.sin(phi) + y * np.cos(phi)], -1)
print('layer points', len(p1), len(p2), flush=True)

sheet = P.Sheet(W, H, seed=23)
# painter's edge: a soft vignette so the field floats in paper
yy, xx = np.mgrid[:H, :W]
rr = np.hypot((xx - cx) / (0.5 * W), (yy - cy) / (0.5 * H))
edge = np.clip((1.02 - rr) / 0.22, 0, 1) ** 1.5

def coverage(pts):
    r = 0.34 * a
    d = P.discs_density(W, H, pts[:, 0], pts[:, 1], np.full(len(pts), r), np.ones(len(pts)), sigma=0.7 * rs)
    return np.clip(d, 0, 1)

def layer(pts, tint, seed):
    if MODE == 'coins':
        pass
    else:
        # honeycomb: draw the edges of the hexagonal graph dual to the triangular lattice: each site's 6 bonds at half length
        segs = []
        for v in (a1, a2, a2 - a1) if tint == 'aqua' else (b1, b2, b2 - b1):
            segs.append(np.concatenate([pts, pts + v], 1))
        segs = np.concatenate(segs)
        d = P.draw_lines_density(W, H, segs, 0.55 * rs, sigma=0.5 * rs)
        sheet.wash(0.8 * np.clip(d, 0, 1) * edge, tint)

if MODE == 'registry':
    from scipy.spatial import cKDTree as _KD
    d1 = coverage(p1)
    sheet.wash(0.75 * d1 * edge, "aqua", granulate=0.10, seed=1)
    # each upper coin: its registry = vector to the nearest lower coin; angle -> pigment (9-cycle, no coral), length -> density
    dist, idx = _KD(p1).query(p2)
    vec = p2 - p1[idx]; ang = np.arctan2(vec[:, 1], vec[:, 0]); h = (ang / (2 * np.pi)) % 1.0
    CYC = [c for c in P.CYCLE if c != 'coral']
    r = 0.34 * a
    hh = h * len(CYC); i0 = np.floor(hh).astype(int) % len(CYC); i1 = (i0 + 1) % len(CYC); t = hh - np.floor(hh)
    lift = np.clip(dist / (0.5 * a), 0, 1)               # coincident coins are faint, far-from-registry coins full
    dens = 0.55 + 1.05 * lift
    for c, name in enumerate(CYC):
        w = np.where(i0 == c, 1 - t, 0) + np.where(i1 == c, t, 0)
        m_ = w > 0.02
        if not m_.any(): continue
        d = P.discs_density(W, H, p2[m_, 0], p2[m_, 1], np.full(m_.sum(), r), (w * dens)[m_], sigma=0.7 * rs)
        sheet.wash(np.clip(d, 0, 2) * edge, name, granulate=0.08, seed=10 + c)
elif MODE == 'coins':
    # opaque pastel coins: the blush layer lies ON TOP of the aqua layer and hides it where they coincide,
    # so the AA sites (coincidence) carry less pigment than the AB regions (interleaved) — that is the moiré
    d1 = coverage(p1); d2 = coverage(p2)
    sheet.wash(1.25 * d1 * (1 - 0.92 * d2) * edge, 'aqua', granulate=0.10, seed=1)
    sheet.wash(1.25 * d2 * edge, 'blush', granulate=0.10, seed=2)
else:
    layer(p1, 'aqua', 1)
    layer(p2, 'blush', 2)
print('layers [%.0fs]' % (time.time() - t0), flush=True)

# ---- the moiré superlattice, exactly: reciprocal vectors of each layer; moiré G = G1 - G2 ----
def reciprocal(a1, a2):
    A = np.array([a1, a2]).T
    B = 2 * np.pi * np.linalg.inv(A).T
    return B[:, 0], B[:, 1]
g1, g2 = reciprocal(a1, a2); h1, h2 = reciprocal(b1, b2)
Gm1, Gm2 = g1 - h1, g2 - h2
Mrec = np.array([Gm1, Gm2]).T
Mreal = 2 * np.pi * np.linalg.inv(Mrec).T          # moiré real-space basis
m1, m2 = Mreal[:, 0], Mreal[:, 1]
L = np.linalg.norm(m1)
print('moire period %.1f canvas px = %.2f a; theory a/(2 sin(th/2)) = %.2f a' % (L, L / a, 1 / (2 * np.sin(th / 2))), flush=True)
# AA sites: the origin (cx,cy) is a common site of both layers; the moiré lattice through it
n = int(np.hypot(W, H) / L) + 2
i, j = np.mgrid[-n:n + 1, -n:n + 1]
mpts = np.stack([cx + i * m1[0] + j * m2[0], cy + i * m1[1] + j * m2[1]], -1).reshape(-1, 2)
mm = (mpts[:, 0] > -L) & (mpts[:, 0] < W + L) & (mpts[:, 1] > -L) & (mpts[:, 1] < H + L)
mpts = mpts[mm]
# Wigner–Seitz cell of the moiré lattice in ink: distance to the nearest two moiré sites equal → bisector web
from scipy.spatial import cKDTree
tree = cKDTree(mpts)
dd, ii = tree.query(np.stack([xx.ravel(), yy.ravel()], -1), k=2)
wall = (dd[:, 1] - dd[:, 0]).reshape(H, W)
ink = P.ink_from_distance(wall / 2, 0.9 * rs)
if TWP == 0:
    sheet.wash(0.28 * ink * edge, 'ink')
# coral AA sites: a small ring where the layers coincide
ring = np.zeros((H, W), np.float32)
if TWP > 0:
    # AA sites of a radial twist: layer-2 coins that are LOCAL MINIMA of the registry distance (within 2.5 a)
    # and lie where the local moiré period is smaller than the sheet (cells exist there)
    from scipy.spatial import cKDTree as _KD2
    dd_, _ = _KD2(p1).query(p2)
    T2 = _KD2(p2); nb = T2.query_ball_point(p2, 2.5 * a)
    ismin = np.array([dd_[i] <= dd_[js].min() + 1e-9 for i, js in enumerate(nb)])
    r2 = np.hypot(p2[:, 0] - cx, p2[:, 1] - cy); phi2 = th * (r2 / (0.5 * W)) ** TWP
    period2 = a / (2 * np.sin(np.maximum(phi2, 1e-6) / 2))
    mpts = p2[ismin & (dd_ < 0.12 * a) & (period2 < 0.28 * W)]
    # the law as coral rings: radii where the local period is 4a, 6a, 9a, 14a
    law = np.zeros((H, W), np.float32); law_r = []
    for kk in (5, 7, 10, 15):
        thk = 2 * np.arcsin(1 / (2 * kk)); rk = 0.5 * W * (thk / th) ** (1 / TWP)
        if rk < 0.5 * W:
            law += np.exp(-((np.hypot(xx - cx, yy - cy) - rk) / (1.0 * rs)) ** 2); law_r.append((kk, float(rk / W)))
    sheet.wash(0.9 * law, 'coral')
    print('law rings', law_r, flush=True)
for (x, y) in mpts:
    if -L < x < W + L and -L < y < H + L:
        r0 = np.hypot(xx - x, yy - y)
        ring += np.exp(-((r0 - 0.55 * a) / (0.8 * rs)) ** 2)
sheet.wash(1.1 * np.clip(ring, 0, 1) * edge, 'coral')
print('moire ink [%.0fs]' % (time.time() - t0), flush=True)

title = 'The Lattice in Neither Layer'
if TWP > 0:
    sub = (f'Two identical lattices of coins. The upper one is turned against the lower by an angle that grows from 0 at the centre to {THETA:g}° at the '
           'edge, and each upper coin is tinted by its offset from the nearest lower coin — by the relation, not by anything of its own. '
           'The cells you see are a / (2 sin(θ/2)) wide: the coral circles are where that is 15, 10, 7 and 5 coins. Neither layer has cells.')
else:
  sub = (f'Two identical lattices of coins, aqua and blush, turned {THETA:g}° against each other. Each alone repeats every a; '
       f'together they repeat every a / (2 sin(θ/2)) = {1 / (2 * np.sin(th / 2)):.1f} a. The ink hexagons are that period, exactly; '
       'coral marks where the two layers coincide. Nothing on the page is as large as the pattern you see.')
fs_t = int(0.036 * H); fs_s = int(0.0125 * H)
sheet.caption_strip(0.905, 0.995, 0.6)
items = [(title, 0.05 * W, 0.935 * H, fs_t, 'serif_bold', 'ls')]
for j_, line in enumerate(P.wrap(sub, fs_s, 'italic', 0.90 * W)):
    items.append((line, 0.05 * W, (0.958 + 0.018 * j_) * H, fs_s, 'italic', 'ls'))
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(theta_deg=THETA, pitch=PITCH, mode=MODE, moire_period_over_a=float(L / a), theory=float(1 / (2 * np.sin(th / 2))),
               n_moire_sites=int(len(mpts)), seconds=time.time() - t0), open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
