"""Print-Gallery (Droste) twist of a picture that contains itself.

base: an image (N x N) in which the square `canvas` (x0, y0, side) must show the
whole image again.  Self-similarity centre f satisfies canvas = f + s (image - f).
Twist: output z -> w = log z, source = exp(w * beta), beta = 1 - i L / 2pi, L = ln(1/s):
going once round the output centre goes once round AND one canvas deeper.
"""
import numpy as np
from scipy.ndimage import map_coordinates

def fixed_point(N, x0, y0, side):
    s = side / N
    return np.array([x0 / (1 - s), y0 / (1 - s)]), s

def sample(base, xs, ys):
    out = np.zeros(xs.shape + (base.shape[2],), np.float32)
    for c in range(base.shape[2]):
        out[..., c] = map_coordinates(base[..., c], [ys, xs], order=1, mode='nearest')
    return out

def twist(base, canvas, M, zoom=1.0, rot=0.0, ss=2, twist=True, centre_out=None, strands=1):
    N = base.shape[0]
    x0, y0, side = canvas
    f, s = fixed_point(N, x0, y0, side)
    L = np.log(1 / s)
    beta = strands - 1j * L / (2 * np.pi) if twist else 1.0
    acc = np.zeros((M, M, base.shape[2]), np.float32)
    cx, cy = (M / 2, M / 2) if centre_out is None else centre_out
    for sy in range(ss):
        for sx in range(ss):
            yy, xx = np.mgrid[0:M, 0:M].astype(np.float64)
            z = ((xx + (sx + 0.5) / ss - cx) + 1j * (yy + (sy + 0.5) / ss - cy)) / M * N / zoom
            z = z * np.exp(1j * rot)
            z[z == 0] = 1e-9
            w = np.log(z) * beta
            p = np.exp(w)  # relative to f, in base pixels
            # fold into the fundamental region: inside the image but not inside the canvas
            for _ in range(80):
                X = f[0] + p.real; Y = f[1] + p.imag
                out = (X < 0) | (X >= N - 1) | (Y < 0) | (Y >= N - 1)
                inn = (X > x0 + 1) & (X < x0 + side - 1) & (Y > y0 + 1) & (Y < y0 + side - 1)
                if not out.any() and not inn.any(): break
                p = np.where(out, p * s, np.where(inn, p / s, p))
            X = f[0] + p.real; Y = f[1] + p.imag
            acc += sample(base, X, Y)
    return acc / (ss * ss)
