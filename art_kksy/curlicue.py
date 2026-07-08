#!/usr/bin/env python3
"""
Panel C: Curlicues — the geometry of the quadratic Weyl sum.

P_N = sum_{n<=N} exp(i pi n^2 x).  The path of partial sums looks like a
random walk, but it secretly transcribes the continued fraction of x:
each partial quotient a_k becomes a level of spirals-of-spirals
(Berry & Goldberg's renormalisation  x -> -1/x mod 2).

Numerics: n^2 x mod 2 via cumsum of increments (2n+1)x mod 2 -- exact
enough (drift ~1e-6 rad at N=1e7); never form n^2 * x directly.
"""
import numpy as np, sys, time
from math import pi, e, sqrt, log
from PIL import Image
from scipy.ndimage import gaussian_filter

def phases(x, N, chunk=8_000_000):
    """exp(i pi n^2 x) for n=0..N-1, stable at large N."""
    out = np.empty(N, np.complex128)
    carry = 0.0
    for a in range(0, N, chunk):
        b = min(a + chunk, N)
        n = np.arange(a, b, dtype=np.float64)
        d = np.mod(x * (2 * n + 1), 2.0)          # ulp fine: arg < ~1e8
        cs = np.cumsum(d)
        ph = np.mod(carry + cs - d, 2.0)          # exclusive: phi_n, n=a..b-1
        out[a:b] = np.exp(1j * np.pi * ph)
        carry = float(np.mod(carry + cs[-1], 2.0))
    return out

def path(x, N):
    z = phases(x, N)
    return np.cumsum(z)

def splat_path(P, S=1024, ss=2, qlo=0.4, qhi=99.6, pad=0.06,
               stops=None, wexp=1.0, subdiv=1):
    W = S * ss
    if subdiv > 1:
        # linear interp between successive partial sums (unit chords)
        k = np.arange(subdiv, dtype=np.float32) / subdiv
        P = (P[:-1, None] * (1 - k)[None, :] + P[1:, None] * k[None, :]).ravel()
    X, Y = P.real, P.imag
    x0, x1 = np.percentile(X, [qlo, qhi]); y0, y1 = np.percentile(Y, [qlo, qhi])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = max(x1 - x0, y1 - y0) / 2 * (1 + pad)
    scale = (W / 2 - 2) / half
    px = (X - cx) * scale + W / 2
    py = (Y - cy) * scale + W / 2

    if stops is None:
        stops = np.array([                       # non-cyclic ramp: ink->fire
            [0.10, 0.16, 0.42],   # deep blue (early)
            [0.05, 0.45, 0.55],   # teal
            [0.55, 0.85, 0.70],   # jade light
            [0.98, 0.85, 0.45],   # gold
            [1.00, 0.45, 0.15],   # ember (late)
        ])
    N = len(P)
    acc = np.zeros((W, W, 3), np.float32)
    CH = 8_000_000
    for a in range(0, N, CH):
        b = min(a + CH, N)
        x = px[a:b]; y = py[a:b]
        tt = (np.arange(a, b) / N) * (len(stops) - 1)
        i0 = np.minimum(tt.astype(np.int64), len(stops) - 2)
        f = (tt - i0)[:, None]
        col = (stops[i0] * (1 - f) + stops[i0 + 1] * f).astype(np.float32)
        xi = np.floor(x).astype(np.int64); yi = np.floor(y).astype(np.int64)
        fx = (x - xi).astype(np.float32); fy = (y - yi).astype(np.float32)
        ok = (xi >= 0) & (xi < W - 1) & (yi >= 0) & (yi < W - 1)
        xi, yi, fx, fy, col = xi[ok], yi[ok], fx[ok], fy[ok], col[ok]
        for c in range(3):
            v = col[:, c]
            np.add.at(acc[:, :, c], (yi, xi), v * (1 - fx) * (1 - fy))
            np.add.at(acc[:, :, c], (yi, xi + 1), v * fx * (1 - fy))
            np.add.at(acc[:, :, c], (yi + 1, xi), v * (1 - fx) * fy)
            np.add.at(acc[:, :, c], (yi + 1, xi + 1), v * fx * fy)
    return acc

def tone(acc, S, k=1.4, halo=0.30, blur=2.0, gamma=1.15, lum_exp=1.0):
    W = acc.shape[0]
    lum = acc.mean(2)
    p = np.percentile(lum[lum > 0], 98.5) if (lum > 0).any() else 1
    img = acc / max(p, 1e-9)
    if lum_exp != 1.0:
        # compress dynamic range: scale luminance to lum^lum_exp, keep hue
        l = img.mean(2)
        nz = l > 1e-12
        f = np.ones_like(l)
        f[nz] = l[nz] ** (lum_exp - 1.0)
        img = img * f[..., None]
    soft = np.stack([gaussian_filter(img[:, :, c], blur * W / 2048) for c in range(3)], -1)
    img = img + halo * soft
    img = 1.0 - np.exp(-k * img)
    img = img ** (1 / gamma)
    return Image.fromarray((img.clip(0, 1) * 255).astype(np.uint8)[::-1]).resize(
        (S, S), Image.LANCZOS)

XS = {
    "pi":    pi,
    "e":     e,
    "sqrt2": sqrt(2),
    "phi":   (1 + sqrt(5)) / 2,
    "gamma": 0.5772156649015329,
    "ln2":   log(2),
    "cbrt2": 2 ** (1 / 3),
    "champ": 0.123456789101112131415,
}

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    names = sys.argv[3].split(",") if len(sys.argv) > 3 else list(XS)
    for nm in names:
        t0 = time.time()
        P = path(XS[nm], N)
        acc = splat_path(P, S=S)
        tone(acc, S).save(f"draft_curl_{nm}_{S}.png")
        print(nm, f"{time.time()-t0:.1f}s extent~{np.ptp(P.real):.0f}")
