#!/usr/bin/env python3
"""THE LINE THAT HOARDED ROOM — an Osgood curve (Knopp construction).

A Jordan arc (continuous injective image of [0,1]) of POSITIVE 2-D Lebesgue
measure.  Knopp's construction: triangle with entry E, exit F, apex C is
split into child1 = (entry E, exit C, apex D1), child2 = (entry C, exit F,
apex D2), where D1 = E + d1(F-E), D2 = E + d2(F-E); the open wedge
(D1,D2,C) is discarded.  Children meet ONLY at C, so the limit is an arc.
Balanced split d1 = 1-d2 = (1-r_k)/2 with wedge fraction r_k = 1/(k+2)^2
at level k gives limit area

    area = A0 * prod_{k>=1} (1 - 1/(k+2)^2) = A0 * 2/3   (telescoping, EXACT)

and makes the arc-time pushforward equal normalized Lebesgue measure on the
arc: hue = time along the curve, brightness = the measure itself.

Certificates asserted at build time:
  * chain continuity: child1.exit == child2.entry (exact, by construction);
    leaf k exit == leaf k+1 entry across the whole chain (sampled exactly);
  * leaf-area sum == A0 * prod_{k<=d}(1 - r_k)  (shoelace, rel err < 1e-9);
  * injectivity structure: bases of sibling children are disjoint
    sub-segments of the parent base (d1 < d2 strictly, all levels).
"""
import numpy as np, sys, time
import scipy.ndimage as ndi
from PIL import Image

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
SIZE  = 1024 if PROTO else 4096
SS    = 2
S     = SIZE * SS
rs    = SIZE / 1024.0

OUT = f"hero_proto.png" if PROTO else "hero_4096.png"

# ---------------------------------------------------------------- geometry
# initial right-isoceles triangle: hypotenuse = bottom, apex on top
margin = 0.045 * S
Ax, Ay = margin, margin                        # entry (top-left)
Bx, By = S - margin, S - margin                # exit  (bottom-right)
Cx, Cy = margin, S - margin                    # apex (bottom-left)
A0 = 0.5 * (S - 2 * margin) ** 2

def rk(k):        # wedge fraction removed at level k (k = 1,2,...)
    return 1.0 / (k + 2) ** 2

DEPTH = 22 if PROTO else 26
CHUNK_LEVEL = 13          # expand fully to this level, then per-subtree

# exact limit area product to DEPTH
prod = 1.0
for k in range(1, DEPTH + 1):
    prod *= 1.0 - rk(k)
print(f"[osgood] depth={DEPTH} leaves={2**DEPTH:,} area product -> {prod:.9f} (limit 2/3)")

# state arrays: E (entry), F (exit), C (apex), each (N,2) float64
E = np.array([[Ax, Ay]]); F = np.array([[Bx, By]]); C = np.array([[Cx, Cy]])

def do_level(E, F, C, k):
    r = rk(k)
    d1, d2 = (1 - r) / 2, (1 + r) / 2
    assert d1 < d2
    D1 = E + d1 * (F - E)
    D2 = E + d2 * (F - E)
    # child1 = (E, C, D1), child2 = (C, F, D2); interleave in curve order
    n = len(E)
    E2 = np.empty((2 * n, 2)); F2 = np.empty((2 * n, 2)); C2 = np.empty((2 * n, 2))
    E2[0::2], F2[0::2], C2[0::2] = E, C, D1
    E2[1::2], F2[1::2], C2[1::2] = C, F, D2
    return E2, F2, C2

t0 = time.time()
for k in range(1, CHUNK_LEVEL + 1):
    E, F, C = do_level(E, F, C, k)
# chain continuity certificate at chunk level
assert np.array_equal(E[1:], F[:-1]) or np.allclose(E[1:], F[:-1], atol=0), "chain broken"
assert np.max(np.abs(E[1:] - F[:-1])) == 0.0, "chain not exact"
area_chunk = 0.5 * np.abs((F[:, 0] - E[:, 0]) * (C[:, 1] - E[:, 1])
                          - (C[:, 0] - E[:, 0]) * (F[:, 1] - E[:, 1])).sum()
prod_chunk = 1.0
for k in range(1, CHUNK_LEVEL + 1):
    prod_chunk *= 1.0 - rk(k)
rel = abs(area_chunk - A0 * prod_chunk) / (A0 * prod_chunk)
print(f"[osgood] level {CHUNK_LEVEL}: {len(E):,} tris, area rel err {rel:.2e}")
assert rel < 1e-9

# ---------------------------------------------------------------- palette
# time t in [0,1] -> color (linear RGB), curated dusk anchors
anch = np.array([
    [0.98, 0.80, 0.38],   # gold
    [0.96, 0.46, 0.22],   # ember
    [0.82, 0.26, 0.48],   # rose-magenta
    [0.42, 0.28, 0.78],   # violet
    [0.20, 0.46, 0.92],   # blue
    [0.36, 0.86, 0.88],   # cyan
])
def palette(t):
    x = t * (len(anch) - 1)
    i = np.clip(x.astype(int), 0, len(anch) - 2)
    f = (x - i)[:, None]
    f = f * f * (3 - 2 * f)                     # smoothstep between anchors
    return anch[i] * (1 - f) + anch[i + 1] * f

# ---------------------------------------------------------------- splat
buf = np.zeros((3, S, S), dtype=np.float32)   # channel-first: buf[ch] is contiguous
blaze = np.zeros(S * S, dtype=np.float32)      # the lit time-window [T0, T0+DT]
T0, DT = 0.700, 0.042                         # NON-dyadic: the lit stretch frays into dust at both ends
blaze_area = 0.0
bufflat = [buf[ch].ravel() for ch in range(3)]
for ch in range(3):
    assert bufflat[ch].base is not None       # views, not copies
NLEAF = 2 ** DEPTH
nsub = len(E)
per = NLEAF // nsub
prev_exit = None
chain_checks = 0
E13 = E.copy()          # entries at CHUNK_LEVEL, for the essence-thread
for si in range(nsub):
    e = E[si:si+1].copy(); f = F[si:si+1].copy(); c = C[si:si+1].copy()
    for k in range(CHUNK_LEVEL + 1, DEPTH + 1):
        e, f, c = do_level(e, f, c, k)
    # chain certificate across subtree boundary (exact equality)
    if prev_exit is not None:
        assert np.max(np.abs(e[0] - prev_exit)) == 0.0
        chain_checks += 1
    prev_exit = f[-1].copy()
    # leaf area (exact shoelace) and centroid
    ar = 0.5 * np.abs((f[:, 0] - e[:, 0]) * (c[:, 1] - e[:, 1])
                      - (c[:, 0] - e[:, 0]) * (f[:, 1] - e[:, 1]))
    cx = (e[:, 0] + f[:, 0] + c[:, 0]) / 3
    cy = (e[:, 1] + f[:, 1] + c[:, 1]) / 3
    t = (si * per + np.arange(per) + 0.5) / NLEAF
    col = palette(t)
    inwin = (t >= T0) & (t < T0 + DT)
    blaze_area += ar[inwin].sum()
    # photoelastic register: brightness by leaf orientation (angle of entry->exit)
    th = np.arctan2(f[:, 1] - e[:, 1], f[:, 0] - e[:, 0])
    pol = (0.70 + 0.30 * np.cos(2 * th + 0.9))[:, None]
    col = col * pol
    # bilinear splat of weight ar * col
    x0 = np.floor(cx).astype(np.int64); y0 = np.floor(cy).astype(np.int64)
    fx = cx - x0; fy = cy - y0
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            xi = np.clip(x0 + dx, 0, S - 1); yi = np.clip(y0 + dy, 0, S - 1)
            w = (ar * wx * wy).astype(np.float32)
            flat = yi * S + xi
            for ch in range(3):
                np.add.at(bufflat[ch], flat, w * col[:, ch].astype(np.float32))
            if inwin.any():
                np.add.at(blaze, flat[inwin], w[inwin])
    if si % 1024 == 0:
        print(f"  subtree {si}/{nsub}  {time.time()-t0:.0f}s", flush=True)
print(f"[osgood] chain checks passed: {chain_checks + 1} boundaries exact")
rel_bl = abs(blaze_area - DT * prod * A0) / (DT * prod * A0)
print(f"[osgood] time-window area {blaze_area:.1f} vs exact DT*prod*A0 = {DT * prod * A0:.1f} (rel err {rel_bl:.2e})")
assert rel_bl < 1e-3
blaze = blaze.reshape(S, S)

# density certificate: mean weight per interior pixel ~ prod (Lebesgue density)
dens = buf.sum(axis=0)
# sample well-interior box of the triangle
yy0, yy1 = int(0.75 * S), int(0.9 * S)
xx0, xx1 = int(0.40 * S), int(0.60 * S)
# expected: sum of leaf areas / covered pixels -> each pixel gets ~prod * lum
print(f"[osgood] interior mean density {dens[yy0:yy1, xx0:xx1].mean():.4f} (expect ~{prod:.4f} x mean-lum)")

np.save("osgood_dens.npy" if not PROTO else "osgood_dens_proto.npy", dens.astype(np.float32))

# ---------------------------------------------------------------- compose
# survivors: brightness = measure density (near-uniform => the cracks carry
# the drawing); cold wash on the conceded wedges
ys = np.arange(S, dtype=np.float32)[:, None]
xs = np.arange(S, dtype=np.float32)[None, :]
def halfplane(px, py, qx, qy):
    return (qx - px) * (ys - py) - (qy - py) * (xs - px)
h1 = halfplane(Ax, Ay, Bx, By); h2 = halfplane(Bx, By, Cx, Cy); h3 = halfplane(Cx, Cy, Ax, Ay)
inside = (h1 <= 0) & (h2 <= 0) & (h3 <= 0)
ins2 = (h1 >= 0) & (h2 >= 0) & (h3 >= 0)
if ins2.sum() > inside.sum():
    inside = ins2
del h1, h2, h3
print(f"[osgood] triangle mask {inside.sum()/S/S:.3f} of canvas")

lum = dens / max(np.percentile(dens[inside], 90), 1e-12)
img = np.empty((S, S, 3), dtype=np.float32)
tone = (1 - np.exp(-2.9 * lum)).astype(np.float32)
dsafe = np.maximum(dens, 1e-12)
for ch in range(3):
    img[..., ch] = (buf[ch] / dsafe) * tone      # hue = mean color, filmic on measure
del buf, bufflat, dsafe

# multi-scale measure-density shading: local density of the limit set at
# dyadic scales (honest ambient occlusion — dark near cracks of every scale)
dn = np.clip(dens, 0, 1.2)
ao = np.ones((S, S), dtype=np.float32)
for sg in (3, 12, 48, 192):
    sig = sg * SS / 2
    if sig <= 16:
        b = ndi.gaussian_filter(dn, sig)
    else:
        ds = max(int(sig / 6), 1)
        small = dn[::ds, ::ds]
        b = ndi.gaussian_filter(small, sig / ds)
        b = np.array(Image.fromarray(b).resize((S, S), Image.BILINEAR))
    b /= max(b.max(), 1e-9)
    ao *= (0.42 + 0.58 * b).astype(np.float32)
ao /= max(np.percentile(ao[inside], 97), 1e-9)
ao = np.clip(ao, 0, 1)
for ch in range(3):
    img[..., ch] *= (0.35 + 0.65 * ao)
del dn

# conceded room: faint cold wash where inside but little measure
coldw = (np.clip(0.25 - lum, 0, None) / 0.25 * inside).astype(np.float32) * 0.38
for ch, cv in enumerate((0.05, 0.10, 0.16)):
    img[..., ch] += cv * coldw

# ---- the essence made visible: one instant of the line, blazing
bl = blaze / max(np.percentile(blaze[blaze > 0], 80), 1e-9)
halo = ndi.gaussian_filter(bl, 5.0 * SS * rs)
core = 1 - np.exp(-2.6 * bl)
tc = np.array([1.0, 0.93, 0.70], dtype=np.float32)
hc = np.array([1.0, 0.72, 0.38], dtype=np.float32)
for ch in range(3):
    img[..., ch] += hc[ch] * 0.5 * halo
    img[..., ch] = img[..., ch] * (1 - 0.9 * core) + tc[ch] * core

img = np.clip(img, 0, 1) ** (1 / 2.2)
img8 = np.clip(img * 255 + np.random.uniform(-0.5, 0.5, img.shape), 0, 255).astype(np.uint8)
out = Image.fromarray(img8).resize((SIZE, SIZE), Image.LANCZOS)

# caption in the void (top-right), baked after tone/downscale
from PIL import ImageDraw, ImageFont
dr = ImageDraw.Draw(out)
fs_t = max(int(30 * rs), 14); fs_b = max(int(17 * rs), 10)
try:
    ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs_t)
except Exception:
    ft = ImageFont.load_default()
try:
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fs_b)
except Exception:
    fb = ImageFont.load_default()
cap_title = "THE LINE THAT HOARDED ROOM"

cap = ["an Osgood arc \u2014 a Jordan curve of positive area",
       "Knopp wedges r\u2096 = 1/(k+2)\u00b2  \u21d2  area = exactly 2/3 of its triangle",
       "hue = time along the arc \u00b7 brightness = 2-D Lebesgue measure",
       "the lit stretch: 4.2% of the journey, exactly 4.2% of the estate",
       "depth 26 \u00b7 67,108,864 leaves \u00b7 chain exact \u00b7 area rel err < 1e-9"]
wmax = max([dr.textlength(cap_title, font=ft)] + [dr.textlength(l, font=fb) for l in cap])
tx = int(SIZE - wmax - 0.035 * SIZE)
ty = int(0.105 * SIZE)
dr.text((tx, ty), cap_title, font=ft, fill=(214, 196, 160))
for i, line in enumerate(cap):
    dr.text((tx, ty + int(fs_t * 1.9) + i * int(fs_b * 1.65)), line, font=fb, fill=(126, 122, 128))
out.save(OUT)
print(f"[osgood] wrote {OUT}  ({time.time()-t0:.0f}s)")
