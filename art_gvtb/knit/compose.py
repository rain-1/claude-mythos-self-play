"""Flat-lay: a Fair-Isle swatch of Gaussian tiles on a whitewashed table.
python3 compose.py SIZE out.png"""
import numpy as np, sys
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont
from knit import render_knit, srgb2lin
from design import design, WHEEL, CREAM


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)


def table(H, W, s, rng):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # pale whitewashed oak planks running horizontally
    plank = (y / (H / 4.6)).astype(int)
    n1 = ndimage.gaussian_filter(rng.standard_normal((H // 8 + 1, W // 64 + 1)).astype(np.float32), (1.0, 2.0))
    n1 = np.kron(n1, np.ones((8, 64), np.float32))[:H, :W]
    grain = np.sin(y * 0.09 / s + 3 * n1 + plank * 1.7) * 0.5 + 0.5
    grain = grain ** 6
    base = srgb2lin([0.955, 0.925, 0.915]) * np.ones((H, W, 3), np.float32)
    tint = srgb2lin([0.86, 0.80, 0.82])
    g = 0.10 * grain[..., None]
    out = base * (1 - g) + tint * g
    # plank seams
    seam = np.abs((y / (H / 4.6)) % 1 - 0.0)
    seam = np.exp(-((y % (H / 4.6)) / (2.2 * s)) ** 2)
    out *= (1 - 0.18 * seam)[..., None]
    # soft window light from upper left
    vign = 1.04 - 0.10 * ((x / W - 0.25) ** 2 + (y / H - 0.2) ** 2)
    return out * vign[..., None]


def place(canvas, rgb, a, x0, y0):
    h, w = a.shape
    sl = (slice(y0, y0 + h), slice(x0, x0 + w))
    canvas[sl] = rgb * a[..., None] + canvas[sl] * (1 - a[..., None])


def rotate(img, ang, order=1):
    return ndimage.rotate(img, ang, axes=(1, 0), reshape=True, order=order, mode='constant')


def needle(H, W, p0, p1, r, col, knob, s):
    """A wooden knitting needle as a shaded capsule with a tapered tip and a bead knob."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    e = p1 - p0; L = np.linalg.norm(e); e /= L
    nrm = np.array([-e[1], e[0]])
    t = (x - p0[0]) * e[0] + (y - p0[1]) * e[1]
    q = (x - p0[0]) * nrm[0] + (y - p0[1]) * nrm[1]
    tt = t / L
    rad = r * np.clip(np.where(tt > 0.86, 1 - (tt - 0.86) / 0.14 * 0.85, 1.0), 0.15, 1)
    inside = (tt >= 0) & (tt <= 1) & (np.abs(q) < rad)
    u = q / rad
    z = np.sqrt(np.clip(1 - u * u, 0, 1))
    shade = 0.55 + 0.45 * np.clip(-u * 0.6 + z * 0.8, 0, 1) + 0.25 * np.clip(z - 0.75, 0, 1) * (u < 0)
    wood = srgb2lin(col) * (0.95 + 0.05 * np.sin(t / (3.0 * s)))[..., None]
    rgb = wood * shade[..., None]
    a = inside.astype(np.float32)
    # knob
    kc = p0 - e * r * 1.2
    d = np.hypot(x - kc[0], y - kc[1]) / (r * 2.1)
    kin = d < 1
    kz = np.sqrt(np.clip(1 - d * d, 0, 1))
    ksh = 0.5 + 0.5 * np.clip((-(x - kc[0]) - (y - kc[1])) / (r * 2.1) * 0.5 + kz * 0.7, 0, 1)
    ksh += 0.35 * np.clip(kz - 0.8, 0, 1) * ((x - kc[0]) < 0)
    rgb = np.where(kin[..., None], srgb2lin(knob) * ksh[..., None], rgb)
    a = np.maximum(a, kin.astype(np.float32))
    a = ndimage.gaussian_filter(a, 0.7)
    return rgb, a


def yarn_ball(Rpx, col, seed, s):
    rng = np.random.default_rng(seed)
    n = 2 * Rpx + 4
    y, x = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
    rr = np.sqrt(x * x + y * y) / Rpx
    inside = rr < 1
    z = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    P = np.stack([x / Rpx, y / Rpx, z], -1)
    lam = np.clip(P[..., 0] * -0.5 + P[..., 1] * -0.55 + P[..., 2] * 0.67, 0, 1)
    tex = np.zeros((n, n), np.float32); grv = np.zeros((n, n), np.float32)
    axes = [rng.standard_normal(3) for _ in range(9)]
    for k, ax in enumerate(axes):
        ax = ax / np.linalg.norm(ax)
        ang = np.arcsin(np.clip(P @ ax, -1, 1))
        lay = (np.abs(P @ ax) < 0.5) | (k == 0)
        ph = ang * Rpx / (15.0 * s)
        fr = ph - np.floor(ph)
        prof = np.sqrt(np.clip(1 - ((fr - 0.5) * 2) ** 2, 0, 1))  # round strand
        # ply twist along the strand
        az = np.arctan2(P @ np.cross(ax, [0.3, 0.2, 0.9]), P @ np.cross(ax, np.cross(ax, [0.3, 0.2, 0.9])))
        tw = 0.85 + 0.15 * np.cos(2 * np.pi * (az * Rpx / (9.0 * s) + 2.0 * fr))
        tex = np.where(lay, prof * tw, tex)
        grv = np.where(lay, 1.0, grv)
    shade = (0.45 + 0.65 * lam) * (0.55 + 0.45 * tex)
    rgb = srgb2lin(col) * shade[..., None]
    a = np.clip((1 - rr) * Rpx / 1.5, 0, 1) * inside
    return rgb.astype(np.float32), a.astype(np.float32)


def main(S, out):
    s = S / 4096
    rng = np.random.default_rng(4)
    C, info = design(W=73, bands=5, bh=13, gap=4)
    # cream garter edges top and bottom
    w = 40 * s
    rgb, a, hgt, pad = render_knit(C, w=w, seed=2)
    # fabric is a little soft: gaps are shadowed yarn
    under = ndimage.gaussian_filter(rgb, (w * 0.25, w * 0.25, 0))
    rgb = rgb + (1 - a[..., None]) * under * 0.55
    a2 = np.clip(ndimage.gaussian_filter(a, w * 0.3) * 1.6, 0, 1)
    a = np.maximum(a, a2 * (ndimage.binary_fill_holes(a2 > 0.5)))
    ang = -3.5
    rgbR = np.stack([rotate(rgb[..., c], ang) for c in range(3)], -1)
    aR = np.clip(rotate(a, ang), 0, 1)
    H = W = S
    canvas = table(H, W, s, rng)
    # drop shadow
    hh, ww = aR.shape
    x0 = int((W - ww) / 2 - 150 * s); y0 = int(360 * s)
    sh = np.zeros((H, W), np.float32)
    sh[y0:y0 + hh, x0:x0 + ww] = aR
    sh = ndimage.shift(ndimage.gaussian_filter(sh, 26 * s), (22 * s, 16 * s), order=1)
    shc = srgb2lin([0.62, 0.58, 0.72])
    canvas = canvas * (1 - 0.42 * sh[..., None]) + canvas * shc * 0.42 * sh[..., None]
    place(canvas, rgbR, aR, x0, y0)
    # yarn ball + strand to the swatch
    R = int(235 * s)
    yb, ya = yarn_ball(R, [0.80, 0.66, 0.95], 3, s)
    bx, by = int(W - 120 * s - 2 * R), int(250 * s)
    bsh = np.zeros((H, W), np.float32)
    bsh[by:by + ya.shape[0], bx:bx + ya.shape[1]] = ya
    bsh = ndimage.shift(ndimage.gaussian_filter(bsh, 30 * s), (30 * s, 26 * s), order=1)
    canvas = canvas * (1 - 0.40 * bsh[..., None]) + canvas * shc * 0.40 * bsh[..., None]
    # strand: a quadratic curve from the ball to the swatch's lower edge
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    P0 = np.array([bx + R * 0.5, by + R * 1.8]); P2 = np.array([x0 + ww * 0.975, y0 + 215 * s]); P1 = np.array([bx + R * 0.2, y0 + 330 * s])
    ts = np.linspace(0, 1, 400)
    pts = (1 - ts)[:, None] ** 2 * P0 + 2 * ((1 - ts) * ts)[:, None] * P1 + ts[:, None] ** 2 * P2
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    dr.line([tuple(p) for p in pts], fill=255, width=max(2, int(11 * s)), joint='curve')
    st = np.asarray(img, np.float32) / 255
    st = ndimage.gaussian_filter(st, 0.8 * s)
    stsh = ndimage.shift(ndimage.gaussian_filter(st, 6 * s), (8 * s, 6 * s), order=1)
    canvas *= (1 - 0.3 * stsh[..., None])
    canvas = canvas * (1 - st[..., None]) + srgb2lin([0.80, 0.66, 0.95]) * 0.9 * st[..., None]
    place(canvas, yb, ya, bx, by)
    # needles across the top edge (the live row)
    for (p0, p1, kn) in (((x0 - ww * 0.05, y0 + 58 * s), (x0 + ww * 0.97, y0 + 6 * s - ww * 0.0), [0.98, 0.62, 0.70]),
                         ((x0 + ww * 0.80, y0 - 170 * s), (x0 + ww * 0.08, y0 + 95 * s), [0.62, 0.82, 0.98])):
        nr, na = needle(H, W, p0, p1, 17 * s, [0.93, 0.82, 0.66], kn, s)
        nsh = ndimage.shift(ndimage.gaussian_filter(na, 10 * s), (14 * s, 10 * s), order=1)
        canvas *= (1 - 0.35 * nsh[..., None])
        canvas = canvas * (1 - na[..., None]) + nr * na[..., None]
    np.save(out.replace('.png', '.npy'), canvas.astype(np.float32))
    Image.fromarray((to_srgb(canvas) * 255 + 0.5).astype(np.uint8)).save(out)
    print('swatch box', x0, y0, ww, hh)


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2])
