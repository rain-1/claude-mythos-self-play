"""Paper-cut stack of the covering depth: sheet k = {D >= k}; shadows marched in the height field."""
import numpy as np
from numba import njit, prange
from scipy.ndimage import gaussian_filter


@njit(parallel=True, cache=True)
def shadow(H, dx, dy, slope, maxs):
    Hh, Ww = H.shape
    out = np.zeros((Hh, Ww), np.float32)
    for j in prange(Hh):
        for i in range(Ww):
            h0 = H[j, i]
            occ = 0.0
            for s in range(1, maxs):
                x = i + dx * s; y = j + dy * s
                ii = int(x); jj = int(y)
                if ii < 0 or jj < 0 or ii >= Ww or jj >= Hh:
                    break
                e = H[jj, ii] - (h0 + slope * s)
                if e > 0:
                    occ = max(occ, min(1.0, e / 2.0))
                    if occ >= 1.0:
                        break
            out[j, i] = occ
    return out


def lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)


WHEEL = [[0.70, 0.93, 0.84], [0.72, 0.86, 1.0], [0.84, 0.78, 1.0], [1.0, 0.76, 0.88], [1.0, 0.80, 0.72], [1.0, 0.92, 0.66], [1.0, 0.98, 0.86]]


def wheel(t):
    t = np.clip(t, 0, 1) * (len(WHEEL) - 1)
    i = np.minimum(t.astype(int), len(WHEEL) - 2)
    f = (t - i)[..., None]
    a = lin(np.array(WHEEL))
    return np.exp(np.log(a[i]) * (1 - f) + np.log(a[i + 1]) * f)


def render(D, thick, light=(-0.6, -0.8), elev=0.75, ss_px=1.0, paper=(0.99, 0.982, 0.972), cidx=None):
    """D: int depth (−1 outside disc). returns linear rgb."""
    m = D.max()
    H = np.where(D < 0, 0, D + 1).astype(np.float32) * thick   # disc base sheet + levels
    dx, dy = light
    nrm = np.hypot(dx, dy); dx /= nrm; dy /= nrm
    slope = np.tan(elev)
    sh = shadow(H, dx, dy, slope, int(H.max() / slope) + 4)
    sh = gaussian_filter(sh, 2.5 * ss_px)
    # paper edge highlight: lit edges where height steps toward the light
    Hb = gaussian_filter(H, 0.9 * ss_px)
    gy, gx = np.gradient(Hb)
    ed = np.clip(-(gx * dx + gy * dy) / thick, -1, 1)
    lvl = np.where(D < 0, -1, D)
    col = wheel((np.maximum(lvl, 0) / max(m, 1)) ** 0.85 if cidx is None else cidx)
    col[D < 0] = lin(paper)
    # alternate sheets slightly lighter / deeper so neighbouring layers separate
    alt = np.where(lvl % 2 == 0, 1.0, 0.955)
    col = col * alt[..., None]
    ao = 1 - 0.05 * np.clip(gaussian_filter(H, 6 * ss_px) - H, 0, None) / thick
    L = (np.where(D < 0, 1.0, 0.97) + 0.16 * np.clip(ed, 0, 1) - 0.05 * np.clip(-ed, 0, 1)) * ao
    shadow_tint = lin([0.86, 0.84, 0.97])
    out = col * L[..., None]
    out = out * (1 - 0.30 * sh[..., None]) + out * shadow_tint * 0.30 * sh[..., None] if False else out
    out = out * (1 - sh[..., None] * (1 - shadow_tint * 0.92) * 0.55)
    return out
