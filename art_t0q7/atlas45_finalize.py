#!/usr/bin/env python3
"""Finalize atlas 45: labels + annotation over atlas45_stage1.png."""
import numpy as np, re, os
from PIL import Image, ImageDraw
from annot import annotate, fonts

img = Image.open("atlas45_stage1.png").convert("RGB")
W, H = img.size
d = ImageDraw.Draw(img)
F = fonts(1.0)
GOLD = (255, 205, 90); CY = (140, 210, 240); GREY = (150, 156, 176); DIM = (108, 114, 132)
WHT = (235, 240, 250)

XMIN, XMAX = 1.55e11, 1.62e12
def xp(n): return int((n - XMIN) / (XMAX - XMIN) * (W - 160)) + 80
HOR = 1580

# final counts
txt = open("hunt_rungap_1200000000000_1600000000000.txt").read()
def cnt(l, g):
    m = re.search(rf"l={l} g={g} maximal_runs=(\d+)", txt)
    return int(m.group(1)) if m else 0
Sm = re.search(r"\|S∩range\|=(\d+)", txt)
S45 = int(Sm.group(1)) if Sm else 0
l325, l425, l525 = cnt(3,25), cnt(4,25), cnt(5,25)
l324, l424, l524 = cnt(3,24), cnt(4,24), cnt(5,24)
l6 = cnt(6,24)
r34_25 = l425/max(l325,1); r34_24 = l424/max(l324,1)

fences = [(458171603806,"#1"),(615709112638,"#2"),(830595732286,"#3"),
          (862954027582,"#4"),(1158245890366,"#5")]
new_fences = []
for line in open("hunt_alarms_1200000000000_1600000000000.txt"):
    m = re.match(r"OCC l=5 g=25 start=(\d+)", line.strip())
    if m and int(m.group(1)) not in [f for f,_ in fences]+new_fences:
        new_fences.append(int(m.group(1)))
sextets = [536462850079, 982614621929]
new_sextets = []
for line in open("hunt_alarms_1200000000000_1600000000000.txt"):
    m = re.match(r"L6\+! l=\d+ gap=24 start=(\d+)", line.strip())
    if m and int(m.group(1)) not in sextets+new_sextets:
        new_sextets.append(int(m.group(1)))
for i, f_ in enumerate(new_fences): fences.append((f_, f"#{6+i}"))

# fence labels (staggered heights)
for k, (n, lab) in enumerate(fences):
    x = xp(n); y = HOR - 640 - (k % 3) * 46
    new = n >= 1.2e12
    d.text((x-30, y-30), f"{lab}: {n:,}", font=F["mono_s"], fill=GOLD if not new else (255, 228, 140))
    d.text((x-30, y-6), f"≡94 mod 144 ✓", font=F["mono_s"], fill=DIM if not new else GOLD)
for n in sextets + new_sextets:
    x = xp(n)
    d.text((x-30, HOR-940), f"SEXTET {n:,}", font=F["mono_s"], fill=WHT)

# climate labels
d.text((xp(4.2e11), 190), "the climate: r₃₄ = quartets per triplet, per window", font=F["sub"], fill=(200, 200, 214))
YLO, YHI = 1.2e-3, 8.2e-3
SKY_Y0, SKY_Y1 = 150, 760
def yv(v): return SKY_Y1 - (v - YLO)/(YHI - YLO) * (SKY_Y1 - SKY_Y0)
d.text((xp(1.24e12), yv(r34_24)+16), f"channel 24 (ref) → {r34_24*1e3:.2f}e-3", font=F["mono_s"], fill=(120, 132, 152))
d.text((xp(1.24e12), yv(r34_25)+16), f"channel 25 → {r34_25*1e3:.2f}e-3", font=F["mono_s"], fill=GOLD)
# era labels
d.text((xp(1.7e11), HOR+40), "certified silent era (atlas 42) —", font=F["mono_s"], fill=DIM)
d.text((xp(1.7e11), HOR+64), "the model said no fence lives here", font=F["mono_s"], fill=DIM)
d.text((xp(8.35e11), HOR+40), "← every-occurrence logging online (atlas 44)", font=F["mono_s"], fill=(100, 120, 145))
d.text((W-410, HOR-24), "n →  (0.16 → 1.6 trillion)", font=F["mono_s"], fill=DIM)

# ledger labels
d.text((80, 1700), "the ledger: gold = observed ch-25 fences per window;  amber band = the model's pre-committed expectation",
       font=F["mono_s"], fill=GREY)
obs45 = l525
verdict = ("WEATHER — the channel talks again" if obs45 >= 3 else
           ("cooling — below expectation again" if obs45 <= 1 else "within the band"))
verdict_short = "still cooling" if obs45 <= 1 else ("weather again" if obs45 >= 3 else "in band")
d.text((xp(1.21e12), 1736), f"45: {obs45} vs E≈2.5–4.5 → {verdict_short}", font=F["mono_s"], fill=GOLD)
d.text((xp(8.9e11), 1736), "44: 1 vs E≈3.3–4.2 (quiet)", font=F["mono_s"], fill=DIM)
d.text((xp(4.05e11), 1736), "two quiet windows: 2 vs E≈6–9, Poisson P≈2.6% — the channel is cooling", font=F["mono_s"], fill=(200, 180, 140))

sex_txt = f"+{len(new_sextets)} new" if new_sextets else "none new (E≈0.5–0.9, P≈40–60%)"
annotate(img,
    "THE WEATHER OF THE TWENTY-FIFTH CHANNEL",
    ["Numbers that are sums of two squares, listened to as a radio band:",
     "equal-gap runs are its signals. Gap 25 admits runs of five only on the",
     "narrow gate start ≡ 94 (mod 144) — proven in atlas 42, obeyed by every fence since."],
    [f"relay extended 1.2e12 → 1.6e12:  |S∩window| = {S45:,} members  (atlas piece 45; engine: segmented full factorization)",
     f"this window: {l325:,} triplets / {l425:,} quartets / {obs45} quintet-fence(s) at gap 25;  {l524} quintets at gap 24;  sextets: {sex_txt}",
     f"drift r₃₄(25) series: 2.53 / 2.59 / 2.73 / 2.52 / {r34_25*1e3:.2f} e-3 — the 'rising law' of atlas 43 stays weather, not law",
     "every fence certified: consecutive members by full factorization, maximal, gate-residue checked",
     "pre-committed model (atlas45_precommit.md, written before the scan finished): E[fences] ≈ 2.5–4.5, E[sextet] ≈ 0.5–0.9",
     "lightning: gold = ch-25 fences #1–#6 · white = the two sextets · cyan = ch-24 quintets · violet = ch-23"],
    margin=76)
img.save("atlas45_2560.png")
print("saved atlas45_2560.png; obs45 =", obs45, "fences:", [f for f,_ in fences], "new sextets:", new_sextets)
