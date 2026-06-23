"""
Piece 36b -- Prime Landscape of Z[sqrt(-2)] with a long arithmetic progression
==============================================================================
The companion to the Obstruction Atlas. We render the geometric embedding of
the prime-norm points of Z[sqrt(-2)]:  z = a + b*sqrt(-2)  ->  (a, b*sqrt(2)).
On top we draw the longest arithmetic progression of prime-norm points we can
find -- which, by the obstruction law, must use an EVEN rational step da.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SQRT2 = np.sqrt(2.0)


def sieve(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i*i::i] = False
    return s


# ---------- find a long AP (even da) ----------------------------------------
def find_long_ap(W=1500, R=10, kmax=24):
    aa, bb = np.mgrid[-W:W+1, -W:W+1]
    norm = aa*aa + 2*bb*bb
    NMAX = int(norm.max()); isp = sieve(NMAX)
    prime = (norm >= 2) & isp[np.clip(norm, 0, NMAX)]
    best = (0, None, None)
    for da in range(0, R+1, 2):                 # even da only (the good steps)
        for db in range(-R, R+1):
            if da == 0 and db <= 0:
                continue
            running = prime.copy(); wit = None
            for k in range(1, kmax):
                sh = np.roll(np.roll(prime, -k*da, 0), -k*db, 1)
                if k*da > 0: sh[-k*da:, :] = False
                if k*db > 0: sh[:, -k*db:] = False
                elif k*db < 0: sh[:, :-k*db] = False
                running = running & sh
                if not running.any():
                    break
                idx = np.argwhere(running)[0]
                wit = (idx[0]-W, idx[1]-W); L = k+1
            if wit is not None and L > best[0]:
                best = (L, wit, (da, db))
    return best


L, (a0, b0), (da, db) = find_long_ap()
print(f"longest AP found: {L} terms, start=({a0},{b0}), step=({da},{db})")
ap = [(a0 + k*da, b0 + k*db) for k in range(L)]
print("  terms (a,b | norm):", [(a, b, a*a+2*b*b) for a, b in ap])

# ---------- render the landscape --------------------------------------------
S = 2048
# choose view bounds around the AP, with margin
axs = [p[0] for p in ap]; bys = [p[1] for p in ap]
cx = (min(axs)+max(axs))/2; cy = (min(bys)+max(bys))/2
span = max(max(axs)-min(axs), (max(bys)-min(bys))) * 1.0 + 28
amin, amax = cx-span, cx+span
bmin, bmax = cy-span/SQRT2, cy+span/SQRT2     # keep aspect via sqrt2 stretch

A = int(np.ceil(max(abs(amin), abs(amax)))) + 2
B = int(np.ceil(max(abs(bmin), abs(bmax)))) + 2
aa, bb = np.mgrid[-A:A+1, -B:B+1]
norm = aa*aa + 2*bb*bb
NMAX = int(norm.max()); isp = sieve(NMAX)
prime_mask = (norm >= 2) & isp[np.clip(norm, 0, NMAX)]
pa = aa[prime_mask]; pb = bb[prime_mask]; pn = norm[prime_mask]

img = np.zeros((S, S, 3), np.float64)


def to_px(a, b):
    x = (a - amin) / (amax - amin) * (S - 1)
    y = (b*SQRT2 - bmin*SQRT2) / ((bmax - bmin) * SQRT2) * (S - 1)
    return x, S - 1 - y


def splat(cx, cy, rad, amp, color):
    x0, x1 = max(0, int(cx-3*rad)), min(S, int(cx+3*rad)+1)
    y0, y1 = max(0, int(cy-3*rad)), min(S, int(cy+3*rad)+1)
    if x1 <= x0 or y1 <= y0:
        return
    gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    g = amp * np.exp(-((gx-cx)**2 + (gy-cy)**2)/(2*rad*rad))
    for c in range(3):
        img[y0:y1, x0:x1, c] += g*color[c]


# background prime field: cool glow, hue from argument, brightness from 1/norm
for a, b, nrm in zip(pa, pb, pn):
    x, y = to_px(a, b)
    if -10 < x < S+10 and -10 < y < S+10:
        ang = np.arctan2(b*SQRT2, a)
        col = np.array([0.32+0.22*np.cos(ang), 0.58+0.30*np.cos(ang+2.0),
                        0.90+0.10*np.cos(ang+4.0)])
        splat(x, y, 2.7, 0.95*(7.0/nrm)**0.05, np.clip(col, 0, 1))

# the AP: golden rail + bright nodes
pts = [to_px(a, b) for a, b in ap]
for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
    steps = int(np.hypot(x2-x1, y2-y1)) + 1
    for t in np.linspace(0, 1, steps*2):
        splat(x1+(x2-x1)*t, y1+(y2-y1)*t, 1.6, 0.10, np.array([1.0, 0.72, 0.28]))
for (x, y), (a, b) in zip(pts, ap):
    splat(x, y, 6.5, 1.3, np.array([1.0, 0.86, 0.55]))
    splat(x, y, 2.6, 1.6, np.array([1.0, 0.99, 0.92]))

# tone map
img = 1.0 - np.exp(-1.8*img)
img = np.clip(img, 0, 1) ** (1/1.8)
out = (img*255 + 0.5).astype(np.uint8)
pim = Image.fromarray(out, "RGB")

# caption
d = ImageDraw.Draw(pim)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    fsm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
except Exception:
    font = ImageFont.load_default(); fsm = font
d.text((28, 24), "Z[√-2]  prime landscape", fill=(235, 235, 245), font=font)
d.text((28, 64), f"{L}-term AP  start ({a0},{b0})  step ({da},{db})  —  even da, as the obstruction law requires",
        fill=(255, 205, 130), font=fsm)
pim.save("out/36b_sqrt2_landscape.png")
print("wrote out/36b_sqrt2_landscape.png")
