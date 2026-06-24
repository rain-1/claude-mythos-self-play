"""Piece 3 — "Legendre's Lacunae" (sums of three squares).

Legendre/Gauss three-square theorem: a non-negative integer n is a sum of three
squares iff n is NOT of the form 4^a (8b + 7). Those excluded numbers form a
self-similar (4-adic) set of holes. We lay the integers 0..side^2-1 along a
Hilbert curve and color each by r3(n) = number of representations as an ordered
signed sum of three squares (coefficient of q^n in theta(q)^3). The
non-representable numbers carve a fractal of voids out of the glowing field.
"""
import sys, numpy as np
sys.path.insert(0, "src")
import render as R


def r3_via_theta(Nmax, dtype=np.float32):
    """r3(n) for n in [0, Nmax] via theta(q)^3, theta = 1 + 2 sum q^{k^2}.
    Uses linear convolution (FFT) with no aliasing into [0, Nmax]."""
    from scipy.fft import rfft, irfft, next_fast_len
    theta = np.zeros(Nmax + 1, dtype=dtype)
    theta[0] = 1.0
    ks = np.arange(1, int(np.floor(np.sqrt(Nmax))) + 1)
    theta[ks * ks] = 2.0
    L = next_fast_len(3 * Nmax + 1)
    A = rfft(theta, n=L)
    cube = irfft(A * A * A, n=L)[:Nmax + 1]
    return np.rint(cube).astype(np.int64)


def morton_xy(side):
    """Z-order (Morton) coords: n's even bits -> x, odd bits -> y. Multiplying
    n by 4 shifts both x and y by one bit -> the 4-adic factor 4^a becomes a
    spatial zoom, so the 4^a(8b+7) exclusion set is self-similar in 2D."""
    n_total = side * side
    n = np.arange(n_total, dtype=np.int64)
    x = np.zeros(n_total, dtype=np.int64)
    y = np.zeros(n_total, dtype=np.int64)
    bit = 0
    shift = 0
    while (1 << (2 * shift)) < n_total:
        x |= ((n >> (2 * shift)) & 1) << shift
        y |= ((n >> (2 * shift + 1)) & 1) << shift
        shift += 1
    return x, y


def hilbert_xy(side):
    """Return x[n], y[n] pixel coords for n in [0, side*side) along a Hilbert
    curve. side must be a power of two."""
    n_total = side * side
    idx = np.arange(n_total, dtype=np.int64)
    x = np.zeros(n_total, dtype=np.int64)
    y = np.zeros(n_total, dtype=np.int64)
    t = idx.copy()
    s = 1
    while s < side:
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        # rotate
        swap = ry == 0
        # where rx == 1: reflect
        refl = swap & (rx == 1)
        x[refl] = s - 1 - x[refl]
        y[refl] = s - 1 - y[refl]
        # swap x,y where ry==0
        xs = x.copy()
        x[swap] = y[swap]
        y[swap] = xs[swap]
        x += s * rx
        y += s * ry
        t //= 4
        s *= 2
    return x, y


def main(side=512, out="out/p3_legendre.png", down=None, layout="hilbert",
         palette=R.PAL_EMBER, k=2.0, gamma=1.0, detrend=True):
    Nmax = side * side - 1
    print("computing r3 up to", Nmax)
    r3 = r3_via_theta(Nmax)
    n = np.arange(side * side)
    if detrend:
        # r3(n) grows ~ sqrt(n) on average; divide it out to expose the
        # stationary arithmetic fluctuation (class-number texture + holes).
        val = r3.astype(np.float64) / np.sqrt(n + 8.0)
    else:
        val = np.log1p(r3.astype(np.float64))
    mask = r3 > 0                                   # representable

    img = np.zeros((side, side), dtype=np.float64)
    voidmask = np.zeros((side, side), dtype=bool)
    if layout == "hilbert":
        x, y = hilbert_xy(side)
    elif layout == "morton":
        x, y = morton_xy(side)
    else:  # row-major
        x, y = None, None
    if x is not None:
        img[y, x] = val
        voidmask[y, x] = ~mask
    else:
        img = val.reshape(side, side)
        voidmask = (~mask).reshape(side, side)

    # spread contrast across the representable range with percentile clip
    lo, hi = np.percentile(val[mask], 4), np.percentile(val[mask], 99.5)
    f = np.clip((img - lo) / (hi - lo), 0, 1)
    field = (1.0 - np.exp(-k * f)) / (1.0 - np.exp(-k))
    field = np.clip(field, 0, 1) ** gamma

    lut = R.palette_lut(palette, 2048)
    rgb = R.apply_lut(field, lut)
    rgb[voidmask] = np.array([0.010, 0.0, 0.022])    # the fractal of holes
    R.save(rgb, out, downscale_to=down)
    print("wrote", out, "void fraction", round((~mask).mean(), 4))


if __name__ == "__main__":
    main()
