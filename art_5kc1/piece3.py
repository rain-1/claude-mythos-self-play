#!/usr/bin/env python3
"""THE OPEN CHANNELS — 2560².  Atlas piece 40, Z[sqrt2] country.
26 channels, one per gap g; depth = log10 n from 10^2.5 down to the 3.2e10
shoreline.  Three materials: 2-adically FORBIDDEN gaps = ice-capped dark slots;
open-and-visited gaps = fence glyphs / density ropes of every l=5 run, gold;
open-and-SILENT gaps (14, 17 near; 23, 24, 25 far) = cold empty shafts that exit
the frame past the shoreline, each lit only by the model's ghost fence at its
predicted first depth.  Header spectrum: singular series R(g) — the width of each
doorway; the discovery: R(14)=R(2), R(17)=R(1) — the tower does not shut them."""
import sys, json, numpy as np
from artlib import canvas, polyline, star, bloom, tonemap, save, bake_text, _splat_points

PREVIEW = "--preview" in sys.argv
S = 1024 if PREVIEW else 2560
SS = 1 if PREVIEW else 2
R_ = S * SS
rs = R_ / 1024.0
rng = np.random.default_rng(11)
buf = canvas(R_)

C_GOLD = np.array([1.00, 0.78, 0.30])
C_ICE  = np.array([0.55, 0.88, 1.00])
C_DUST = np.array([0.28, 0.40, 0.62])
C_AMBER= np.array([1.00, 0.55, 0.22])
C_STEEL= np.array([0.60, 0.70, 0.88])

GMAX = 26
ADM = {1,2,4,7,8,9,14,15,16,17,18,23,24,25}
SILENT = {14,17,23,24,25}

# ---- data ----
try:
    D = json.load(open("atlas40_data.json"))
    Rg = {int(k): v for k, v in D["R"].items()}
    deep = {int(k): v for k, v in D.get("deep_l5", {}).items()}
    predW = {g: D.get(f"pred_W5_{g}") for g in (14, 17)}
    fit = D["fit"]
except Exception:
    D = None
    Rg = {1:.1128,2:.05638,4:.02819,7:.1128,8:.9161,9:.9145,14:.05638,15:4.329,
          16:1.36,17:.1128,18:.4573,24:7.216,23:.1128,25:.1128}
    deep = {}; predW = {14: 0.05, 17: 0.02}; fit = [-1.5, 0.30, -0.8]
runs = {}   # g -> array of starts (<= 4e9)
for line in open("sqrt2_l5runs_prev.txt"):
    p = line.split()
    g = int(p[1]); runs.setdefault(g, []).append(int(p[0]))

XL, XR = 84 * rs, 985 * rs
YTOP, YBOT = 238 * rs, 908 * rs          # depth field; shoreline at YSHORE
LGTOP, LGBOT = 2.5, 10.51
YSHORE = YTOP + (np.log10(3.2e10) - LGTOP) / (LGBOT - LGTOP) * (YBOT - YTOP)
Y4E9 = YTOP + (np.log10(4e9) - LGTOP) / (LGBOT - LGTOP) * (YBOT - YTOP)
CW = (XR - XL) / GMAX
def xg(g): return XL + (g - 0.5) * CW
def ydep(n): return YTOP + (np.log10(n) - LGTOP) / (LGBOT - LGTOP) * (YBOT - YTOP)

# ---- background depth wash + void haze below shoreline ----
yy = np.linspace(0, 1, R_, dtype=np.float32)[:, None, None]
buf += 0.020 * np.exp(-((yy - YTOP / R_) / 0.45) ** 2) * np.array([0.10, 0.13, 0.30], np.float32)
ysh = YSHORE / R_
haze = np.clip((yy[:, :, 0] - ysh) / (1 - ysh), 0, 1) ** 1.5
buf += 0.05 * haze[..., None] * np.array([0.05, 0.09, 0.16], np.float32)

# ---- shoreline ----
xs = np.linspace(XL - 20 * rs, XR + 20 * rs, int(2200 * rs))
_splat_points(buf, xs, np.full_like(xs, YSHORE), 0.10 * rs, C_STEEL, 1)
_splat_points(buf, xs, np.full_like(xs, Y4E9), 0.022 * rs, C_STEEL * 0.7, 1)

# ---- header spectrum: R(g) bars ----
SB0 = 228 * rs   # bar baseline y
for g in range(1, GMAX + 1):
    x = xg(g)
    r = Rg.get(g, 0.0)
    if g not in ADM or r <= 0:
        star(buf, x, SB0 - 4 * rs, C_ICE * 0.7, amp=0.8, rad=1.6 * rs)
        continue
    hbar = (np.log10(r) + 2.1) / 3.1 * 58 * rs      # log scale -2.1..1
    hbar = max(hbar, 2 * rs)
    ys = np.linspace(SB0 - hbar, SB0, max(4, int(hbar / rs)))
    col = C_ICE if g in SILENT else C_GOLD
    _splat_points(buf, np.full_like(ys, x), ys, 0.30 * rs, col, 1)

# ---- channels ----
def fence_glyph(x, y, col, amp, w):
    px = x + (np.arange(5) - 2) * w / 4.0
    _splat_points(buf, px, np.full(5, y), amp, col, 1)
    xs2 = np.linspace(px[0], px[-1], 12)
    _splat_points(buf, xs2, np.full_like(xs2, y), amp * 0.25, col, 1)

for g in range(1, GMAX + 1):
    x = xg(g)
    if g not in ADM:
        # frozen slot: ice cap + faint dark fill
        ysc = np.linspace(YTOP, YTOP + 14 * rs, int(16 * rs))
        _splat_points(buf, np.full_like(ysc, x), ysc, 0.22 * rs, C_ICE * 0.85, 1)
        star(buf, x, YTOP + 4 * rs, C_ICE, amp=0.9, rad=1.8 * rs)
        continue
    # open channel rim: two faint verticals, brightness ~ R^0.3
    w = CW * 0.30
    rimamp = (0.05 if g in SILENT else 0.022) * rs * (0.5 + Rg.get(g, .05) ** 0.3)
    rimcol = C_ICE if g in SILENT else C_STEEL
    yend = YBOT if g in SILENT else YSHORE
    ysr = np.linspace(YTOP, yend, int(700 * rs))
    for sgn in (-1, 1):
        _splat_points(buf, np.full_like(ysr, x + sgn * w), ysr, rimamp, rimcol, 1)
    pos = np.array(sorted(runs.get(g, [])), dtype=np.float64)
    npos = len(pos)
    if npos > 400:
        # density rope: splat every run position, jittered across the channel width
        py = ydep(pos)
        pxr = x + rng.uniform(-w * 0.8, w * 0.8, npos)
        _splat_points(buf, pxr, py, 22.0 * rs / np.sqrt(npos), C_GOLD, 1)
    else:
        for n_ in pos:
            fence_glyph(x, ydep(n_), C_GOLD, 0.85, CW * 0.62)
    if npos:
        # first-occurrence gate
        star(buf, x, ydep(pos[0]), C_GOLD, amp=1.7, rad=2.1 * rs)
    # deep zone: new runs between 4e9 and 3.2e10 from deep census
    dg = deep.get(g)
    prev_count = npos
    if dg and dg["count"] > prev_count:
        newc = dg["count"] - prev_count
        fy = ydep(dg["first"]) if dg["first"] > 4e9 else None
        # mark the deep-zone finds
        if dg["first"] > 4e9:
            star(buf, x, ydep(dg["first"]), C_AMBER, amp=2.0, rad=2.2 * rs)
    if g in SILENT:
        # ghost fence at predicted first depth (model); channels 23..25: off-frame
        if predW.get(g):
            Xfirst = 4e9 / max(predW[g], 1e-12)
            if Xfirst < 10 ** LGBOT:
                fence_glyph(x, ydep(Xfirst), C_ICE, 0.7, CW * 0.62)
        # cold mouth glow at shoreline exit
        ysm = np.linspace(YSHORE, YBOT, int(120 * rs))
        _splat_points(buf, np.full_like(ysm, x), ysm, 0.055 * rs, C_ICE, 1)

for e in range(3, 11):
    ye = ydep(10 ** e)
    xs4 = np.linspace(XL - 26 * rs, XL - 12 * rs, int(16 * rs))
    _splat_points(buf, xs4, np.full_like(xs4, ye), 0.06 * rs, C_STEEL * 0.8, 1)
buf = bloom(buf, sigmas=(1.8 * rs, 7 * rs, 24 * rs), weights=(1.0, 0.4, 0.2), thresh=0.5)
img = tonemap(buf, k=1.35, gamma=0.92)
if SS > 1:
    from PIL import Image
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((S, S), Image.LANCZOS)
    img = np.asarray(im).astype(np.float32) / 255.0

fs = S / 1024.0
texts = [
    (0.040 * S, 0.020 * S, "THE OPEN CHANNELS", int(30 * fs), (0.93, 0.88, 0.78), True, "la"),
    (0.040 * S, 0.056 * S, "AP-obstruction atlas, piece 40  -  Z[sqrt2]:  S = { n with v_p(n) even for every p = 3,5 mod 8 }   -   every run of FIVE consecutive",
     int(12.5 * fs), (0.60, 0.64, 0.76), False, "la"),
    (0.040 * S, 0.076 * S, "members with equal gaps g, to depth 3.2x10^10.  header bars: singular series R(g).  ice = the 2-adic tower forbids;  gold = fences found;",
     int(12.5 * fs), (0.60, 0.64, 0.76), False, "la"),
    (0.040 * S, 0.096 * S, "cold shafts = OPEN but silent: R(14) = R(2) and R(17) = R(1) exactly - the door is wide; the country is too crowded for solitude.",
     int(12.5 * fs), (0.60, 0.64, 0.76), False, "la"),
]
for e in (3, 5, 7, 9, 10):
    texts.append(((XL - 30 * rs) / R_ * S, ydep(10 ** e) / R_ * S, f"1e{e}", int(10 * fs), (0.48, 0.54, 0.66), False, "rm"))
texts.append(((XL - 30 * rs) / R_ * S, YSHORE / R_ * S, "3.2e10", int(10 * fs), (0.60, 0.66, 0.78), False, "rm"))
for g in range(1, GMAX + 1):
    col = (0.65, 0.85, 0.95) if g in SILENT else ((0.75, 0.70, 0.58) if g in ADM else (0.45, 0.55, 0.68))
    texts.append((xg(g) / R_ * S, 0.152 * S, str(g), int(11 * fs), col, g in SILENT, "mm"))
img = bake_text(img, texts, S)
out = "piece3_preview.png" if PREVIEW else "channels_2560.png"
save(img, out, dither=True)
print("saved", out)
