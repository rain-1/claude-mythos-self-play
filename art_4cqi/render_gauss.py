"""render_gauss.py — WHAT THE CIRCLE CANNOT SEE: Gauss's map of the ellipse onto the disc, for a family of
ellipses from nearly round to a needle.  Inside each ellipse: the disc's polar net pulled back (ink hairlines,
circles |w| = j/12 and 40 rays), pigment by |w| (mint heart -> lavender -> blush rim) with density = the
conformal factor |w'| (the harmonic measure seen from the centre), so the tips the circle cannot see fade to
paper.  Coral: the foci.  Caption per ellipse: the share of the circle the tips beyond the foci receive.
    python3 render_gauss.py FINAL_W
"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from pastel import *
from gauss import ellipse_map, modulus_for_ratio
FINALW = int(sys.argv[1]); SS = 2
W = FINALW * SS; H = int(W * 1.6); rs = FINALW / 1024 * SS
BAS = [0.8, 0.55, 0.38, 0.25, 0.15]
cert = json.load(open('cert_gauss.json')) if False else None
sheet = Sheet(W, H, seed=41)
mx = 0.07
gap = 0.035 * W
aw = min((1 - 2 * mx) * W / 2, (0.85 * H - gap * (len(BAS) - 1) - 12 * rs * len(BAS)) / (2 * sum(BAS)))
gap = gap + 12 * rs
tot = sum(BAS) * 2 * aw + gap * (len(BAS) - 1)
y = 0.06 * H + (0.86 * H - tot) / 2
ink_all = np.zeros((H, W), np.float32)
labels = []
foci = []
for ba in BAS:
    m, c = modulus_for_ratio(ba)
    a, b = np.cosh(c), np.sinh(c)
    bh = ba * aw
    cy = y + bh; cxp = W / 2
    y += 2 * bh + gap
    # pixel grid of this ellipse's box
    y0, y1 = int(cy - bh - 4 * rs), int(cy + bh + 4 * rs)
    yy, xx = np.mgrid[y0:y1, 0:W].astype(np.float64)
    X = (xx - cxp) / aw * a; Y = -(yy - cy) / aw * a
    Z = X + 1j * Y
    inside = (X / a) ** 2 + (Y / b) ** 2 < 1
    Zc = np.where(inside, Z, 0)
    w, _, _ = ellipse_map(Zc, ba)
    absw = np.abs(w); argw = np.angle(w)
    # conformal factor by finite differences (pixel units)
    gx = np.gradient(w, axis=1); gy = np.gradient(w, axis=0)
    fac = np.abs(gx) * (aw / a)            # |dw/dz| in units of 1/ellipse-units ... relative only
    fac = np.where(inside, fac, 0)
    med = np.median(fac[inside])
    # hairlines: circles |w| = j/12 and rays every 9 degrees
    def lines(field, step, grad):
        frac = (field / step) % 1.0
        dist = np.minimum(frac, 1 - frac) * step / (grad + 1e-12)
        return ink_from_distance(dist, 0.6 * rs)
    gA = np.hypot(np.gradient(absw, axis=1), np.gradient(absw, axis=0))
    ph = np.exp(1j * argw)
    gP = np.hypot(np.abs(np.gradient(ph, axis=1)), np.abs(np.gradient(ph, axis=0)))
    ink = lines(absw, 1 / 12, gA) * 0.7 + lines(argw / (2 * np.pi), 1 / 36, gP / (2 * np.pi)) * 0.5 * np.clip(absw * 6, 0, 1)
    ink = np.where(inside, ink, 0)
    ink = np.where(gA / (1 / 12) > 0.5, 0, ink)
    # rim
    # distance to the ellipse rim ~ |1 - sqrt((X/a)^2+(Y/b)^2)| * local scale; use the implicit function / gradient
    F = np.sqrt((X / a) ** 2 + (Y / b) ** 2) - 1
    gF = np.hypot(np.gradient(F, axis=1), np.gradient(F, axis=0)) + 1e-12
    ink += ink_from_distance(np.abs(F) / gF, 0.9 * rs) * 0.8
    ink_all[y0:y1] += ink
    # pigment: hue by |w| through mint -> aqua -> lavender -> blush ; density by the conformal factor
    ramp = ['lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']
    h = np.clip(absw, 0, 0.999) * (len(ramp) - 1)
    i0 = np.floor(h).astype(int); i1 = np.minimum(i0 + 1, len(ramp) - 1); fr = (h - i0).astype(np.float32)
    dens = np.clip(fac / med, 0, 3.0) ** 0.75 * 0.72 * inside
    dens = dens.astype(np.float32)
    for j, name in enumerate(ramp):
        mmask = dens * (np.where(i0 == j, 1 - fr, 0) + np.where(i1 == j, fr, 0))
        full = np.zeros((H, W), np.float32); full[y0:y1] = mmask
        sheet.wash(full, name, granulate=0.1, seed=j + 5)
    # foci
    fx = aw / a
    foci += [(cxp - fx, cy), (cxp + fx, cy)]
    # label: tip share
    yf = b * np.sqrt(1 - 1 / a ** 2)
    wf, _, _ = ellipse_map(np.array([1 + 1j * yf]), ba)
    hm = np.angle(wf[0]) / np.pi
    xs_ = np.linspace(1, a, 20001)
    area_tip = 2 * np.trapezoid(b * np.sqrt(np.clip(1 - xs_ ** 2 / a ** 2, 0, None)), xs_) / (np.pi * a * b)
    pct = lambda v: np.format_float_positional(100 * v, precision=2, unique=False, fractional=False, trim='-') + ' %'
    labels.append((f'b/a = {ba}:  beyond the foci lies {pct(area_tip)} of the ellipse; the circle gives those two tips {pct(hm)} of its rim',
                   W / 2, cy + bh + 3 * rs + (0 if ba > 0.2 else 8 * rs), 15 * rs, 'italic', 'ma'))
    print(ba, 'tip area', area_tip, 'harmonic', hm, flush=True)
sheet.wash(gaussian_filter(ink_all, 0.3 * rs) * 0.8, 'ink')
sheet.wash(discs_density(W, H, [p[0] for p in foci], [p[1] for p in foci], [3.2 * rs] * len(foci), [1.0] * len(foci), sigma=0.7 * rs), 'coral')
sheet.wash(text_density(W, H, labels), 'ink')
sheet.caption_strip(0.925, 0.99, 0.5)
title = 'What the Circle Cannot See'
sub = ('Gauss\'s unpublished map of the ellipse onto the disc (1834): w = √k·sn((2K/π)·arcsin z). The disc\'s circles and rays, pulled back; '
       'pigment by |w|, tone by how much of the circle each place receives. The thinner the ellipse, the less of it the circle can see.')
lines_ = wrap(sub, 17 * rs, 'italic', 0.86 * W)
items = [(title, W / 2, 0.943 * H, 36 * rs, 'serif_bold', 'mm')] + [(ln, W / 2, (0.962 + 0.013 * i) * H, 17 * rs, 'italic', 'mm') for i, ln in enumerate(lines_)]
sheet.wash(text_density(W, H, items), 'ink')
img = sheet.develop()
out = f'cache/gauss_{FINALW}.png' if FINALW < 2048 else f'ellipse_{FINALW}.png'
finish(img, (FINALW, int(FINALW * 1.6)), out)
