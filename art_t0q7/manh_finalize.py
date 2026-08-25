#!/usr/bin/env python3
"""Finalize piece 2: fence-approach inset + det/floor skyline inset + annotation."""
import numpy as np, json
from PIL import Image, ImageDraw
from scipy.linalg import eig
from annot import annotate, fonts

img = Image.open("manh_main_nolabel.png").convert("RGB")
W, H = img.size
d = ImageDraw.Draw(img)
F = fonts(1.0)
GOLD = (255, 200, 80); CYAN = (140, 216, 248); GREY = (150, 156, 176); DIM = (110, 118, 138)

# ---------- inset 1 (top-left): approach to the 60-degree fence ----------
iw, ih = 560, 420
x0, y0 = 70, 70
d.rectangle([x0, y0, x0+iw, y0+ih], fill=(8, 10, 18), outline=(90, 96, 116), width=2)
def halfrev(n):
    h = n // 2
    return np.concatenate([np.arange(h)[::-1], np.arange(h, n)[::-1]])
ns = np.array([10, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256])
gaps = []
for n in ns:
    A = np.abs(np.subtract.outer(np.arange(n), np.arange(n))).astype(float)
    p = halfrev(n)
    B = np.abs(np.subtract.outer(p, p)).astype(float)
    mu = eig(A, B, right=False)
    gaps.append(60.0 - np.degrees(np.abs(np.angle(mu))).max())
gaps = np.array(gaps)
# log-log: x = log2 n in [3, 8.2], y = log10 gap in [-1.05, 1.1]
lx = np.log2(ns); ly = np.log10(gaps)
def tr(a, b):
    px = x0 + 46 + (a - 3.0) / (8.2 - 3.0) * (iw - 76)
    py = y0 + 30 + (1.1 - b) / (1.1 + 1.05) * (ih - 90)
    return px, py
# fit slope
A1 = np.polyfit(np.log(ns), np.log(gaps), 1)
for k in range(len(ns) - 1):
    d.line([tr(lx[k], ly[k]), tr(lx[k+1], ly[k+1])], fill=GOLD, width=3)
for k in range(len(ns)):
    px, py = tr(lx[k], ly[k]); r = 5
    d.ellipse([px-r, py-r, px+r, py+r], fill=(255, 226, 150))
for n_lab in (16, 64, 256):
    k = list(ns).index(n_lab)
    px, py = tr(lx[k], ly[k])
    d.text((px+8, py-24), f"n={n_lab}", font=F["mono_s"], fill=GREY)
d.text((x0+16, y0+8), "the climb to the fence: 60° − max|arg μ| for half-reversal σ",
       font=F["mono_s"], fill=CYAN)
d.text((x0+16, y0+ih-58), f"log–log slope {A1[0]:.3f}  ⇒  gap ≈ c/n :", font=F["mono_s"], fill=GREY)
d.text((x0+16, y0+ih-34), "the cone |arg μ| < π/3 is approached, never crossed", font=F["mono_s"], fill=GREY)

# ---------- inset 2 (bottom-right): det spectrum above the floor ----------
big = json.load(open("manh_big_10.json"))
hist = np.array(big["hist"], float)   # log2(det/floor) in [0,20), 2000 bins
iw2, ih2 = 620, 380
x1, y1 = W - iw2 - 70, H - ih2 - 240
d.rectangle([x1, y1, x1+iw2, y1+ih2], fill=(8, 10, 18), outline=(90, 96, 116), width=2)
nb = 400
hh = hist[:nb].reshape(nb//4, 4).sum(1)   # bins of 0.02 in log2 up to 2.0... (20/2000*4=0.04)
hh = np.log1p(hh)
hh /= hh.max()
bw = (iw2 - 60) / len(hh)
for k, v in enumerate(hh):
    if v <= 0: continue
    bx = x1 + 30 + k*bw
    bh = v * (ih2 - 96)
    col = (255, 216, 120) if k == 0 else (110, 170, 205)
    d.rectangle([bx, y1 + ih2 - 40 - bh, bx + max(bw-1, 1), y1 + ih2 - 40], fill=col)
d.text((x1+16, y1+8), "n=10, all 3,628,800 shuffles: |det|/floor (log₂ scale)",
       font=F["mono_s"], fill=CYAN)
d.text((x1+30, y1+ih2-30), "floor pillar: exactly 2 shuffles — nothing below",
       font=F["mono_s"], fill=GOLD)

# ---------- axis labels ----------
d.text((W//2 - 240, 26), "|arg μ| = 60° — the fence no ratio crosses", font=F["mono_s"], fill=GOLD)
d.text((W//2 - 130, H - 46), "log |μ|  →", font=F["mono_s"], fill=DIM)
d.text((W - 560, H//2 + 16), "← the river: real ratios (width = density)", font=F["mono_s"], fill=DIM)

# ---------- main annotation ----------
annotate(img,
    "THE UNBREAKABLE FLOOR",
    ["Scramble n city blocks: D_π = |i−j| + |π(i)−π(j)|.  Conjecture (MO 514626):",
     "|det D_π| ≥ (n−1)·4ⁿ⁻¹ — no shuffle undercuts the straight line.  Here: every",
     "ratio μ of the pencil (A, ΠAΠᵀ);  |det D_π| = |det A|·∏|1+μ|,  ∏μ = 1."],
    ["verified exhaustively n ≤ 11 (43,589,145 shuffles): zero below the floor; equality only id & reversal",
     "second-smallest is quantized: floor + (n−2)4ⁿ⁻² — one rung, exactly",
     "observed laws: Re μ > 0;  |arg μ| < 60° sharp (half-reversal climbs as c/n);  complex μ shun |μ|=1",
     "gold star at μ=1: the identity — all ratios equal, Minkowski equality, the floor itself",
     "reverse-Minkowski for Lorentzian pairs is FALSE in general — yet this floor holds: the permutation saves it",
     "chart: x = log|μ|, y = arg μ (power-warped);  4,000,000 ratios from 400,000 random shuffles at n=10"],
    margin=76)
img.save("manh25_2560.png")
print("saved manh25_2560.png")
