"""Sand art in a glass frame: one poured layer per alpha, thickness = stationary density of Y.
python3 sand.py SIZE out.png"""
import numpy as np, sys
from scipy import ndimage
from PIL import Image

WHEEL = np.array([
    [0.98, 0.55, 0.62], [1.00, 0.72, 0.55], [1.00, 0.88, 0.52], [0.74, 0.90, 0.52],
    [0.52, 0.87, 0.73], [0.53, 0.79, 0.97], [0.62, 0.65, 0.97], [0.80, 0.61, 0.94],
    [0.97, 0.59, 0.84]])
CORAL = np.array([0.98, 0.45, 0.40])


def lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)


def wheel(t):
    t = (t % 1) * len(WHEEL); i = int(t); f = t - i
    a = WHEEL[i % len(WHEEL)]; b = WHEEL[(i + 1) % len(WHEEL)]
    return np.exp(np.log(a) * (1 - f) + np.log(b) * f)


def layers(step=2, gamma=0.40, smooth=1.5):
    d = np.load('../math_fib/stationary.npz')
    al = d['alphas']; Hh = d['hist_log']
    out = []
    for i in range(0, len(al), step):
        g = ndimage.gaussian_filter1d(Hh[i], smooth * 4)
        g = np.clip(g, 0, None) ** gamma
        out.append((al[i], g / g.mean()))
    return out, d


def main(S, out, seed=1):
    s = S / 4096
    rng = np.random.default_rng(seed)
    H = W = S
    # wall
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    canvas = lin([0.975, 0.955, 0.95]) * np.ones((H, W, 3), np.float32)
    canvas *= (1.02 - 0.06 * ((xx / W - 0.4) ** 2 + (yy / H - 0.3) ** 2))[..., None]
    # frame geometry
    fx0, fx1 = int(330 * s), int(W - 330 * s)
    fy0, fy1 = int(260 * s), int(3330 * s)
    bw = int(120 * s)                    # wooden border width
    ix0, ix1, iy0, iy1 = fx0 + bw, fx1 - bw, fy0 + bw, fy1 - bw
    IW, IH = ix1 - ix0, iy1 - iy0
    # shadow of the frame on the wall
    m = np.zeros((H, W), np.float32); m[fy0:fy1, fx0:fx1] = 1
    sh = ndimage.shift(ndimage.gaussian_filter(m, 40 * s), (36 * s, 24 * s), order=1)
    canvas *= (1 - 0.30 * sh)[..., None] * 1 + 0
    canvas = canvas * (1 - 0.0 * sh[..., None])
    # --- sand ---
    L, d = layers()
    n = len(L)
    X = np.linspace(0, 1, IW)
    # backing card: a pale dawn sky
    v = np.linspace(0, 1, IH)[:, None]
    sky = (lin([0.70, 0.80, 1.00]) * (1 - v[..., None]) ** 1.2 + lin([1.0, 0.93, 0.90]) * (1 - (1 - v[..., None]) ** 1.2))
    sand = np.broadcast_to(sky, (IH, IW, 3)).copy()
    # a soft butter sun
    sy_, sx_ = np.mgrid[0:IH, 0:IW]
    rr = np.hypot(sx_ - IW * 0.2, sy_ - IH * 0.2) / (IH * 0.075)
    disc = np.clip((1 - rr) * 30, 0, 1)
    halo = np.exp(-np.maximum(rr - 1, 0) * 1.2) * 0.35 * (rr > 1)
    sand = sand * (1 - disc[..., None]) + lin([1.0, 0.93, 0.70]) * disc[..., None]
    sand = sand + halo[..., None] * (lin([1.0, 0.96, 0.86]) - sand) 
    total = 0.80 * IH
    base = np.zeros(IW)
    gk = max(2, int(round(3.2 * s)))
    grain = rng.standard_normal((IH // gk + 2, IW // gk + 2)).astype(np.float32)
    grain = np.kron(grain, np.ones((gk, gk), np.float32))[:IH, :IW]
    grain = ndimage.gaussian_filter(grain, 0.6)
    grain2 = ndimage.gaussian_filter(rng.standard_normal((IH, IW)).astype(np.float32), 1.0 * max(1, s * 2))
    grain2 /= grain2.std()
    lid = np.full((IH, IW), -1, np.int32)
    ystar = None
    alpha_star = 0.9041921190624
    tops = []
    edge_noise = ndimage.gaussian_filter1d(rng.standard_normal((n + 2, IW)), 2.0, axis=1) * 2.5 * s
    ssum = np.zeros(IW)
    for k, (a, g) in enumerate(L):
        ssum += np.interp(X * (len(g) - 1), np.arange(len(g)), g) / n
    total = 0.60 * IH / np.quantile(ssum, 0.5)
    raw = ssum * total
    hmax = 0.90 * IH
    comp = np.where(raw > 0, hmax * np.tanh(raw / hmax) / np.maximum(raw, 1e-9), 1.0)
    for k, (a, g) in enumerate(L):
        prof = np.interp(X * (len(g) - 1), np.arange(len(g)), g)
        t = prof * total / n * comp
        # thin white separator every few layers, coral seam at alpha*
        newbase = base + t
        top = newbase + edge_noise[k]
        rows_b = IH - 1 - base
        rows_t = IH - 1 - top
        mask = (np.arange(IH)[:, None] <= rows_b[None, :]) & (np.arange(IH)[:, None] > rows_t[None, :])
        lid[mask] = k
        tops.append(top.copy())
        if ystar is None and a > alpha_star:
            ystar = k
        base = newbase
    # colours per layer
    cols = []
    for k, (a, g) in enumerate(L):
        c = wheel(0.42 + 0.95 * k / n)
        if k % 2 == 1:
            c = c * 0.62 + np.array([1, 1, 1]) * 0.38
        if k % 6 == 5:
            c = np.array([0.99, 0.975, 0.95])
        cols.append(c)
    cols = np.array(cols)
    if ystar is not None:
        cols[ystar] = CORAL
    cl = lin(cols)
    have = lid >= 0
    base_rgb = cl[np.clip(lid, 0, n - 1)]
    # grains: mixed brightness + a few coloured speckles from neighbouring layers
    gb = 1 + 0.09 * grain + 0.04 * grain2
    sp = np.kron(rng.random((IH // gk + 2, IW // gk + 2)), np.ones((gk, gk)))[:IH, :IW]
    nb = cl[np.clip(lid + rng.integers(-2, 3, (IH, IW)), 0, n - 1)]
    rgbS = np.where((sp < 0.06)[..., None], nb, base_rgb) * gb[..., None]
    white = (sp > 0.985)
    rgbS = np.where(white[..., None], lin([1, 0.99, 0.97]), rgbS)
    # tiny relief so grains catch the light from upper left
    relief = ndimage.gaussian_filter(grain, 0.7)
    lit = 1 + 0.06 * (np.roll(relief, 1, 0) - relief + np.roll(relief, 1, 1) - relief)
    rgbS *= lit[..., None]
    sand = np.where(have[..., None], rgbS, sand)
    # inner shadow on the sand from the frame lip
    inner = np.ones((IH, IW), np.float32)
    inner[:int(30 * s), :] = 0; inner[:, :int(30 * s)] = 0; inner[:, -int(8 * s):] = 0
    inner = ndimage.gaussian_filter(inner, 28 * s)
    sand *= (0.80 + 0.20 * inner)[..., None]
    # glass sheen: two soft diagonal bands
    u = (np.arange(IW)[None, :] / IW + np.arange(IH)[:, None] / IH * 0.55)
    sheen = 0.07 * np.exp(-((u - 0.35) / 0.05) ** 2) + 0.04 * np.exp(-((u - 0.47) / 0.015) ** 2)
    sand = sand * (1 - sheen[..., None]) + sheen[..., None] * 1.0
    canvas[iy0:iy1, ix0:ix1] = sand
    # wooden frame: pale birch with a bevel
    fr = np.zeros((H, W), bool); fr[fy0:fy1, fx0:fx1] = True; fr[iy0:iy1, ix0:ix1] = False
    dx = np.minimum(np.abs(xx - fx0), np.abs(xx - fx1)); dy = np.minimum(np.abs(yy - fy0), np.abs(yy - fy1))
    dxi = np.minimum(np.abs(xx - ix0), np.abs(xx - ix1)); dyi = np.minimum(np.abs(yy - iy0), np.abs(yy - iy1))
    dist_out = np.minimum(dx, dy); dist_in = np.minimum(dxi, dyi)
    # mitred bevel: brightness by which side the pixel belongs to
    dd = np.stack([xx - fx0, yy - fy0, fx1 - xx, fy1 - yy])
    side = np.argmin(dd, 0)
    left = side == 0; top_ = side == 1; right = side == 2
    side_sh = np.choose(side, [1.0, 1.06, 0.86, 0.80])
    prof = np.clip(np.minimum(dist_out, dist_in) / (bw * 0.5), 0, 1)
    bevel = 0.92 + 0.10 * np.sin(np.pi * np.clip(dist_out / bw, 0, 1))
    woodn = ndimage.gaussian_filter1d(rng.standard_normal(W).astype(np.float32), 3)
    woodv = ndimage.gaussian_filter1d(rng.standard_normal(H).astype(np.float32), 3)
    grainw = np.where(top_ | (~left & ~right), woodv[:, None] * np.ones((1, W)), woodn[None, :] * np.ones((H, 1)))
    wood = lin([0.95, 0.88, 0.80]) * (side_sh * bevel * (1 + 0.025 * grainw))[..., None]
    canvas = np.where(fr[..., None], wood, canvas)
    # thin inner lip line
    lip = fr & (dist_in < 6 * s)
    canvas = np.where(lip[..., None], canvas * 0.86, canvas)
    np.save(out.replace('.png', '.npy'), canvas.astype(np.float32))
    Image.fromarray((to_srgb(canvas) * 255 + 0.5).astype(np.uint8)).save(out)
    print('layers', n, 'coral layer', ystar, L[ystar][0] if ystar is not None else None)


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2])
