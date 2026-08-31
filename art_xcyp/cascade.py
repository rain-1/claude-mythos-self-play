#!/usr/bin/env python3
"""THE RICHEST HOUR AND THE POOREST — one Osgood arc, unequal inheritance.

Knopp's construction, wedge schedule r_k = 1/(k+2)^2: a Jordan arc of area
EXACTLY (2/3) A0 (telescoping). Time always splits in half; the estate splits
p : q = 0.30 : 0.70 (times (1-r)). The arc-time measure becomes a binomial
multiplicative cascade ON the arc -- singular w.r.t. area even though the arc
itself has positive area. A leaf's estate share of the total is EXACTLY
prod(p or q along its address) -- independent of the wedge schedule.

Main triangle: the cascade world (p = 0.30). Its two lit stretches are THE
richest and THE poorest hours of the journey (argmax/argmin over all windows
of width 4.2%, computed exactly from the depth-22 cascade CDF): equal hours,
wildly unequal estates (gold vs ice). Medallion: the balanced world (p = 1/2),
same pipeline, same window width -- every hour owns exactly 4.2%.

Certificates asserted at build time: bit-exact chain continuity every level;
total leaf area == A0 * prod(1-r_k) rel err < 1e-9; depth-13 subtree areas ==
A0 * prod(1-r_k) * p^j q^(13-j) (binomial law) max rel err < 1e-9; measured
window estates match the CDF prediction; balanced medallion shares == width.
"""
import numpy as np, sys, time
import scipy.ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
SIZE  = 1024 if PROTO else 2560
SS    = 2
S     = SIZE * SS
rs    = SIZE / 1024.0
OUT   = "cascade_proto.png" if PROTO else "cascade_2560.png"

P_MAIN = 0.30
DT = 0.042
AREA_THRESH = 0.30 * (SS * SS)
CERT_DEPTH = 9 if PROTO else 13

def rk(k): return 1.0 / (k + 2) ** 2

# ---------- exact cascade CDF at depth 22: estate share of dyadic leaves
DCDF = 22
sh = np.ones(1)
for _ in range(DCDF):
    sh = np.stack([sh * P_MAIN, sh * (1 - P_MAIN)], axis=-1).reshape(-1)
cdf = np.concatenate([[0.0], np.cumsum(sh)])
assert abs(cdf[-1] - 1) < 1e-9
def wshare(t0, dt):
    i0 = t0 * (1 << DCDF); i1 = (t0 + dt) * (1 << DCDF)
    return float(cdf[int(round(i1))] - cdf[int(round(i0))])
grid = np.arange(0.02, 0.94, 0.001)
shares = np.array([wshare(t, DT) for t in grid])
T_RICH = float(grid[np.argmax(shares)]); SH_RICH = shares.max()
T_POOR = float(grid[np.argmin(shares)]); SH_POOR = shares.min()
print(f"[cascade] richest hour t={T_RICH:.3f} owns {100*SH_RICH:.2f}%  |  "
      f"poorest t={T_POOR:.3f} owns {100*SH_POOR:.4f}%  (width {100*DT:.1f}%)")

margin = 0.048 * S
MAIN = dict(p=P_MAIN, E=(margin, margin), F=(S - margin, S - margin),
            C=(margin, S - margin),
            windows=[(T_RICH, "rich"), (T_POOR, "poor")])
MED  = dict(p=0.5, E=(0.660 * S, 0.330 * S), F=(0.935 * S, 0.605 * S),
            C=(0.660 * S, 0.605 * S),
            windows=[(T_RICH, "rich"), (T_POOR, "poor")])
WINGS = [MAIN, MED]

anch = np.array([
    [0.98, 0.80, 0.38], [0.96, 0.46, 0.22], [0.82, 0.26, 0.48],
    [0.42, 0.28, 0.78], [0.20, 0.46, 0.92], [0.36, 0.86, 0.88],
])
def palette(t):
    x = t * (len(anch) - 1)
    i = np.clip(x.astype(int), 0, len(anch) - 2)
    f = (x - i)[:, None]
    f = f * f * (3 - 2 * f)
    return anch[i] * (1 - f) + anch[i + 1] * f

buf   = np.zeros((3, S, S), dtype=np.float32)
tdens = np.zeros((S, S), dtype=np.float32)
blz   = {"rich": np.zeros(S * S, dtype=np.float32),
         "poor": np.zeros(S * S, dtype=np.float32)}
bufflat = [buf[ch].ravel() for ch in range(3)]
tflat = tdens.ravel()
for v in bufflat + [tflat]:
    assert v.base is not None

t_start = time.time()
report = {}
for wing in WINGS:
    p = wing["p"]; q = 1 - p
    A0w = 0.5 * abs((wing["F"][0]-wing["E"][0]) * (wing["C"][1]-wing["E"][1])
                    - (wing["C"][0]-wing["E"][0]) * (wing["F"][1]-wing["E"][1]))
    E = np.array([list(wing["E"])]); F = np.array([list(wing["F"])]); C = np.array([list(wing["C"])])
    tlo = np.array([0.0])
    wing_area = 0.0
    wblaze = {name: 0.0 for _, name in wing["windows"]}
    level = 0; prod = 1.0; nsplat = 0
    while len(E):
        level += 1
        r = rk(level)
        d1 = p * (1 - r); d2 = d1 + r
        D1 = E + d1 * (F - E); D2 = E + d2 * (F - E)
        n = len(E)
        E2 = np.empty((2*n,2)); F2 = np.empty((2*n,2)); C2 = np.empty((2*n,2))
        E2[0::2], F2[0::2], C2[0::2] = E, C, D1
        E2[1::2], F2[1::2], C2[1::2] = C, F, D2
        assert np.max(np.abs(E2[1::2] - F2[0::2])) == 0.0
        tw = 0.5 ** level
        t2 = np.empty(2*n); t2[0::2] = tlo; t2[1::2] = tlo + tw
        prod *= (1 - r)
        E, F, C, tlo = E2, F2, C2, t2
        ar = 0.5 * np.abs((F[:,0]-E[:,0])*(C[:,1]-E[:,1]) - (C[:,0]-E[:,0])*(F[:,1]-E[:,1]))
        if level == CERT_DEPTH:
            jj = np.zeros(len(E)); idx = np.arange(len(E))
            for b in range(CERT_DEPTH):
                jj += 1 - ((idx >> b) & 1)
            expect = A0w * prod * (p ** jj) * (q ** (CERT_DEPTH - jj))
            relmax = np.max(np.abs(ar - expect) / expect)
            assert relmax < 1e-9, relmax
            rel = abs(ar.sum() - A0w * prod) / (A0w * prod)
            assert rel < 1e-9
            report[f"cert_p{p}"] = f"binomial law depth {CERT_DEPTH} max rel err {relmax:.2e}"
        done = ar < AREA_THRESH
        if level >= 50: done = np.ones(len(E), bool)
        if done.any():
            e, f, c, a, tl = E[done], F[done], C[done], ar[done], tlo[done]
            cx = (e[:,0]+f[:,0]+c[:,0])/3; cy = (e[:,1]+f[:,1]+c[:,1])/3
            tmid = tl + 0.5 ** (level + 1)
            w = np.full(len(a), 0.5 ** level, dtype=np.float64)
            col = palette(tmid)
            wing_area += a.sum(); nsplat += len(a)
            wins = {}
            for T0w, name in wing["windows"]:
                iw = (tmid >= T0w) & (tmid < T0w + DT)
                wins[name] = iw
                wblaze[name] += a[iw].sum()
            x0 = np.floor(cx).astype(np.int64); y0 = np.floor(cy).astype(np.int64)
            fx = cx - x0; fy = cy - y0
            for dx, wx in ((0, 1-fx), (1, fx)):
                for dy, wy in ((0, 1-fy), (1, fy)):
                    xi = np.clip(x0+dx, 0, S-1); yi = np.clip(y0+dy, 0, S-1)
                    ww = (w * wx * wy).astype(np.float32)
                    flat = yi * S + xi
                    for ch in range(3):
                        np.add.at(bufflat[ch], flat, ww * col[:, ch].astype(np.float32))
                    np.add.at(tflat, flat, ww)
                    for name, iw in wins.items():
                        if iw.any():
                            np.add.at(blz[name], flat[iw], ww[iw])
            keep = ~done
            E, F, C, tlo = E[keep], F[keep], C[keep], tlo[keep]
        if level % 8 == 0:
            print(f"  p={p} level {level}: frontier {len(E):,} splat {nsplat:,} {time.time()-t_start:.0f}s", flush=True)
    for T0w, name in wing["windows"]:
        meas = wblaze[name] / wing_area
        pred = wshare(T0w, DT) if p == P_MAIN else DT
        report[f"share_{p}_{name}"] = (meas, pred)
        print(f"[cascade] p={p} window '{name}' t={T0w:.3f}: measured estate {100*meas:.4f}% "
              f"(predicted {100*pred:.4f}%)", flush=True)
        assert abs(meas - pred) < 0.15 * pred + 2e-4

# ---------- wing masks
ys = np.arange(S, dtype=np.float32)[:, None]
xs = np.arange(S, dtype=np.float32)[None, :]
def trimask(E, F, C):
    def hp(P, Q):
        return (Q[0]-P[0])*(ys-P[1]) - (Q[1]-P[1])*(xs-P[0])
    h1, h2, h3 = hp(E, F), hp(F, C), hp(C, E)
    m1 = (h1 <= 0) & (h2 <= 0) & (h3 <= 0)
    m2 = (h1 >= 0) & (h2 >= 0) & (h3 >= 0)
    return m1 if m1.sum() > m2.sum() else m2
mask_main = trimask(MAIN["E"], MAIN["F"], MAIN["C"])
mask_med  = trimask(MED["E"], MED["F"], MED["C"])

img = np.zeros((S, S, 3), dtype=np.float32)
dsafe = np.maximum(tdens, 1e-12)
for mask in (mask_main, mask_med):
    m = mask & (tdens > 0)
    if m.sum() == 0: continue
    ld = np.log(np.maximum(tdens, 1e-20))
    vals = np.sort(ld[m])
    he = np.searchsorted(vals, ld).astype(np.float32) / max(len(vals)-1, 1)
    spread = float(vals[int(0.98*len(vals))] - vals[int(0.02*len(vals))])
    whe = min(0.72, max(0.15, spread / 8.0))
    lin = 1 - np.exp(-2.2 * tdens / max(np.percentile(tdens[m], 85), 1e-12))
    mix = whe * he + (1 - whe) * lin
    tone = (0.05 + 1.15 * np.power(np.clip(mix, 0, 1), 2.6)).astype(np.float32)
    print(f"[tone] spread={spread:.2f} whe={whe:.2f}")
    for ch in range(3):
        img[..., ch] = np.where(mask, (buf[ch] / dsafe) * tone, img[..., ch])

# cold slate wash on the conceded wedges
slate = np.array([0.095, 0.125, 0.168], np.float32)
wedge = (mask_main | mask_med) & (tdens <= 1e-12)
for ch in range(3):
    img[..., ch] = np.where(wedge, slate[ch], img[..., ch])

# ---------- multi-scale density AO
dn = np.clip(tdens / np.percentile(tdens[tdens > 0], 60), 0, 1.4)
ao = np.ones((S, S), dtype=np.float32)
for sg in (3, 12, 48):
    sig = sg * SS / 2
    ds = max(1, int(sig / 6))
    b = ndi.zoom(ndi.gaussian_filter(dn[::ds, ::ds], sig/ds), ds, order=1)[:S, :S]
    if b.shape != (S, S):
        b = np.pad(b, ((0, S-b.shape[0]), (0, S-b.shape[1])), mode="edge")
    ao *= (0.72 + 0.28 * np.clip(b, 0, 1))
img *= ao[..., None]

# ---------- the two lit windows: gold (rich) and ice (poor)
tints = {"rich": np.array([1.22, 0.95, 0.42], np.float32),
         "poor": np.array([0.50, 0.86, 1.22], np.float32)}
for name in ("rich", "poor"):
    ball = blz[name].reshape(S, S)
    for wm in (mask_main, mask_med):
        b = np.where(wm, ball, 0.0)
        nz = b[b > 0]
        if len(nz) == 0: continue
        bl = b / max(np.percentile(nz, 70), 1e-12)
        wgt = (1 - np.exp(-1.9 * np.power(np.clip(bl, 0, None), 0.55)))[..., None] * 0.90
        img = img * (1 - wgt) + tints[name][None, None, :] * wgt * (0.50 + 0.50 * np.clip(bl, 0, 1.4))[..., None]

# bloom on true foci
hot = np.clip(img.sum(2) - 1.55, 0, None)
ds = 4
bloom = ndi.zoom(ndi.gaussian_filter(hot[::ds, ::ds], 10*rs), ds, order=1)[:S, :S]
if bloom.shape != (S, S):
    bloom = np.pad(bloom, ((0, S-bloom.shape[0]), (0, S-bloom.shape[1])), mode="edge")
img += bloom[..., None] * np.array([0.9, 0.8, 0.55])[None, None, :] * 0.28

img = np.clip(img, 0, None)
img = img / (1 + 0.16 * img)
img = np.power(np.clip(img, 0, 1), 1/2.2)
img = (img + np.random.uniform(-1/255, 1/255, img.shape)).clip(0, 1)

im = Image.fromarray((img * 255).astype(np.uint8))
im = im.resize((SIZE, SIZE), Image.LANCZOS)

# ---------- annotation (after bloom; each face its own fallback)
def loadfont(path, sz):
    try: return ImageFont.truetype(path, sz)
    except Exception: return ImageFont.load_default()
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
d = ImageDraw.Draw(im)
x0 = int(0.395 * SIZE); y = int(0.070 * SIZE)
d.text((x0, y), "THE RICHEST HOUR AND THE POOREST", font=loadfont(FB, int(27*rs)),
       fill=(238, 214, 160)); y += int(52 * rs)
mr = report[f"share_{P_MAIN}_rich"][0] * 100
mp = report[f"share_{P_MAIN}_poor"][0] * 100
for line in [
    "one Osgood arc -- a Jordan curve owning exactly 2/3 of its triangle",
    "time splits in half at every fork; the estate splits 0.30 : 0.70",
    "the arc-time measure becomes a multiplicative cascade on the arc:",
    "full time lives on a set of zero area  (equal hours, unequal estate)",
    f"gold: the richest {100*DT:.1f}% of the journey owns {mr:.1f}% of the estate",
    f"ice: the poorest {100*DT:.1f}% owns {mp:.2f}%",
    "medallion: the balanced law p = 1/2 -- every hour owns its 4.2%",
    "chain bit-exact / binomial estate law rel err < 1e-9 / shares match CDF",
]:
    d.text((x0, y), line, font=loadfont(FR, int(16.5*rs)), fill=(168, 172, 182))
    y += int(28 * rs)
im.save(OUT)
print(f"[cascade] wrote {OUT} in {time.time()-t_start:.0f}s")
print("[cascade] report:", report)
