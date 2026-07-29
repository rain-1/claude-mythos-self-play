"""
render.py — shared rendering toolkit for the Held triptych.
Dark-field additive float32 buffers, Gaussian splats, filmic tonemap.
All drawing in canvas pixel coordinates; supersample SS then LANCZOS down.
"""

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, W, H, ss=2):
        self.W, self.H, self.ss = W, H, ss
        self.buf = np.zeros((H * ss, W * ss, 3), np.float32)

    @property
    def w(self):
        return self.W * self.ss

    @property
    def h(self):
        return self.H * self.ss


def splat_points(canvas, xs, ys, amps, color, sigma_px=1.2):
    """Additive Gaussian point splats. xs, ys in SS pixels.
    Blur is LOCAL to the points' bounding box (padded), never full-canvas."""
    buf = canvas.buf
    h, w, _ = buf.shape
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    amps = np.broadcast_to(np.asarray(amps, float), xs.shape)
    ok = (xs > -10) & (xs < w + 10) & (ys > -10) & (ys < h + 10)
    xs, ys, amps = xs[ok], ys[ok], amps[ok]
    if len(xs) == 0:
        return None
    pad = int(4 * sigma_px + 3)
    x0 = max(int(xs.min()) - pad, 0)
    x1 = min(int(xs.max()) + pad + 2, w)
    y0 = max(int(ys.min()) - pad, 0)
    y1 = min(int(ys.max()) + pad + 2, h)
    lay = np.zeros((y1 - y0, x1 - x0), np.float32)
    lx, ly = xs - x0, ys - y0
    xi = np.clip(np.floor(lx).astype(int), 0, lay.shape[1] - 2)
    yi = np.clip(np.floor(ly).astype(int), 0, lay.shape[0] - 2)
    fx, fy = lx - xi, ly - yi
    np.add.at(lay, (yi, xi), amps * (1 - fx) * (1 - fy))
    np.add.at(lay, (yi, xi + 1), amps * fx * (1 - fy))
    np.add.at(lay, (yi + 1, xi), amps * (1 - fx) * fy)
    np.add.at(lay, (yi + 1, xi + 1), amps * fx * fy)
    if sigma_px > 0:
        lay = gaussian_filter(lay, sigma_px)
    for c in range(3):
        buf[y0:y1, x0:x1, c] += lay * color[c]
    return None


def line_pts(p0, p1, n=None, spacing=0.7):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = np.hypot(*(p1 - p0))
    if n is None:
        n = max(int(L / spacing), 2)
    t = np.linspace(0, 1, n)
    return p0[None] + (p1 - p0)[None] * t[:, None], t


def circle_pts(cx, cy, r, n=None, spacing=0.7, a0=0, a1=2 * np.pi):
    if n is None:
        n = max(int(abs(a1 - a0) * r / spacing), 12)
    a = np.linspace(a0, a1, n, endpoint=False)
    return cx + r * np.cos(a), cy + r * np.sin(a), a


def draw_ring(canvas, cx, cy, r, color, amp=1.0, width=1.4, spacing=None,
              a0=0.0, a1=2 * np.pi):
    """Anti-aliased glowing circle: direct Gaussian annulus in a local window.
    amp = peak per-pixel level, width = gaussian sigma in px."""
    buf = canvas.buf
    h, w, _ = buf.shape
    pad = 4 * width + 2
    x0 = int(max(cx - r - pad, 0))
    x1 = int(min(cx + r + pad + 1, w))
    y0 = int(max(cy - r - pad, 0))
    y1 = int(min(cy + r + pad + 1, h))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.ogrid[y0:y1, x0:x1]
    d = np.hypot(xx - cx, yy - cy)
    lay = np.exp(-((d - r) ** 2) / (2 * width ** 2)).astype(np.float32) * amp
    if a1 - a0 < 2 * np.pi - 1e-9:
        ang = np.arctan2(yy - cy, xx - cx) % (2 * np.pi)
        lo, hi = a0 % (2 * np.pi), a1 % (2 * np.pi)
        m = (ang >= lo) & (ang <= hi) if lo <= hi else ((ang >= lo) | (ang <= hi))
        lay = lay * m
    for c in range(3):
        buf[y0:y1, x0:x1, c] += lay * color[c]


def draw_disc(canvas, cx, cy, r, color, amp=1.0, grad_pow=1.6):
    """Soft interior fill: radial gradient brightening toward the rim."""
    buf = canvas.buf
    h, w, _ = buf.shape
    x0, x1 = int(max(cx - r - 3, 0)), int(min(cx + r + 4, w))
    y0, y1 = int(max(cy - r - 3, 0)), int(min(cy + r + 4, h))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.ogrid[y0:y1, x0:x1]
    d = np.hypot(xx - cx, yy - cy) / r
    m = np.clip(1 - d, 0, 1)
    fill = (1 - m) ** grad_pow * (d <= 1.0)
    aa = np.clip((1.0 - d) * r, 0, 1)          # anti-alias edge
    lay = (0.25 + 0.75 * fill) * aa * amp
    for c in range(3):
        buf[y0:y1, x0:x1, c] += lay * color[c]


def draw_segment(canvas, p0, p1, color, amp=1.0, width=1.4, spacing=0.6):
    pts, _ = line_pts(p0, p1, spacing=spacing)
    m = amp * spacing / max(width, 0.6) * 0.8
    splat_points(canvas, pts[:, 0], pts[:, 1], m, color, sigma_px=width)


def glow(canvas, cx, cy, sigma, color, peak):
    """Direct Gaussian glow with controlled PEAK level (no splat dilution)."""
    buf = canvas.buf
    h, w, _ = buf.shape
    R = int(3.2 * sigma)
    x0, x1 = int(max(cx - R, 0)), int(min(cx + R, w))
    y0, y1 = int(max(cy - R, 0)), int(min(cy + R, h))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.ogrid[y0:y1, x0:x1]
    lay = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma ** 2)) * peak
    for c in range(3):
        buf[y0:y1, x0:x1, c] += lay * color[c]


def bloom(canvas, sigma, gain, thresh=0.55):
    """Warm halo around bright regions. Downsample->blur->upsample for big sigma."""
    buf = canvas.buf
    lum = buf.mean(2)
    mx = lum.max() or 1.0
    mask = np.clip(lum / (0.75 * mx) - thresh, 0, None)
    src = buf * mask[..., None]
    if sigma > 8:
        ds = max(int(sigma / 6), 1)
        small = src[::ds, ::ds]
        smallb = np.stack([gaussian_filter(small[..., c], sigma / ds) for c in range(3)], -1)
        big = np.kron(smallb, np.ones((ds, ds, 1), np.float32))[:buf.shape[0], :buf.shape[1]]
        halo = gaussian_filter(big, 2)
    else:
        halo = np.stack([gaussian_filter(src[..., c], sigma) for c in range(3)], -1)
    peak = halo.max() or 1.0
    buf += halo * (gain * mx * 0.12 / peak)


def to_img(canvas, k=1.0, gamma=0.88, base=(0.012, 0.016, 0.024)):
    buf = canvas.buf.copy()
    for c in range(3):
        buf[..., c] = base[c] + buf[..., c]
    out = 1.0 - np.exp(-k * buf)
    out = np.clip(out, 0, 1) ** gamma
    out += (np.random.default_rng(7).random(out.shape) - 0.5) / 255.0
    out = np.clip(out, 0, 1)
    img = Image.fromarray((out * 255).astype(np.uint8))
    if canvas.ss > 1:
        img = img.resize((canvas.W, canvas.H), Image.LANCZOS)
    return img


# ------------------------------------------------------------------ palette
# curvature -> color (the 5 is the only cold one: the unheld coin)
PAL = {
    -1: (0.72, 0.68, 0.60),   # tray: warm silver
    2: (1.00, 0.62, 0.22),    # amber
    3: (0.98, 0.40, 0.34),    # coral rose
    4: (1.00, 0.84, 0.38),    # gold
    5: (0.30, 0.85, 1.00),    # CYAN — the unheld five
    6: (0.35, 0.80, 0.62),    # jade
    7: (0.82, 0.62, 1.00),    # violet
    8: (0.85, 0.70, 0.50),
    9: (0.60, 0.60, 0.70),
}
GHOST = (0.55, 0.58, 0.66)
STRESS = (1.00, 0.78, 0.30)
WOUND = (0.30, 0.85, 1.00)


def curvature_of(r):
    return int(round(1.0 / r))


# ------------------------------------------------------- court renderer
def draw_court(canvas, cx, cy, R, centers, radii, stress_pairs=None,
               scale_amp=1.0, tray_amp=1.0, coin_amp=1.0, rim_w=None,
               chain_amp=1.0, beads=True, tray_r=1.0):
    """Draw one tray + coins + force chains.
    centers/radii in tray units (tray radius tray_r -> R px at (cx,cy)).
    stress_pairs: list of (kind, i, j_or_None, omega) with omega in [0,1]."""
    if rim_w is None:
        rim_w = max(1.1 * canvas.ss, 0.0016 * R)
    S = R / tray_r
    # tray rim
    draw_ring(canvas, cx, cy, R, PAL[-1], amp=0.85 * tray_amp * scale_amp,
              width=rim_w * 1.15)
    # per-coin borne stress (sum of incident omegas)
    borne = np.zeros(len(radii))
    if stress_pairs:
        for kind, i, j, w in stress_pairs:
            borne[i] += w
            if kind == "pair":
                borne[j] += w
        if borne.max() > 0:
            borne = borne / borne.max()
    # coins: dark glass, thin bright rim, core glow = how hard it is held
    for k, ((x, y), r) in enumerate(zip(centers, radii)):
        p = curvature_of(r)
        col = PAL.get(p, GHOST)
        px, py, pr = cx + x * S, cy + y * S, r * S
        draw_disc(canvas, px, py, pr, col, amp=0.030 * coin_amp * scale_amp)
        draw_ring(canvas, px, py, pr, col, amp=1.35 * coin_amp * scale_amp,
                  width=rim_w)
        if borne[k] > 0:
            # pressure glow at the core: brightness = how hard the coin is held
            wcol = tuple(0.55 * c + 0.45 for c in col)   # toward white-hot
            glow(canvas, px, py, pr * 0.38,
                 col, 0.42 * borne[k] * coin_amp * scale_amp)
            glow(canvas, px, py, pr * 0.14,
                 wcol, 0.5 * borne[k] * coin_amp * scale_amp)
    # force chains — photoelastic ropes
    if stress_pairs:
        wmax = max(w for *_, w in stress_pairs) or 1.0
        for kind, i, j, w in stress_pairs:
            wn = w / wmax
            if wn < 0.02:
                continue
            xi = np.array([cx + centers[i][0] * S, cy + centers[i][1] * S])
            if kind == "pair":
                xj = np.array([cx + centers[j][0] * S, cy + centers[j][1] * S])
            else:  # tray: from center outward to rim point
                d = np.array(centers[i]) / (np.hypot(*centers[i]) or 1.0)
                xj = np.array([cx + d[0] * R, cy + d[1] * R])
            amp = (0.7 + 2.6 * wn) * chain_amp * scale_amp
            wd = rim_w * (0.75 + 1.5 * wn)
            # wide soft under-glow + crisp rope
            draw_segment(canvas, xi, xj, STRESS, amp=amp * 0.8, width=wd * 3.2)
            draw_segment(canvas, xi, xj, (1.0, 0.88, 0.52), amp=amp, width=wd)
            if beads:
                if kind == "pair":
                    ri, rj = radii[i], radii[j]
                    t = ri / (ri + rj)
                    bx = xi + (xj - xi) * t
                else:
                    bx = xj
                splat_points(canvas, [bx[0]], [bx[1]],
                             [amp * 34 * canvas.ss], (1.0, 0.92, 0.62),
                             sigma_px=rim_w * 1.35)


def draw_ghost_court(canvas, cx, cy, R, centers, radii, scale_amp=1.0):
    """A ring that closes in angle but overlaps: thin ghost rings,
    overlap lenses lit cold."""
    S = R
    draw_ring(canvas, cx, cy, R, GHOST, amp=0.4 * scale_amp,
              width=1.1 * canvas.ss)
    N = len(radii)
    for (x, y), r in zip(centers, radii):
        p = curvature_of(r)
        col = tuple(0.72 * c + 0.28 * g for c, g in zip(PAL.get(p, GHOST), GHOST))
        draw_ring(canvas, cx + x * S, cy + y * S, r * S, col,
                  amp=0.55 * scale_amp, width=1.0 * canvas.ss)
    # overlap wounds
    for i in range(N):
        for j in range(i + 1, N):
            d = np.hypot(centers[i][0] - centers[j][0],
                         centers[i][1] - centers[j][1])
            if d < radii[i] + radii[j] - 1e-9:
                # lens: light both arcs inside the other circle
                for (a, b) in ((i, j), (j, i)):
                    xs, ys, _ = circle_pts(cx + centers[a][0] * S,
                                           cy + centers[a][1] * S,
                                           radii[a] * S, spacing=0.5)
                    dx = xs - (cx + centers[b][0] * S)
                    dy = ys - (cy + centers[b][1] * S)
                    ins = np.hypot(dx, dy) < radii[b] * S
                    if ins.any():
                        splat_points(canvas, xs[ins], ys[ins],
                                     0.30 * scale_amp * canvas.ss,
                                     WOUND, sigma_px=1.6 * canvas.ss)


# ------------------------------------------------------- apollonian dream
def soddy_fill(circles, tray_r=1.0, min_r=0.004, depth=64000):
    """Given tangent structure incl. tray, cascade inner Soddy circles in all
    curvilinear-triangle pockets. circles: list of (x, y, r). Tray = curvature
    -1/tray_r centered origin. Returns list of ghost (x,y,r).
    Complex Descartes: b4 z4 = b1 z1 + b2 z2 + b3 z3 ± 2 sqrt(b1 b2 z1 z2 + ...)."""
    base = [(-1.0 / tray_r, 0j)]
    for (x, y, r) in circles:
        base.append((1.0 / r, complex(x, y)))

    def tangent(c1, c2):
        b1, z1 = c1
        b2, z2 = c2
        d = abs(z1 - z2)
        if b1 < 0 or b2 < 0:
            bi, zi = (c1 if b1 > 0 else c2)
            return abs(d - (tray_r - 1.0 / bi)) < 1e-7
        return abs(d - (1.0 / b1 + 1.0 / b2)) < 1e-7

    out = []
    from itertools import combinations
    pockets = []
    for trip in combinations(range(len(base)), 3):
        c1, c2, c3 = base[trip[0]], base[trip[1]], base[trip[2]]
        if tangent(c1, c2) and tangent(c2, c3) and tangent(c1, c3):
            pockets.append((c1, c2, c3))

    existing = list(base)

    def free(b, z):
        r = 1.0 / b
        if abs(z) + r > tray_r + 1e-7:
            return False
        for bb, zz in existing:
            if bb < 0:
                continue
            rr = 1.0 / bb
            if abs(z - zz) < r + rr - 1e-7:
                return False
        return True

    work = pockets
    while work and len(out) < depth:
        nxt = []
        for (c1, c2, c3) in work:
            (b1, z1), (b2, z2), (b3, z3) = c1, c2, c3
            s = b1 * b2 * z1 * z2 + b2 * b3 * z2 * z3 + b1 * b3 * z1 * z3
            rt = np.sqrt(complex(b1 * b2 + b2 * b3 + b1 * b3))
            for sgn in (+1, -1):
                b4 = b1 + b2 + b3 + sgn * 2 * rt.real
                if b4 <= 0 or 1.0 / b4 < min_r:
                    continue
                zrt = np.sqrt(s)
                for zsgn in (+1, -1):
                    z4 = (b1 * z1 + b2 * z2 + b3 * z3 + zsgn * 2 * zrt) / b4
                    # check tangency to all three parents
                    okc = all(
                        abs(abs(z4 - zz) - abs(1.0 / b4 + (1.0 / bb if bb > 0 else -tray_r)))
                        < 2e-6 if bb < 0 else
                        abs(abs(z4 - zz) - (1.0 / b4 + 1.0 / bb)) < 2e-6
                        for bb, zz in (c1, c2, c3))
                    if okc and free(b4, z4):
                        existing.append((b4, z4))
                        out.append((z4.real, z4.imag, 1.0 / b4))
                        c4 = (b4, z4)
                        nxt += [(c1, c2, c4), (c1, c3, c4), (c2, c3, c4)]
                        break
        work = nxt
    return out
