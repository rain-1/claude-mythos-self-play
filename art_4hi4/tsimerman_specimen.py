"""Specimen card: THE MEETING OF -67 AND -163 (study for the Ceiling).

Both discriminants have class number one, so their Hilbert class polynomials
are linear and the resultant is literally the difference of two legendary
integers:  j((1+sqrt(-67))/2) = -5280^3  and  j((1+sqrt(-163))/2) = -640320^3
(the j-value behind Ramanujan's constant e^(pi sqrt 163)).

Gross-Zagier: every prime factor of their difference is at most
67*163/4 = 2730.  The card shows the complete factorization -- an 18-digit
integer built entirely from primes you could check by hand.
"""
import numpy as np
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import filmic, bloom
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))

j67 = -5280 ** 3
j163 = -640320 ** 3
diff = j67 - j163          # positive: -5280^3 + 640320^3
assert diff == 640320 ** 3 - 5280 ** 3

# factor by trial division with primes <= 2730 (the GZ ceiling)
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if s[p]:
            s[p * p::p] = False
    return np.nonzero(s)[0]

ceil = 67 * 163 // 4
n = diff
fac = []
for p in [int(x) for x in primes_upto(ceil)]:
    m = 0
    while n % p == 0:
        n //= p; m += 1
    if m:
        fac.append((p, m))
assert n == 1, f"cofactor {n} - GZ violated?!"
fs = " · ".join((f"{p}" if m == 1 else f"{p}^{m}") for p, m in fac)
print("diff =", diff)
print("factorization:", fs)
maxp = max(p for p, m in fac)

# ---------------------------------------------------------------- the card
W, H = 2048, 930
img = Image.new("RGB", (W, H), (7, 10, 13))
dr = ImageDraw.Draw(img)

def font(sz, mono=False, bold=False):
    try:
        if mono:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", sz)
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sz)
    except OSError:
        return ImageFont.load_default()

GOLD = (232, 180, 90)
TEAL = (110, 185, 190)
FG = (208, 216, 214)
DIM = (120, 132, 130)

y = 90
dr.text((W // 2, y), "THE MEETING OF −67 AND −163", font=font(64, bold=True),
        fill=GOLD, anchor="mm")
y += 74
dr.text((W // 2, y), "a specimen for Jacob Tsimerman — Gross–Zagier on two class-number-one moduli",
        font=font(30), fill=DIM, anchor="mm")
y += 96
dr.text((W // 2, y), "j((1+√−67)/2) = −5280³        j((1+√−163)/2) = −640320³",
        font=font(44, mono=True), fill=TEAL, anchor="mm")
y += 86
dr.text((W // 2, y), "their difference:", font=font(32), fill=DIM, anchor="mm")
y += 62
dr.text((W // 2, y), f"{diff:,}", font=font(52, mono=True), fill=FG, anchor="mm")
y += 60
dr.text((W // 2, y), f"({len(str(diff))} digits)", font=font(26), fill=DIM, anchor="mm")
y += 90
dr.text((W // 2, y), "factors completely as", font=font(32), fill=DIM, anchor="mm")
y += 70
dr.text((W // 2, y), fs, font=font(46, mono=True), fill=GOLD, anchor="mm")
y += 96
dr.text((W // 2, y), f"every prime ≤ the Gross–Zagier ceiling  ⌊67·163/4⌋ = {ceil}   (largest used: {maxp})",
        font=font(34), fill=TEAL, anchor="mm")
y += 78
dr.text((W // 2, y), "two transcendental-looking numbers, permitted to meet only in small primes",
        font=font(30), fill=DIM, anchor="mm")

# frame
dr.rectangle([46, 46, W - 46, H - 46], outline=(60, 72, 76), width=2)
dr.rectangle([54, 54, W - 54, H - 54], outline=(35, 44, 48), width=1)

arr = np.asarray(img).astype(np.float64) / 255.0
glow = np.stack([gaussian_filter(arr[..., c], 6.0) for c in range(3)], -1)
out = np.clip(arr + 0.35 * glow, 0, 1)
Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(
    os.path.join(HERE, "specimen_67_163.png"))
print("saved specimen_67_163.png")
