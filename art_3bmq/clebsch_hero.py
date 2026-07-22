"""THE TWENTY-SEVEN LINES NOBODY DREW  --  hero render.

Ray-traced Clebsch diagonal cubic (sum x_i = 0, sum x_i^3 = 0 in P^4),
affine chart from clebsch_lines.py, clipped to a ball. Closed-form
(trig/Cardano) cubic solve per ray, Newton-polished. The 15 'rational'
lines burn cool silver-cyan; the 12 golden-ratio lines burn gold; the 10
Eckardt points (3 lines concurrent) blaze white.

usage: python3 clebsch_hero.py SIZE OUT [--cam tilt_deg orbit_deg dist fov]
"""
import sys
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom
from PIL import Image

# ---------------------------------------------------------------- params
SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 640
OUT = sys.argv[2] if len(sys.argv) > 2 else "art_3bmq/proto/hero_proto.png"
TILT = float(sys.argv[3]) if len(sys.argv) > 3 else 28.0    # deg from 3-fold axis
ORBIT = float(sys.argv[4]) if len(sys.argv) > 4 else 18.0   # deg around axis
DIST = float(sys.argv[5]) if len(sys.argv) > 5 else 9.0
FOV = float(sys.argv[6]) if len(sys.argv) > 6 else 46.0     # deg full
SS = 2
S = SIZE * SS
rs = SIZE / 2560.0 if SIZE > 1200 else SIZE / 640.0         # stroke scale

RCLIP = float(__import__('os').environ.get('RCLIP', 3.35))
LINE_W = 0.020            # world-units gaussian width of line glow
ECK_W = 0.10

dat = np.load("art_3bmq/lines27.npz")
P27, V27, B, ECK = dat["P"], dat["V"], dat["B"], dat["eck"]
A5 = B[:, :3]             # 5x3: coefficient rows for affine coords
A0 = B[:, 3]              # constant per row

def Gval(pts):            # pts (...,3)
    r = pts @ A5.T + A0   # (...,5)
    return (r ** 3).sum(-1)

def Ggrad(pts):
    r = pts @ A5.T + A0
    return 3.0 * np.einsum('...i,ij->...j', r ** 2, A5)

# ---------------------------------------------------------------- camera
ax = np.deg2rad(TILT); az = np.deg2rad(ORBIT)
cam = DIST * np.array([np.sin(ax) * np.cos(az), np.sin(ax) * np.sin(az), np.cos(ax)])
look = np.array([0.0, 0.0, -0.15])
fwd = look - cam; fwd /= np.linalg.norm(fwd)
right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
if np.linalg.norm(right) < 1e-6:
    right = np.array([1.0, 0.0, 0.0])
right /= np.linalg.norm(right)
up = np.cross(right, fwd)
half = np.tan(np.deg2rad(FOV) / 2)

# ---------------------------------------------------------------- cubic solve
def cubic_roots(c3, c2, c1, c0):
    """real roots of c3 t^3+c2 t^2+c1 t+c0, shape (...,3), NaN-padded."""
    out = np.full(c3.shape + (3,), np.nan)
    lin = np.abs(c3) < 1e-12 * np.maximum(1, np.abs(c2) + np.abs(c1) + np.abs(c0))
    # quadratic / linear fallback
    if lin.any():
        a2, b2, cc = c2[lin], c1[lin], c0[lin]
        quad = np.abs(a2) > 1e-14
        disc = b2 * b2 - 4 * a2 * cc
        ok = quad & (disc >= 0)
        r1 = np.full(a2.shape, np.nan); r2 = np.full(a2.shape, np.nan)
        sq = np.sqrt(np.where(ok, disc, 0.0))
        r1[ok] = ((-b2 + sq) / (2 * a2))[ok]
        r2[ok] = ((-b2 - sq) / (2 * a2))[ok]
        linl = (~quad) & (np.abs(b2) > 1e-14)
        r1[linl] = (-cc / b2)[linl]
        sub = out[lin]; sub[:, 0] = r1; sub[:, 1] = r2; out[lin] = sub
    cub = ~lin
    a, b, c, d = c3[cub], c2[cub], c1[cub], c0[cub]
    b_, c_, d_ = b / a, c / a, d / a
    p = c_ - b_ * b_ / 3.0
    q = 2 * b_**3 / 27.0 - b_ * c_ / 3.0 + d_
    sh = -b_ / 3.0
    disc = -4 * p**3 - 27 * q * q
    res = np.full(p.shape + (3,), np.nan)
    three = disc > 0
    if three.any():
        pt, qt = p[three], q[three]
        m = 2 * np.sqrt(np.maximum(-pt / 3.0, 1e-300))
        arg = np.clip(3 * qt / (pt * m + 1e-300), -1, 1)
        th = np.arccos(arg)
        for k in range(3):
            res[three, k] = m * np.cos(th / 3 - 2 * np.pi * k / 3)
    one = ~three
    if one.any():
        po, qo = p[one], q[one]
        D = np.sqrt(np.maximum(q[one]**2 / 4 + po**3 / 27, 0.0))
        u = np.cbrt(-qo / 2 + D)
        v = np.cbrt(-qo / 2 - D)
        res[one, 0] = u + v
    res = res + sh[:, None]
    out[cub] = res
    return out

# ---------------------------------------------------------------- render
acc = np.zeros((S, S, 3), np.float32)
depth_fog = 6.5

BASE_LO = np.array([0.020, 0.030, 0.055])     # deep slate-indigo
BASE_HI = np.array([0.14, 0.22, 0.27])      # petrol sheen
RIMCOL = np.array([0.25, 0.62, 0.72])       # cyan glaze
COL15 = np.array([0.62, 0.85, 1.00])        # silver-cyan (rational lines)
COL12 = np.array([1.00, 0.72, 0.28])        # gold (golden-ratio lines)
ECKCOL = np.array([1.00, 0.92, 0.75])
BGA = np.array([0.012, 0.011, 0.022])
BGB = np.array([0.030, 0.020, 0.048])

L1 = np.array([0.45, 0.35, 0.82]); L1 /= np.linalg.norm(L1)
L2 = np.array([-0.7, -0.45, 0.25]); L2 /= np.linalg.norm(L2)

CH = 128 if S > 4000 else S   # row chunk
ys = np.arange(S)
for r0 in range(0, S, CH):
    r1 = min(r0 + CH, S)
    py, px = np.meshgrid(ys[r0:r1], ys, indexing="ij")
    u = (px + 0.5) / S * 2 - 1
    v = -((py + 0.5) / S * 2 - 1)
    d = fwd[None, None, :] + half * (u[..., None] * right + v[..., None] * up)
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    # sphere clip
    oc = cam
    bq = (d @ oc)
    cq = oc @ oc - RCLIP * RCLIP
    disc = bq * bq - cq
    hit_ball = disc > 0
    sq = np.sqrt(np.maximum(disc, 0))
    tin = -bq - sq
    tout = -bq + sq
    # cubic coefficients along ray by 4-point interpolation
    tsamp = np.array([0.0, 1.0, 2.0, 3.0])
    Vand = np.vander(tsamp, 4)              # t^3..t^0
    Vinv = np.linalg.inv(Vand)
    o = np.broadcast_to(cam, d.shape)
    Gs = np.stack([Gval(o + (t * 1.0) * d) for t in tsamp], axis=-1)
    coef = Gs @ Vinv.T                       # (...,4): c3,c2,c1,c0
    roots = cubic_roots(coef[..., 0], coef[..., 1], coef[..., 2], coef[..., 3])
    # newton polish (2 it)
    for _ in range(2):
        pts = o[..., None, :] + roots[..., :, None] * d[..., None, :]
        g = Gval(pts)
        gp = np.einsum('...kj,...j->...k', Ggrad(pts), d)
        step = g / np.where(np.abs(gp) > 1e-9, gp, np.inf)
        roots = roots - step
    bad = ~np.isfinite(roots) | (roots < tin[..., None]) | (roots > tout[..., None]) | ~hit_ball[..., None]
    rts = np.where(bad, np.inf, roots)
    rts = np.sort(rts, axis=-1)
    t_hit = rts[..., 0]
    ok = np.isfinite(t_hit)

    X = o + t_hit[..., None] * d
    col = np.empty(d.shape, np.float32)
    # background gradient
    bgmix = (v * 0.5 + 0.5)[..., None]
    col[:] = BGA * (1 - bgmix) + BGB * bgmix

    if ok.any():
        Xh = X[ok]
        n = Ggrad(Xh)
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        vd = d[ok]
        n = np.where((np.einsum('ij,ij->i', n, vd) > 0)[:, None], -n, n)
        lam1 = np.clip(n @ L1, 0, 1)
        lam2 = np.clip(n @ L2, 0, 1)
        ndv = np.clip(-np.einsum('ij,ij->i', n, vd), 0, 1)
        rim = (1 - ndv) ** 3
        base = BASE_LO[None, :] + (0.85 * lam1)[:, None] * (BASE_HI - BASE_LO)[None, :] \
            + lam2[:, None] * np.array([0.115, 0.070, 0.030])[None, :]
        # specular
        hvec = L1 - vd; hvec /= np.linalg.norm(hvec, axis=-1, keepdims=True)
        spec = np.clip((n * hvec).sum(-1), 0, 1) ** 42
        shade = base + 0.32 * rim[:, None] * RIMCOL[None, :] + 0.22 * spec[:, None]
        # ball-cut edge darkening
        rr = np.linalg.norm(Xh, axis=-1) / RCLIP
        edge = np.clip((rr - 0.965) / 0.035, 0, 1)
        shade *= (1 - 0.55 * edge[:, None])
        # depth fog
        fog = np.exp(-np.maximum(t_hit[ok] - (DIST - RCLIP), 0) / depth_fog)
        shade = shade * fog[:, None] + (1 - fog)[:, None] * np.array([0.030, 0.018, 0.050])[None, :]

        # line glow (front sheet)
        dP = Xh[:, None, :] - P27[None, :, :]
        crs = np.cross(dP, V27[None, :, :])
        dist = np.linalg.norm(crs, axis=-1)              # (n,27)
        glow = np.exp(-(dist / LINE_W) ** 2)
        g15 = glow[:, :15].sum(1)
        g12 = glow[:, 15:].sum(1)
        fogl = (0.35 + 0.65 * fog)[:, None]
        shade += 1.5 * g15[:, None] * COL15[None, :] * fogl
        shade += 1.9 * g12[:, None] * COL12[None, :] * fogl
        # Eckardt stars
        de = np.linalg.norm(Xh[:, None, :] - ECK[None, :, :], axis=-1)
        ge = np.exp(-(de / ECK_W) ** 2).sum(1)
        shade += 1.6 * ge[:, None] * ECKCOL[None, :] * fogl
        col[ok] = shade

        # translucent ghost: second sheet's lines shine through
        t2 = rts[..., 1]
        ok2 = ok & np.isfinite(t2)
        if ok2.any():
            X2 = (o + t2[..., None] * d)[ok2]
            dP2 = X2[:, None, :] - P27[None, :, :]
            crs2 = np.cross(dP2, V27[None, :, :])
            dist2 = np.linalg.norm(crs2, axis=-1)
            gl2 = np.exp(-(dist2 / (LINE_W * 1.6)) ** 2)
            gh = 0.16 * (gl2[:, :15].sum(1)[:, None] * COL15[None, :] * 1.0
                         + gl2[:, 15:].sum(1)[:, None] * COL12[None, :] * 1.3)
            col[ok2] += gh
    acc[r0:r1] = col

# ---------------------------------------------------------------- post
lum = acc @ np.array([0.30, 0.55, 0.15])
mask = np.clip((lum - 0.75) / 1.2, 0, 1)[..., None] * acc
sig1 = max(2.0, 2.2 * SS * rs)
bloom = np.stack([gaussian_filter(mask[..., i], sig1) for i in range(3)], -1)
# wide bloom via downsample
ds = 8
small = mask[::ds, ::ds]
sig2 = max(3.0, 40 * SS * rs / ds)
wide = np.stack([gaussian_filter(small[..., i], sig2) for i in range(3)], -1)
widef = ndzoom(wide, (ds, ds, 1), order=1)[:S, :S]
img = acc + 1.15 * bloom + 0.7 * widef
img = 1 - np.exp(-1.35 * img)
img = np.clip(img, 0, 1) ** (1 / 1.32)
pil = Image.fromarray((img * 255).astype(np.uint8))
pil = pil.resize((SIZE, SIZE), Image.LANCZOS)
pil.save(OUT)
print("saved", OUT)
