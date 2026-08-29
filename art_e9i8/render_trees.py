#!/usr/bin/env python3
"""THE MIRROR AND THE DESERT — MO 514744 panel (2560²).

The (m,n) plane of grid graphs, 2..200 each axis.  Every cell asked one
question — is your spanning-tree count T(m,n) a perfect square? — and
interrogated by 48 primes.  Luminance = how long the cell survived
(first non-residue witness index): the off-diagonal desert dies young,
by luck alone (geometric speckle).  On the mirror line m=n the law
T(n,n)·n = 2^(n-1)·Q² decides instead: gold stars where n is an odd
square or twice a square — squares by necessity, forever.
Usage: render_trees.py SIZE SS OUT
"""
import sys, math
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom
from PIL import Image, ImageDraw, ImageFont

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
SS = int(sys.argv[2]) if len(sys.argv) > 2 else 1
OUT = sys.argv[3] if len(sys.argv) > 3 else "trees_proto.png"
S = SIZE * SS
rs = S / 2560.0

N = 200
W = np.full((N + 1, N + 1), -1, np.int32)
NZ = np.zeros((N + 1, N + 1), np.int32)
for line in open("trees200.txt"):
    if line.startswith("W "):
        _, m, n, w, nz = line.split()
        m, n, w = int(m), int(n), int(w)
        W[m, n] = w; W[n, m] = w
        NZ[m, n] = NZ[n, m] = int(nz)
surv = [(m, n) for m in range(2, N + 1) for n in range(m, N + 1)
        if W[m, n] == 0]
magic = sorted(m for m, n in surv)

# ---- canvas ----
img = np.zeros((S, S, 3), np.float32)
M0 = 0.085 * S          # carpet origin (left/top margins)
M1 = 0.075 * S          # right margin
LEDGE = 0.145 * S       # bottom ledger band
CW = S - M0 - M1        # carpet width
CH = S - M0 - LEDGE - 0.06 * S
cs = min(CW, CH) / (N - 1)
ox, oy = M0, 0.115 * S

def cell_px(m, n):       # m -> x, n -> y (y down = larger n)
    return ox + (m - 2) * cs, oy + (n - 2) * cs

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

COLD = np.array([0.36, 0.62, 0.95])
COLD2 = np.array([0.55, 0.85, 1.05])
GOLD = (1.00, 0.74, 0.28)
STAR = (1.00, 0.95, 0.82)
SPINE = (0.95, 0.72, 0.30)

# ---- carpet as a field (vectorized) ----
# grid of cell centers -> paint into a (N-1)x(N-1) small image, then upsample
small = np.zeros((N - 1, N - 1, 3), np.float32)
for m in range(2, N + 1):
    for n in range(2, N + 1):
        w = W[m, n]
        if w == 0:
            continue                      # survivors drawn as stars later
        # survival time: 1..48 -> luminance, steep so the desert stays dark
        u = math.log(1 + w) / math.log(49)
        L = 0.018 + 1.05 * u ** 3.3
        col = COLD * (1 - 0.5 * u) + COLD2 * (0.5 * u)
        small[n - 2, m - 2] = L * col
# upsample to carpet px with smooth grain
up = int(math.ceil(cs))
big = ndzoom(small, ((N - 1) * cs / small.shape[0] / 1.0,
                     (N - 1) * cs / small.shape[1] / 1.0, 1), order=0)
big = gaussian_filter(big, (0.14 * cs, 0.14 * cs, 0))
big = np.clip(big, 0, None)
h, w_ = big.shape[:2]
y0i, x0i = int(oy), int(ox)
img[y0i:y0i + h, x0i:x0i + w_, :] += big * 0.9

# rare long-lived sparks get true glow
for m in range(2, N + 1):
    for n in range(2, N + 1):
        w = W[m, n]
        if w >= 9:
            px, py = cell_px(m, n)
            u = math.log(1 + w) / math.log(49)
            splat(px, py, 1.1 * cs, (0.75, 0.92, 1.0), 0.5 * u)

# mirror spine
for m in range(2, N + 1):
    px, py = cell_px(m, m)
    splat(px, py, 0.55 * cs, SPINE, 0.10)

# survivors: gold stars
for m, n in surv:
    px, py = cell_px(m, m)
    splat(px, py, 1.6 * cs, GOLD, 0.9)
    splat(px, py, 0.55 * cs, STAR, 2.0)
    splat(px, py, 4.5 * cs, GOLD, 0.12)

# ---- bloom ----
lum = img.sum(axis=2)
thr = np.percentile(lum[lum > 0], 99.3) / 2.0
hi = np.maximum(img - thr / 3.0, 0)
ds = 4
blo = ndzoom(ndzoom(hi, (1 / ds, 1 / ds, 1), order=1), (ds, ds, 1),
             order=1)[:S, :S]
blo = gaussian_filter(blo, (6 * rs, 6 * rs, 0))
img += 0.5 * blo
del hi, blo, lum

# ---- tone map ----
BG = np.array([0.010, 0.013, 0.026], np.float32)
img += BG[None, None, :]
out = 1.0 - np.exp(-1.6 * img)
out = np.power(np.clip(out, 0, 1), 1 / 1.8)
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

k = SIZE / S
txt(40 * fs, 30 * fs, "THE MIRROR AND THE DESERT", 46 * fs, (235, 238, 245), bold=True)
txt(40 * fs, 88 * fs,
    "T(m,n) = spanning trees of the m×n grid.  Is it ever a perfect square?  "
    "Brightness = how many prime interrogations the cell survived.", 24 * fs, (168, 176, 192))
txt(40 * fs, 122 * fs,
    "Off the mirror: luck only — every one of 19,884 cells dies (geometric speckle).  "
    "On the mirror m=n: the law T·n = 2ⁿ⁻¹Q² decides.", 24 * fs, (168, 176, 192))
# magic labels along diagonal
side = 1
for m in magic:
    px, py = cell_px(m, m)
    px *= k; py *= k
    off = 26 * fs
    txt(px + off * (1 if side > 0 else -0.6) * (1 if m > 6 else 2.4),
        py - off * side * 0.8 - 6 * fs, str(m), 24 * fs, (255, 215, 130),
        bold=True, anchor="lm" if side > 0 else "rm")
    side = -side
# axes ticks
for v in (50, 100, 150, 200):
    px, py = cell_px(v, 2); txt(px * k, oy * k - 18 * fs, str(v), 20 * fs, (110, 118, 135), mono=True, anchor="mm")
    px, py = cell_px(2, v); txt((ox * k - 26 * fs), py * k, str(v), 20 * fs, (110, 118, 135), mono=True, anchor="rm")
txt((ox + (N - 2) * cs * 0.82) * k, oy * k - 44 * fs, "m →", 20 * fs, (110, 118, 135), mono=True, anchor="mm")

# ledger band
ly = SIZE - LEDGE * k + 10 * fs
txt(40 * fs, ly,
    "THE LAW (proved):  T(n,n)·n = 2ⁿ⁻¹·Q²  ⇒  T(n,n) is a square  ⟺  n·2ⁿ⁻¹ is a square  ⟺  "
    "n ∈ {odd squares} ∪ {2·squares}", 26 * fs, (255, 205, 110))
txt(40 * fs, ly + 40 * fs,
    "gold stars: n = 2, 8, 9, 18, 25, 32, 49, 50, 72, 81, 98, 121, 128, 162, 169, 200 — "
    "squares by necessity, all n, forever  (exact-integer certificates to n = 128)",
    22 * fs, (190, 198, 214))
txt(40 * fs, ly + 76 * fs,
    "THE DESERT (measured):  if off-mirror squareness is luck, the expected number of squares "
    "with max(m,n) > 81 is 1.4×10⁻²³;  beyond this census (200), 1.3×10⁻⁵⁷.", 22 * fs, (150, 158, 175))
txt(40 * fs, ly + 112 * fs,
    "48 primes ≈ 10³, verdicts by T mod p = Res(q_m, f_n)·m⁻¹;  engine validated "
    "against exact T for all m ≤ n ≤ 12  ·  MO 514744, census 2 ≤ m ≤ n ≤ 200",
    20 * fs, (120, 128, 145))
im.save(OUT)
print("wrote", OUT)
