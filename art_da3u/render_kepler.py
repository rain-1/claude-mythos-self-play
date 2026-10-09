"""Companion: Kepler's equation in the camera.  Nine needle pinwheels, one per panel, shutter per panel."""
import sys, numpy as np
from PIL import Image
from paint import SORBET, paint_pinwheel, paint_hub, caption
OUT = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
SS = int(sys.argv[2]) if len(sys.argv) > 2 else 2
name = sys.argv[3] if len(sys.argv) > 3 else f'kepler_{OUT}.png'
u = OUT/1200.0
W = OUT*SS; H = int(OUT*1.2)*SS
img = np.ones((H, W, 3))*np.array([0.992, 0.987, 0.978])
rng = np.random.default_rng(3)
img += (rng.random((H, W, 1)) - 0.5)*0.008
ETIP = [0.6, 0.95, 1.3, 1.8, 2.6, 3.6, 5.0, 7.0, 10.0]
HUES = ['strawberry', 'coral', 'peach', 'butter', 'lime', 'mint', 'sky', 'periwinkle', 'lilac', 'bubblegum', 'rose']
N = 9
cols = [SORBET[HUES[i]] for i in range(N)]
mx, top, gap = 70*u*SS, 60*u*SS, 26*u*SS
P = (W - 2*mx - 2*gap)/3
R = P*0.46
for idx, e in enumerate(ETIP):
    iy, ix = divmod(idx, 3)
    x0, y0 = mx + ix*(P + gap), top + iy*(P + gap + 34*u*SS)
    sub = img[int(y0):int(y0 + P), int(x0):int(x0 + P)]
    Y, X = np.mgrid[0:sub.shape[0], 0:sub.shape[1]].astype(float)
    # faint panel: a pale disc of the swept area
    cx = cy = P/2
    rr = np.hypot(X - cx, Y - cy)
    a = np.clip(R*1.04 - rr, 0, 1)[..., None]*0.35
    sub[:] = sub*(1 - a) + a*np.array([0.95, 0.95, 0.99])
    k = e*P/(2*np.pi*R)                        # e_tip = 2 pi k R / Hpanel
    paint_pinwheel(sub, X, Y, cx, cy, R, N, k, sub.shape[0], cols, phase=0.4,
                   r0=0.07, width=0.075, ink=1.3*u*SS)
    paint_hub(sub, X, Y, cx, cy, R*0.05, SORBET['butter'], ink=1.3*u*SS)
    if e > 1:
        rs = R/e
        ang = np.arctan2(Y - cy, X - cx)
        dash = np.clip((np.sin(ang*40) + 0.2)*3, 0, 1)
        a = (np.clip(1 - np.abs(rr - rs)/(1.5*u*SS), 0, 1)*dash)[..., None]
        sub[:] = sub*(1 - 0.9*a) + SORBET['coral']*0.9*a
im = Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8))
if SS > 1: im = im.resize((OUT, int(OUT*1.2)), Image.LANCZOS)
for idx, e in enumerate(ETIP):
    iy, ix = divmod(idx, 3)
    x0, y0 = (mx + ix*(P + gap))/SS, (top + iy*(P + gap + 34*u*SS))/SS
    mean = N if e <= 1 else N*(1 - 2*np.arccos(1/e)/np.pi + 2*np.sqrt(e*e - 1)/np.pi)
    caption(im, x0 + P/SS/2, y0 + P/SS + 2*u, [(f'e = {e:g} at the tip  ·  {mean:.1f} crossings on the rim, on average', 'i', 14)], scale=u, align='center')
caption(im, 70*u, 1272*u, [('Kepler in the Camera', 'b', 30),
  ('nine needles photographed by a shutter that reads one row at a time: a needle crosses the circle of radius r where  φ − e sin φ = M,  e = 2πkr/H', 'i', 14.5),
  ('coral dashes: r = H/2πk, where e = 1.  Inside, one crossing per needle; outside, on average  N(1 − 2 arccos(1/e)/π + 2√(e²−1)/π)', 'i', 14.5)], scale=u)
im.save(name); print('saved', name)
