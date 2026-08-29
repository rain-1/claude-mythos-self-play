#!/usr/bin/env python3
"""THE GATE KEEPS ITS WORD — Atlas piece 48 (2560²).

The completed window: relay [2,100,243,202,048 → 2.6e12] over the ℤ[√2]
two-squares country S = {n : n and n+1 both sums of two squares}.
Registers, top to bottom:
  sky      — every fence (l=5 run) as a beacon: ch-24 ice, ch-25 gold,
             ch-23 violet; sextets (l=6, g=24) as white stars.  Nightscape
             reflection below the horizon.
  field    — all l=4 g=25 occurrences as candle ticks: gold = fertile
             class 94, slate = {103,110,119}; ringed = ≡0 (mod 25).
  climb    — cumulative N24(x), N25(x), N23(x) against the pre-committed
             expectation bands (atlas48_precommit.md).
  ledger   — the gate theorem, the counts, the verdict.
Usage: render_atlas.py SIZE SS OUT
"""
import sys, math, json
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom
from PIL import Image, ImageDraw, ImageFont

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
SS = int(sys.argv[2]) if len(sys.argv) > 2 else 1
OUT = sys.argv[3] if len(sys.argv) > 3 else "atlas_proto.png"
S = SIZE * SS
rs = S / 2560.0

R = json.load(open("atlas48_results.json"))
V = json.load(open("atlas48_verdict.json"))   # verdict strings + final counts
X0, X1 = 2100243202048, 2600000000000
XW = R["scanned_to"] - X0                      # actual scanned width

AL = "hunt_alarms_2100243202048_2600000000000.txt"
occ4, f24, f23, f25, sext = [], [], [], [], []
for line in open(AL):
    p = line.split()
    if p[0] != "OCC":
        if p[0] == "FIRST":
            continue
        continue
    l = int(p[1][2:]); g = int(p[2][2:]); s = int(p[3][6:])
    if g == 25 and l == 4: occ4.append(s)
    elif g == 24 and l == 5: f24.append(s)
    elif g == 23 and l == 5: f23.append(s)
    elif g == 25 and l == 5: f25.append(s)
    elif g == 24 and l >= 6: sext.append(s)
sext = sorted(set(sext))
# FIRST lines are also fences; merge from results json
f25 = sorted(set(f25) | set(R["fences25"]["starts"]))
f23 = sorted(set(f23) | set(R["fences23"]["starts"]))

img = np.zeros((S, S, 3), np.float32)

def xpix(n): return 0.045 * S + (n - X0) / (X1 - X0) * 0.925 * S

def splat(px, py, sigma, color, amp):
    n_ = int(max(3.0 * sigma, 2))
    x0, x1 = int(px) - n_, int(px) + n_ + 1
    y0, y1 = int(py) - n_, int(py) + n_ + 1
    if x1 < 0 or y1 < 0 or x0 >= S or y0 >= S: return
    x0c, x1c = max(x0, 0), min(x1, S); y0c, y1c = max(y0, 0), min(y1, S)
    gy, gx = np.mgrid[y0c:y1c, x0c:x1c]
    g = np.exp(-(((gx - px) ** 2 + (gy - py) ** 2) /
                 (2 * sigma ** 2))).astype(np.float32)
    for c in range(3):
        img[y0c:y1c, x0c:x1c, c] += amp * color[c] * g

def vline(px, y0, y1, w, color, amp):
    x0c, x1c = max(int(px - 3 * w), 0), min(int(px + 3 * w) + 1, S)
    y0c, y1c = max(int(y0), 0), min(int(y1), S)
    if x0c >= x1c or y0c >= y1c: return
    gx = np.arange(x0c, x1c)
    g = np.exp(-((gx - px) ** 2) / (2 * w ** 2)).astype(np.float32)
    for c in range(3):
        img[y0c:y1c, x0c:x1c, c] += amp * color[c] * g[None, :]

GOLD = (1.00, 0.74, 0.28); ICE = (0.42, 0.72, 1.00)
VIOL = (0.62, 0.48, 0.95); WHITE = (1.0, 0.97, 0.9)
SLATE = (0.40, 0.46, 0.60); EMBER = (1.0, 0.36, 0.25)

# ---- sky band ----
HOR = 0.470 * S            # horizon y
sky_top = 0.130 * S
# horizon glow
gy = np.arange(S, dtype=np.float32)
horg = np.exp(-((gy - HOR) ** 2) / (2 * (14 * rs) ** 2))
for c in range(3):
    img[:, :, c] += 0.09 * np.array([0.5, 0.62, 0.85])[c] * horg[:, None]
# scanned-region ground tint (very faint) up to scanned_to
img[int(HOR):int(HOR + 4 * rs), int(xpix(X0)):int(xpix(R["scanned_to"])), :] += \
    np.array([0.10, 0.13, 0.20], np.float32) * 0.5

def beacon(n, col, h, w, amp, star=False):
    px = xpix(n)
    vline(px, HOR - h, HOR, w * rs, col, amp)
    vline(px, HOR, HOR + 0.25 * h, w * rs, col, amp * 0.10)   # reflection
    splat(px, HOR - h, 3.2 * rs * (1.6 if star else 1.0), WHITE if star else col,
          1.2 if star else 0.55)

for n in f24: beacon(n, ICE, 0.135 * S, 1.1, 0.5)
for n in f23: beacon(n, VIOL, 0.205 * S, 1.4, 0.85)
for n in f25: beacon(n, GOLD, 0.290 * S, 1.8, 1.0, star=True)
for n in sext:
    px = xpix(n)
    beacon(n, WHITE, 0.235 * S, 1.2, 0.8, star=True)
    splat(px, HOR - 0.235 * S, 9 * rs, GOLD, 0.5)

# ---- fertile candle field ----
FT, FB = 0.560 * S, 0.660 * S
for s_ in occ4:
    px = xpix(s_)
    cls = s_ % 144
    if cls == 94:
        vline(px, FT, FB, 1.0 * rs, GOLD, 0.55)
    else:
        vline(px, FT + 0.012 * S, FB - 0.012 * S, 0.9 * rs, SLATE, 0.30)
    if s_ % 25 == 0:
        splat(px, (FT + FB) / 2, 4.5 * rs, EMBER, 0.9)

# ---- cumulative climb band ----
CT, CB = 0.700 * S, 0.865 * S
def climb(events, col, cap, amp=0.9):
    if not events: return
    ev = sorted(events)
    xs = [xpix(X0)] + [xpix(e) for e in ev] + [xpix(R["scanned_to"])]
    ys = list(range(0, len(ev) + 1)) + [len(ev)]
    for i in range(len(xs) - 1):
        y = CB - (ys[i] / cap) * (CB - CT)
        x0_, x1_ = xs[i], xs[i + 1]
        n = max(int((x1_ - x0_) / (1.5 * rs)), 1)
        for t in range(n + 1):
            splat(x0_ + (x1_ - x0_) * t / max(n, 1), y, 1.1 * rs, col, amp * 0.28)
# expectation bands (pre-committed, scaled to full window, drawn as wedges)
def band(lo, hi, col, cap):
    for frac_i in range(220):
        f = frac_i / 219.0
        x = xpix(X0 + f * (X1 - X0))
        for yv in (lo * f, hi * f):
            y = CB - (yv / cap) * (CB - CT)
            splat(x, y, 0.9 * rs, col, 0.10)
cap24 = max(len(f24) * 1.25, 140)
band(105, 135, ICE, cap24); climb(f24, ICE, cap24)
cap25 = 12
band(2.1, 4.7, GOLD, cap25); climb(f25, GOLD, cap25, amp=1.3)
cap23 = 14
band(6, 10, VIOL, cap23); climb(f23, VIOL, cap23, amp=1.1)

# ---- bloom / tone ----
lum = img.sum(axis=2)
thr = np.percentile(lum[lum > 0], 99.6) / 2.0
hi = np.maximum(img - thr / 3.0, 0)
ds = 4
blo = ndzoom(ndzoom(hi, (1 / ds, 1 / ds, 1), order=1), (ds, ds, 1),
             order=1)[:S, :S]
blo = gaussian_filter(blo, (6 * rs, 6 * rs, 0))
img += 0.5 * blo
del hi, blo, lum
BG = np.array([0.010, 0.013, 0.026], np.float32)
img += BG[None, None, :]
out = 1.0 - np.exp(-1.55 * img)
out = np.power(np.clip(out, 0, 1), 1 / 1.82)
out += (np.random.rand(S, S, 1).astype(np.float32) - 0.5) / 255.0
out = np.clip(out, 0, 1)
im = Image.fromarray((out * 255).astype(np.uint8))
if SS > 1:
    im = im.resize((SIZE, SIZE), Image.LANCZOS)

# ---- text ----
d = ImageDraw.Draw(im)
fs = SIZE / 2560.0
FP = "/usr/share/fonts/truetype/dejavu/"
def font(sz, bold=False, mono=False):
    f = "DejaVuSansMono.ttf" if mono else ("DejaVuSans-Bold.ttf" if bold
                                           else "DejaVuSans.ttf")
    try: return ImageFont.truetype(FP + f, int(sz))
    except Exception: return ImageFont.load_default()
def txt(x, y, s, sz, col, bold=False, mono=False, anchor="la"):
    d.text((x, y), s, font=font(sz, bold, mono), fill=col, anchor=anchor)

txt(40 * fs, 28 * fs, "THE GATE KEEPS ITS WORD", 46 * fs, (235, 238, 245), bold=True)
txt(40 * fs, 86 * fs,
    "Atlas piece 48 — the window piece 47 lost to contention, completed:  "
    f"relay [{X0:,} → 2.6×10¹²]  over  S = {{n : n, n+1 both sums of two squares}}",
    24 * fs, (168, 176, 192))
txt(40 * fs, 120 * fs,
    "gold beacons: ch-25 fences (l=5, gap 25) — every one ≡ 94 (mod 144), as the "
    "certified gate theorem demands  ·  ice: ch-24  ·  violet: ch-23  ·  white stars: sextets (l=6)",
    22 * fs, (150, 158, 175))
k = SIZE / S
# axis ticks
for tv in (2.1002432e12, 2.2e12, 2.3e12, 2.4e12, 2.5e12, 2.6e12):
    px = xpix(tv) * k
    txt(px, HOR * k + 26 * fs, f"{tv/1e12:.4g}e12", 20 * fs, (110, 118, 135),
        mono=True, anchor="mm")
# fence labels for ch-25
for i, n in enumerate(f25):
    px = min(xpix(n) * k, SIZE - 150 * fs)
    st = 26 * (i % 2)
    txt(px, (HOR - 0.290 * S) * k - (46 - st) * fs, f"{n:,}", 19 * fs, (255, 210, 120),
        mono=True, anchor="mm")
    txt(px, (HOR - 0.290 * S) * k - (26 - st) * fs, "≡ 94", 17 * fs, (200, 170, 100),
        mono=True, anchor="mm")
for n in sext:
    px = xpix(n) * k
    txt(px, (HOR - 0.235 * S) * k - 8 * fs, "sextet", 17 * fs, (230, 235, 245),
        mono=True, anchor="mm")
# register captions
txt(40 * fs, (FT) * k - 24 * fs,
    f"the fertile field — all {len(occ4)} four-runs at gap 25: gold ≡ 94 (fertile), "
    "slate ≡ {103,110,119} (sterile);  ember rings: the 5-adic survivors ≡ 0 (mod 25)",
    21 * fs, (150, 158, 175))
txt(40 * fs, CT * k - 24 * fs,
    "the climb — cumulative fences vs the bands pre-committed before any data was read",
    21 * fs, (150, 158, 175))
txt(0.975 * SIZE, (CB - (135 / cap24) * (CB - CT)) * k - 14 * fs, "E\u2082\u2084 105\u2013135", 19 * fs,
    (120, 170, 220), mono=True, anchor="rm")
txt(0.975 * SIZE, (CB - (4.7 / cap25) * (CB - CT)) * k + 16 * fs, "E\u2082\u2085 2.1 (long-run) \u2013 4.7 (warm)", 19 * fs,
    (220, 180, 110), mono=True, anchor="rm")
txt(0.975 * SIZE, (CB - (10 / cap23) * (CB - CT)) * k, "E\u2082\u2083 6\u201310", 19 * fs,
    (170, 150, 220), mono=True, anchor="rm")
# ledger
ly = 0.878 * SIZE
for i, line in enumerate(V["ledger"]):
    txt(40 * fs, ly + (14 + 30 * i) * fs, line, 22 * fs,
        (255, 205, 110) if i == 0 else (170, 178, 195))
im.save(OUT)
print("wrote", OUT)
