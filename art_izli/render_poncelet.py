"""THE DANCE THAT CANNOT MISS — Poncelet porism, pastel register (2560²).

Center: the full rotating family of closing 2/7 heptagrams (72 phases) between
two circles — the porism as a woven mandala whose caustic IS the inner circle.
Flanks: closing families 1/3 (Chapple), 1/4 (Fuss), 2/5, 3/8.
Bottom: the rotation-number field over the (d, r) parameter triangle with the
exact closure curves inked — a smooth wash, no Arnold tongues: integrability
means the dance never locks.
"""
import numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont
from pastel import Watercolor, stroke_polyline, PIGMENTS
from scipy.ndimage import gaussian_filter

SS = 2
FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 900
W = H = FINAL * SS
data = json.load(open('poncelet_data.json'))
AMPSC = (FINAL / 900) ** 0.6   # overlap-fog compensation at size jumps

wc = Watercolor(H, W, seed=21)

def draw_family(cx, cy, RAD, entry, pigcycle, chord_w, amp, ink_amp):
    d, r, q = entry['d'], entry['r'], entry['q']
    orbits = entry['orbits']
    nph = len(orbits)
    flds = {p: np.zeros((H, W), np.float32) for p in set(pigcycle)}
    for oi, orb in enumerate(orbits):
        # pigment for this phase: cycle smoothly
        t = oi / nph * len(pigcycle)
        pig = pigcycle[int(t) % len(pigcycle)]
        pts = np.stack([cx + RAD * np.cos(orb), cy + RAD * np.sin(orb)], 1)
        stroke_polyline(flds[pig], pts, chord_w, amp=amp)
    for pig, f in flds.items():
        wc.wash(f, pig)
    # circles in fine ink
    th = np.linspace(0, 2 * np.pi, 700)
    ink = np.zeros((H, W), np.float32)
    stroke_polyline(ink, np.stack([cx + RAD * np.cos(th), cy + RAD * np.sin(th)], 1),
                    1.0 * SS, amp=ink_amp)
    stroke_polyline(ink, np.stack([cx + RAD * (d + r * np.cos(th)),
                                   cy + RAD * r * np.sin(th)], 1),
                    1.0 * SS, amp=ink_amp)
    wc.wash(ink, 'graphite')

# ---- hero mandala -----------------------------------------------------------
hero_c = (0.5 * W, 0.375 * H)
hero_R = 0.315 * W
draw_family(hero_c[0], hero_c[1], hero_R, data['hero'],
            ['periwinkle', 'lilac', 'rose', 'lilac'],
            2.2 * SS, 0.085 * AMPSC, 0.35 * AMPSC)
# warm underwash of the TRUE annulus (outside the offset inner circle)
yy_, xx_ = np.mgrid[0:H, 0:W]
rr_ = np.hypot(xx_ - hero_c[0], yy_ - hero_c[1]) / hero_R
d_h, r_h = data['hero']['d'], data['hero']['r']
ri_ = np.hypot(xx_ - (hero_c[0] + d_h * hero_R), yy_ - hero_c[1]) / hero_R
ann = ((rr_ < 1.01) & (ri_ > r_h * 0.99)).astype(np.float32)
ann *= np.clip(1.06 - rr_, 0, 1) ** 0.45
wc.wash(0.14 * ann, 'butter', granulate=0.2)

# ---- flanking medallions ----------------------------------------------------
med_pos = [(0.115, 0.13), (0.885, 0.13), (0.115, 0.52), (0.885, 0.52)]
med_R = 0.085 * W
pigsets = [['sky', 'seafoam'], ['peach', 'butter'], ['sage', 'seafoam'], ['lilac', 'rose']]
for entry, (fx, fy), pigs in zip(data['medallions'], med_pos, pigsets):
    entry = dict(entry, orbits=entry['orbits'][::2])
    draw_family(fx * W, fy * H, med_R, entry, pigs, 1.5 * SS, 0.16 * AMPSC, 0.3 * AMPSC)

# ---- parameter-triangle wash ------------------------------------------------
G = np.load('poncelet_rho.npy')
d0, d1, r0, r1 = np.load('poncelet_axes.npy')
bx0, bx1 = int(0.08 * W), int(0.92 * W)
by0, by1 = int(0.735 * H), int(0.965 * H)
bw, bh = bx1 - bx0, by1 - by0
# resample grid to band (r upward)
from scipy.ndimage import zoom
Gs = np.flipud(G)                      # row 0 = top = large r
zy, zx = bh / Gs.shape[0], bw / Gs.shape[1]
Gz = zoom(np.nan_to_num(Gs, nan=-1), (zy, zx), order=1)[:bh, :bw]
Mz = zoom((~np.isnan(Gs)).astype(float), (zy, zx), order=1)[:bh, :bw] > 0.55
s = np.clip(Gz * 2, 0, 1)              # 0..1 over rho in (0, 1/2)
# 3-stop pastel gradient: sky (rho->0) -> butter -> rose (rho->1/2)
wA = np.clip(1 - 2 * s, 0, 1)          # sky
wB = np.clip(1 - np.abs(2 * s - 1), 0, 1)   # butter
wC = np.clip(2 * s - 1, 0, 1)          # rose
for wgt, pig in ((wA, 'sky'), (wB, 'butter'), (wC, 'rose')):
    f = np.zeros((H, W), np.float32)
    f[by0:by1, bx0:bx1] = 0.62 * wgt * Mz
    wc.wash(f, pig, granulate=0.15)
# closure curves in ink
ink = np.zeros((H, W), np.float32)
for name, cur in data['curves'].items():
    dd = np.array(cur['d']); rr = np.array(cur['r'])
    keep = (rr > 0.05) & (dd < 0.87)
    dd, rr = dd[keep], rr[keep]
    px = bx0 + (dd - d0) / (d1 - d0) * bw
    py = by1 - (rr - r0) / (r1 - r0) * bh
    stroke_polyline(ink, np.stack([px, py], 1), 0.7 * SS, amp=0.42)
wc.wash(ink, 'graphite')
# specimen dots (hero + medallions)
dot = np.zeros((H, W), np.float32)
marks = [(data['hero']['d'], data['hero']['r'])] + \
        [(m['d'], m['r']) for m in data['medallions']]
yy, xx = np.mgrid[0:H, 0:W]
for dm, rm in marks:
    px = bx0 + (dm - d0) / (d1 - d0) * bw
    py = by1 - (rm - r0) / (r1 - r0) * bh
    dot += 3.0 * np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * (2.6 * SS) ** 2))
wc.wash(dot, 'ink')

# ---- labels -----------------------------------------------------------------
img = Image.new('L', (W, H), 0)
dr = ImageDraw.Draw(img)
try:
    f_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(0.024 * H))
    f_sub = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(0.0105 * H))
    f_tiny = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(0.0088 * H))
except Exception:
    f_title = f_sub = f_tiny = ImageFont.load_default()
title = "The Dance That Cannot Miss"
bb = dr.textbbox((0, 0), title, font=f_title)
dr.text(((W - bb[2]) / 2, 0.662 * H), title, fill=255, font=f_title)
for i, sub in enumerate([
    "Poncelet's porism: if one chain of tangent chords closes, every chain closes —",
    "seventy-two dances between the same two circles, and none may miss.",
    "Below: the rotation-number field over all circle pairs; on the inked curves the dance closes."]):
    bb2 = dr.textbbox((0, 0), sub, font=f_sub)
    dr.text(((W - bb2[2]) / 2, (0.694 + 0.016 * i) * H), sub, fill=255, font=f_sub)
# curve fraction labels at left ends
for name, cur in data['curves'].items():
    dd = np.array(cur['d']); rr = np.array(cur['r'])
    px = bx0 + (dd[0] - d0) / (d1 - d0) * bw
    py = by1 - (rr[0] - r0) / (r1 - r0) * bh
    dr.text((px - 0.030 * W, py - 0.0045 * H), name, fill=255, font=f_tiny)
dr.text((bx0, by1 + 0.004 * H), "d (center offset) →", fill=255, font=f_tiny)
tf = np.asarray(img, dtype=np.float32) / 255.0
wc.wash(2.0 * gaussian_filter(tf, 0.6 * SS), 'ink')

wc.save(f'poncelet_{FINAL}.png', final_size=(FINAL, FINAL), dmax=2.4)
print('saved', FINAL)
