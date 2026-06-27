"""03 - The Tamed Logarithm.

The dilogarithm Li_2(z) is multi-valued: carry it once around 0 or 1 and it
comes back changed (its monodromy). The Bloch-Wigner function

    D(z) = Im Li_2(z) + arg(1-z) log|z|

is the unique combination whose monodromy cancels -- a single-valued real
function on C\{0,1}. It vanishes on the whole real axis (flat, degenerate
tetrahedra: zero volume) and rises to +-Cl_2(pi/3) ~ 1.015 at e^{+-i pi/3}.
Geometrically D(z) is the hyperbolic volume of the ideal tetrahedron with
vertices 0,1,infinity,z -- the building block from which every hyperbolic
3-manifold's volume is assembled. We draw its level sets: equally spaced in
volume, so they crowd toward the two cusps where the gradient diverges.
"""
import numpy as np
from PIL import Image
from dilog_core import bloch_wigner


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def render(S, supersample=2, fname="03_the_tamed_logarithm.png"):
    W = S * supersample
    # window: show both cusps 0 and 1, the two peaks, the zero river
    xlo, xhi = -1.15, 2.15
    ylo, yhi = -1.65, 1.65
    xs = np.linspace(xlo, xhi, W)
    ys = np.linspace(yhi, ylo, W)            # image y downward
    X, Y = np.meshgrid(xs, ys)
    Z = X + 1j * Y
    print("  evaluating Bloch-Wigner on", W, "x", W, "grid...")
    D = bloch_wigner(Z).astype(np.float64)

    # gradient magnitude PER PIXEL (for constant-width antialiased contours + relief)
    gy, gx = np.gradient(D)
    gmag = np.hypot(gx, gy) + 1e-9
    cell = (xhi - xlo) / W

    # ---- base diverging field: teal (neg) -> dark (0) -> amber (pos), very dim ----
    t = np.tanh(D / 0.62)                      # bounded [-1,1]
    pos = np.clip(t, 0, 1)
    neg = np.clip(-t, 0, 1)
    amber = np.array([1.00, 0.58, 0.16])       # warm, positive volume
    teal = np.array([0.13, 0.60, 0.80])        # cool, negative volume
    base = np.zeros((W, W, 3))
    for c in range(3):
        base[..., c] = (pos ** 1.1) * amber[c] + (neg ** 1.1) * teal[c]
    base *= 0.16                                # dim; the light comes from the level sets

    # ---- level sets: equally spaced in D (volume); crowd toward the cusps ----
    dlev = 0.045
    phase = D / dlev
    dist = np.abs(phase - np.round(phase))      # 0..0.5, distance to nearest contour (levels)
    pix_d = dist * dlev / gmag                   # distance to contour in PIXELS
    width = 0.9 * supersample                    # line half-width in pixels
    line = np.exp(-(pix_d / width) ** 2)

    # bright sign-coloured filaments
    warm = np.array([1.00, 0.82, 0.40])
    cold = np.array([0.42, 0.86, 1.00])
    cont = np.zeros((W, W, 3))
    for c in range(3):
        cont[..., c] = line * (pos * warm[c] + neg * cold[c] + 0.12)
    cont *= 1.35

    # ---- relief / emboss from gradient (subtle sculpt on the dim base) ----
    lightdir = np.array([-0.55, -0.83])
    nx = -gx / cell
    ny = -gy / cell
    nn = np.sqrt(nx * nx + ny * ny + 1.0)
    shade = (nx * lightdir[0] + ny * lightdir[1] + 0.85) / (nn * 1.3)
    shade = np.clip(0.6 + 0.7 * shade, 0.25, 1.4)

    img = base * shade[..., None] + cont

    # ---- the zero river: a thin dark seam on the real axis (volume = 0) ----
    river = np.exp(-(np.abs(D) / (1.4 * dlev)) ** 2)
    img *= (1.0 - 0.45 * river[..., None])

    # ---- cusp glows at 0 and 1 (the ideal vertices / punctures), small + tight ----
    for (cx, cy), tint in [((0.0, 0.0), np.array([0.55, 0.86, 1.0])),
                           ((1.0, 0.0), np.array([1.0, 0.76, 0.42]))]:
        r2 = (X - cx) ** 2 + (Y - cy) ** 2
        glow = np.exp(-r2 / (2 * 0.0016))
        img += glow[..., None] * tint * 1.1

    # ---- gentle bloom (small sigma only; no low-frequency haze) ----
    from scipy.ndimage import gaussian_filter
    lum = np.clip(img.mean(axis=2) - 0.12, 0, None)   # only bright filaments bloom
    for sig, amp in [(1.6, 0.40), (4.5, 0.26)]:
        b = gaussian_filter(lum, sig)
        img += (b[..., None]) * amp * np.array([1.0, 0.86, 0.62])

    # ---- filmic tone + gamma ----
    k = 1.7
    img = 1.0 - np.exp(-k * np.clip(img, 0, None))
    img = np.clip(img, 0, 1) ** (1 / 1.85)

    out = (img * 255).astype(np.uint8)
    im = Image.fromarray(out, "RGB")
    if supersample != 1:
        im = im.resize((S, S), Image.LANCZOS)
    im.save(fname)
    print("  saved", fname, im.size)
    return im


if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 512
    ss = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    render(S, ss)
