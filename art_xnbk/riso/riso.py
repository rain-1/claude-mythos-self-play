"""Risograph print simulator.

Each ink layer is a coverage map in [0,1]. It is screened (rotated AM halftone
or stochastic grain), shifted by a small misregistration, mottled like a drum
that ran a little dry, and multiplied over paper (riso inks are translucent,
so overlaps mix subtractively: pink x aqua = lavender).
"""
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

INKS = {  # sRGB of a solid on white
    'fluo_pink': (255, 72, 176), 'aqua': (94, 200, 229), 'yellow': (255, 232, 0),
    'sunflower': (255, 181, 0), 'mint': (130, 216, 213), 'lavender': (165, 146, 220),
    'coral': (255, 116, 119), 'cornflower': (98, 168, 229), 'green': (0, 169, 92),
    'orange': (255, 108, 47), 'violet': (157, 122, 210), 'plum': (132, 89, 145),
}

def lin(c):
    c = np.asarray(c, np.float32) / 255
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)

def noise(H, W, sigma, rng):
    n = gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), sigma)
    return n / (n.std() + 1e-9)

def paper(H, W, rng, base=(0.992, 0.985, 0.975)):
    g = 0.012 * noise(H, W, 0.8, rng) + 0.008 * noise(H, W, 6, rng)
    fib = 0.006 * noise(H, W, 1.2, rng)
    p = np.ones((H, W, 3), np.float32) * np.array(base, np.float32)
    p += (g + fib)[..., None]
    return np.clip(p, 0, 1)

def screen(cov, angle_deg, cell, rng, kind='am', soft=0.9):
    """returns ink fraction per pixel (0..1) from coverage map"""
    H, W = cov.shape
    if kind == 'grain':
        t = rng.random((H, W)).astype(np.float32)
        t = gaussian_filter(t, 0.6); t = (t - t.min()) / (t.max() - t.min())
        return np.clip((cov - t) / 0.08 + 0.5, 0, 1)
    a = np.radians(angle_deg)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (x * np.cos(a) + y * np.sin(a)) / cell
    v = (-x * np.sin(a) + y * np.cos(a)) / cell
    fu = u - np.floor(u) - 0.5; fv = v - np.floor(v) - 0.5
    # round dot that grows into a checkerboard-ish chain at 50%
    d = np.sqrt(fu * fu + fv * fv)  # 0..0.707
    r = np.sqrt(np.clip(cov, 0, 1) / np.pi)  # radius giving area=cov for small cov
    # beyond 0.5 use the complement dot so 100% is solid
    hi = cov > 0.5
    d2 = np.sqrt((0.5 - np.abs(fu)) ** 2 + (0.5 - np.abs(fv)) ** 2)
    lo_ink = np.clip((r - d) * cell / soft + 0.5, 0, 1)
    hole = np.sqrt(np.clip(1 - cov, 0, 1) / np.pi)
    hi_ink = 1 - np.clip((hole - d2) * cell / soft + 0.5, 0, 1)
    return np.where(hi, hi_ink, lo_ink)

def shift(img, dx, dy, rot=0.0):
    H, W = img.shape
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    c, s = np.cos(rot), np.sin(rot)
    xs = c * (x - cx) - s * (y - cy) + cx - dx
    ys = s * (x - cx) + c * (y - cy) + cy - dy
    return map_coordinates(img, [ys, xs], order=1, mode='constant', cval=0)

def print_riso(layers, H, W, seed=1, paper_base=(0.992, 0.985, 0.975), misreg=3.0, density=0.92):
    """layers: list of dict(ink=name|rgb, cov=array, angle, cell, kind)"""
    rng = np.random.default_rng(seed)
    out = paper(H, W, rng, paper_base)
    for L in layers:
        ink = L['ink']; ink = INKS[ink] if isinstance(ink, str) else ink
        col = lin(ink)
        cov = L['cov'].astype(np.float32)
        frac = screen(cov, L.get('angle', 15), L.get('cell', 7.0), rng, L.get('kind', 'am'))
        # drum mottle + starved edges
        mott = 1 - 0.10 * np.clip(noise(H, W, L.get('mottle_sigma', 18), rng), -2, 2) * 0.5 \
                 - 0.05 * np.clip(noise(H, W, 2.0, rng), -2, 2) * 0.5
        frac = frac * np.clip(mott, 0, 1) * L.get('density', density)
        if misreg:
            frac = shift(frac, rng.normal(0, misreg), rng.normal(0, misreg), rng.normal(0, 0.0012))
        # translucent: multiply
        out = out * (1 - frac[..., None] * (1 - col))
    return srgb(out)
