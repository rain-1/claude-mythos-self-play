"""Storybook origami paper boats (upright 3/4 view) with a little V-wake along their heading."""
import numpy as np
from PIL import Image, ImageDraw


def _poly(S, sc, x0, pts, box):
    bx0, by0, bw, bh = box
    m = Image.new('L', (bw, bh), 0)
    ImageDraw.Draw(m).polygon([((x - x0) * sc - bx0, (y - x0) * sc - by0) for x, y in pts], fill=255)
    return np.asarray(m, np.float32) / 255


def render_boats(W, x0, x1, boats, light_dir, ss=3):
    """boats: list of (cx, cy, L, heading, rgb_linear). returns colour (W,W,3), alpha (W,W), wake (W,W)."""
    S = W * ss
    sc = S / (x1 - x0)
    col = np.zeros((S, S, 3), np.float32)
    alp = np.zeros((S, S), np.float32)
    wake = Image.new('L', (S, S), 0)
    wd = ImageDraw.Draw(wake)
    for (cx, cy, L, hd, rgb) in boats:
        rgb = np.array(rgb, np.float32)
        f = 1.0 if np.cos(hd) >= 0 else -1.0     # bow on the side the boat is heading
        def P(pts):
            return [(cx + f * x * L, cy + y * L) for x, y in pts]
        h = 0.26
        bx0 = int((cx - 0.8 * L - x0) * sc); by0 = int((cy - 0.8 * L - x0) * sc)
        bw = bh = int(1.6 * L * sc) + 2
        box = (bx0, by0, bw, bh)
        cs = col[by0:by0 + bh, bx0:bx0 + bw]; as_ = alp[by0:by0 + bh, bx0:bx0 + bw]
        faces = [
            (P([(-0.5, 0), (0.5, 0), (0.42, -0.07), (-0.42, -0.07)]), 0.74),  # open deck (inside)
            (P([(-0.5, 0), (0.5, 0), (0.27, h), (-0.27, h)]), 0.97),          # hull side
            (P([(-0.5, 0), (-0.27, h), (-0.20, h * 0.55)]), 0.86),            # stern fold
            (P([(0.5, 0), (0.27, h), (0.20, h * 0.55)]), 0.88),               # bow fold
            (P([(-0.26, -0.035), (0.0, -0.035), (0.0, -0.60)]), 1.05),          # sail, lit
            (P([(0.0, -0.035), (0.26, -0.035), (0.0, -0.60)]), 0.84),           # sail, shade
        ]
        for pts, sh in faces:
            a = _poly(S, sc, x0, pts, box)
            cs[:] = cs * (1 - a[..., None]) + rgb * sh * a[..., None]
            as_[:] = np.maximum(as_, a)
        # crease lines
        m = Image.new('L', (bw, bh), 0); d = ImageDraw.Draw(m)
        lw = max(1, int(0.012 * L * sc))
        for seg in [P([(0.0, -0.035), (0.0, -0.60)]), P([(-0.5, 0), (0.5, 0)]), P([(-0.2, h * 0.55), (-0.27, h)]), P([(0.2, h * 0.55), (0.27, h)])]:
            d.line([((x - x0) * sc - bx0, (y - x0) * sc - by0) for x, y in seg], fill=255, width=lw)
        a = np.asarray(m, np.float32) / 255 * 0.5
        cs[:] = cs * (1 - a[..., None] * 0.25)
        # V-wake: two thin arcs trailing behind along -heading
        ux, uy = np.cos(hd), np.sin(hd)
        bx, by = cx - ux * 0.45 * L, cy - uy * 0.45 * L + 0.2 * h * L
        for side in (-1, 1):
            for j, s in enumerate((1.0, 1.7, 2.4)):
                ang = hd + np.pi + side * 0.33
                ex, ey = bx + np.cos(ang) * s * L, by + np.sin(ang) * s * L
                q = [((bx + (ex - bx) * t - x0) * sc, (by + (ey - by) * t - x0) * sc) for t in np.linspace(0.15 * j + 0.1, 0.15 * j + 0.55, 8)]
                wd.line(q, fill=int(200 - 50 * j), width=max(1, int(0.022 * L * sc)))
    col = col.reshape(W, ss, W, ss, 3).mean((1, 3))
    alp = alp.reshape(W, ss, W, ss).mean((1, 3))
    wk = (np.asarray(wake, np.float32) / 255).reshape(W, ss, W, ss).mean((1, 3))
    return col, alp, wk
