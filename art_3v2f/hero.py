"""HERO — The Flame That Spells an Integer  (j on the log-polar q-disk)

Chart: horizontal = arg q in [0, 2pi), vertical = v = ln(-ln|q|), so the whole
punctured q-disk becomes a strip: the cusp q=0 is the open sky above, the unit
circle |q|=1 is the burning floor below.  Per pixel we Gauss-reduce tau into the
SL2(Z) fundamental domain (vectorized), evaluate j exactly there by its q-series
(coefficients computed exactly from E4^3/Delta), and paint:
  - flames: brightness = nearness of the reduced point to a cusp copy (Im tau_red)
  - skeleton: cyan glow where j is REAL = the edges of the modular tessellation
  - the Heegner meridian arg q = pi: seven rungs d=3,7,11,19,43,67,163 where the
    flame goes integer-quiet (j = exact integers, verified in-render), plus
    d=4,8 on the wrap-around meridian arg q = 0.
"""
import numpy as np, math, time, sys
from scipy.ndimage import gaussian_filter
import kit

PROTO = "--proto" in sys.argv
S = 1024 if PROTO else 4096
SS = 1 if PROTO else 2
W = H = S * SS
rs = (S * SS) / 1024.0

t0 = time.time()

# ---------------- exact j coefficients (same engine as verify_163.py) ----------
NT = 34
def poly_mul(a, b, N):
    out = [0] * N
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if i + j >= N: break
                out[i + j] += ai * bj
    return out
euler = [0] * NT
k = 0
while True:
    g1, g2 = k * (3 * k - 1) // 2, k * (3 * k + 1) // 2
    if g1 >= NT and g2 >= NT and k > 0: break
    s = 1 if k % 2 == 0 else -1
    if g1 < NT: euler[g1] += s
    if g2 < NT and k > 0: euler[g2] += s
    k += 1
e24 = euler
for _ in range(0):
    pass
e2 = poly_mul(euler, euler, NT); e4 = poly_mul(e2, e2, NT)
e8 = poly_mul(e4, e4, NT); e16 = poly_mul(e8, e8, NT)
e24 = poly_mul(e16, e8, NT)
sig3 = [0] * NT
for n in range(1, NT):
    for m in range(n, NT, n): sig3[m] += n ** 3
E4 = [1] + [240 * sig3[n] for n in range(1, NT)]
E43 = poly_mul(poly_mul(E4, E4, NT), E4, NT)
jq = [0] * NT
for n in range(NT):
    acc = E43[n] - sum(e24[kk] * jq[n - kk] for kk in range(1, n + 1))
    jq[n] = acc // e24[0]
assert jq[0] == 1 and jq[1] == 744 and jq[2] == 196884 and jq[3] == 21493760
CO = np.array(jq, dtype=np.float64)          # j*q = sum CO[n] q^n

def j_of_q(qc):
    """j at complex q (|q| small, reduced); Horner on j*q then /q."""
    acc = np.zeros_like(qc)
    for cn in CO[::-1]:
        acc = acc * qc + cn
    return acc / qc

# ---------------- verification: reduction + rung integers ----------------------
def reduce_tau(x, y, itmax=400):
    ninv = np.zeros(x.shape, np.int16)
    for _ in range(itmax):
        x -= np.round(x)
        r2 = x * x + y * y
        m = r2 < 1.0 - 1e-12
        if not m.any(): break
        inv = 1.0 / r2[m]
        x[m] = -x[m] * inv
        y[m] = y[m] * inv
        ninv[m] += 1
    x -= np.round(x)
    return x, y, ninv

rng = np.random.default_rng(163)
xs = rng.uniform(-2, 2, 400); ys = rng.uniform(0.5, 0.9, 400)
jd = j_of_q(np.exp(2j * np.pi * (xs + 1j * ys)))
xr, yr, _ = reduce_tau(xs.copy(), ys.copy())
jr = j_of_q(np.exp(2j * np.pi * (xr + 1j * yr)))
err = np.abs(jd - jr) / (1 + np.abs(jd))
assert err.max() < 1e-9, err.max()
print(f"reduction invariance check: max rel err {err.max():.2e}")

HEEGNER = [(3, 0), (7, -3375), (11, -32768), (19, -884736),
           (43, -884736000), (67, -147197952000), (163, -262537412640768000)]
HEEGNER_EDGE = [(4, 1728), (8, 8000)]
for d, jint in HEEGNER + HEEGNER_EDGE:
    thet = np.pi if d % 4 == 3 else 0.0
    u = np.pi * math.sqrt(d)
    qc = np.array([np.exp(1j * thet - u)])
    jv = j_of_q(qc)[0].real
    rel = abs(jv - jint) / max(abs(jint), 1.0)
    assert rel < 1e-11, (d, jv, jint)
print("rung integers verified in float64 (rel < 1e-11)")

# ---------------- field computation --------------------------------------------
VMIN, VMAX = -3.35, 3.88
def v_to_row(v):  # v = ln u -> pixel row (0 top)
    return (VMAX - v) / (VMAX - VMIN) * (H - 1)
def row_to_u(rows):
    v = VMAX - rows / (H - 1) * (VMAX - VMIN)
    return np.exp(v)

theta = (np.arange(W) + 0.5) / W * 2 * np.pi          # 0..2pi, pi at center
YRED = np.zeros((H, W), np.float32)
NINV = np.zeros((H, W), np.int16)
LOGJ = np.zeros((H, W), np.float32)
REAL = np.zeros((H, W), np.float32)                    # |sin arg j| (realness->0)

BAND = 256 * SS
for r0 in range(0, H, BAND):
    r1 = min(H, r0 + BAND)
    rows = np.arange(r0, r1)[:, None] + 0.0
    u = row_to_u(rows)                                  # (h,1)
    y = np.broadcast_to(u / (2 * np.pi), (r1 - r0, W)).astype(np.float64).copy()
    x = np.broadcast_to(theta / (2 * np.pi), (r1 - r0, W)).astype(np.float64).copy()
    if u.min() < 2 * np.pi:                             # only these need reduction
        x, y, ninv = reduce_tau(x, y)
    else:
        ninv = np.zeros(x.shape, np.int16)
    ured = 2 * np.pi * y
    big = ured > 60.0
    qc = np.exp(2j * np.pi * x - np.clip(ured, 0, 60))
    jv = j_of_q(qc)
    aj = np.abs(jv)
    logj = np.where(big, ured, np.log(np.maximum(aj, 1e-30)))
    realness = np.abs(jv.imag) / np.maximum(aj, 1e-30)
    realness[big] = np.abs(np.sin(2 * np.pi * x[big]))  # arg j ~ -arg q for huge j
    YRED[r0:r1] = y
    NINV[r0:r1] = ninv
    LOGJ[r0:r1] = logj
    REAL[r0:r1] = realness
    print(f"band {r0:>5}-{r1:<5} u=[{u.min():.3f},{u.max():.3f}] "
          f"maxninv={ninv.max()} {time.time()-t0:.0f}s", flush=True)

# ---------------- paint ---------------------------------------------------------
buf = np.zeros((H, W, 3), np.float32)

# (1) flame layer: heat = nearness of reduced point to a cusp copy
storm = NINV > 0
heat = np.clip(np.log(np.maximum(YRED / (math.sqrt(3) / 2), 1e-9)) / math.log(30.0), 0, 1)
FLAME_STOPS = [(0.00, (0.16, 0.035, 0.06)), (0.30, (0.55, 0.12, 0.06)),
               (0.55, (0.92, 0.38, 0.10)), (0.80, (1.00, 0.72, 0.25)),
               (1.00, (1.00, 0.96, 0.72))]
fl_col = kit.ramp(heat, FLAME_STOPS)
Lfl = (0.05 + 1.9 * heat ** 1.25) * storm            # faint garnet base inside tiles
buf += fl_col * Lfl[..., None]

# (2) ambient: one continuous vertical gradient, black at the crown, faint indigo sky
uu = np.broadcast_to(row_to_u(np.arange(H)[:, None] + 0.0), (H, W))
amb = np.clip((np.log(np.maximum(uu, 1e-9)) - math.log(5.4)) / (math.log(60) - math.log(5.4)), 0, 1)
AMB_COL = np.array([0.030, 0.028, 0.085], np.float32)
buf += (amb ** 2.2)[..., None] * AMB_COL[None, None, :]

# (3) skeleton: cyan glow where j is real; aerial perspective = dim with tile depth
sk = np.exp(-(REAL / 0.10) ** 2).astype(np.float32)
persp = 1.0 / (1.0 + 0.45 * np.clip(NINV - 1, 0, None))
sk_w = sk * persp * (0.20 + 0.80 * np.clip(1.0 - 1.4 * heat, 0, 1))
SK_COL = np.array([0.25, 0.75, 0.85], np.float32)
buf += sk_w[..., None] * SK_COL[None, None, :] * 0.62

# (4) rung stars + halos: radius encodes log|j|, white-core intensity encodes
#     the depth of the silence (-log10 of the near-integer miss)
MISS = {19: 0.2223, 43: 2.225e-4, 67: 1.3375e-6, 163: 7.4993e-13}
star = np.zeros((H, W), np.float32)
core = np.zeros((H, W), np.float32)
ring = np.zeros((H, W), np.float32)
GOLD = np.array([1.0, 0.85, 0.45], np.float32)
ICE = np.array([0.55, 0.9, 1.0], np.float32)
for d, jint in HEEGNER + HEEGNER_EDGE:
    u_d = np.pi * math.sqrt(d)
    row = v_to_row(math.log(u_d))
    cols = [W / 2.0] if d % 4 == 3 else [0.0, W - 1.0]
    if d == 3:                       # j = 0 : the star that is a hole
        kit.splat_points(ring, cols, [row] * len(cols), 1.0, 13 * rs, (H, W))
        continue
    rad = (2.4 + 1.15 * math.sqrt(math.log(abs(jint)))) * rs
    silence = max(-math.log10(MISS[d]), 0.0) if d in MISS else 0.0
    for colx in cols:
        w0 = 1.0 if d % 4 == 3 else 0.55
        kit.splat_points(star, [colx], [row], w0, rad, (H, W))
        kit.splat_points(core, [colx], [row], w0 * (0.25 + 0.16 * silence), 1.6 * rs, (H, W))
buf += star[..., None] * GOLD[None, None, :] * 1.9
buf += core[..., None] * np.array([1.0, 1.0, 0.97], np.float32)[None, None, :] * 1.4
rung_halo = gaussian_filter(star + ring, 6 * rs)
buf += rung_halo[..., None] * GOLD[None, None, :] * 0.8
annulus = np.clip(gaussian_filter(ring, 2.5 * rs) - 1.15 * ring, 0, None)
buf += annulus[..., None] * ICE[None, None, :] * 2.6

# (4b) graded fog near the floor: calm sub-pixel filigree
depthramp = np.clip((-1.2 - (VMAX - np.arange(H) / (H - 1) * (VMAX - VMIN))) / 1.9, 0, 1)
if depthramp.max() > 0:
    soft = gaussian_filter(buf, (2.2 * SS, 2.2 * SS, 0))
    a = (0.75 * depthramp ** 1.5)[:, None, None]
    buf = buf * (1 - a) + soft * a

# (5) gentle bloom on the whole thing
buf = kit.bloom(buf, mask_thresh=0.55, sigma=18 * rs, gain=0.35, tint=(1.0, 0.85, 0.6))

img = kit.filmic(buf, k=1.25, gamma=0.90)
if SS > 1:
    from PIL import Image
    img = np.array(Image.fromarray(img).resize((S, S), Image.LANCZOS))

# ---------------- inscriptions --------------------------------------------------
fs = max(14, int(15 * S / 1024))
texts = []
for d, jint in HEEGNER:
    row = v_to_row(math.log(np.pi * math.sqrt(d))) / SS
    texts.append((S * 0.5 + 18 * S / 1024, row, f"d={d}   j = {jint}", "lm", (205, 185, 150)))
# the apex gets the near-integer itself, on a second line
row163 = v_to_row(math.log(np.pi * math.sqrt(163))) / SS
texts.append((S * 0.5 + 18 * S / 1024, row163 + 1.6 * fs,
              "e^(pi sqrt 163) = 262537412640768743.99999999999925...", "lm", (150, 170, 185)))
for d, jint in HEEGNER_EDGE:
    row = v_to_row(math.log(np.pi * math.sqrt(d))) / SS
    texts.append((14 * S / 1024, row, f"d={d}  j={jint}", "lm", (160, 150, 130)))
img = kit.stamp_text(img, texts, fontsize=fs)

from PIL import Image
out = "hero_proto.png" if PROTO else "flame_that_spells_an_integer.png"
Image.fromarray(img).save(out)
print("saved", out, f"{time.time()-t0:.0f}s")
