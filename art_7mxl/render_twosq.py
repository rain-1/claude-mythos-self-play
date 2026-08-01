"""'The Ladders in the Thin Set' — 2560². AP-obstruction atlas, piece 37.

MO 513787: arithmetic progressions of consecutive sums of two squares.
Four specimen strips: the FIRST equal-gap run of length 3,4,5,6 among
consecutive elements of S = {x²+y²} (verified to 10⁹). Ground: the mod-8
loom — residues {3,6,7} can never be sums of two squares (the ramified
prime 2's good-step law). Beads: members of S, brightness = log r₂(n).
Gold: the ladder. Bottom: part (b) — smallest k with 1,1+k,…,1+(l−1)k ∈ S.
"""
import numpy as np
import pickle
import sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, zoom

S = int(sys.argv[1]) if len(sys.argv) > 1 else 2560
rs = S / 2560.0
H = W = S

res = pickle.load(open("twosq_results.pkl", "rb"))
records = [(3, 0, 1), (4, 757, 4), (5, 2989, 4), (6, 28059605, 12)]
krec = res["krec"]


def r2(n):
    if n < 0:
        return 0
    c = 0
    x = 0
    while x * x <= n:
        y2 = n - x * x
        y = int(round(y2 ** 0.5))
        for yy in (y - 1, y, y + 1):
            if yy >= 0 and yy * yy == y2:
                c += (2 if x else 1) * (2 if yy else 1) // 1
                # count signed pairs: (±x, ±y); handle zeros
                break
        x += 1
    return c


def inS(n):
    if n < 0:
        return False
    if n == 0:
        return True
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            e = 0
            while m % p == 0:
                m //= p
                e += 1
            if p % 4 == 3 and e % 2 == 1:
                return False
        p += 1
    if m > 1 and m % 4 == 3:
        return False
    return True


b_loom = np.zeros((H, W), np.float32)
b_bead = np.zeros((H, W), np.float32)
b_gold = np.zeros((H, W), np.float32)
b_forb = np.zeros((H, W), np.float32)


def splat(buf, x, y, sigma, amp, m=48):
    rng = np.random.default_rng(int(x * 7 + y * 13) & 0x7FFFFFFF)
    th = rng.normal(size=(2, m))
    xs = x + th[0] * sigma
    ys = y + th[1] * sigma
    ix = np.clip(np.round(xs).astype(int), 0, W - 1)
    iy = np.clip(np.round(ys).astype(int), 0, H - 1)
    np.add.at(buf, (iy, ix), np.full(m, amp / m))


x_lo, x_hi = 0.065 * W, 0.935 * W
strip_ys = [0.150, 0.315, 0.480, 0.645]

for (L, start, gap), fy in zip(records, strip_ys):
    span = (L - 1) * gap
    pad = max(int(span * 1.25), 36)
    wlo = max(0, start - pad)
    whi = start + span + pad
    nslots = whi - wlo + 1
    slot = (x_hi - x_lo) / nslots
    y0 = fy * H
    terms = set(start + gap * j for j in range(L))
    # loom ground: one soft column per integer, cold if ≡3,6,7 mod 8
    for m in range(wlo, whi + 1):
        x = x_lo + (m - wlo + 0.5) * slot
        r = m % 8
        forb = r in (3, 6, 7)
        ys = np.linspace(y0 - 0.046 * H, y0 + 0.030 * H, 240)
        buf = b_forb if forb else b_loom
        amp = 0.052 if forb else 0.016
        for off in (-0.9 * rs, 0.0, 0.9 * rs):
            ix = np.clip(np.round(np.full(240, x + off)).astype(int), 0, W - 1)
            iy = np.clip(np.round(ys).astype(int), 0, H - 1)
            np.add.at(buf, (iy, ix), np.full(240, amp / 3))
    # beads
    for m in range(wlo, whi + 1):
        if not inS(m):
            continue
        x = x_lo + (m - wlo + 0.5) * slot
        rr = r2(m)
        lum = np.log1p(rr) * 0.55
        if m in terms:
            splat(b_gold, x, y0, 3.4 * rs, 10.0 + lum * 2.5, m=420)
        else:
            splat(b_bead, x, y0, 2.6 * rs, 1.6 + 1.8 * lum, m=200)
    # arc bridges between consecutive rungs (the harp motif)
    tlist = sorted(terms)
    for a, b in zip(tlist[:-1], tlist[1:]):
        xa = x_lo + (a - wlo + 0.5) * slot
        xb = x_lo + (b - wlo + 0.5) * slot
        cx, r = 0.5 * (xa + xb), 0.5 * (xb - xa)
        th = np.linspace(0, np.pi, 240)
        xs = cx + r * np.cos(th)
        ys = y0 - 0.55 * r * np.sin(th) - 2.0 * rs
        ix = np.clip(np.round(xs).astype(int), 0, W - 1)
        iy = np.clip(np.round(ys).astype(int), 0, H - 1)
        np.add.at(b_gold, (iy, ix), np.full(240, 0.055))

# part (b) staircase
y_base = 0.880 * H
y_topmax = 0.780 * H
ls = sorted(krec)
import math
kmax = max(krec.values())
bar_w = (x_hi - x_lo) / (len(ls) + 3)
for i, L in enumerate(ls):
    k = krec[L]
    x = x_lo + (i + 0.5) * bar_w
    hgt = (math.log10(k) + 0.25) / (math.log10(kmax) + 0.25)
    ytop = y_base - hgt * (y_base - y_topmax)
    v2 = 0
    kk = k
    while kk % 2 == 0:
        v2 += 1
        kk //= 2
    warm = 0.35 + 0.16 * v2
    isnew = (i == 0) or (krec[ls[i - 1]] != k)
    amp = 0.020 if isnew else 0.008
    ys = np.linspace(ytop, y_base, 160)
    grad = np.linspace(1.0, 0.45, 160)
    for off in (-1.1 * rs, 0, 1.1 * rs):
        ix = np.clip(np.round(np.full(160, x + off)).astype(int), 0, W - 1)
        iy = np.clip(np.round(ys).astype(int), 0, H - 1)
        np.add.at(b_gold, (iy, ix), grad * (amp * warm / 3))
    splat(b_gold, x, ytop, 1.9 * rs, 3.2 if isnew else 1.1, m=140)

# compose
img = np.zeros((H, W, 3), np.float32)


def tone(x, k, g):
    return np.power(np.clip(1 - np.exp(-k * x), 0, 1), g)


def nzp(a, p):
    m = a[a > 1e-9]
    return np.percentile(m, p) if len(m) else 1.0


b_loom = gaussian_filter(b_loom, 1.3 * rs)
b_forb = gaussian_filter(b_forb, 1.3 * rs)
# baseline glow per strip
yyg = np.arange(H, dtype=np.float32)[:, None]
xxg = np.arange(W, dtype=np.float32)[None, :]
for fy in strip_ys:
    g = np.exp(-((yyg - fy * H) / (10 * rs)) ** 2) * 0.05
    xmaskg = ((xxg >= x_lo) & (xxg <= x_hi)).astype(np.float32)
    b_loom += (g * xmaskg).astype(np.float32)
b_bead_s = gaussian_filter(b_bead, 0.8 * rs)
b_gold_s = gaussian_filter(b_gold, 0.7 * rs)
img += tone(b_loom / nzp(b_loom, 99), 1.3, 0.8)[..., None] * np.array([0.24, 0.27, 0.36])
img += tone(b_forb / nzp(b_forb, 99), 1.3, 0.8)[..., None] * np.array([0.34, 0.16, 0.22])
img += tone(b_bead_s / nzp(b_bead_s, 99.5), 2.0, 0.62)[..., None] * np.array([0.55, 0.70, 0.95])
img += tone(b_gold_s / nzp(b_gold_s, 99.5), 2.0, 0.60)[..., None] * np.array([1.00, 0.78, 0.32])

# bloom
lum = img.sum(2)
thr = np.percentile(lum, 99.2)
mask = np.clip(lum - thr, 0, None)[..., None] * img / (lum[..., None] + 1e-9)
small = mask[::4, ::4]
bl = gaussian_filter(small, (9 * rs / 4, 9 * rs / 4, 0))
bloom = zoom(bl, (mask.shape[0] / small.shape[0], mask.shape[1] / small.shape[1], 1),
             order=1)[:H, :W]
img += 0.85 * np.clip(bloom, 0, None)
img = np.clip(img, 0, 1)
img = np.clip(img + (np.random.default_rng(1).random(img.shape) - 0.5) / 255.0, 0, 1)
out = Image.fromarray((img * 255).astype(np.uint8))

fs1 = int(S * 0.0135)
fs2 = int(S * 0.0085)
fsl = int(S * 0.0095)
f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", fs1)
f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fs2)
fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fsl)
dr = ImageDraw.Draw(out)
dr.text((int(0.065 * W), int(0.035 * H)), "THE LADDERS IN THE THIN SET",
        fill=(235, 208, 152), font=f1)
dr.text((int(0.065 * W), int(0.035 * H) + int(fs1 * 1.5)),
        "arithmetic progressions of consecutive sums of two squares (MO 513787)  ·  AP-obstruction atlas, piece 37",
        fill=(150, 152, 158), font=f2)
labels = ["l = 3 :  0, 1, 2   (gap 1) — where the set is still dense",
          "l = 4 :  757, 761, 765, 769   (gap 4 — the first ladder forced into the good sublattice)",
          "l = 5 :  2989 … 3005   (gap 4)",
          "l = 6 :  28,059,605 … 28,059,665   (gap 12) — nothing longer below 10⁹"]
for lab, fy in zip(labels, strip_ys):
    dr.text((int(0.065 * W), int((fy - 0.076) * H)), lab, fill=(168, 170, 176), font=fl)
dr.text((int(0.065 * W), int(0.726 * H)),
        "part (b): smallest k with 1, 1+k, …, 1+(l−1)k all sums of two squares — k = 1, 4, 12, 336; no k < 2×10⁶ reaches l = 17",
        fill=(168, 170, 176), font=fl)
kl = sorted(krec)
for i, L in enumerate(kl):
    x = x_lo + (i + 0.5) * bar_w
    dr.text((int(x - fs2 * 0.6), int(0.890 * H)), str(L), fill=(130, 132, 140), font=f2)
    if i == 0 or krec[L] != krec[kl[i - 1]]:
        tw = dr.textlength(str(krec[L]), font=f2)
        dr.text((int(x - tw / 2), int(0.760 * H)), str(krec[L]),
                fill=(210, 185, 130), font=f2)
dr.text((int(0.065 * W), int(0.938 * H)),
        "ground: the mod-8 loom — cold red columns are residues 3, 6, 7 mod 8, which no sum of two squares ever occupies",
        fill=(150, 152, 158), font=f2)
dr.text((int(0.065 * W), int(0.938 * H) + int(fs2 * 1.5)),
        "the ladder's step must preserve the norm-form residue at the ramified prime 2  ·  beads: members of S, brightness = log r₂(n)",
        fill=(150, 152, 158), font=f2)
out.save(f"twosq_{S}.png")
print("saved", f"twosq_{S}.png")
