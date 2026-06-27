"""01 - The Braid That Remembers (centerpiece).

Abelian anyons are point particles in 2+1 dimensions; dragging one around
another multiplies the wavefunction by a phase that depends only on HOW the
paths wound -- not on the details of the motion. Their world-lines form a
braid, and the Kauffman bracket assigns to that braid an invariant of the
weave. A *closed* braid is a link: here the (p,q) torus link, the closure of
(sigma_1 ... sigma_{p-1})^q. We draw it honestly as it lives on a torus, then
tilt the torus to the eye. The over/under weave -- the thing the bracket
remembers -- falls out of the true 3-D geometry: a strand in front simply
hides the strand behind. gcd(p,q) coloured components = gcd(p,q) anyons whose
histories can never be combed apart.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from math import gcd


# ----- curated high-lightness, non-cyclic palette (distinct components) -----
PALETTE = np.array([
    [1.00, 0.36, 0.42],   # coral
    [1.00, 0.62, 0.24],   # amber
    [0.96, 0.86, 0.30],   # gold
    [0.46, 0.90, 0.46],   # green
    [0.30, 0.85, 0.80],   # teal
    [0.36, 0.66, 1.00],   # azure
    [0.62, 0.50, 1.00],   # violet
    [1.00, 0.50, 0.85],   # pink
])


def torus_link_points(p, q, R=1.0, r=0.46, tube=0.5, samples=2600,
                      tilt=1.02, yaw=0.22, persp=0.30):
    """Return (xy in [-1,1]-ish, depth, comp_id, normal_z) for all tube samples.

    The (p,q) torus link: theta = p t, phi = q t, t in [0, 2pi*g) split into
    g = gcd(p,q) components offset around the tube.
    """
    g = gcd(p, q)
    pr, qr = p // g, q // g
    # rotation: tilt about x then yaw about y
    cx, sx = np.cos(tilt), np.sin(tilt)
    cy, sy = np.cos(yaw), np.sin(yaw)

    allpts = []
    for c in range(g):
        t = np.linspace(0, 2 * np.pi, samples, endpoint=False)
        theta = pr * t
        phi = qr * t + 2 * np.pi * c / g
        # torus surface point and its outward normal (for shading)
        ct, st = np.cos(theta), np.sin(theta)
        cph, sph = np.cos(phi), np.sin(phi)
        X = (R + r * cph) * ct
        Y = (R + r * cph) * st
        Z = r * sph
        # outward surface normal
        nX = cph * ct
        nY = cph * st
        nZ = sph
        # tilt about x-axis
        Y2 = cx * Y - sx * Z
        Z2 = sx * Y + cx * Z
        nY2 = cx * nY - sx * nZ
        nZ2 = sx * nY + cx * nZ
        # yaw about y-axis
        X3 = cy * X + sy * Z2
        Z3 = -sy * X + cy * Z2
        nX3 = cy * nX + sy * nZ2
        nZ3 = -sy * nX + cy * nZ2
        # perspective (camera down +z); larger z -> nearer the eye
        f = 1.0 / (1.0 - persp * (Z3 / (R + r)))
        sx_ = X3 * f
        sy_ = Y2 * f
        # screen-space tangent (for off-centre specular line along the tube)
        tx = np.gradient(sx_)
        ty = np.gradient(sy_)
        tn = np.hypot(tx, ty) + 1e-9
        tx, ty = tx / tn, ty / tn
        allpts.append(np.stack([sx_, sy_, Z3,
                                np.full_like(sx_, c),
                                nZ3, f, tx, ty], axis=1))
    return np.concatenate(allpts, axis=0)


def render(S, p=9, q=4, supersample=2, fname=None, seed_extent=1.0):
    g = gcd(p, q)
    if fname is None:
        fname = "01_the_braid_that_remembers.png"
    W = S * supersample
    pts = torus_link_points(p, q, samples=max(2400, int(2400 * W / 2048)))
    # screen mapping: fit the link into the canvas with margin
    span = 1.62                     # world half-extent to map to canvas
    sxp = pts[:, 0]
    syp = pts[:, 1]
    depth = pts[:, 2]
    comp = pts[:, 3].astype(int)
    nz = pts[:, 4]
    persp_f = pts[:, 5]
    tang = pts[:, 6:8]
    LIGHT = np.array([-0.5, -0.72])           # screen-space light direction
    BODY_FLOOR = float(__import__("os").environ.get("BODY_FLOOR", "0.45"))

    px = (sxp / span * 0.5 + 0.5) * (W - 1)
    py = (-syp / span * 0.5 + 0.5) * (W - 1)

    # tube radius in pixels, with mild perspective scaling
    base_tube = 0.0135 * W
    rad = base_tube * persp_f

    # spread g component colours across the palette wheel for max separation
    pal_step = max(1, len(PALETTE) // g)

    col = np.zeros((W, W, 3), dtype=np.float32)
    glow = np.zeros((W, W), dtype=np.float32)

    # painter's algorithm: far (small depth) first, near last (on top)
    order = np.argsort(depth)
    dmin, dmax = depth.min(), depth.max()

    for idx in order:
        x0, y0 = px[idx], py[idx]
        rr = rad[idx]
        c = comp[idx]
        base = PALETTE[(c * pal_step) % len(PALETTE)]
        # depth cue: nearer -> brighter
        dcue = 0.55 + 0.65 * (depth[idx] - dmin) / (dmax - dmin + 1e-9)
        ri = int(np.ceil(rr)) + 1
        ix0, ix1 = int(x0) - ri, int(x0) + ri + 1
        iy0, iy1 = int(y0) - ri, int(y0) + ri + 1
        if ix1 <= 0 or iy1 <= 0 or ix0 >= W or iy0 >= W:
            continue
        ix0c, iy0c = max(ix0, 0), max(iy0, 0)
        ix1c, iy1c = min(ix1, W), min(iy1, W)
        yy, xx = np.mgrid[iy0c:iy1c, ix0c:ix1c]
        dx = xx - x0
        dy = yy - y0
        d = np.sqrt(dx * dx + dy * dy)
        # soft tube cross-section: opaque core, soft rim (antialiased)
        alpha = np.clip(rr - d, 0, 1.5) / 1.5
        alpha = np.clip(alpha, 0, 1)
        if alpha.max() <= 0:
            continue
        # signed perpendicular coordinate across the tube (for cylinder shading)
        tx_, ty_ = tang[idx]
        perp = (-ty_) * dx + (tx_) * dy           # distance across the tube
        u = np.clip(perp / (rr + 1e-6), -1, 1)     # -1..1 across cross-section
        # Lambert-ish cylinder body: darker on the side away from the light
        lside = -((-ty_) * LIGHT[0] + (tx_) * LIGHT[1])   # which side faces light
        body = np.clip(BODY_FLOOR + (1.0 - BODY_FLOOR) * np.cos(u * 1.35 - np.sign(lside) * 0.7), 0.12, 1.0)
        # off-centre specular line (glossy rod)
        spec_u = 0.42 * np.sign(lside)
        spec = np.exp(-((u - spec_u) / 0.33) ** 2) * np.sqrt(1 - u * u)
        shade = body * dcue
        c_rgb = (base[None, None, :] * shade[..., None]
                 + np.array([1.0, 0.97, 0.9])[None, None, :] * (spec * 0.6 * dcue)[..., None])
        a3 = alpha[..., None]
        region = col[iy0c:iy1c, ix0c:ix1c, :]
        col[iy0c:iy1c, ix0c:ix1c, :] = region * (1 - a3) + c_rgb * a3
        # glow: use MAXIMUM (not sum) so dense overlapping samples of one tube
        # don't pile up to white -- the halo tracks coverage, not overdraw
        gslice = glow[iy0c:iy1c, ix0c:ix1c]
        np.maximum(gslice, (alpha * body * dcue).astype(np.float32), out=gslice)

    # ----- background: deep cool vignette -----
    yy, xx = np.mgrid[0:W, 0:W]
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - W / 2) / (W / 2)) ** 2)
    bg = np.array([0.018, 0.022, 0.040])[None, None, :] * np.clip(1.2 - 0.6 * rr, 0, 1)[..., None]
    img = bg + col

    # ----- bloom (tight + wide), restrained so colour survives -----
    for sig, amp, tint in [(2.0 * supersample, 0.15, [1.0, 0.88, 0.75]),
                           (7.0 * supersample, 0.10, [0.95, 0.9, 0.85]),
                           (20.0 * supersample, 0.05, [0.85, 0.88, 1.0])]:
        b = gaussian_filter(glow, sig)
        img += b[..., None] * amp * np.array(tint)

    # ----- saturation boost (keep the woven strands jewel-toned) -----
    lum = img.mean(axis=2, keepdims=True)
    img = lum + (img - lum) * 1.28

    # ----- filmic tone + gamma -----
    k = 1.05
    img = 1.0 - np.exp(-k * np.clip(img, 0, None))
    img = np.clip(img, 0, 1) ** (1 / 1.9)

    out = (img * 255).astype(np.uint8)
    im = Image.fromarray(out, "RGB")
    if supersample != 1:
        im = im.resize((S, S), Image.LANCZOS)
    im.save(fname)
    print(f"  saved {fname} {im.size}  T({p},{q}) g={g} components")
    return im


if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 512
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    q = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    ss = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    render(S, p, q, ss)
