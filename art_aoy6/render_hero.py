"""render_hero.py — THE HALF-STEP (4096^2), mirrored two-shores composition.

Census of the fundamental unit of Z[sqrt d] for all squarefree d <= 1e8.
x = log10 d. A horizon splits the canvas:
  ABOVE (ember gold):  d with ODD continued-fraction period — the negative
     Pell equation x^2 - d y^2 = -1 is solvable; the unit ladder has a
     half-step, eps has norm -1.
  BELOW, mirrored (steel cyan + slate violet): d with EVEN period. Cyan =
     eligible (no prime 3 mod 4, allowed to but didn't); violet = a prime
     3 mod 4 forbids -1 from the start.
Height above/below horizon = log10 R, R = regulator. The Richaud-Degert
roads (d = m^2 +- 1, ...) hug the horizon on both sides. Twin record stars:
gold d=99,890,389 (P=28,965, 14,869-digit solution), cyan-world absolute
record d=97,544,899 (P=29,818, 15,221 digits).
Horizon band: windowed share of gold among the eligible, vs the proven
limit 1-alpha = 0.58058 (Stevenhagen -> Koymans-Pagano 2022): still 0.760
at 1e8 — the census cannot see the limit.
usage: render_hero.py SIZE
"""
import sys
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
rs = SIZE / 1024.0
OUT = "/tmp/claude-0/-home-user-claude-mythos-self-play/adf44c3e-737f-5218-82c7-9c74bc24d1b1/scratchpad/pell1e8"
N = 100_000_000
W = H = SIZE

flags = np.fromfile(f"{OUT}/flags.u8", dtype=np.uint8)
period = np.fromfile(f"{OUT}/period.u32", dtype=np.uint32)
reg = np.fromfile(f"{OUT}/reg.f32", dtype=np.float32)
d = np.arange(N + 1, dtype=np.int64)
proc = (flags & 4) != 0
elig = (flags & 2) != 0
odd = (period & 1) == 1

# ---- chart geometry ----
X0, X1 = 2.35, 8.06                # log10 d
YHOR = 0.545 * H                   # horizon row
YLIM = 3.72                        # max of log10(R/floor)
UP_H = YHOR - 0.02 * H             # px height of upper world
DN_H = H - YHOR - 0.03 * H
GAP = 0.050 * H                    # reserved horizon strip (Stevenhagen band)

def xpix(lx): return (lx - X0) / (X1 - X0) * (W - 1)
# height = log10( R / ln(2 sqrt d) ): excess weight over the lightest
# possible key (the m^2+1 road); roads sit exactly on the horizon
def ypix_up(ly): return YHOR - GAP - np.maximum(ly, 0) / YLIM * (UP_H - GAP)
def ypix_dn(ly): return YHOR + GAP + np.maximum(ly, 0) / YLIM * (DN_H - GAP)

lx_all = np.log10(d[proc].astype(np.float64))
floor_all = np.log(2.0) + 0.5 * np.log(d[proc].astype(np.float64))
lr_all = np.log10(np.maximum(reg[proc].astype(np.float64) / floor_all, 1.0))
o = odd[proc]; e = elig[proc]

def splat(px, py):
    g = np.zeros(W * H)
    x0 = np.floor(px).astype(np.int64); y0 = np.floor(py).astype(np.int64)
    fx = px - x0; fy = py - y0
    for dx, dy, wt in ((0, 0, (1-fx)*(1-fy)), (1, 0, fx*(1-fy)),
                       (0, 1, (1-fx)*fy), (1, 1, fx*fy)):
        xi = x0 + dx; yi = y0 + dy
        m = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
        np.add.at(g, (yi[m] * W + xi[m]), wt[m])
    return g.reshape(H, W)

print("splatting ...")
Ggold = splat(xpix(lx_all[o]), ypix_up(lr_all[o]))
Gcyan = splat(xpix(lx_all[~o & e]), ypix_dn(lr_all[~o & e]))
Gviol = splat(xpix(lx_all[~o & ~e]), ypix_dn(lr_all[~o & ~e]))
# Richaud-Degert roads: period <= 8, extra light in both worlds
P_all = period[proc]
road = P_all <= 8
Groad_u = splat(xpix(lx_all[o & road]), ypix_up(lr_all[o & road]))
Groad_d = splat(xpix(lx_all[~o & road]), ypix_dn(lr_all[~o & road]))

def lum_of(g, gammax=1.2):
    """histeq(log) 52/48 soft-knee blend, nonzero-masked"""
    g = gaussian_filter(g, 0.55 * rs)
    pos = g > 1e-9
    logd = np.where(pos, np.log1p(g), 0.0)
    vals = logd[pos]
    order = np.argsort(vals)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(len(vals)) / max(len(vals) - 1, 1)
    he = np.zeros_like(logd); he[pos] = ranks
    lin = 1.0 - np.exp(-g / max(np.percentile(g[pos], 99.2) * 0.55, 1e-9))
    return (0.52 * he + 0.48 * lin) ** gammax

Lg = lum_of(Ggold)
# lower world: one luminance from the total, hue from the cyan fraction
Glow = Gcyan * 4.0 + Gviol
Llow = lum_of(Glow)
fcyan = np.where(Glow > 1e-9, (Gcyan * 4.0) / np.maximum(Glow, 1e-12), 0.0)
fcyan = gaussian_filter(fcyan, 1.0 * rs)

C_gold = np.array([1.00, 0.68, 0.22])
C_gold_hi = np.array([1.00, 0.88, 0.55])
C_cyan = np.array([0.25, 0.66, 0.88])
C_cyan_hi = np.array([0.62, 0.88, 1.00])
C_viol = np.array([0.30, 0.24, 0.44])

img = np.zeros((H, W, 3))
# lower world: violet body warmed toward cyan where the eligible live
C_viol_body = np.array([0.40, 0.32, 0.60])
low_col = C_viol_body[None, None, :] * (1 - fcyan[..., None]) + \
    (C_cyan * 0.5 + C_cyan_hi * 0.5)[None, None, :] * fcyan[..., None]
img += (Llow ** 1.05)[..., None] * low_col * 1.0
img += Lg[..., None] * (C_gold * (1 - Lg[..., None]) + C_gold_hi * Lg[..., None]) * 1.15
# roads: warm-white filaments hugging the horizon
Ru = gaussian_filter(np.minimum(Groad_u, 3.0), 0.7 * rs)
Rd = gaussian_filter(np.minimum(Groad_d, 3.0), 0.7 * rs)
img += np.clip(Ru * 0.5, 0, 1.3)[..., None] * np.array([1.0, 0.85, 0.50])
img += np.clip(Rd * 0.4, 0, 1.1)[..., None] * np.array([0.65, 0.85, 1.0])

# bloom true crests only
def wide_bloom(layer, sigma):
    ds = max(1, int(sigma / 6))
    small = layer[::ds, ::ds]
    b = gaussian_filter(small, sigma / ds)
    return np.kron(b, np.ones((ds, ds)))[:H, :W]

# record coastlines: per-column max height in each world, ghost hairlines
def coastline(pxv, pyv, col, amp):
    cx = np.clip(pxv.astype(int), 0, W - 1)
    top = np.full(W, np.nan)
    np.fmin.at(top, cx, pyv)          # smallest py = highest point
    ys = np.copy(top)
    ink2 = np.zeros((H, W))
    for x in range(W):
        if np.isfinite(ys[x]):
            yi = int(np.clip(ys[x] - 2.0 * rs, 0, H - 1))
            ink2[yi, x] += 1.0
    ink2 = gaussian_filter(ink2, 1.0 * rs)
    return np.clip(ink2, 0, 1.0)[..., None] * col * amp

pxu = xpix(lx_all[o]); pyu = ypix_up(lr_all[o])
pxd = xpix(lx_all[~o]); pyd = ypix_dn(lr_all[~o])
img += coastline(pxu, pyu, np.array([1.0, 0.9, 0.65]), 0.5)
img += coastline(pxd, -pyd, np.array([0.7, 0.85, 1.0]), 0.0)  # lower world: skip (mirror sym)
top_d = np.full(W, np.nan)
np.fmax.at(top_d, np.clip(pxd.astype(int), 0, W - 1), pyd)
inkd = np.zeros((H, W))
for x in range(W):
    if np.isfinite(top_d[x]):
        yi = int(np.clip(top_d[x] + 2.0 * rs, 0, H - 1))
        inkd[yi, x] += 1.0
img += np.clip(gaussian_filter(inkd, 1.0 * rs), 0, 1.0)[..., None] * np.array([0.7, 0.85, 1.0]) * 0.4

hotg = np.where(Lg > 0.80, Lg - 0.80, 0.0) * 3.0
hotc = np.where(Llow > 0.85, Llow - 0.85, 0.0) * 3.0
img += (gaussian_filter(hotg, 2.2 * rs) * 0.45 + wide_bloom(hotg, 13 * rs) * 0.30)[..., None] * C_gold
img += (gaussian_filter(hotc, 2.2 * rs) * 0.25 + wide_bloom(hotc, 13 * rs) * 0.17)[..., None] * C_cyan

# ---- twin record stars ----
yy, xx = np.ogrid[0:H, 0:W]
def star_at(sx, sy, col, amp=1.0):
    rr2 = (xx - sx) ** 2 + (yy - sy) ** 2
    core = np.exp(-rr2 / (2 * (1.9 * rs) ** 2)) * 1.5 * amp
    halo = np.exp(-np.sqrt(rr2) / (8 * rs)) * 0.32 * amp
    ang = np.arctan2(yy - sy, xx - sx)
    spike = np.exp(-np.abs(np.sin(2 * ang)) * np.sqrt(rr2) / (1.9 * rs)) \
        * np.exp(-np.sqrt(rr2) / (22 * rs)) * 0.45 * amp
    return (core + halo + spike)[..., None] * col

dg, dc = 99890389, 97544899
def ynorm(dv): return np.log10(reg[dv] / (np.log(2.0) + 0.5 * np.log(float(dv))))
img += star_at(xpix(np.log10(dg)), ypix_up(ynorm(dg)), np.array([1.0, 0.88, 0.60]))
img += star_at(xpix(np.log10(dc)), ypix_dn(ynorm(dc)), np.array([0.75, 0.92, 1.0]))

# ---- Stevenhagen ribbon on the horizon ----
elig_mask = proc & elig
ldx = np.log10(d[elig_mask].astype(np.float64))
oddp = odd[elig_mask].astype(np.float64)
srt = np.argsort(ldx)
ldx_s, oddp_s = ldx[srt], oddp[srt]
# sliding log windows of half-width 0.16 dex, spanning the full axis
fx = np.linspace(2.45, 8.0, 300)
fr = np.full(len(fx), np.nan)
for i, c in enumerate(fx):
    lo = np.searchsorted(ldx_s, c - 0.16)
    hi = np.searchsorted(ldx_s, c + 0.16)
    if hi - lo >= 25:
        fr[i] = oddp_s[lo:hi].mean()
keep = np.isfinite(fr)
fx, fr = fx[keep], fr[keep]
# ribbon band: fraction mapped to +-0.042 H around horizon (centre 0.70)
def f_to_y(f): return YHOR + (0.70 - f) / 0.20 * 0.042 * H
ink = np.zeros((H, W))
pts = list(zip(xpix(fx), f_to_y(fr)))
for (ax, ay), (bx2, by2) in zip(pts[:-1], pts[1:]):
    n = max(2, int(np.hypot(bx2 - ax, by2 - ay) / 0.6))
    xs = np.linspace(ax, bx2, n); ys = np.linspace(ay, by2, n)
    xi = np.clip(xs.astype(int), 0, W - 1); yi = np.clip(ys.astype(int), 0, H - 1)
    ink[yi, xi] += 1.0 / n * 14
ink = gaussian_filter(ink, 1.15 * rs)
img += np.clip(ink, 0, 1.8)[..., None] * np.array([1.0, 0.82, 0.42])
# terminal bead: where the census leaves the frame, still at 0.760
bx, by = xpix(fx[-1]), f_to_y(fr[-1])
rrb = (xx - bx) ** 2 + (yy - by) ** 2
img += (np.exp(-rrb / (2 * (2.4 * rs) ** 2)) * 1.4)[..., None] * np.array([1.0, 0.85, 0.5])

# asymptote: dashed ice line at 0.58058
asy = np.zeros((H, W))
y_asy = int(f_to_y(0.58058))
xs = np.arange(int(xpix(2.5)), W)
dash = (xs // int(9 * rs)) % 2 == 0
asy[y_asy, xs[dash]] = 1.0
asy = gaussian_filter(asy, 0.9 * rs)
img += np.clip(asy, 0, 1.2)[..., None] * np.array([0.55, 0.85, 1.0]) * 1.1

# faint horizon hairline to anchor the mirror
hairline = np.zeros((H, W))
hairline[int(YHOR), :] = 0.5
hairline = gaussian_filter(hairline, 1.2 * rs)
img += hairline[..., None] * np.array([0.9, 0.85, 0.75]) * 0.5

# ---- tone map ----
img = 1.0 - np.exp(-1.28 * img)
img = img ** (1 / 1.72)
img += (np.random.default_rng(7).random((H, W, 3)) - 0.5) / 255.0
img = np.clip(img, 0, 1)
out = Image.fromarray((img * 255).astype(np.uint8))

# ---- annotations ----
if SIZE >= 2048:
    dr = ImageDraw.Draw(out)
    try:
        F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(13.5 * rs))
        Fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(20 * rs))
        Fi = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", int(12.5 * rs))
    except OSError:
        F = Fb = Fi = ImageFont.load_default()
    gold = (255, 208, 125); cyan = (150, 218, 255); grey = (168, 168, 185)
    dr.text((30 * rs, 20 * rs), "THE HALF-STEP", font=Fb, fill=gold)
    dr.text((30 * rs, 48 * rs),
            "all 60,792,693 squarefree d ≤ 10⁸ · x = log₁₀ d · height = log₁₀( R / ln 2√d ),  R = log ε_d,  ε_d = fundamental solution of x² − d y² = ±1",
            font=F, fill=grey)
    dr.text((30 * rs, 69 * rs),
            "above the horizon: continued-fraction period ODD — ε has norm −1, the ladder takes a half-step and x² − d y² = −1 is solved",
            font=F, fill=gold)
    dr.text((30 * rs, 90 * rs),
            "below, mirrored: period EVEN — cyan was allowed −1 (no prime ≡ 3 mod 4) and refused; violet was forbidden from the start",
            font=F, fill=cyan)
    sx = xpix(np.log10(dg)); sy = float(ypix_up(ynorm(dg)))
    dr.text((sx - 40 * rs, sy - 34 * rs),
            "gold record d = 99,890,389 : period 28,965 — the smallest x has 14,869 digits", font=F, fill=(255, 232, 185), anchor="rm")
    sx = xpix(np.log10(dc)); sy = float(ypix_dn(ynorm(dc)))
    dr.text((sx - 40 * rs, sy + 24 * rs),
            "absolute record d = 97,544,899 : period 29,818 — 15,221 digits, and still no half-step", font=F, fill=(190, 230, 255), anchor="rm")
    dr.text((xpix(2.50), f_to_y(0.70) - 30 * rs),
            "share of gold among the eligible — 0.760 at 10⁸ and falling by a hair per decade", font=Fi, fill=gold)
    dr.text((xpix(7.92), f_to_y(0.58058) + 8 * rs),
            "proven limit 1−α = 0.58058…  (Stevenhagen 1993 → Koymans–Pagano 2022): the horizon the census cannot see", font=Fi, fill=cyan, anchor="rm")
    dr.text((xpix(7.92), float(ypix_up(0.0)) - 22 * rs),
            "the roads d = m² + r, r | 4m  (period ≤ 8) ride the horizon", font=F, fill=(230, 205, 160), anchor="rm")
    dr.text((30 * rs, YHOR - GAP - 0.24 * H),
            "height = log₁₀ ( R / ln 2√d )  —  the toll paid above the lightest possible key", font=Fi, fill=grey)

out.save(f"art_aoy6/half_step_{SIZE}.png")
print(f"saved art_aoy6/half_step_{SIZE}.png")
