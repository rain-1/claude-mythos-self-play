"""render_venus.py — HESPERUS IS PHOSPHORUS.
Geocentric path of Venus (JPL DE421, ecliptic J2000 frame, Earth at the centre, the stars fixed).
Cloud: every half-day 1900-2053 (the rose turns -2.4 deg per 8-year cycle); pigment by which star it is:
evening star (east of the Sun) warm, morning star (west) cool; density = dwell time (strobe register).
Ink: one 8-year cycle. Coral: the transits of 2004 and 2012 (Earth, Venus, Sun in one line)."""
import numpy as np, sys, os, time
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from pastel import *
from ephem import geo_path, ts

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2
W = H = FINAL * SS
rs = FINAL / 1024 * SS
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/venus_{FINAL}.png'
Y0, Y1 = 1900, 2053
CYC = (2009.0, 2017.0)     # the ink cycle (years, decimal)
SCALE = 0.255 * W          # pixels per AU
cx, cy = W / 2, H / 2 - 0.02 * H

NCYC = float(os.environ.get('NCYC', '1'))          # cycles in the main cloud
GHOST = float(os.environ.get('GHOST', '0.22'))      # strength of the 153-year ghost cloud
INKW = float(os.environ.get('INKW', '0.0'))
dg = geo_path('venus', Y0, Y1, 0.5)
CY0 = CYC[0]; CY1 = CYC[0] + 8.0 * NCYC
d = geo_path('venus', int(CY0), int(CY1) + 1, 0.02)
def unpack(d):
    yr = 2000.0 + (d['t'] - 2451545.0) / 365.25
    x, y = d['x'], d['y']
    dl = (d['lon'] - d['slon'] + 180) % 360 - 180      # >0: east of the Sun = evening star
    return yr, x, y, dl, cx + x * SCALE, cy - y * SCALE
yr, x, y, dl, px, py = unpack(d)
sel = (yr >= CY0) & (yr < CY1)
yr, x, y, dl, px, py = yr[sel], x[sel], y[sel], dl[sel], px[sel], py[sel]
gyr, gx, gy, gdl, gpx, gpy = unpack(dg)
sh = Sheet(W, H, seed=11)

def cloud(PX, PY, mask, sigma, wts=None):
    hgt, _, _ = np.histogram2d(PY[mask], PX[mask], bins=[H, W], range=[[0, H], [0, W]], weights=None if wts is None else wts[mask])
    return gaussian_filter(hgt.astype(np.float32), sigma)

t0 = time.time()
SIG = float(os.environ.get('SIG', '1.6'))
KNEE = float(os.environ.get('KNEE', '1.0'))
el = np.abs(dl)                                   # elongation from the Sun (deg)
VLO, VHI = float(os.environ.get('VLO', '6')), float(os.environ.get('VHI', '22'))
vis = np.clip((el - VLO) / (VHI - VLO), 0, 1); vis = vis * vis * (3 - 2 * vis)   # visible only away from the glare
far = np.clip((el - 20.0) / 27.0, 0, 1)          # 0 near the Sun ... 1 at greatest elongation (47 deg)
both = cloud(px, py, np.ones(len(px), bool), SIG * rs)
ref = np.percentile(both[both > 0.03 * both.max()], 30)   # a typical pixel on the fast (outer) arcs
print('ref', ref, 'max', both.max())
def tone(c, k=1.0):
    return 1 - np.exp(-c / (ref * k))
CLOUD = float(os.environ.get('CLOUD', '1.3'))
for mask, pa, pb, sd in ([(dl > 0, 'apricot', 'blush', 3), (dl <= 0, 'aqua', 'lavender', 4)] if CLOUD > 0 else []):
    for j, (lo, hi) in enumerate([(0, 0.5), (0.5, 1.01)]):
        band = np.clip(1 - np.abs(far - (lo + hi) / 2) / 0.5, 0, 1) if False else ((far >= lo) & (far < hi)).astype(np.float32)
        c = cloud(px, py, mask, SIG * rs, wts=vis * band)
        sh.wash(CLOUD * tone(c, KNEE), mix_tint(pa, pb, 0.15 + 0.7 * j), granulate=0.12, seed=sd + j)
CHORD = float(os.environ.get('CHORD', '0.0'))
if CHORD > 0:
    # Ptolemy's epicycle, honestly: the Sun->Venus radius at equal time steps (one per 12 h)
    step = int(round(0.5 / 0.02))
    sxp = cx + d['sx'][sel][::step] * SCALE; syp = cy - d['sy'][sel][::step] * SCALE
    segs = np.stack([sxp, syp, px[::step], py[::step]], 1)
    ch = draw_lines_density(W, H, segs, max(1, 0.7 * rs), sigma=0.6 * rs)
    chref = np.percentile(ch[ch > 0.02 * ch.max()], 50)
    for mask, pig in [((dl[::step] > 0), 'apricot'), ((dl[::step] <= 0), 'aqua')]:
        chm = draw_lines_density(W, H, segs[mask], max(1, 0.7 * rs), sigma=0.6 * rs)
        sh.wash(CHORD * (1 - np.exp(-chm / (chref * 2.0))), mix_tint('lemon', pig, 0.5), granulate=0.1, seed=17)
MOON = float(os.environ.get('MOON', '0.0'))
if MOON > 0:
    # the phases of Venus: at every half day a disc of its apparent size, lit as the telescope sees it,
    # horns turned from the Sun; evening moons warm, morning moons cool, faded in the Sun's glare
    step = int(round(float(os.environ.get('MSTEP', '0.5')) / 0.02))
    idx = np.arange(0, len(px), step)
    R0 = float(os.environ.get('R0', '3.6')) * rs
    Fw = np.zeros((H, W), np.float32); Fc = np.zeros((H, W), np.float32)
    ds = d
    for i in idx:
        j = np.where(sel)[0][i]
        vx, vy, vz = ds['x'][j], ds['y'][j], ds['z'][j]
        sxv, syv, szv = ds['sx'][j] - vx, ds['sy'][j] - vy, ds['sz'][j] - vz      # Venus -> Sun
        exv, eyv, ezv = -vx, -vy, -vz                                                  # Venus -> Earth
        ns = np.sqrt(sxv ** 2 + syv ** 2 + szv ** 2); ne = np.sqrt(exv ** 2 + eyv ** 2 + ezv ** 2)
        cph = (sxv * exv + syv * eyv + szv * ezv) / (ns * ne)                          # cos(phase angle)
        R = R0 * 0.72 / ne
        shx, shy = sxv / ns, -syv / ns                                                  # sun direction in pixel coords
        n = int(np.ceil(R)) + 2
        cxi, cyi = px[i], py[i]
        x0, y0 = int(np.floor(cxi)) - n, int(np.floor(cyi)) - n
        if x0 < 0 or y0 < 0 or x0 + 2 * n + 2 >= W or y0 + 2 * n + 2 >= H: continue
        gy, gx = np.mgrid[y0:y0 + 2 * n + 2, x0:x0 + 2 * n + 2]
        qx, qy = gx + 0.5 - cxi, gy + 0.5 - cyi
        a = qx * shx + qy * shy; b = -qx * shy + qy * shx
        rr2 = a * a + b * b
        disc = np.clip(R + 0.5 - np.sqrt(rr2), 0, 1)
        c2 = max(cph * cph, 1e-6)
        ell = a * a / (R * R * c2) + b * b / (R * R)
        if cph >= 0:
            lit = (a > 0) | (ell < 1)
        else:
            lit = (a > 0) & (ell > 1)
        w = MOON * vis[i] * disc * lit
        tgt = Fw if dl[i] > 0 else Fc
        tgt[y0:y0 + 2 * n + 2, x0:x0 + 2 * n + 2] += w.astype(np.float32)
    Fw = gaussian_filter(Fw, 0.45 * rs); Fc = gaussian_filter(Fc, 0.45 * rs)
    MK = float(os.environ.get('MKNEE', '1.5'))     # soft cap on stacked moons (the loop tips went black)
    Fw = MK * (1 - np.exp(-Fw / MK)); Fc = MK * (1 - np.exp(-Fc / MK))
    sh.wash(Fw, mix_tint('apricot', 'blush', 0.4), granulate=0.1, seed=21)
    sh.wash(Fc, mix_tint('aqua', 'lavender', 0.4), granulate=0.1, seed=22)
# the reference: the whole path as a hairline of ink
ink = cloud(px, py, np.ones(len(px), bool), 0.7 * rs)
sh.wash(float(os.environ.get('INKC', '0.30')) * tone(ink, 0.6), 'ink')
r = np.hypot(x, y)
if GHOST > 0:
    gev = cloud(gpx, gpy, gdl > 0, 1.3 * rs); gmo = cloud(gpx, gpy, gdl <= 0, 1.3 * rs)
    gref = len(gpx) / (np.pi * (1.75 * SCALE) ** 2)
    sh.wash(GHOST * (1 - np.exp(-gev / (gref * 2.0))), 'apricot')
    sh.wash(GHOST * (1 - np.exp(-gmo / (gref * 2.0))), 'aqua')
print('cloud', time.time() - t0)

# the Sun's circle (lemon, faint ring) and the ecliptic cross-hair? no: air.
yy, xx = np.mgrid[0:H, 0:W]
rr = np.hypot(xx - cx, yy - cy)
ring = np.exp(-((rr - SCALE) / (1.6 * rs)) ** 2)
sh.wash(0.75 * ring, 'lemon')
GLARE = float(os.environ.get('GLARE', '0.14'))
if GLARE > 0:   # the Sun's glare: a wide lemon halo on its yearly circle, where the planet is lost
    sh.wash(GLARE * np.exp(-((rr - SCALE) / (0.10 * SCALE)) ** 2), mix_tint('lemon', 'apricot', 0.3))
del ring

# ink: one 8-year cycle as a thread
if INKW > 0:
    m = (yr >= CYC[0]) & (yr < CYC[1])
    pts = np.stack([px[m][::5], py[m][::5]], 1)
    ink = polyline_density(W, H, pts, 1.4 * rs, 1.0, sigma=0.5 * rs)
    sh.wash(INKW * np.clip(ink, 0, 1), 'ink')
# Earth: small ink dot at the centre
sh.wash(discs_density(W, H, [cx], [cy], [3.0 * rs], [1.0], sigma=0.6 * rs) * 0.8, 'ink')

# transits: inferior conjunction with tiny angular separation
dd = dg
sep = np.degrees(np.arccos(np.clip((dd['x'] * dd['sx'] + dd['y'] * dd['sy'] + dd['z'] * dd['sz']) /
      np.sqrt((dd['x'] ** 2 + dd['y'] ** 2 + dd['z'] ** 2) * (dd['sx'] ** 2 + dd['sy'] ** 2 + dd['sz'] ** 2)), -1, 1)))
gr = np.hypot(dd['x'], dd['y'])
cand = np.where((sep < 0.27) & (gr < 0.5) & (gyr >= CY0) & (gyr < CY1))[0]
# group consecutive
groups = np.split(cand, np.where(np.diff(cand) > 4)[0] + 1) if len(cand) else []
tr_idx = [g[np.argmin(sep[g])] for g in groups]
print('transits:', [(ts.tt_jd(dd['t'][i]).utc_iso()[:10], round(float(sep[i]), 3)) for i in tr_idx])
segs = []
for i in tr_idx:
    sx_, sy_ = cx + dd['sx'][i] * SCALE, cy - dd['sy'][i] * SCALE
    segs.append([cx, cy, sx_, sy_])
    sh.wash(discs_density(W, H, [sx_], [sy_], [5.0 * rs], [1.0], sigma=1.0 * rs) * 0.9, 'lemon')
if segs:
    sh.wash(0.55 * np.clip(draw_lines_density(W, H, segs, 1.2 * rs, sigma=0.5 * rs), 0, 1), 'coral')
    sh.wash(discs_density(W, H, [gpx[i] for i in tr_idx], [gpy[i] for i in tr_idx], [6.5 * rs] * len(tr_idx), [1.0] * len(tr_idx), sigma=1.2 * rs) * 1.1, 'coral')

# caption
sh.caption_strip(0.905, 0.985, 0.62)
items = [('Hesperus Is Phosphorus', W / 2, 0.925 * H, 30 * rs, 'serif_bold', 'mm'),
         ('one planet, two names: Venus around the Earth for eight years (2009–2017), the stars held still. Ink: where it went. Warm: seen at dusk. Cool: seen at dawn. Paper: lost in the Sun.', W / 2, 0.958 * H, 13.5 * rs, 'italic', 'mm')]
sh.wash(text_density(W, H, items) * 0.95, 'ink')
img = sh.develop()
finish(img, (FINAL, FINAL), out)
print('done', time.time() - t0)
