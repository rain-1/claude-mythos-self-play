#!/usr/bin/env python3
"""THE PLUMB LINE (2560², companion to notes_514763.md, MO 514763).

Top register — the root curtain: all roots of H_1..H_400 (physicists'
Hermite), row n at height n; roots = eigenvalues of the Jacobi matrix
(off-diagonal sqrt(k/2)), certified against exact interlacing.  The gold
plumb line hangs at x = 1: by the mod-p gcd certificate (hermite.c) no two
curtain threads ever cross it at the same point — in fact no thread touches
it at all (H_n(1) != 0 checked exactly), yet the curtain crowds it forever.
The one shared vertical of the whole curtain is x = 0, lit as a cold pillar:
the root every odd H_n carries.

Bottom register — the miss: m(n) = sqrt(2n) * min_k |1 - x_k(n)|, the
normalized distance from the plumb line to the nearest root.  Bounded away
from zero-forever is the conjecture; the record-low so far is starred.
"""
import numpy as np, math, sys
import scipy.ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
from sympy import Poly, symbols, ZZ

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
SIZE = 1280 if PROTO else 2560
SS = 2
S = SIZE * SS
rs = S / 5120.0

NMAX = 400
# ---------------------------------------------------------------- roots
roots = []
prev = None
for n in range(1, NMAX + 1):
    b = np.sqrt(np.arange(1, n) / 2.0)
    J = np.diag(b, 1) + np.diag(b, -1)
    ev = np.linalg.eigvalsh(J) if n > 1 else np.array([0.0])
    ev.sort()
    if prev is not None and n > 1:
        # interlacing certificate: prev roots strictly between consecutive ev
        assert np.all(ev[:-1] < prev) and np.all(prev < ev[1:]), f"interlacing fails at n={n}"
    prev = ev
    roots.append(ev)
print(f"[plumb] {NMAX} root rows; interlacing certified for all consecutive pairs")

# exact check H_n(1) != 0 via integer recurrence (H_n(1) exact bigint)
h0, h1 = 1, 2
assert h1 != 0
for k in range(1, NMAX):
    h0, h1 = h1, 2 * h1 - 2 * k * h0
    assert h1 != 0, f"H_{k+1}(1) = 0 ?!"
print("[plumb] H_n(1) != 0 exactly for all n <= 400 (integer recurrence)")

miss = np.array([np.sqrt(2 * n) * np.min(np.abs(1.0 - r)) for n, r in enumerate(roots, 1)])
rec_n = int(np.argmin(miss)) + 1
print(f"[plumb] min normalized miss m(n): {miss.min():.6f} at n={rec_n}; max {miss.max():.4f}")

# ---------------------------------------------------------------- layout
XR = math.sqrt(2 * NMAX) * 1.04
def xpix(x): return S * (0.5 + 0.46 * x / XR)
CT, CB = 0.115 * S, 0.685 * S          # curtain band (n=1 top .. NMAX bottom)
def ypix(n): return CT + (n - 1) / (NMAX - 1) * (CB - CT)
MT, MB = 0.755 * S, 0.935 * S          # miss band

cold = np.zeros((S, S), np.float32)
warm = np.zeros((S, S), np.float32)
cy   = np.zeros((S, S), np.float32)

def splat_pts(buf, xs, ys, amp):
    x0 = np.floor(xs).astype(np.int64); y0 = np.floor(ys).astype(np.int64)
    fx = (xs - x0).astype(np.float32); fy = (ys - y0).astype(np.float32)
    fl = buf.ravel()
    a = np.broadcast_to(np.asarray(amp, np.float32), xs.shape)
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            xi = np.clip(x0 + dx, 0, S - 1); yi = np.clip(y0 + dy, 0, S - 1)
            np.add.at(fl, yi * S + xi, a * wx * wy)

# curtain: threads via dense row sampling (draw each root row as points; the
# vertical continuity comes from interlacing so points align into threads)
for n, r in enumerate(roots, 1):
    xs = xpix(r); ys = np.full(len(r), ypix(n))
    # subrow supersampling: 3 vertical jitters to fuse threads
    for dy in (-0.33, 0.0, 0.33):
        splat_pts(cold, xs, ys + dy * (CB - CT) / (NMAX - 1), 1.1)
    # nearest-to-1 root glows warm, brightness by closeness
    k = int(np.argmin(np.abs(r - 1.0)))
    closeness = 1.0 / (0.08 + abs(r[k] - 1.0) * math.sqrt(2 * n))
    for dy in (-0.33, 0.0, 0.33):
        splat_pts(warm, xs[k:k+1], np.array([ys[k] + dy * (CB - CT) / (NMAX - 1)]),
                  2.2 * min(closeness, 3.5))

# the shared pillar x=0 (root of every odd H_n): cold cyan pillar
ysp = np.arange(int(CT), int(CB))
splat_pts(cy, np.full(len(ysp), xpix(0.0)), ysp.astype(float), 0.55)
# the plumb line x=1: gold, hanging from above the curtain into the miss panel
ysg = np.arange(int(0.075 * S), int(MB))
splat_pts(warm, np.full(len(ysg), xpix(1.0)), ysg.astype(float), 0.30)

# ---------------------------------------------------------------- miss panel
mmax = miss.max() * 1.12
def ymiss(v): return MB - v / mmax * (MB - MT)
xs_n = np.array([xpix(-XR) + (n - 1) / (NMAX - 1) * (xpix(XR) - xpix(-XR)) for n in range(1, NMAX + 1)])
# floor line (the forbidden zero)
xfl = np.arange(int(xs_n[0]), int(xs_n[-1]))
splat_pts(cy, xfl.astype(float), np.full(len(xfl), ymiss(0.0)), 0.5)
# the miss polyline, in warm gold
for i in range(len(miss) - 1):
    x0_, x1_ = xs_n[i], xs_n[i + 1]
    y0_, y1_ = ymiss(miss[i]), ymiss(miss[i + 1])
    npts = max(int(abs(x1_ - x0_) / 0.7), 2)
    t = np.linspace(0, 1, npts)
    splat_pts(warm, x0_ + t * (x1_ - x0_), y0_ + t * (y1_ - y0_), 1.25)
# record star
splat_pts(warm, np.array([xs_n[rec_n - 1]]), np.array([ymiss(miss[rec_n - 1])]), 30.0)

# ---------------------------------------------------------------- compose
warmb = warm + 0.55 * ndi.gaussian_filter(warm, 6 * rs * SS)
cyb = cy + 0.5 * ndi.gaussian_filter(cy, 5 * rs * SS)
img = np.zeros((S, S, 3), np.float32)
img[..., 0] = 0.004; img[..., 1] = 0.005; img[..., 2] = 0.011
ICE = np.array([0.55, 0.68, 0.92]); GOLD = np.array([1.0, 0.78, 0.34]); CYC = np.array([0.36, 0.85, 0.88])
for c in range(3):
    img[..., c] += ICE[c] * (1 - np.exp(-0.75 * cold)) * 0.9
    img[..., c] += GOLD[c] * (1 - np.exp(-0.85 * warmb))
    img[..., c] += CYC[c] * (1 - np.exp(-0.8 * cyb)) * 0.9
img = np.clip(img, 0, 1) ** (1 / 2.2)
img8 = np.clip(img * 255 + np.random.uniform(-0.5, 0.5, img.shape), 0, 255).astype(np.uint8)
out = Image.fromarray(img8).resize((SIZE, SIZE), Image.LANCZOS)

# ---------------------------------------------------------------- text
dr = ImageDraw.Draw(out)
sc = SIZE / 2560
def font(sz, bold=False):
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf", int(sz))
    except Exception:
        return ImageFont.load_default()
ft, fm, fsm = font(58 * sc, True), font(27 * sc), font(22 * sc)
dr.text((int(0.045 * SIZE), int(0.022 * SIZE)), "THE PLUMB LINE", font=ft, fill=(228, 208, 164))
dr.text((int(0.045 * SIZE), int(0.022 * SIZE) + int(72 * sc)),
        "every root of every Hermite polynomial H₁..H₄₀₀  ·  MO 514763: can a fixed nonzero algebraic number be a root of infinitely many?",
        font=fsm, fill=(132, 128, 134))
dr.text((int(0.045 * SIZE), int(0.022 * SIZE) + int(102 * sc)),
        "certified (gcd mod p, all 124,750 pairs m<n≤500): the only shared vertical is x = 0, the cyan pillar — the gold plumb at x = 1 is crowded forever, touched never",
        font=fsm, fill=(132, 128, 134))
# labels
px1 = xpix(1.0) / S * SIZE
dr.text((px1 + 10 * sc, 0.085 * SIZE), "x = 1", font=fm, fill=(226, 190, 120))
px0 = xpix(0.0) / S * SIZE
dr.text((px0 + 10 * sc, 0.60 * SIZE), "x = 0 — the one shared root", font=fsm, fill=(120, 200, 205))
dr.text((int(0.045 * SIZE), (MT / S) * SIZE - int(34 * sc)),
        "the miss  ·  m(n) = √(2n) · dist(1, roots of Hₙ) — the normalized gap the plumb line keeps",
        font=fsm, fill=(132, 128, 134))
rx = xs_n[rec_n - 1] / S * SIZE
dr.text((min(rx + 12 * sc, SIZE - 300 * sc), (ymiss(miss[rec_n - 1]) / S) * SIZE - int(34 * sc)),
        f"record miss: m({rec_n}) = {miss.min():.4f} — a root of H_{rec_n} sits {miss.min()/math.sqrt(2*rec_n):.2e} from 1, and is not 1", font=fsm, fill=(240, 210, 150))
dr.text((int(0.045 * SIZE), 0.955 * SIZE),
        f"roots via Jacobi eigenvalues, interlacing certified n≤400  ·  Hₙ(1) ≠ 0 exactly (integer recurrence)  ·  min m(n) = {miss.min():.4f}, never 0",
        font=fsm, fill=(110, 108, 116))
for ntick in (100, 200, 300, 400):
    dr.text((int(0.030 * SIZE), (ypix(ntick) / S) * SIZE - int(10 * sc)), f"n={ntick}",
            font=fsm, fill=(86, 90, 102))
out.save("plumb_proto.png" if PROTO else "plumb_2560.png")
print("[plumb] wrote", "plumb_proto.png" if PROTO else "plumb_2560.png")
