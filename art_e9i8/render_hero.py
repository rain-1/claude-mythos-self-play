#!/usr/bin/env python3
"""THE RIM'S DECREE — hero render v2 (MO 514722 census).

A night field of the thirteen champion circles — for each achievable
on-count k <= 32, the SMALLEST circle through exactly k lattice points —
placed on one true shared lattice (integer translations are the symmetry
of the problem, so every fractional center, radius, on-point and interior
point is exact).  Each court softly lights the lattice points its rim
imprisons; the exactly-5 court carries its 106 — the number the rim
decrees, proved minimal.  Bottom strip: the full census of 8.9 million
circles with r <= 32 as rarity strata.
Usage: render_hero.py SIZE SS OUT [nolabel]
"""
import sys, math, json
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom
from PIL import Image, ImageDraw, ImageFont

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = int(sys.argv[2]) if len(sys.argv) > 2 else 1
OUT = sys.argv[3] if len(sys.argv) > 3 else "hero_proto.png"
LABELS = "nolabel" not in sys.argv
S = SIZE * SS
rs = S / 2048.0

D = json.load(open("hero_data.json"))
champ = {int(k): v for k, v in D["champions"].items()}
ghosts = {int(k): v for k, v in D["ghost_radii"].items()}
hist = {int(k): v for k, v in D["hist"].items()}

STRIP_H = int(0.150 * S)            # census strip
FH = S - STRIP_H                    # field height
U = FH / 56.0                       # px per lattice unit (field 64 x 56 units)
FCX, FCY = S * 0.5, FH * 0.5        # field center px

def to_px(ux, uy):                  # lattice units -> px (y up)
    return FCX + ux * U, FCY - uy * U

# layout: desired court centers in lattice units (origin field center)
LAY = {7: (-12.0, 3.0), 32: (22.0, 14.0), 20: (-25.0, -9.5),
       9: (11.0, -13.0), 24: (28.5, -9.0), 10: (-8.0, -15.0),
       5: (8.0, 21.0), 16: (12.0, -21.0), 12: (20.5, -22.5),
       6: (25.6, -23.3), 8: (29.6, -24.2), 3: (29.9, -19.8),
       4: (31.0, -25.6)}

img = np.zeros((S, S, 3), np.float32)

def splat(px, py, sigma, color, amp):
    n = int(max(3.2 * sigma, 2))
    x0, x1 = int(px) - n, int(px) + n + 1
    y0, y1 = int(py) - n, int(py) + n + 1
    if x1 < 0 or y1 < 0 or x0 >= S or y0 >= S: return
    x0c, x1c = max(x0, 0), min(x1, S); y0c, y1c = max(y0, 0), min(y1, S)
    gy, gx = np.mgrid[y0c:y1c, x0c:x1c]
    g = np.exp(-(((gx - px) ** 2 + (gy - py) ** 2) /
                 (2 * sigma ** 2))).astype(np.float32)
    for c in range(3):
        img[y0c:y1c, x0c:x1c, c] += amp * color[c] * g

def ring(pcx, pcy, rpx, sigma, color, amp, ymax=None):
    n = int(rpx + 4 * sigma + 2)
    x0c, x1c = max(int(pcx) - n, 0), min(int(pcx) + n + 1, S)
    y0c, y1c = max(int(pcy) - n, 0), min(int(pcy) + n + 1, ymax if ymax else S)
    if x0c >= x1c or y0c >= y1c: return
    gy, gx = np.mgrid[y0c:y1c, x0c:x1c]
    rr = np.hypot(gx - pcx, gy - pcy)
    g = np.exp(-((rr - rpx) ** 2) / (2 * sigma ** 2)).astype(np.float32)
    for c in range(3):
        img[y0c:y1c, x0c:x1c, c] += amp * color[c] * g

# ---- palette ----
BG    = np.array([0.008, 0.011, 0.024])
LATT  = (0.30, 0.42, 0.62)
GOLD  = (1.00, 0.72, 0.28)
ICE   = (0.42, 0.72, 1.00)
EMBER = (1.00, 0.32, 0.24)
DUST  = (1.00, 0.52, 0.24)
INWASH_E = (0.30, 0.50, 0.75)
INWASH_O = (0.85, 0.55, 0.25)
STAR_W = (1.00, 0.96, 0.88)
STAR_C = (0.88, 0.96, 1.00)
SLATE = (0.60, 0.66, 0.80)

def cls_color(k):
    if k == 7: return EMBER
    return GOLD if k % 2 else ICE

# ---- lattice ground (field only) ----
for ux in range(-33, 34):
    for uy in range(-29, 30):
        px, py = to_px(ux, uy)
        if -2 < px < S + 2 and -2 < py < FH:
            splat(px, py, 1.1 * rs, LATT, 0.10)

# ---- courts ----
placed = {}
for k, c in champ.items():
    c0x, c0y = -c["G"] / (2 * c["A"]), -c["F"] / (2 * c["A"])
    tx, ty = LAY[k]
    T = (round(tx - c0x), round(ty - c0y))
    cx, cy = c0x + T[0], c0y + T[1]
    placed[k] = (cx, cy, T)
    pcx, pcy = to_px(cx, cy)
    rpx = c["r"] * U
    col = cls_color(k)
    big = c["r"] > 4
    # rim
    ring(pcx, pcy, rpx, 1.5 * rs, col, 1.05, ymax=FH)
    ring(pcx, pcy, rpx, 6.5 * rs, col, 0.16, ymax=FH)
    # interior lattice softly lit (the decree)
    r2 = c["r"] ** 2
    R = int(c["r"]) + 1
    icx, icy = round(cx), round(cy)
    wash = INWASH_O if k % 2 else INWASH_E
    if k == 7: wash = (0.95, 0.40, 0.28); 
    for ux in range(icx - R, icx + R + 1):
        for uy in range(icy - R, icy + R + 1):
            if (ux - cx) ** 2 + (uy - cy) ** 2 < r2:
                px, py = to_px(ux, uy)
                if py < FH:
                    splat(px, py, 1.3 * rs, wash, (0.36 if k in (7,5,9) else 0.28) if big else 0.38)
    # on-point stars
    scol = STAR_W if k % 2 else STAR_C
    for (dx, dy) in c["on"]:
        px, py = to_px(cx + dx, cy + dy)
        if py < FH + 20:
            em = k in (5, 7)
            splat(px, py, (4.6 if em else 3.4) * rs, scol, 1.6 if em else 1.0)
            splat(px, py, (12 if em else 8) * rs, col, 0.30)

# the 106: brighten exactly-5 interior dust
c5 = champ[5]; cx, cy, T = placed[5][0], placed[5][1], placed[5][2]
for (dx, dy) in c5["inn"]:
    px, py = to_px(cx + dx, cy + dy)
    splat(px, py, 1.9 * rs, DUST, 0.55)

# ---- census strip ----
y0s = FH + int(0.012 * S)
rowk = [3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 24, 32]
nrow = len(rowk)
rh = (S - y0s - int(0.004 * S)) / nrow
xL, xR = 0.075 * S, 0.985 * S
def rx(r): return xL + (r / 32.5) * (xR - xL)
# strip plate
img[y0s - int(0.006 * S):, :, :] += np.array([0.006, 0.008, 0.016],
                                             np.float32)[None, None, :]
for i, k in enumerate(rowk):
    yr = y0s + (i + 0.55) * rh
    col = cls_color(k)
    if k in (3, 4):
        for b, cnt, mi in hist[k]:
            r = (b + 0.5) * 0.125
            a = min(cnt / 4000.0, 1.0)
            splat(rx(r), yr, 1.5 * rs, col, 0.05 + 0.55 * a)
    else:
        for r in ghosts[k]:
            splat(rx(r), yr, 1.4 * rs, col, 0.30)
    # champion star
    r0 = champ[k]["r"]
    splat(rx(r0), yr, 3.2 * rs, STAR_W if k % 2 else STAR_C, 1.5)

# ---- bloom ----
lum = img.sum(axis=2)
thr = np.percentile(lum, 99.75) / 2.2
hi = np.maximum(img - thr / 3.0, 0)
ds = 4
blo = ndzoom(ndzoom(hi, (1 / ds, 1 / ds, 1), order=1), (ds, ds, 1),
             order=1)[:S, :S]
blo = gaussian_filter(blo, (7 * rs, 7 * rs, 0))
img += 0.5 * blo
del hi, blo, lum

# ---- tone map ----
img += BG[None, None, :].astype(np.float32)
out = 1.0 - np.exp(-1.5 * img)
out = np.power(np.clip(out, 0, 1), 1 / 1.85)
out += (np.random.rand(S, S, 1).astype(np.float32) - 0.5) / 255.0
out = np.clip(out, 0, 1)
im = Image.fromarray((out * 255).astype(np.uint8))
if SS > 1:
    im = im.resize((SIZE, SIZE), Image.LANCZOS)

# ---- labels (at final size) ----
if LABELS:
    W = SIZE
    fs = W / 4096.0
    d = ImageDraw.Draw(im)
    FP = "/usr/share/fonts/truetype/dejavu/"
    def font(sz, bold=False, mono=False):
        f = "DejaVuSansMono.ttf" if mono else ("DejaVuSans-Bold.ttf" if bold
                                               else "DejaVuSans.ttf")
        try: return ImageFont.truetype(FP + f, int(sz))
        except Exception: return ImageFont.load_default()
    def txt(x, y, s, sz, col, bold=False, mono=False, anchor="la"):
        d.text((x, y), s, font=font(sz, bold, mono), fill=col, anchor=anchor)
    scale = U * (SIZE / S)
    def court_tag(k, ux, uy, s1, s2, col, sz1=34, sz2=26, anchor="lm"):
        px, py = to_px(ux, uy)
        px *= SIZE / S; py *= SIZE / S
        txt(px, py, s1, sz1 * fs, col, bold=True, anchor=anchor)
        if s2:
            txt(px, py + (sz1 + 6) * fs, s2, sz2 * fs, (170, 178, 195), anchor=anchor)
    # feature labels inside the three story courts
    court_tag(7, -21, 12, "k = 7   first at r = \u221a276250/22 \u2248 23.891",
              "1793 within \u2014 a prime count demands a cube", (255, 120, 100))
    court_tag(5, 14.6, 23.5, "k = 5   r = 25/\u221a18",
              "106 within \u2014 proved minimal", (255, 200, 110))
    court_tag(9, 8.5, -9.5, "k = 9   r = 65/\u221a18 < \u03c1(7)",
              "9 = 3\u00d73 comes cheaper than prime 7", (255, 200, 110))
    # small id tags for the rest
    import fractions
    def rstr(k):
        c = champ[k]
        num = c.get("num", c["G"]**2 + c["F"]**2)
        return f"\u221a{num}/{2*c['A']}"
    tags = {32: (30.5, -8.2, "rm"), 20: (-28.5, -20.5, "lm"), 24: (27.5, -4.5, "mm"),
            10: (-14.5, -27.2, "lm"), 16: (7.2, -26.9, "lm"), 12: (19.0, -18.3, "lm"),
            6: (23.3, -26.3, "lm"), 8: (27.2, -27.3, "lm"), 3: (28.3, -16.6, "lm"),
            4: (29.4, -24.2, "lm")}
    for k, (ux, uy, an) in tags.items():
        col = tuple(int(255 * v) for v in cls_color(k))
        court_tag(k, ux, uy, f"k = {k}", "", col, sz1=24, anchor=an)
    # title
    txt(40 * fs, 34 * fs, "THE RIM'S DECREE", 58 * fs, (235, 238, 245), bold=True)
    txt(40 * fs, 106 * fs,
        "the smallest circle through exactly k lattice points, for every "
        "achievable k ≤ 32 — drawn true on one lattice", 30 * fs, (168, 176, 192))
    txt(40 * fs, 148 * fs,
        "every rim softly lights the lattice points it imprisons: the count "
        "the rim decrees   ·   MO 514722, exhaustive census, exact arithmetic",
        26 * fs, (128, 136, 152))
    # strip labels
    sy0 = (y0s / S) * SIZE
    for i, k in enumerate(rowk):
        yr = (y0s + (i + 0.55) * rh) / S * SIZE
        cnt = (sum(c for _, c, _ in hist[k]) if k in (3, 4)
               else len(ghosts[k]))
        txt(28 * fs, yr, f"{k}", 24 * fs, tuple(int(255 * v) for v in cls_color(k)),
            mono=True, anchor="rm")
        txt(38 * fs, yr + 2 * fs, f"\u00d7{cnt:,}", 15 * fs,
            (120, 128, 145), mono=True, anchor="lm")
    txt(58 * fs, sy0 - 20 * fs,
        "census: all 8,909,743 circles with r ≤ 32, by on-count k (rows) and radius →   "
        "counts 11,13,14,15,17,… never occur below r = 32", 24 * fs, (150, 158, 175))
    for rr in (5, 10, 15, 20, 25, 30):
        xr = rx(rr) / S * SIZE
        txt(xr, SIZE - 16 * fs, str(rr), 22 * fs, (110, 118, 135), anchor="mm", mono=True)
im.save(OUT)
print("wrote", OUT)
