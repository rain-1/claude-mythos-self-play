"""Shared render kit for the art_eqbf triptych."""
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation, zoom as ndzoom
from PIL import Image


def filmic(buf, k=1.0, gamma=0.92):
    """Bounded tone map: 1-exp(-k x), then gamma lift. buf: (H,W,3) float."""
    out = 1.0 - np.exp(-k * np.clip(buf, 0, None))
    return np.clip(out, 0, 1) ** gamma


def save(buf_rgb01, path, down=1):
    img = (np.clip(buf_rgb01, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img)
    if down > 1:
        im = im.resize((im.width // down, im.height // down), Image.LANCZOS)
    im.save(path)
    print("saved", path, im.size)


def ramp(t, stops):
    """Piecewise-linear color ramp. t in [0,1] any shape; stops: list of (pos,(r,g,b))."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        if not m.any():
            continue
        f = (t[m] - p0) / max(p1 - p0, 1e-9)
        for k in range(3):
            out[..., k][m] = c0[k] + f * (c1[k] - c0[k])
    return out


# a curated dusk->gold ramp (deep indigo -> teal -> ember -> gold)
DUSK = [(0.00, (0.02, 0.03, 0.10)),
        (0.25, (0.05, 0.12, 0.28)),
        (0.50, (0.10, 0.35, 0.42)),
        (0.72, (0.75, 0.42, 0.12)),
        (0.90, (1.00, 0.78, 0.30)),
        (1.00, (1.00, 0.95, 0.72))]

CYAN = np.array([0.35, 0.95, 1.0])
GOLD = np.array([1.0, 0.82, 0.38])
EMBER = np.array([0.95, 0.45, 0.15])


def contour_ridge(U, spacing, width_px):
    """Gaussian ridge on level sets of U with constant screen width.
    spacing: level spacing; width via |U mod s| * s?  Use the memory recipe:
    line_dist_px = dist_in_U / |grad U per pixel|."""
    gy, gx = np.gradient(U)
    g = np.hypot(gx, gy) + 1e-12
    m = np.abs(((U / spacing + 0.5) % 1.0) - 0.5) * spacing  # distance in U to nearest level
    d_px = m / g
    return np.exp(-(d_px / width_px) ** 2)


def locus_glow(Q, width_px):
    """Glow on the zero set of scalar field Q with ~constant pixel width."""
    gy, gx = np.gradient(Q)
    g = np.hypot(gx, gy) + 1e-12
    d_px = np.abs(Q) / g
    return np.exp(-(d_px / width_px) ** 2)


def splat_star(buf, xy, color, amp, sigma, halo_sigma=None, halo_amp=0.5):
    """Add a Gaussian star at pixel coords xy=(col,row) into buf (H,W,3)."""
    H, W = buf.shape[:2]
    cx, cy = xy
    r = int(max(sigma, halo_sigma or 0) * 5) + 2
    x0, x1 = max(0, int(cx) - r), min(W, int(cx) + r + 1)
    y0, y1 = max(0, int(cy) - r), min(H, int(cy) + r + 1)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    core = amp * np.exp(-d2 / (2 * sigma ** 2))
    field = core
    if halo_sigma:
        field = field + halo_amp * amp * np.exp(-d2 / (2 * halo_sigma ** 2))
    for k in range(3):
        buf[y0:y1, x0:x1, k] += field * color[k]


def bloom(buf, sigma, amount, thresh=0.55):
    """Bloom only the bright foci (memory craft note)."""
    lum = buf.mean(-1)
    t0, t1 = thresh, min(1.0, thresh + 0.28)
    m = np.clip((lum - t0) / (t1 - t0), 0, 1)
    m = m * m * (3 - 2 * m)
    src = buf * m[..., None]
    if sigma > 8:
        ds = max(1, int(sigma / 6))
        small = src[::ds, ::ds]
        small = gaussian_filter(small, (sigma / ds, sigma / ds, 0))
        halo = ndzoom(small, (buf.shape[0] / small.shape[0],
                              buf.shape[1] / small.shape[1], 1), order=1)
        halo = halo[:buf.shape[0], :buf.shape[1]]
    else:
        halo = gaussian_filter(src, (sigma, sigma, 0))
    return buf + amount * halo


def fatten(ink, px):
    """Grey-dilate a stroke buffer so strokes survive downscale."""
    if px <= 1:
        return ink
    n = int(round(px))
    return grey_dilation(ink, size=(n, n) if ink.ndim == 2 else (n, n, 1))


def line_splat(buf, pts, color, amp_per_px, width_px=1.4):
    """Additively draw a polyline given as (N,2) pixel coords (col,row),
    with sub-pixel bilinear splatting, resampled to ~1 sample/px."""
    pts = np.asarray(pts, np.float64)
    seg = np.diff(pts, axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    n = np.maximum(1, np.ceil(L).astype(int))
    allp = []
    for i in range(len(seg)):
        f = np.linspace(0, 1, n[i], endpoint=False)
        allp.append(pts[i] + f[:, None] * seg[i])
    P = np.concatenate(allp + [pts[-1:]])
    H, W = buf.shape[:2]
    x, y = P[:, 0], P[:, 1]
    ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
    x, y = x[ok], y[ok]
    xf, yf = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - xf, y - yf
    a = amp_per_px
    for dxx, dyy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                        (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        for k in range(3):
            np.add.at(buf[..., k], (yf + dyy, xf + dxx), a * w * color[k])
    return buf
