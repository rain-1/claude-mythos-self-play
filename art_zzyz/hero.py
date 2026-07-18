"""THE WALL AT ZERO -- hero render, log-depth chart (wall at bottom).

x = Im s, y = ln Re s. The prime zeta field Re P(s); every zeta zero rho
spawns a singularity at rho/n on the stratum Re = 1/(2n); the strata descend
forever and condense on the wall Re s = 0 (bottom edge). Mobius decides each
light: zero-sparks blaze where mu(n) = -1, darken where mu(n) = +1; the pole
ladder at s = 1/n (Im = 0) does the opposite. Nothing analytic crosses.
"""
import numpy as np, os, sys, time
from scipy.ndimage import zoom as ndzoom, gaussian_filter
from PIL import Image
import hero_field as hf
from hero_field import smoothstep

PROTO = "--proto" in sys.argv
FINAL = 1024 if PROTO else 4096
SS = 2
S = FINAL * SS
CW = 1024 if PROTO else 4096
CD = CW // 2
NK = 16                       # kernel-extracted lines n <= NK
RE0, RE1, IM0, IM1 = hf.RE0, hf.RE1, hf.IM0, hf.IM1
Y0, Y1 = hf.Y0, hf.Y1
PXX = S / (IM1 - IM0)         # px per Im-unit
PXY = S / (Y1 - Y0)           # px per ln-unit


def s2px(re, im):
    return (im - IM0) * PXX - 0.5, (Y1 - np.log(re)) * PXY - 0.5


def sing_catalog():
    """columns: re, im, amp=1/n, bright(+1/-1), n, is_pole"""
    zs = np.load("zeros_cat.npy")
    parts = []
    for n in hf.SQF:
        mu = hf.MU[n]
        g = zs[zs <= n * IM1]
        gm = -zs[zs <= -n * IM0]
        gg = np.concatenate([g, gm])
        c = np.empty((len(gg) + 1, 6))
        c[:len(gg)] = np.stack([np.full(len(gg), 0.5 / n), gg / n,
                                np.full(len(gg), 1.0 / n),
                                np.full(len(gg), -mu),
                                np.full(len(gg), n), np.zeros(len(gg))], 1)
        c[-1] = (1.0 / n, 0.0, 1.0 / n, mu, n, 1)
        parts.append(c)
    cat = np.concatenate(parts)
    keep = (cat[:, 0] > RE0) & (cat[:, 0] <= RE1)
    cat = cat[keep]
    print(f"catalog: {len(cat)} sings ({(cat[:,3]>0).sum()} bright)")
    return cat


def kernel_patch(shape, re_p, im_p, R, sgn_amp, pxx, pxy, y1):
    """Windowed log|s-p| on the log-chart grid; s-space isotropic window."""
    H, W = shape
    x0 = int(max(0, np.floor((im_p - R - IM0) * pxx)))
    x1 = int(min(W, np.ceil((im_p + R - IM0) * pxx) + 1))
    ylo = np.log(max(re_p - R, 1e-6))
    yhi = np.log(re_p + R)
    r0 = int(max(0, np.floor((y1 - yhi) * pxy)))
    r1 = int(min(H, np.ceil((y1 - ylo) * pxy) + 1))
    if x0 >= x1 or r0 >= r1:
        return None
    xs = IM0 + (np.arange(x0, x1) + 0.5) / pxx
    ys = y1 - (np.arange(r0, r1) + 0.5) / pxy
    r = np.hypot(np.exp(ys)[:, None] - re_p, xs[None, :] - im_p)
    r = np.maximum(r, 1e-9)
    w = np.where(r < R, np.cos(0.5 * np.pi * np.minimum(r / R, 1.0)) ** 2, 0.0)
    return r0, r1, x0, x1, sgn_amp * np.log(r) * w


def kernel_R(n, grid_pxy, re_p):
    """Window radius: s-space, but at least ~4 grid rows tall locally."""
    return max(0.30 / n, 4.5 * re_p / grid_pxy)   # note: local dy = dRe/Re


def build_field(cat):
    Ff = np.load(f"ffine_{CW}.npy")
    ker = cat[cat[:, 4] <= NK]
    cpxx, cpxy = CW / (IM1 - IM0), CW / (Y1 - Y0)
    t0 = time.time()
    for re_p, im_p, amp, sgn, n, _ in ker:
        R = kernel_R(n, cpxy, re_p)
        got = kernel_patch(Ff.shape, re_p, im_p, R, sgn * amp, cpxx, cpxy, Y1)
        if got:
            r0, r1, x0, x1, p = got
            Ff[r0:r1, x0:x1] -= p
    print(f"extracted {len(ker)} kernels ({time.time()-t0:.0f}s)")
    F = ndzoom(Ff, S / CW, order=3, mode="nearest").astype(np.float32)
    del Ff
    Fd = np.load(f"fdeep_{CD}.npy")
    F += ndzoom(Fd, S / CD, order=3, mode="nearest").astype(np.float32)
    del Fd
    t0 = time.time()
    for re_p, im_p, amp, sgn, n, _ in ker:
        R = kernel_R(n, CW / (Y1 - Y0), re_p)   # SAME window as subtracted
        got = kernel_patch(F.shape, re_p, im_p, R, sgn * amp, PXX, PXY, Y1)
        if got:
            r0, r1, x0, x1, p = got
            F[r0:r1, x0:x1] += p.astype(np.float32)
    print(f"re-added kernels at fine res ({time.time()-t0:.0f}s)")
    return F


def splat(buf, px, py, amp, sig):
    n = len(px)
    if n == 0:
        return
    rad = int(np.ceil(2.7 * sig))
    ix, iy = np.round(px).astype(np.int64), np.round(py).astype(np.int64)
    H, W = buf.shape
    ok = (ix >= -rad) & (ix < W + rad) & (iy >= -rad) & (iy < H + rad)
    ix, iy, px, py = ix[ok], iy[ok], px[ok], py[ok]
    amp = np.broadcast_to(np.asarray(amp), ok.shape)[ok]
    for dy in range(-rad, rad + 1):
        yy = iy + dy
        okr = (yy >= 0) & (yy < H)
        for dx in range(-rad, rad + 1):
            xx = ix + dx
            okc = okr & (xx >= 0) & (xx < W)
            if not okc.any():
                continue
            d2 = (xx - px) ** 2 + (yy - py) ** 2
            np.add.at(buf, (yy[okc], xx[okc]),
                      (amp * np.exp(-d2 / (2 * sig * sig)))[okc].astype(buf.dtype))


def fast_bloom(x, sigma):
    ds = max(1, int(sigma / 6))
    small = gaussian_filter(x[::ds, ::ds], sigma / ds)
    return ndzoom(small, (x.shape[0] / small.shape[0], x.shape[1] / small.shape[1]),
                  order=1).astype(np.float32)


P = dict(
    kp=1.0, kn=0.8, cool_crush=2.8,
    warm=[1.00, 0.66, 0.24], warm_hi=[1.00, 0.94, 0.80],
    cool=[0.24, 0.34, 0.98], cool_hi=[0.60, 0.75, 1.00],
    cyan=[0.32, 0.95, 0.86],
    bg=[0.012, 0.014, 0.030],
    star_amp=1.5, star_gamma=0.52, glint_amp=0.5, ov_pow=0.58,
    deep_gain=2.4,
    beacon_amp=2.4, bloom_sigma=0.010, bloom_gain=0.55,
    expo=1.30, gamma=0.90,
)


def render():
    cat = sing_catalog()
    F = build_field(cat)
    H = W = S
    yfrac = (np.arange(H, dtype=np.float32) + 0.5) / H
    dg = (1 + P["deep_gain"] * smoothstep((yfrac - 0.33) / 0.45)
          + 1.8 * smoothstep((yfrac - 0.86) / 0.12))
    F *= dg[:, None]
    toe = 0.06
    pos = np.maximum(F - toe, 0)
    neg = np.maximum(-F, 0)
    warm = 1 - np.exp(-P["kp"] * pos)
    coolL = (1 - np.exp(-P["kn"] * neg)) * np.exp(-neg / P["cool_crush"])
    wramp = np.clip(pos / 2.6, 0, 1) ** 1.4
    cramp = np.clip(neg / 3.2, 0, 1) ** 1.2
    del F
    rgb = np.empty((H, W, 3), dtype=np.float32)
    for c in range(3):
        rgb[..., c] = (P["bg"][c]
                       + warm * ((1 - wramp) * P["warm"][c] + wramp * P["warm_hi"][c])
                       + coolL * ((1 - cramp) * P["cool"][c] + cramp * P["cool_hi"][c]))
    del pos, neg, warm, coolL, wramp, cramp
    stars = np.zeros((H, W), dtype=np.float32)
    glints = np.zeros((H, W), dtype=np.float32)
    rim = np.zeros((H, W), dtype=np.float32)
    px, py = s2px(cat[:, 0], cat[:, 1])
    bright = cat[:, 3] > 0
    pole = cat[:, 5] > 0
    n_of = cat[:, 4]
    # --- overlap-normalised spark ink: per line n, divide by how many
    # neighbours land in one blur footprint (horizontally on the line, and
    # vertically from adjacent strata) so the wall never stacks to white.
    ns = np.unique(n_of).astype(int)
    zcount = {int(n): int(((n_of == n) & ~pole & bright).sum()) for n in ns}
    sig_g = 0.85 * SS
    sig_s = 2.2 * SS
    amp_eff = np.zeros(len(cat))
    for n in ns:
        m = (n_of == n) & bright & ~pole
        cnt = max(zcount.get(int(n), 0), 1)
        dx_ov = max(1.0, cnt / S * 2.5 * (sig_s if n <= 10 else sig_g))
        dy_gap = PXY * 1.6 / n            # px between adjacent strata
        dy_ov = max(1.0, 2.0 * sig_g / max(dy_gap, 1e-9))
        base = (1.0 / n) ** (0.78 if n <= 10 else P["star_gamma"])
        cresc = 1 + 2.0 * smoothstep((np.log(n) - np.log(60)) /
                                     (np.log(420) - np.log(60)))
        amp_eff[m] = base * cresc / (dx_ov * dy_ov) ** P["ov_pow"]
    big = bright & ~pole & (n_of <= 10)
    small = bright & ~pole & (n_of > 10)
    splat(stars, px[big], py[big], P["star_amp"] * amp_eff[big], sig_s)
    splat(stars, px[big], py[big], 0.55 * P["star_amp"] * amp_eff[big], 1.0 * SS)
    splat(glints, px[small], py[small], P["glint_amp"] * amp_eff[small], sig_g)
    ampl = cat[:, 2] ** P["star_gamma"]
    bp = pole & bright
    splat(stars, px[bp], py[bp], P["beacon_amp"] * ampl[bp], 5.0 * SS)
    splat(stars, px[bp], py[bp], 1.2 * P["beacon_amp"] * ampl[bp], 1.8 * SS)
    dp = pole & ~bright
    ampr = cat[:, 2] ** 0.8
    splat(rim, px[dp], py[dp], 0.85 * ampr[dp], 5.5 * SS)
    splat(rim, px[dp], py[dp], -0.94 * 0.85 * ampr[dp], 3.6 * SS)
    dz = ~bright & ~pole & (n_of <= 3)
    splat(rim, px[dz], py[dz], 0.8 * ampl[dz], 4.6 * SS)
    splat(rim, px[dz], py[dz], -0.77 * ampl[dz], 3.1 * SS)
    rim = np.maximum(rim, 0)
    rgb[..., 0] += stars + glints + rim * P["cyan"][0] * 0.9
    rgb[..., 1] += stars * 0.86 + glints * 0.8 + rim * P["cyan"][1] * 0.9
    rgb[..., 2] += stars * 0.62 + glints * 0.55 + rim * P["cyan"][2] * 0.9
    del stars, glints, rim
    lum = rgb.mean(-1)
    mask = np.clip((lum - 0.75) / 0.6, 0, 1) ** 2
    bs = P["bloom_sigma"] * S
    for c in range(3):
        rgb[..., c] += P["bloom_gain"] * fast_bloom(rgb[..., c] * mask, bs)
    out = 1 - np.exp(-P["expo"] * np.maximum(rgb, 0))
    out = np.clip(out, 0, 1) ** P["gamma"]
    img = Image.fromarray((out * 255).astype(np.uint8))
    img = img.resize((FINAL, FINAL), Image.LANCZOS)
    name = "proto_wall.png" if PROTO else "wall_at_zero.png"
    img.save(name)
    print("saved", name)


if __name__ == "__main__":
    render()
