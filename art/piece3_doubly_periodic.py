"""
Doubly Periodic
===============
Seed: mathoverflow "elliptic integrals" / special functions.

The Weierstrass elliptic function

    P(z) = 1/z^2  +  sum over nonzero lattice w of [ 1/(z-w)^2 - 1/w^2 ]

is the canonical doubly-periodic meromorphic function: P(z + w) = P(z) for
every w in a 2D lattice. It has a double pole at every lattice point and two
zeros per fundamental cell. Domain-colour it -- hue = phase, banding =
modulus -- and the plane fills with a crystal of poles and zeros that repeats
in *two* independent directions at once.

We use the hexagonal (equianharmonic) lattice w1 = 1, w2 = exp(i*pi/3), whose
6-fold symmetry makes the tiling sing.

Implementation note: P is lattice-periodic, so we first reduce every pixel
z into the fundamental cell, then sum only a small surrounding lattice
(exact, because the function is periodic). That keeps a 4096^2 render cheap.
"""
import numpy as np
from PIL import Image

W1 = 1.0 + 0.0j
W2 = np.exp(1j * np.pi / 3.0)          # hexagonal / equianharmonic lattice

def reduce_to_cell(z):
    """Map z into the fundamental parallelogram (a,b in [-0.5,0.5)) of {W1,W2}."""
    # z = a*W1 + b*W2 ; solve the real 2x2 system.
    det = W1.real * W2.imag - W1.imag * W2.real
    a = (z.real * W2.imag - z.imag * W2.real) / det
    b = (W1.real * z.imag - W1.imag * z.real) / det
    a -= np.round(a)
    b -= np.round(b)
    return a * W1 + b * W2

def weierstrass_P(z, M=8):
    """Sum the Weierstrass series on |m|,|n| <= M about the reduced cell."""
    zr = reduce_to_cell(z)
    out = 1.0 / (zr * zr)
    for m in range(-M, M + 1):
        for n in range(-M, M + 1):
            if m == 0 and n == 0:
                continue
            w = m * W1 + n * W2
            out += 1.0 / (zr - w) ** 2 - 1.0 / (w * w)
    return out

# A curated CYCLIC palette (deep teal -> cyan -> indigo -> violet -> rose ->
# amber -> back). Richer and less neon than raw HSV; loops smoothly.
_ANCHORS = np.array([
    [0.04, 0.22, 0.30],   # deep teal
    [0.10, 0.62, 0.72],   # cyan
    [0.18, 0.30, 0.66],   # indigo
    [0.42, 0.20, 0.62],   # violet
    [0.80, 0.22, 0.46],   # rose
    [0.92, 0.45, 0.24],   # ember
    [0.93, 0.80, 0.34],   # amber
    [0.04, 0.22, 0.30],   # back to teal (loop)
])

def _cyclic(h):
    """h in [0,1) -> RGB via piecewise-linear interp around the loop."""
    n = len(_ANCHORS) - 1
    x = (h % 1.0) * n
    i = np.floor(x).astype(int)
    f = (x - i)[..., None]
    c0 = _ANCHORS[i]; c1 = _ANCHORS[i + 1]
    return c0 * (1 - f) + c1 * f

def domain_color(w):
    """Enhanced phase portrait: cyclic hue=arg, modulus bands, phase spokes."""
    arg = np.angle(w)
    mag = np.abs(w)
    logm = np.log(mag + 1e-30)

    H = (arg / (2 * np.pi)) % 1.0
    rgb = _cyclic(H)                                   # saturated base chroma

    # Gentle log-spaced modulus rings, faded out where they would alias
    # (deep inside poles/zeros) so singularities stay clean, not noisy.
    ring = 0.5 + 0.5 * np.sin(2 * np.pi * logm / np.log(2))
    ring_fade = np.exp(-(logm / 7.0) ** 2)
    bright = 0.66 + 0.16 * (ring - 0.5) * ring_fade

    # crisp black at the two zeros per cell, white-hot at the lattice poles
    bright = bright * (0.5 + 0.5 * np.tanh(0.7 * (logm + 4.5)))
    rgb = rgb * bright[..., None]
    hot = np.clip((logm - 3.5) / 5.0, 0, 1) ** 1.3
    rgb = rgb + (1.0 - rgb) * hot[..., None]

    # thin phase spokes (six per turn -> echoes the hexagonal lattice)
    ph_band = np.abs(((arg / (np.pi / 6)) % 1.0) - 0.5) * 2
    rgb = rgb * (1.0 - 0.22 * np.exp(-(ph_band / 0.06) ** 2))[..., None]

    return np.clip(rgb, 0, 1)

def render(size, periods=3.0, M=8, chunk=256, supersample=1, seed=0):
    S = size * supersample
    span = periods                                   # show this many cells across
    xs = np.linspace(-span, span, S)
    ys = np.linspace(-span, span, S)
    img = np.empty((S, S, 3), dtype=np.float32)
    for j0 in range(0, S, chunk):
        j1 = min(j0 + chunk, S)
        X, Y = np.meshgrid(xs, ys[j0:j1])
        Z = X + 1j * Y
        W = weierstrass_P(Z, M=M)
        img[j0:j1] = domain_color(W).astype(np.float32)
        print(f"  rows {j1}/{S}", end="\r")
    print()
    out = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    pil = Image.fromarray(out, "RGB")
    if supersample > 1:
        pil = pil.resize((size, size), Image.LANCZOS)
    return pil

if __name__ == "__main__":
    import sys
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    out = sys.argv[2] if len(sys.argv) > 2 else "gallery/preview3.png"
    render(size).save(out)
    print("saved", out, size)
