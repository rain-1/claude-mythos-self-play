"""render_neck.py — WHERE ONE WORLD BECOMES TWO: the whole life of a Ricci-flow dumbbell in one object.

Every recorded moment of the flow is a solid of revolution (the embedded profile (z, psi) spun about the
axis), drawn as GLASS: the pigment density at a pixel is the chord length of the solid along the line of
sight, 2*sqrt(psi(z)^2 - y^2) — a physically honest x-ray.  Moments at equal time steps are laid on top of
one another (dwell time = tone), so the picture is the flow's occupation measure.  Ink: the profile at a
few chosen times.  Coral: the neck that is cut away at the surgery.
    python3 render_neck.py <tag> <final_px> <mode>      mode: hue | two
"""
import sys, pickle, json
import numpy as np
from scipy.ndimage import gaussian_filter
from pastel import *

tag = sys.argv[1] if len(sys.argv) > 1 else 'dev'
FINAL = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
MODE = sys.argv[3] if len(sys.argv) > 3 else 'two'
SS = 1 if FINAL >= 2048 else 2
W = H = FINAL * SS
rs = FINAL / 1024 * SS
rec = pickle.load(open('cache/rec_%s.pkl' % tag, 'rb'))
cert = json.load(open('cache/cert_%s.json' % tag))
T_end = rec[-1][0]
T_surg = [e for e in cert['events'] if e[0] == 'surgery'][0][2]
print('frames', len(rec), 'T_surg', T_surg, 'T_end', T_end)

# ---- geometry: centre the parent at its midpoint; children keep their centroid at surgery ----------
def solid_centroid(z, psi):
    w = psi ** 2
    return np.sum(z * w) / max(np.sum(w), 1e-12)

def frame_bodies(fr):
    """list of (name, z_centred, psi) with z in world units, centred by the gauge rule"""
    out = []
    for body in fr[1]:
        name, z, psi, s = body
        out.append((name, z, psi))
    return out

# gauge: parent centred at z-midpoint (symmetric dumbbell); children anchored so that their centroid stays
# where it was at the moment of surgery (the natural 'centre of mass stays put' choice)
anchors = {}
z0_first = None
placed = []   # (t, name, zc(array in world coords, centred), psi)
for t, bodies in rec:
    for name, z, psi, s in bodies:
        if name == 'S':
            zc = z - 0.5 * (z[0] + z[-1])
        else:
            if name not in anchors:
                # centroid of the child at birth, in the parent's frame: parent's frame is z centred
                # we need the parent's z at surgery: use the previous frame's parent
                anchors[name] = None
            c = solid_centroid(z, psi)
            if anchors[name] is None:
                # position at birth: find the parent's last frame and locate this child's material
                anchors[name] = ('pending', c)
            zc = z - c
        placed.append((t, name, zc, psi))

# resolve child birth positions: at surgery the left child occupies the parent's left part; the parent's
# last frame gives the neck centre at 0, so the left child's centroid sits at -(distance) ... compute from
# the parent's last frame directly
last_parent = [p for p in placed if p[1] == 'S'][-1]
zP, psiP = last_parent[2], last_parent[3]      # zP is already centred
loc = np.where((psiP[1:-1] < psiP[:-2]) & (psiP[1:-1] <= psiP[2:]))[0] + 1
imin = loc[np.argmin(psiP[loc])]
h_cut = max(2.5 * cert['eps'], 1.6 * psiP[imin])
i_l = imin
while i_l > 0 and psiP[i_l] < h_cut: i_l -= 1
i_r = imin
while i_r < len(psiP) - 1 and psiP[i_r] < h_cut: i_r += 1
cL = solid_centroid(zP[:i_l + 1], psiP[:i_l + 1])
cR = solid_centroid(zP[i_r:], psiP[i_r:])
offset = {'S': 0.0, 'SL': cL, 'SR': cR}
print('child anchors', cL, cR, 'neck z', zP[imin])

# ---- canvas ---------------------------------------------------------------------------------
sheet = Sheet(W, H, seed=16)
zmax = max(np.abs(p[2] + offset[p[1]]).max() for p in placed)
rmax = max(p[3].max() for p in placed)
scale = 0.78 * W / (2 * zmax)          # world -> px
cx, cy = W / 2, H * 0.43
print('zmax', zmax, 'rmax', rmax, 'scale', scale)

yy = (np.arange(H, dtype=np.float32) - cy) / scale    # world y per row
xx = (np.arange(W, dtype=np.float32) - cx) / scale    # world z per column

def chord_field(zc, psi):
    """chord length 2*sqrt(psi(z)^2 - y^2) on the pixel grid (float32, H x W)"""
    pz = np.interp(xx, zc, psi, left=0.0, right=0.0).astype(np.float32)
    v = pz[None, :] ** 2 - yy[:, None] ** 2
    return (2.0 * np.sqrt(np.clip(v, 0, None))) ** 0.75

# choose frames at equal time steps (all of them) — dwell honesty
frames = placed
n_fr = len(frames)
dt_rec = rec[1][0] - rec[0][0]
print('slices', n_fr, 'dt', dt_rec)

# pigment plan
if MODE == 'hue':
    ramp = ['lemon', 'apricot', 'blush', 'orchid', 'lavender', 'cornflower', 'aqua', 'mint']
else:
    ramp = None

acc = {}   # pigment -> density accumulator
def add(pig, dens):
    if pig not in acc:
        acc[pig] = np.zeros((H, W), np.float32)
    acc[pig] += dens

# glaze weight: total absorbance at the heart ~ (n_fr * chord * w) -> choose w so that the deepest tone ~ 1.9
w_glaze = None
tot = np.zeros((H, W), np.float32)
for (t, name, zc, psi) in frames:
    tot += chord_field(zc + offset[name], psi)
peak = np.percentile(tot[tot > 0], 99.7)
w_glaze = 2.1 / peak
print('peak dwell', peak, 'w', w_glaze)
del tot

for (t, name, zc, psi) in frames:      # second pass: no field is kept (memory)
    f = chord_field(zc + offset[name], psi)
    u = t / T_end
    if MODE == 'drift':
        # two families drifting with time: parent warm lemon -> apricot -> blush -> orchid over [0, T_surg],
        # children cool lavender -> cornflower -> aqua -> mint over [T_surg, T_end]
        if name == 'S':
            fam = ['lemon', 'apricot', 'blush', 'orchid']; v = t / T_surg
        else:
            fam = ['orchid', 'lavender', 'cornflower', 'aqua']; v = (t - T_surg) / max(T_end - T_surg, 1e-9)
        h = np.clip(v, 0, 1) * (len(fam) - 1)
        i0 = int(np.floor(h)); i1 = min(i0 + 1, len(fam) - 1); fr = h - i0
        add(fam[i0], f * w_glaze * (1 - fr))
        add(fam[i1], f * w_glaze * fr)
    elif MODE == 'hue':
        h = u * (len(ramp) - 1)
        i0 = int(np.floor(h)); i1 = min(i0 + 1, len(ramp) - 1); fr = h - i0
        add(ramp[i0], f * w_glaze * (1 - fr))
        add(ramp[i1], f * w_glaze * fr)
    else:
        if name == 'S':
            # parent: cornflower deepening toward the surgery, a touch of lavender late
            add('cornflower', f * w_glaze * (1 - 0.5 * u))
            add('lavender', f * w_glaze * 0.5 * u)
        else:
            add('mint', f * w_glaze * 0.7)
            add('aqua', f * w_glaze * 0.5)

for pig, dens in acc.items():
    sheet.wash(dens, pig)

# ---- the doomed neck in coral: the part of the parent's last frame between the cuts ----------------
zn = zP[i_l:i_r + 1] + offset['S']
pn = psiP[i_l:i_r + 1]
fneck = chord_field(zn, pn)
# thicken visually: the neck is thin (2.5 eps); draw its outline as ink-like coral and a soft fill
sheet.wash(fneck * 6.0, 'coral')

# ---- ink: profiles at chosen times (few), width by epoch -------------------------------------
def outline(zc, psi, width, weight=1.0):
    X = cx + zc * scale
    Yt = cy - psi * scale
    Yb = cy + psi * scale
    pts = list(zip(X, Yt)) + list(zip(X[::-1], Yb[::-1]))
    return polyline_density(W, H, pts, width, weight=weight, closed=True)

ink = np.zeros((H, W), np.float32)
# every frame as a hairline (the flow's own contour lines: dense where slow, sparse where fast)
for (t, name, zc, psi) in placed:
    ink += outline(zc + offset[name], psi, max(1.0, 0.9 * rs), weight=0.07)
picks = [0.0, 0.25 * T_surg, 0.5 * T_surg, 0.75 * T_surg, T_surg * 0.97]
picks += [T_surg + (T_end - T_surg) * q for q in (0.15, 0.4, 0.65, 0.85, 0.97)]
for tp in picks:
    k = int(np.argmin([abs(fr[0] - tp) for fr in rec]))
    t, bodies = rec[k]
    for name, z, psi, s in bodies:
        zc = (z - 0.5 * (z[0] + z[-1])) if name == 'S' else (z - solid_centroid(z, psi))
        ink += outline(zc + offset[name], psi, max(1.0, 1.6 * rs), weight=0.5 if tp > 0 else 1.0)
# coral outline of the cut neck
neck_ink = polyline_density(W, H, list(zip(cx + zn * scale, cy - pn * scale)), max(1.0, 1.6 * rs), weight=1.0) + \
           polyline_density(W, H, list(zip(cx + zn * scale, cy + pn * scale)), max(1.0, 1.6 * rs), weight=1.0)
sheet.wash(gaussian_filter(np.clip(ink, 0, 1.2), 0.45 * rs) * 0.95, 'ink')
sheet.wash(gaussian_filter(neck_ink, 0.5 * rs) * 1.2, 'coral')

# extinction points: two small coral dots where the children end
for name in ('SL', 'SR'):
    last = [p for p in placed if p[1] == name][-1]
    zc = last[2] + offset[name]
    zend = 0.5 * (zc[0] + zc[-1])
    d = discs_density(W, H, [cx + zend * scale], [cy], [2.2 * rs], [1.0], sigma=0.6 * rs)
    sheet.wash(d, 'coral')

# ---- film strip: nine moments, small glass objects, left to right ---------------------------
strip_t = [0.0, 0.5 * T_surg, 0.85 * T_surg, T_surg * 0.999] + [T_surg + (T_end - T_surg) * q for q in (0.02, 0.3, 0.6, 0.85, 0.99)]
nS = len(strip_t)
sw = 0.90 * W / nS
sscale = 0.42 * sw / zmax
sy = H * 0.835
sacc = {}
for k, tp in enumerate(strip_t):
    j = int(np.argmin([abs(fr[0] - tp) for fr in rec]))
    t, bodies = rec[j]
    sxc = W * 0.05 + (k + 0.5) * sw
    for name, z, psi, s_ in bodies:
        zc = (z - 0.5 * (z[0] + z[-1])) if name == 'S' else (z - solid_centroid(z, psi))
        zc = zc + offset[name]
        X = sxc + zc * sscale
        xs_ = (np.arange(W) - sxc) / sscale
        ys_ = (np.arange(H) - sy) / sscale
        pz = np.interp(xs_, zc, psi, left=0.0, right=0.0).astype(np.float32)
        v = pz[None, :] ** 2 - ys_[:, None].astype(np.float32) ** 2
        f = (2.0 * np.sqrt(np.clip(v, 0, None))) ** 0.75
        if name == 'S':
            fam = ['lemon', 'apricot', 'blush', 'orchid']; u = t / T_surg
        else:
            fam = ['orchid', 'lavender', 'cornflower', 'aqua']; u = (t - T_surg) / max(T_end - T_surg, 1e-9)
        h = np.clip(u, 0, 1) * 3; i0 = int(np.floor(h)); i1 = min(i0 + 1, 3); fr_ = h - i0
        for nm, wgt in ((fam[i0], 1 - fr_), (fam[i1], fr_)):
            if wgt > 0:
                sacc[nm] = sacc.get(nm, 0) + f * wgt * 0.9
        pts = list(zip(X, sy - psi * sscale)) + list(zip(X[::-1], sy + psi[::-1] * sscale))
        ink += polyline_density(W, H, pts, max(1.0, 1.2 * rs), weight=0.7, closed=True)
    if k == 3:   # the moment of surgery: the neck to be cut, in coral
        zz = zP[i_l:i_r + 1] + offset['S']; pp = psiP[i_l:i_r + 1]
        Xn = sxc + zz * sscale
        for sgn in (-1, 1):
            ink_c = polyline_density(W, H, list(zip(Xn, sy + sgn * pp * sscale)), max(1.0, 1.6 * rs), weight=1.0)
            sheet.wash(gaussian_filter(ink_c, 0.4 * rs) * 1.2, 'coral')
for nm, dens in sacc.items():
    sheet.wash(dens, nm)
sheet.wash(gaussian_filter(np.clip(ink, 0, 1.2), 0.45 * rs) * 0.95, 'ink')
ink = np.zeros((H, W), np.float32)
# tiny time labels under the strip
lab = []
for k, tp in enumerate(strip_t):
    sxc = W * 0.05 + (k + 0.5) * sw
    lab.append(('t = %.3f' % tp, sxc, H * 0.885, int(13 * rs), 'mono', 'mm'))
sheet.wash(text_density(W, H, lab) * 0.8, 'ink')

# ---- caption --------------------------------------------------------------------------------
sheet.caption_strip(0.91, 0.99, f=0.5)
title = 'Where One World Becomes Two'
sub = ('Ricci flow on a dumbbell three-sphere: the neck pinches in finite time, is cut away, '
       'and each half rounds off and ends at a point.')
size_t = int(46 * rs); size_s = int(24 * rs)
items = [(title, W / 2, H * 0.93, size_t, 'serif_bold', 'mm')]
lines = wrap(sub, size_s, 'italic', 0.80 * W)
for i, ln in enumerate(lines):
    items.append((ln, W / 2, H * (0.958 + 0.026 * i), size_s, 'italic', 'mm'))
sheet.wash(text_density(W, H, items) * 1.0, 'ink')

img = sheet.develop()
finish(img, (FINAL, FINAL), 'cache/neck_%s_%s_%d.png' % (tag, MODE, FINAL))
