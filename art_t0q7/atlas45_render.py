#!/usr/bin/env python3
"""ATLAS 45 (2560^2): THE WEATHER OF THE TWENTY-FIFTH CHANNEL.

Registers: (sky) drift-climate ridges r34(25), r34(24) per window;
(storm) exact lightning strikes — fences l5g25 gold, sextets l6 white,
quintets l5g24 cyan ticks (instrumented era), l5g23 violet;
(ledger) per-window observed fence counts vs the pre-committed E-bands.
"""
import numpy as np, re, os
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from annot import annotate, fonts

W = H = 2560
img = np.zeros((H, W, 3), np.float32)
rng = np.random.default_rng(7)

XMIN, XMAX = 1.55e11, 1.62e12
def xp(n): return int((n - XMIN) / (XMAX - XMIN) * (W - 160)) + 80

# ---------------- data ----------------
windows = [  # (lo, hi, l3g25, l4g25, l5g25, l3g24, l4g24, l5g24)
    (4.0e11, 5.6e11, 127085, 321, 1, 847480, 5835, 19),
    (5.6e11, 7.2e11, 132473, 343, 1, 879019, 6080, 27),
    (7.2e11, 8.8e11, 136089, 372, 2, 903152, 6314, 27),
    (8.8e11, 1.2e12, 282388, 712, 1, 1859078, 13398, 37),
]
# this run's window, parsed if present
newf = "hunt_rungap_1200000000000_1600000000000.txt"
new_window = None
if os.path.exists(newf):
    txt = open(newf).read()
    def cnt(l, g):
        m = re.search(rf"l={l} g={g} maximal_runs=(\d+)", txt)
        return int(m.group(1)) if m else 0
    new_window = (1.2e12, 1.6e12, cnt(3,25), cnt(4,25), cnt(5,25), cnt(3,24), cnt(4,24), cnt(5,24))
    windows.append(new_window)

fences = [458171603806, 615709112638, 830595732286, 862954027582, 1158245890366]
sextets = [536462850079, 982614621929]
quintets24, quintets23 = [], []
for fn in os.listdir("hist"):
    if fn.startswith("alarms"):
        for line in open("hist/"+fn):
            m = re.match(r"(?:OCC|FIRST) l=(\d+) g=(\d+) start=(\d+)", line.strip())
            if m:
                l, g, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if l == 5 and g == 24: quintets24.append(s)
                if l == 5 and g == 23: quintets23.append(s)
af = "hunt_alarms_1200000000000_1600000000000.txt"
new_fences, new_sextets = [], []
if os.path.exists(af):
    for line in open(af):
        m = re.match(r"(?:OCC|FIRST|L6\+!) l=(\d+) g(?:ap)?=(\d+) start=(\d+)", line.strip())
        if m:
            l, g, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if l == 5 and g == 25 and s not in new_fences: new_fences.append(s)
            if l == 5 and g == 24: quintets24.append(s)
            if l == 5 and g == 23: quintets23.append(s)
            if l >= 6 and g == 24 and s not in new_sextets: new_sextets.append(s)
fences_all = fences + new_fences
sextets_all = sextets + new_sextets
quintets24 = sorted(set(quintets24) - set(sextets_all))
quintets23 = sorted(set(quintets23))

# ---------------- geometry ----------------
SKY_Y0, SKY_Y1 = 150, 760          # climate band
HOR = 1580                          # storm horizon
LED_Y0, LED_Y1 = 1780, 2130        # ledger band

def put_line(pts, col, wpx, buf=img):
    # additive anti-aliased polyline via dense sampling
    pts = np.asarray(pts, float)
    for k in range(len(pts)-1):
        a, b = pts[k], pts[k+1]
        L = max(int(np.hypot(*(b-a))), 2)
        t = np.linspace(0, 1, L*2)
        xs = a[0] + t*(b[0]-a[0]); ys = a[1] + t*(b[1]-a[1])
        for dx in range(-wpx, wpx+1):
            for dy in range(-wpx, wpx+1):
                w = np.exp(-(dx*dx+dy*dy)/(0.6*wpx*wpx+0.4))
                ix = np.clip(xs+dx, 0, W-1).astype(int)
                iy = np.clip(ys+dy, 0, H-1).astype(int)
                for c in range(3):
                    np.add.at(buf[..., c], (iy, ix), 0.04*w*col[c])

# sky: climate ridges
YLO, YHI = 1.2e-3, 8.2e-3
def yv(v): return SKY_Y1 - (v - YLO)/(YHI - YLO) * (SKY_Y1 - SKY_Y0)
GOLD = (1.0, 0.78, 0.30); CY = (0.45, 0.80, 0.95); VIO = (0.55, 0.45, 0.85)
for (series_idx, col, wpx) in ((("r25"), GOLD, 3), (("r24"), (0.35,0.42,0.55), 2)):
    pts = []
    for (lo, hi, l325, l425, l525, l324, l424, l524) in windows:
        r = (l425/l325) if series_idx == "r25" else (l424/l324)
        pts.append(((xp(lo)+xp(hi))/2, yv(r)))
    put_line(pts, col, wpx)
    for (lo, hi, l325, l425, l525, l324, l424, l524), (px, py) in zip(windows, pts):
        r = (l425/l325) if series_idx == "r25" else (l424/l324)
        err = r / np.sqrt(max(l425 if series_idx == "r25" else l424, 1))
        put_line([(px, yv(r-err)), (px, yv(r+err))], col, max(wpx-1, 1))

# storm: strikes
def bolt(n, height, col, wpx, glowamp):
    x = xp(n)
    put_line([(x, HOR), (x, HOR - height)], col, wpx)
    yy, xx = np.mgrid[max(HOR-height-40,0):HOR, max(x-30,0):min(x+30,W)]
    g = np.exp(-((xx-x)**2)/(9.0*wpx)) * glowamp
    fade = np.clip((yy - (HOR-height-40)) / max(height*0.8, 1), 0, 1)
    for c in range(3):
        img[max(HOR-height-40,0):HOR, max(x-30,0):min(x+30,W), c] += g*fade*col[c]*0.012
    # reflection
    put_line([(x, HOR+6), (x, HOR + int(height*0.28))], tuple(c*0.25 for c in col), max(wpx-1,1))

for s in quintets23: bolt(s, 120, VIO, 1, 0.5)
for s in quintets24: bolt(s, 210, CY, 1, 0.7)
for s in fences_all: bolt(s, 620, GOLD, 3, 2.2)
for s in sextets_all: bolt(s, 900, (0.95, 0.97, 1.0), 3, 2.6)
# horizon line
put_line([(80, HOR), (W-80, HOR)], (0.5, 0.55, 0.65), 2)
# horizon night-glow (warm near horizon, fading upward)
yy = np.arange(H)[:, None].astype(np.float32)
glowband = np.clip(1 - np.abs(yy - HOR)/440.0, 0, 1)**2.6
img[:, 80:W-80, 0] += glowband[:, :1] * 0.045
img[:, 80:W-80, 1] += glowband[:, :1] * 0.035
img[:, 80:W-80, 2] += glowband[:, :1] * 0.030
# instrumented-era: faint blue floor ticks from 8.3e11
x0i = xp(8.3e11)
img[HOR-16:HOR, x0i:W-80, 2] += 0.10
img[HOR-16:HOR, x0i:W-80, 1] += 0.05
# window separators through all bands
for b in (1.6e11, 4.0e11, 5.6e11, 7.2e11, 8.8e11, 1.2e12, 1.6e12):
    xb = xp(b)
    img[SKY_Y0-40:LED_Y1, xb:xb+2, :] += np.array([0.030, 0.034, 0.045])[None, None, :]

# ledger: observed fences vs pre-committed bands per window
led_wins = [(1.6e11, 4.0e11, 0, (0.31, 0.60), "42: certified silent ✓")] + [
    (4.0e11, 5.6e11, 1, None, ""),
    (5.6e11, 7.2e11, 1, None, ""),
    (7.2e11, 8.8e11, 2, None, ""),
    (8.8e11, 1.2e12, 1, (3.3, 4.2), "44: quiet — 1 vs E≈3.3–4.2"),
]
if new_window:
    led_wins.append((1.2e12, 1.6e12, new_window[4], (2.5, 4.5), "45: verdict"))
def lyv(c): return LED_Y1 - c/5.0*(LED_Y1-LED_Y0)
for (lo, hi, obs, band, lab) in led_wins:
    xa, xb = xp(lo)+8, xp(hi)-8
    if band:
        ya, yb = lyv(band[1]), lyv(band[0])
        img[int(ya):int(yb), xa:xb, :] += np.array([0.16, 0.13, 0.07])[None, None, :]
    put_line([(xa, lyv(obs)), (xb, lyv(obs))], GOLD if obs > 0 else (0.5, 0.55, 0.65), 3)
    # observed bar fill up from 0
    img[int(lyv(obs)):int(lyv(0)), xa:xb, 0] += 0.020
    img[int(lyv(obs)):int(lyv(0)), xa:xb, 1] += 0.016
    img[int(lyv(obs)):int(lyv(0)), xa:xb, 2] += 0.008
put_line([(80, LED_Y1), (W-80, LED_Y1)], (0.35, 0.38, 0.45), 1)

# ---------------- post ----------------
img = gaussian_filter(img, (1.0, 1.0, 0))
lum = img.sum(2)
hi_ = np.clip(img - np.percentile(lum, 99.6)/3, 0, None)
glow = gaussian_filter(hi_, (16, 16, 0))
img = img + 0.8*glow
img = 1 - np.exp(-1.6 * img)
img = np.power(np.clip(img, 0, 1), 1/1.95)
pil = Image.fromarray(np.clip(img*255 + rng.uniform(-1,1,img.shape), 0, 255).astype(np.uint8))
pil.save("atlas45_stage1.png")
print("stage1 saved; windows:", len(windows), "fences:", fences_all, "sextets:", sextets_all,
      "quintets24:", len(quintets24), "q23:", len(quintets23))
