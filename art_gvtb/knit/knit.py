"""Stockinette renderer: a colour chart -> knitted fabric (linear RGB + alpha + height).

Each stitch is a V of two yarn legs.  Legs are tapered capsules with a twisted-ply
striation and a little fuzz.  Rows are laid from the bottom up so each V's point
sits on top of the stitch below it.
"""
import numpy as np
from scipy import ndimage


def srgb2lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def render_knit(C, w=44, hr=0.8, seed=0, light=(-0.55, -0.65, 0.52)):
    """C: (rows, cols, 3) sRGB chart, row 0 at the TOP. Returns rgb (lin), alpha, height."""
    rng = np.random.default_rng(seed)
    R, Q = C.shape[:2]
    h = w * hr
    pad = int(0.8 * h)
    H = int(R * h) + 2 * pad; W = int(Q * w) + 2 * pad
    rgb = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    hgt = np.zeros((H, W), np.float32)
    L = np.array(light, float); L /= np.linalg.norm(L)
    Clin = srgb2lin(C)
    # per-stitch jitter so the fabric breathes
    jx = rng.normal(0, 0.035 * w, (R, Q)); jy = rng.normal(0, 0.03 * h, (R, Q))
    tw = rng.uniform(0, 2 * np.pi, (R, Q, 2))
    fuzz = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 0.8)
    fuzz /= fuzz.std()
    for r in range(R - 1, -1, -1):          # bottom row first
        yc = pad + (r + 0.5) * h
        y0 = int(max(0, yc - 0.85 * h)); y1 = int(min(H, yc + 0.95 * h))
        ys = np.arange(y0, y1)[:, None].astype(np.float32)
        xs = np.arange(W)[None, :].astype(np.float32)
        col = np.clip(((xs - pad) / w).astype(int), 0, Q - 1)  # stitch column of each x
        col = np.broadcast_to(col, (len(ys), W))
        cx = pad + (col + 0.5) * w + jx[r, col]
        cyy = yc + jy[r, col]
        best_z = np.full((len(ys), W), -1.0, np.float32)
        nrm = np.zeros((len(ys), W, 3), np.float32)
        stripe = np.zeros((len(ys), W), np.float32)
        for side in (-1, 1):
            bx = cx + side * 0.03 * w; by = cyy + 0.62 * h
            tx = cx + side * 0.40 * w; ty = cyy - 0.60 * h
            ex, ey = tx - bx, ty - by
            ll = np.sqrt(ex * ex + ey * ey)
            px, py = xs - bx, ys - by
            t = np.clip((px * ex + py * ey) / (ll * ll), 0, 1)
            qx, qy = px - t * ex, py - t * ey
            # bulge outward in the middle (a curved leg)
            bulge = side * 0.07 * w * np.sin(np.pi * t)
            qx = qx - bulge
            d = np.sqrt(qx * qx + qy * qy)
            rad = w * (0.17 + 0.09 * np.sin(np.pi * np.clip(t * 1.05, 0, 1)) ** 0.7) * (0.92 + 0.08 * (1 - t))
            s = d / rad
            inside = s < 1
            z = np.sqrt(np.clip(1 - s * s, 0, 1))
            # normal: across-leg direction in xy, z up
            ax = qx / (d + 1e-6); ay = qy / (d + 1e-6)
            nx = ax * s; ny = ay * s; nz = z
            # ply twist: stripes running diagonally across the leg
            across = (qx * (-ey) + qy * ex) / (ll + 1e-6) / rad
            ph = t * ll / (w * 0.115) + across * 1.3 * side + tw[r, col, (side + 1) // 2]
            st = 0.5 + 0.5 * np.cos(2 * np.pi * ph)
            upd = inside & (z > best_z)
            # depth ordering: second leg drawn only where it is higher
            best_z = np.where(upd, z, best_z)
            for c, v in enumerate((nx, ny, nz)):
                nrm[..., c] = np.where(upd, v, nrm[..., c])
            stripe = np.where(upd, st, stripe)
        cov = best_z >= 0
        if not cov.any():
            continue
        lam = np.clip(nrm[..., 0] * L[0] + nrm[..., 1] * L[1] + nrm[..., 2] * L[2], 0, 1)
        shade = 0.42 + 0.68 * lam
        shade *= 0.80 + 0.20 * stripe
        shade *= 1 + 0.05 * fuzz[y0:y1]
        # soft sheen on top of each ply
        sheen = 0.10 * (np.clip(nrm[..., 2], 0, 1) ** 8) * stripe
        base = Clin[r, col]
        out = base * shade[..., None] + sheen[..., None]
        zz = 1.0 + best_z * 0.6
        a = np.clip(best_z * 6, 0, 1)  # soft silhouette
        sl = (slice(y0, y1), slice(None))
        rgb[sl] = np.where(cov[..., None], out * a[..., None] + rgb[sl] * (1 - a[..., None]), rgb[sl])
        hgt[sl] = np.where(cov, np.maximum(hgt[sl] * (1 - a) + (zz + r * 0) * a, hgt[sl] * 0.0 + zz * a), hgt[sl])
        alpha[sl] = np.maximum(alpha[sl], a * cov)
    # gaps between stitches read as shadowed yarn below
    return rgb, alpha, hgt, pad


if __name__ == '__main__':
    import sys
    from PIL import Image
    from design import design
    C, _ = design(W=24, bands=2, bh=13, gap=4)
    rgb, a, hgt, pad = render_knit(C, w=44)
    bg = srgb2lin([0.55, 0.5, 0.55])
    out = rgb + (1 - a[..., None]) * bg
    g = np.where(out <= 0.0031308, 12.92 * out, 1.055 * np.clip(out, 0, None) ** (1 / 2.4) - 0.055)
    Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8)).save('/tmp/claude-0/knit_test.png')
