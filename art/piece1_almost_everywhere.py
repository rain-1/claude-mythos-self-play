"""
Almost Everywhere
=================
Seed: philosophy.SE "Are we dead almost everywhere?" + measure theory.

A monochromatic random wave (Berry's random-wave model: a uniform
superposition of plane waves of fixed wavenumber, random direction and
phase) is the generic eigenfunction of quantum chaos. Such a field is
positive on a region and negative on a region; it equals zero only on a
one-dimensional *nodal set* -- a curve, hence measure zero in the plane.

So: the field is "dead" (one sign) almost everywhere. Life is the glowing
zero-crossing, a set of measure zero clinging across the void. We render
three independent fields in three hues and add their light.
"""
import numpy as np
from PIL import Image

def random_wave(X, Y, K, n_waves, rng):
    """Sum of n_waves plane waves, |k| = K, random directions + phases."""
    psi = np.zeros_like(X)
    for _ in range(n_waves):
        theta = rng.uniform(0, 2 * np.pi)
        phi = rng.uniform(0, 2 * np.pi)
        kx, ky = K * np.cos(theta), K * np.sin(theta)
        psi += np.cos(kx * X + ky * Y + phi)
    return psi / np.sqrt(n_waves)

def nodal_glow(psi, width_px, dx):
    """Uniform-width glow on the zero set: distance ~ |psi|/|grad psi|."""
    gy, gx = np.gradient(psi, dx)
    grad = np.hypot(gx, gy) + 1e-9
    dist = np.abs(psi) / grad                      # ~ signed distance to nodal line
    return np.exp(-(dist / (width_px * dx)) ** 2)

def render(size, n_waves=600, supersample=2, seed=7):
    S = size * supersample
    rng = np.random.default_rng(seed)
    span = 13.0                                     # world units across the frame
    xs = np.linspace(-span, span, S)
    X, Y = np.meshgrid(xs, xs)
    dx = xs[1] - xs[0]

    # Three independent fields, three wavenumbers -> three scales of filament.
    # Unequal weights: one calm dominant field, two sparser accents.
    # (hue, wavenumber K, line half-width in *pixels*, amplitude)
    layers = [
        (np.array([0.16, 0.85, 1.00]), 0.62, 2.6, 1.35),   # cyan, broad cells
        (np.array([1.00, 0.30, 0.62]), 0.95, 2.2, 1.00),   # magenta-rose accents
        (np.array([1.00, 0.80, 0.30]), 1.45, 1.9, 0.72),   # fine gold tracery
    ]
    img = np.zeros((S, S, 3))
    for hue, K, w, amp in layers:
        psi = random_wave(X, Y, K, n_waves, rng)
        gy, gx = np.gradient(psi, dx)
        dist = np.abs(psi) / (np.hypot(gx, gy) + 1e-9)
        core = np.exp(-(dist / (w * dx)) ** 2)             # crisp bright thread
        halo = 0.22 * np.exp(-(dist / (5.0 * w * dx)) ** 2)  # soft bloom
        img += amp * (core + halo)[..., None] * hue[None, None, :]

    # Tone: gentle filmic compression so bright crossings bloom but don't clip hard.
    img = img / (1.0 + img)
    img = np.power(img, 0.72)

    # Radial vignette -> the void deepens toward the edges.
    r = np.hypot(X, Y) / span
    vign = np.clip(1.0 - 0.35 * r ** 2, 0, 1)
    img *= vign[..., None]

    # A breath of cold base light so the void isn't dead black.
    img += np.array([0.015, 0.02, 0.035])[None, None, :] * (1.0 - 0.5 * r[..., None])

    img = np.clip(img, 0, 1)
    out = (img * 255 + 0.5).astype(np.uint8)
    pil = Image.fromarray(out, "RGB")
    if supersample > 1:
        pil = pil.resize((size, size), Image.LANCZOS)
    return pil

if __name__ == "__main__":
    import sys
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    ss = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    out = sys.argv[3] if len(sys.argv) > 3 else "gallery/preview1.png"
    render(size, supersample=ss).save(out)
    print("saved", out, size)
