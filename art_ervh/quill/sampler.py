"""Hero sampler: quilled unit-side polygons in unit squares, one tile the square itself."""
import numpy as np, json, sys, time
from PIL import Image
from scipy import ndimage as ndi
import quill as Q, tiles as T

def rounded_rect(shape, x0, y0, x1, y1, rad):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]] + 0.5
    dx = np.maximum(np.maximum(x0 + rad - xx, xx - (x1 - rad)), 0)
    dy = np.maximum(np.maximum(y0 + rad - yy, yy - (y1 - rad)), 0)
    d = np.sqrt(dx * dx + dy * dy) - rad
    return np.clip(0.5 - d, 0, 1)

def build(polys, cols, rows, S, gx, gy_, tilt, k, margin_top, exception_idx, W_world, H_world,
          table_top=(0.86,0.87,0.99), table_bot=(0.99,0.86,0.89), seed=0):
    cs = np.cos(np.radians(tilt))
    Sy = S / cs
    H, A = T.card((H_world, W_world), seed)
    yy = np.linspace(0, 1, H_world)[:, None, None]
    A[:] = (np.array(table_top) * (1 - yy) + np.array(table_bot) * yy).astype(np.float32)
    A *= (1 - 0.02 * ndi.gaussian_filter(np.random.default_rng(seed).random((H_world, W_world)), 1.0)[..., None]).astype(np.float32)
    G = np.zeros((H_world, W_world), np.float32)
    plate = np.zeros((H_world, W_world), np.float32)
    x_start = (W_world - (cols * S + (cols - 1) * gx)) / 2
    cardpad = 0.06 * S
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        ox = x_start + c * (S + gx); oy = margin_top + r * (Sy + gy_)
        m = rounded_rect(plate.shape, ox - cardpad, oy - cardpad / cs, ox + S + cardpad, oy + Sy + cardpad / cs, 10 * k)
        plate = np.maximum(plate, m)
        A[:] = A * (1 - m[..., None]) + np.array([0.992, 0.99, 0.985], np.float32) * m[..., None]
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        ox = x_start + c * (S + gx); oy = margin_top + r * (Sy + gy_)
        warm, cool = cols_of(i)
        if i == exception_idx:
            T.tile(H, A, np.zeros((4, 2)), ox, oy, S, (1, 0.8, 0.6), [(1.0, 0.86, 0.56)], frame_col=(0.98, 0.42, 0.42),
                   exception=True, Sy=Sy, hgt=24 * k, wall=5.0 * k, pitch=0.06 * S, sw=2.3 * k, smooth=8 * k, G=G)
        else:
            T.tile(H, A, polys[i], ox, oy, S, warm, cool, Sy=Sy, hgt=24 * k, wall=3.2 * k, pitch=0.06 * S, sw=2.3 * k,
                   smooth=8 * k, G=G)
    H += plate * 3.5 * k
    return H, A, G

WARMS = [(1.0, 0.64, 0.62), (1.0, 0.74, 0.56), (1.0, 0.86, 0.52), (1.0, 0.68, 0.80), (0.99, 0.62, 0.70), (1.0, 0.80, 0.64)]
COOLS = [(0.60, 0.82, 1.0), (0.64, 0.92, 0.80), (0.74, 0.72, 1.0), (0.86, 0.72, 0.98), (0.60, 0.90, 0.92), (0.78, 0.92, 0.64)]
def cols_of(i):
    w = WARMS[i % len(WARMS)]
    j = (i * 2) % len(COOLS)
    return w, COOLS[j:] + COOLS[:j]
