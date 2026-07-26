"""PANEL 3 — The Nine Gates  (the class-number shore, h(-d) to 3,000,000)

Every fundamental discriminant -d with d <= 3e6 is one firefly at
(x, y) = (log d, log h(-d)); h computed by this run's own reduced-forms census
(census.py, verified vs brute force + genus theory).  Color = omega(d) (number of
prime factors): genus theory forces 2^(omega-1) | h, so each hue-stratum floats at
its own quantized height — only prime-like discriminants (ice) can touch the floor
h=1.  Gold gates: the LAST discriminant of each class number n (n=1: d=163).
The cyan thread at the very bottom is the strongest EFFECTIVE lower bound known
(Oesterle 1985, ~ln(d)/55): it stays below h=1 across the entire canvas —
we know the floor rises, we cannot prove where.
"""
import numpy as np, math, sys, time
from scipy.ndimage import gaussian_filter
import kit

PROTO = "--proto" in sys.argv
S = 1024 if PROTO else 2560
SS = 1 if PROTO else 2
W = H = S * SS
rs = W / 1024.0
t0 = time.time()

z = np.load("census.npz")
h_all, fund, omega = z["h"].astype(np.int64), z["fund"], z["omega"].astype(np.int32)
gates_n, gates_d = z["gates_n"], z["gates_d"]
gates = dict(zip(gates_n.tolist(), gates_d.tolist()))
assert gates[1] == 163 and gates[2] == 427 and gates[3] == 907

D = np.nonzero(fund)[0]
hv = h_all[D]
om = omega[D]
assert (hv > 0).all()
print(f"{len(D):,} fundamental discriminants; h max = {hv.max()}   {time.time()-t0:.1f}s")

XMIN, XMAX = math.log(1.7), math.log(3.2e6)
YMIN, YMAX = -1.65, math.log(hv.max()) * 1.06
def to_px(dd, hh):
    x = (np.log(dd) - XMIN) / (XMAX - XMIN) * (W - 1)
    y = (H - 1) - (np.log(hh) - YMIN) / (YMAX - YMIN) * (H - 1)
    return x, y

# ---------------- fog, one accumulator per omega-stratum -----------------------
STRATA = [(1, (0.62, 0.86, 1.00)),   # prime discriminant: ice (h can be odd -> floor)
          (2, (0.28, 0.34, 0.85)),   # indigo
          (3, (0.80, 0.30, 0.12)),   # ember
          (4, (1.00, 0.68, 0.22)),   # gold
          (5, (1.00, 0.90, 0.60))]   # pale gold (omega>=5)
buf = np.zeros((H, W, 3), np.float32)
x, y = to_px(D, hv)
ix, iy = np.floor(x).astype(int), np.floor(y).astype(int)
fx, fy = x - ix, y - iy
accs = []
for wcls, col in STRATA:
    m = (om == wcls) if wcls < 5 else (om >= 5)
    acc = np.zeros((H, W), np.float32)
    for ox, oy, wgt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                        (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        gx, gy = ix[m] + ox, iy[m] + oy
        ok = (gx >= 0) & (gx < W) & (gy >= 0) & (gy < H)
        np.add.at(acc, (gy[ok], gx[ok]), wgt[m][ok])
    accs.append(gaussian_filter(acc, 0.7 * rs))
    print(f"stratum omega={wcls}: {m.sum():>7,} points")

# hue by softmax of stratum share (dominant stratum keeps its color even in the
# mixed wedge); luminance = soft-knee of TOTAL density
Q = 2.5
tot = np.sum(accs, axis=0)
wq = [np.maximum(a, 0) ** Q for a in accs]
wsum = np.maximum(np.sum(wq, axis=0), 1e-12)
hue = np.zeros((H, W, 3), np.float32)
for (wcls, col), aq in zip(STRATA, wq):
    for c in range(3):
        hue[..., c] += (aq / wsum) * col[c]
# luminance: blend histogram-equalized log-density (structure at every scale)
# with a soft knee (physical density feel)
mask = tot > 1e-4
lo = np.log1p(tot)
lum_eq = np.zeros((H, W), np.float32)
vals = lo[mask]
order = np.argsort(vals, kind="stable")
ranks = np.empty(len(vals), np.float32)
ranks[order] = np.linspace(0, 1, len(vals), dtype=np.float32)
lum_eq[mask] = ranks
nz = tot[mask]
p = np.percentile(nz, 99.0) if len(nz) else 1.0
lum_knee = 1.0 - np.exp(-tot / max(p * 0.9, 1e-6))
lum = (0.55 * lum_eq + 0.45 * lum_knee) ** 1.1
buf += hue * lum[..., None] * 0.95

# sparkle layer: the discrete quantized rows (h <= 8) as fireflies, stratum-colored
msmall = hv <= 8
xs_s, ys_s = to_px(D[msmall], hv[msmall])
om_s = np.clip(om[msmall], 1, 5)
spark = np.zeros((H, W, 3), np.float32)
tmp = np.zeros((H, W), np.float32)
for wcls, col in STRATA:
    mm = om_s == wcls
    if not mm.any():
        continue
    tmp[:] = 0
    kit.splat_points(tmp, xs_s[mm], ys_s[mm], 0.9, 1.5 * rs, (H, W))
    spark += np.clip(tmp, 0, 1.2)[..., None] * np.array(col, np.float32)[None, None, :]
buf += spark * 0.75

# ---------------- effective floor: Oesterle ~ ln(d)/55 -------------------------
dd = np.exp(np.linspace(XMIN, XMAX, 4000))
floor_h = np.log(dd) / 55.0
fx_, fy_ = to_px(dd, np.maximum(floor_h, 1e-3))
thread = np.zeros((H, W), np.float32)
for i in range(len(dd) - 1):
    pass
seg = np.zeros((H, W), np.float32)
kit.line_splat(seg, fx_[0], fy_[0], fx_[-1], fy_[-1], 0)  # noop to keep API warm
# draw as polyline via consecutive splats
xs0, ys0 = fx_[:-1], fy_[:-1]
xs1, ys1 = fx_[1:], fy_[1:]
for a, b, cc, e in zip(xs0, ys0, xs1, ys1):
    kit.line_splat(thread, a, b, cc, e, 2.2)
thread = gaussian_filter(thread, 0.9 * rs)
ICE = np.array([0.45, 0.85, 0.95], np.float32)
buf += np.clip(thread, 0, 0.05)[..., None] * ICE[None, None, :] * 9.0

# ---------------- the silence line + nine h=1 stars ----------------------------
nine = D[hv == 1]
assert nine.tolist() == [3, 4, 7, 8, 11, 19, 43, 67, 163]
star = np.zeros((H, W), np.float32)
sx, sy = to_px(nine, np.ones(len(nine)))
kit.splat_points(star, sx, sy, 1.0, 5.0 * rs, (H, W))
# beyond-163 silence rail: the empty floor, drawn as a nearly-dark cold whisper
x163 = to_px(np.array([163.0]), np.array([1.0]))[0][0]
rail = np.zeros((H, W), np.float32)
y1 = to_px(np.array([3.0]), np.array([1.0]))[1][0]
kit.line_splat(rail, x163, y1, W - 1.0, y1, 1.2, n=4000)
rail = gaussian_filter(rail, 1.2 * rs)
buf += np.clip(rail, 0, 0.02)[..., None] * np.array([0.35, 0.5, 0.6], np.float32) * 6.0

# ---------------- gold gates: last d of each class number ----------------------
gate = np.zeros((H, W), np.float32)
gxs, gys, glabels = [], [], []
for n in sorted(gates):
    dlast = gates[n]
    gx, gy = to_px(np.array([float(dlast)]), np.array([float(n)]))
    gxs.append(gx[0]); gys.append(gy[0]); glabels.append((n, dlast))
kit.splat_points(gate, gxs, gys, 1.0, 3.2 * rs, (H, W))
GOLD = np.array([1.0, 0.84, 0.42], np.float32)
buf += gate[..., None] * GOLD[None, None, :] * 2.6
buf += gaussian_filter(gate, 5 * rs)[..., None] * GOLD[None, None, :] * 1.1
buf += star[..., None] * np.array([1.0, 0.95, 0.8], np.float32)[None, None, :] * 3.0
buf += gaussian_filter(star, 8 * rs)[..., None] * GOLD[None, None, :] * 1.0

buf = kit.bloom(buf, mask_thresh=0.6, sigma=14 * rs, gain=0.3, tint=(1.0, 0.9, 0.7))
img = kit.filmic(buf, k=1.35, gamma=0.92)
if SS > 1:
    from PIL import Image
    img = np.array(Image.fromarray(img).resize((S, S), Image.LANCZOS))

# ---------------- inscriptions -------------------------------------------------
fs = max(13, int(14 * S / 1024))
texts = []
for (n, dlast), gx, gy in zip(glabels, gxs, gys):
    if n in (2, 3, 4, 5, 6, 7, 8, 10, 13, 16, 21, 25):
        texts.append((gx / SS + 9 * S / 1024, gy / SS - 7 * S / 1024,
                      f"{n}|{dlast}", "lm", (215, 190, 140)))
for dv in [3, 4, 7, 8, 11, 19, 43, 67, 163]:
    px9, py9 = to_px(np.array([float(dv)]), np.array([1.0]))
    texts.append((px9[0] / SS, py9[0] / SS - 14 * S / 1024, str(dv), "mm", (170, 175, 190)))
sx9, sy9 = to_px(np.array([163.0]), np.array([1.0]))
texts.append((sx9[0] / SS, sy9[0] / SS + 30 * S / 1024,
              "d = 163  -  the last silence (h = 1)", "mm", (200, 220, 235)))
texts.append((S * 0.975, sy9[0] / SS + 52 * S / 1024,
              "the floor stays empty forever: h -> inf  (Siegel, ineffective)", "rm", (115, 130, 145)))
texts.append((S * 0.035, S * 0.062, "THE NINE GATES", "lm", (190, 170, 130)))
texts.append((S * 0.035, S * 0.062 + 1.8 * fs,
              "h(-d), every fundamental discriminant to 3,000,000", "lm", (140, 132, 118)))
texts.append((S * 0.035, S * 0.062 + 3.3 * fs,
              "own census: 906,153,551 reduced forms; hue = prime factors of d (genus strata)",
              "lm", (120, 114, 102)))
texts.append((S * 0.035, S * 0.062 + 4.8 * fs,
              "gold gates: the last d of each class number;  cyan thread: the strongest",
              "lm", (120, 114, 102)))
texts.append((S * 0.035, S * 0.062 + 6.3 * fs,
              "EFFECTIVE lower bound (Oesterle) - below h=1 across the whole picture",
              "lm", (110, 140, 150)))
img = kit.stamp_text(img, texts, fontsize=fs)
from PIL import Image
out = "gates_proto.png" if PROTO else "nine_gates.png"
Image.fromarray(img).save(out)
print("saved", out, f"{time.time()-t0:.0f}s")
