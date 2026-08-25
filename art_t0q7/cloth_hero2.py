#!/usr/bin/env python3
"""Hero stage 2: descent chart + annotation onto hero_stage1.png -> cloth_hero_4096.png"""
import numpy as np, json
from PIL import Image, ImageDraw
from annot import fonts

img = Image.open("hero_stage1.png").convert("RGB")
W, H = img.size
d = ImageDraw.Draw(img)
F = fonts(1.0)
Fb = fonts(1.35)
GOLD = (255, 204, 88); CYAN = (128, 214, 246); GREY = (155, 158, 172); DIM = (105, 110, 126)
EMBER = (232, 120, 44)

# ---------------- title ----------------
d.text((66, 18), "ONE UNIT OF LIGHT, FOLDED THIN", font=Fb["title"], fill=(240, 228, 200))

# ---------------- descent chart (right column) ----------------
cx, cy, cw, ch = 3395, 130, 640, 980
d.rectangle([cx, cy, cx+cw, cy+ch], fill=(9, 8, 12), outline=(80, 76, 92), width=2)
# data
cross = json.load(open("cloth_crossover.json"))
champs = {int(n): cross[n]["best"] for n in cross}
champs.update({64: 0.434037, 128: 0.421497, 256: 0.407789, 512: 0.416089})
exact = {n: (n+1)/(2*n) for n in range(2, 10)}
n10 = 329/600
XL, XRr = 1.0, 9.4      # log2 n
YB, YT = 0.38, 1.02
def tr(n, a):
    px = cx + 56 + (np.log2(n) - XL) / (XRr - XL) * (cw - 86)
    py = cy + 40 + (YT - a) / (YT - YB) * (ch - 130)
    return px, py
# reversal curve
ns = np.geomspace(2, 700, 200)
pts = [tr(n, (n+1)/(2*n)) for n in ns]
for k in range(len(pts)-1):
    d.line([pts[k], pts[k+1]], fill=(90, 86, 100), width=2)
# random mean ~ from survey: 0.6266@64 0.6016@256 0.5968@1024 0.5954@4096 + limit-ish
rnd = {64: 0.6266, 256: 0.6016, 1024: 0.5968}
rpts = [tr(n, a) for n, a in sorted(rnd.items())]
for k in range(len(rpts)-1):
    d.line([rpts[k], rpts[k+1]], fill=(70, 80, 96), width=2)
# C/log n guide through champion at 256
Cg = 0.407789 * np.log(256)
gn = np.geomspace(24, 700, 100)
gp = [tr(n, Cg/np.log(n)) for n in gn]
for k in range(len(gp)-1):
    if k % 3 != 2: d.line([gp[k], gp[k+1]], fill=(70, 96, 88), width=2)
# exact minima gold
for n, a in exact.items():
    px, py = tr(n, a); r = 7
    d.ellipse([px-r, py-r, px+r, py+r], fill=GOLD)
# crossover star n=10
px, py = tr(10, n10)
r = 13
for ang in range(8):
    th = ang * np.pi / 4
    d.line([px - r*np.cos(th), py - r*np.sin(th), px + r*np.cos(th), py + r*np.sin(th)],
           fill=CYAN, width=3)
# champions cyan
cser = sorted((n, a) for n, a in champs.items() if n >= 12)
cpts = [tr(n, a) for n, a in cser]
for k in range(len(cpts)-1):
    d.line([cpts[k], cpts[k+1]], fill=CYAN, width=3)
for (n, a), (pxx, pyy) in zip(cser, cpts):
    d.ellipse([pxx-5, pyy-5, pxx+5, pyy+5], fill=(190, 235, 252))
# labels
d.text((cx+18, cy+10), "how little can be left:  min area of T_σ", font=F["sub"], fill=(210, 205, 220))
d.text((cx+56, cy+52), "1.0 = no overlap", font=F["mono_s"], fill=DIM)
lx, ly = tr(44, 0.548)
d.text((lx, ly), "reversal (n+1)/2n → 1/2", font=F["mono_s"], fill=GREY)
lx, ly = tr(90, 0.62)
d.text((lx-30, ly-38), "random ≈ 0.596", font=F["mono_s"], fill=(120, 132, 150))
lx, ly = tr(2.6, 0.68)
d.text((lx, ly), "exact minima n ≤ 9:\nthe reversal, proven\nby exhaustion", font=F["mono_s"], fill=GOLD)
px, py = tr(10, n10)
d.text((px+20, py+18), "n = 10: the reversal is\nbeaten — area 329/600", font=F["mono_s"], fill=CYAN)
lx, ly = tr(48, 0.432)
d.text((lx-40, ly+34), "annealed champions", font=F["mono_s"], fill=CYAN)
lx, ly = tr(300, Cg/np.log(300))
d.text((lx-250, ly-10), "C/log n (Kuklinski's\nconjectured order)", font=F["mono_s"], fill=(110, 160, 145))
d.text((cx+18, cy+ch-36), "x: n (log scale)", font=F["mono_s"], fill=DIM)

# ---------------- annotation (right column, below chart) ----------------
ax, ay = 3395, 1180
lines = [
 ("MO 514628 · after T. J. Kaczynski (1998)", F["sub"], (200, 196, 210)),
 ("and P. Kuklinski (2023)", F["sub"], (200, 196, 210)),
 ("", F["mono_s"], GREY),
 ("n parallelograms join floor slot i to", F["mono_s"], GREY),
 ("ceiling slot σ(i); each carries area 1/n.", F["mono_s"], GREY),
 ("Total light = 1, always. The union T_σ", F["mono_s"], GREY),
 ("is what you SEE — overlap hides light.", F["mono_s"], GREY),
 ("", F["mono_s"], GREY),
 ("α_n = min area → 0  (theorem), but only", F["mono_s"], GREY),
 ("logarithmically slowly (conjecture C/log n).", F["mono_s"], GREY),
 ("Nothing is approachable; arrival is priced.", F["mono_s"], GREY),
 ("", F["mono_s"], GREY),
 ("NEW here:", F["mono_s"], (220, 214, 190)),
 ("· α_n = (n+1)/2n for n ≤ 9, argmin = the", F["mono_s"], GREY),
 ("  full reversal (exhaustive, exact areas)", F["mono_s"], GREY),
 ("· at n = 10 the reversal is dethroned:", F["mono_s"], GREY),
 ("  σ = [9 8 7 4 3 6 5 2 1 0], area 329/600", F["mono_s"], GREY),
 ("  — the hourglass waist is born", F["mono_s"], GREY),
 ("· annealing discovers the waist at every n:", F["mono_s"], GREY),
 ("  hold the cloth narrow over a whole band", F["mono_s"], GREY),
 ("  of heights, not one pinch — area 0.408", F["mono_s"], GREY),
 ("  at n = 256 (reversal: 0.502)", F["mono_s"], GREY),
 ("", F["mono_s"], GREY),
 ("MAIN: champion σ at n = 512, area 0.4161.", F["mono_s"], (200, 180, 150)),
 ("Brightness = number of overlapping panes:", F["mono_s"], (200, 180, 150)),
 ("all cloths below carry the SAME total light.", F["mono_s"], (200, 180, 150)),
]
yy = ay
for t, f, c in lines:
    d.text((ax, yy), t, font=f, fill=c)
    bb = f.getbbox(t or "x")
    yy += bb[3] - bb[1] + 10

img.save("cloth_hero_4096.png")
print("saved cloth_hero_4096.png")
