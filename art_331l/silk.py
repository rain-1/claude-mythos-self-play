# silk.py — embroidery register: silk floss threads laid over linen, with tube shading,
# Kajiya–Kay sheen (the shimmer of satin stitch changes with stitch direction), floss twist,
# soft lavender thread shadows, a wooden hoop.  Threads are polylines, alpha-OVER in order.
import numpy as np, numba as nb
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, shift as ndshift

WHEEL = np.array([
    (0.95, 0.42, 0.52),  # strawberry
    (1.00, 0.62, 0.48),  # peach
    (0.99, 0.82, 0.42),  # butter
    (0.72, 0.86, 0.45),  # lime
    (0.45, 0.83, 0.70),  # mint
    (0.45, 0.72, 0.95),  # sky
    (0.56, 0.60, 0.95),  # periwinkle
    (0.74, 0.56, 0.93),  # lilac
    (0.96, 0.55, 0.80),  # bubblegum
])
CORAL = np.array((1.0, 0.45, 0.38))
INK = np.array((0.36, 0.30, 0.40))

def wheel(t):
    t = np.clip(t, 0, 1) * (len(WHEEL) - 1)
    i = min(int(t), len(WHEEL) - 2); f = t - i
    return np.exp((1 - f) * np.log(WHEEL[i]) + f * np.log(WHEEL[i + 1]))

def linen(H, W, seed=1, period=5.0, amp=0.022, base=(0.992, 0.985, 0.972)):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # warp/weft with per-thread thickness jitter (slubs)
    nx = int(W / period) + 2; ny = int(H / period) + 2
    jx = rng.normal(0, 1, nx).astype(np.float32); jy = rng.normal(0, 1, ny).astype(np.float32)
    slub = gaussian_filter(rng.normal(0, 1, (H // 8 + 1, W // 8 + 1)).astype(np.float32), 3)
    slub = np.kron(slub, np.ones((8, 8), np.float32))[:H, :W]
    slub /= slub.std() + 1e-6
    ix = (x / period).astype(int); iy = (y / period).astype(int)
    wx = np.sin(np.pi * (x / period)) ** 2 * (0.6 + 0.4 * np.tanh(jx[ix]))
    wy = np.sin(np.pi * (y / period)) ** 2 * (0.6 + 0.4 * np.tanh(jy[iy]))
    checker = ((ix + iy) & 1).astype(np.float32)
    t = checker * wx + (1 - checker) * wy
    tex = 1 + amp * (t - 0.5) + 0.006 * slub
    img = np.empty((H, W, 3), np.float32)
    for c in range(3): img[..., c] = base[c] * tex
    return img

@nb.njit(cache=True)
def draw_polyline(acc, alp, cov, pts, rad, col, opac, lx, ly, lz, twist_period, sheen_amt, sheen_pow):
    """alpha-over one thread (polyline pts Nx2) onto premultiplied acc/alp; cov = coverage sum."""
    H, W = alp.shape
    s_along = 0.0
    for k in range(pts.shape[0] - 1):
        ax, ay = pts[k, 0], pts[k, 1]; bx, by = pts[k + 1, 0], pts[k + 1, 1]
        dx = bx - ax; dy = by - ay; L2 = dx * dx + dy * dy
        if L2 < 1e-9:
            continue
        L = np.sqrt(L2); tx = dx / L; ty = dy / L
        # Kajiya-Kay with V=(0,0,1): spec = sin(T,L)^p
        tl = tx * lx + ty * ly
        sinTL = np.sqrt(max(0.0, 1.0 - tl * tl))
        spec = sinTL ** sheen_pow
        x0 = int(max(0, np.floor(min(ax, bx) - rad - 1))); x1 = int(min(W - 1, np.ceil(max(ax, bx) + rad + 1)))
        y0 = int(max(0, np.floor(min(ay, by) - rad - 1))); y1 = int(min(H - 1, np.ceil(max(ay, by) + rad + 1)))
        for yy in range(y0, y1 + 1):
            for xx in range(x0, x1 + 1):
                px = xx + 0.5 - ax; py = yy + 0.5 - ay
                u = px * tx + py * ty
                # exclude the shared endpoint of the next segment to avoid double hits
                if u < 0.0 or u > L:
                    if k > 0 and u < 0.0:
                        continue
                    if u > L and k < pts.shape[0] - 2:
                        continue
                uc = min(max(u, 0.0), L)
                qx = px - uc * tx; qy = py - uc * ty
                d = np.sqrt(qx * qx + qy * qy)
                a = rad + 0.5 - d
                if a <= 0.0:
                    continue
                if a > 1.0:
                    a = 1.0
                a *= opac
                tt = min(d / rad, 1.0)
                nz = np.sqrt(max(0.0, 1.0 - tt * tt))
                side = -qx * ty + qy * tx  # signed across-thread coordinate
                # floss twist: diagonal stripes along the thread
                tw = 0.5 + 0.5 * np.sin(6.2831853 * ((s_along + u) / twist_period + 0.35 * side / rad))
                diff = 0.58 + 0.42 * nz - 0.07 * tw
                sh = sheen_amt * spec * nz * nz * (0.75 + 0.25 * tw)
                for c in range(3):
                    v = col[c] * diff + sh
                    acc[yy, xx, c] = acc[yy, xx, c] * (1.0 - a) + v * a
                alp[yy, xx] = alp[yy, xx] * (1.0 - a) + a
                cov[yy, xx] += a
        s_along += L

def composite(ground, acc, alp, cov, shadow_dx=4.0, shadow_dy=6.0, shadow_blur=5.0, shadow_k=0.30,
              shadow_tint=(0.80, 0.78, 0.95)):
    sh = gaussian_filter(np.minimum(cov, 3.0) / 3.0, shadow_blur)
    sh = ndshift(sh, (shadow_dy, shadow_dx), order=1, mode='constant')
    sh = np.clip(sh, 0, 1)[..., None]
    tint = np.array(shadow_tint, np.float32)
    g = ground * (1 - shadow_k * sh * (1 - tint) / (1 - tint).max()) * (1 - 0.10 * sh)
    return acc + (1 - alp[..., None]) * g

def bezier(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3

def hoop(img, cx, cy, R, w, ang_clasp=-np.pi / 2, seed=3):
    """wooden embroidery hoop drawn over img (in place). R = inner radius, w = ring width."""
    H, W, _ = img.shape
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = x - cx; dy = y - cy; r = np.sqrt(dx * dx + dy * dy); th = np.arctan2(dy, dx)
    # soft drop shadow of the ring onto the fabric/table
    ring_mask = np.clip(np.minimum(r - R, R + w - r) + 0.5, 0, 1)
    shadow = gaussian_filter(ring_mask, w * 0.35)
    shadow = ndshift(shadow, (w * 0.22, w * 0.12), order=1)
    img *= 1 - shadow[..., None] * np.array([0.20, 0.21, 0.12], np.float32)
    # wood: profile across ring (rounded), grain along angle
    s = np.clip((r - R) / w, 0, 1)
    prof = np.sqrt(np.clip(1 - (2 * s - 1) ** 2, 0, 1))
    nx_ = (2 * s - 1)  # outward slope
    # light from top-left
    lxy = np.array([-0.5, -0.7]); lxy /= np.linalg.norm(lxy)
    ndot = nx_ * (dx / (r + 1e-6) * lxy[0] + dy / (r + 1e-6) * lxy[1]) * 0.8 + prof * 0.6
    gr = np.zeros_like(r)
    for k, f in enumerate([7, 19, 43, 97]):
        ph = rng.uniform(0, 6.28, 3)
        gr += (np.sin(f * th + ph[0] + 3 * np.sin(2 * th + ph[1])) * 0.5 / (k + 1))
    grain = 0.5 + 0.5 * np.sin(55 * s + 2.5 * gr + 4 * np.sin(3 * th))
    wood = np.stack([0.95 - 0.06 * grain, 0.84 - 0.08 * grain, 0.68 - 0.08 * grain], -1)
    shade = (0.78 + 0.30 * ndot)[..., None]
    spec = (np.clip(ndot, 0, 1) ** 12 * 0.25)[..., None]
    col = wood * shade + spec
    # inner/outer seam line between the two rings
    seam = np.exp(-((s - 0.5) / 0.03) ** 2)[..., None] * 0.10
    col = col * (1 - seam)
    a = ring_mask[..., None]
    img[:] = img * (1 - a) + col * a
    # brass clasp
    ccx = cx + (R + w * 0.5) * np.cos(ang_clasp); ccy = cy + (R + w * 0.5) * np.sin(ang_clasp)
    bw, bh = w * 0.9, w * 1.7
    m = (np.abs(x - ccx) < bw / 2) & (np.abs(y - ccy) < bh / 2)
    gy = (y - (ccy - bh / 2)) / bh
    brass = np.stack([0.98 - 0.15 * gy, 0.86 - 0.18 * gy, 0.58 - 0.15 * gy], -1)
    sh2 = gaussian_filter(m.astype(np.float32), w * 0.15); sh2 = ndshift(sh2, (w * 0.12, w * 0.08), order=1)
    img *= (1 - 0.18 * sh2[..., None])
    mm = gaussian_filter(m.astype(np.float32), 0.7)[..., None]
    img[:] = img * (1 - mm) + brass * mm
    # screw head
    rr = np.sqrt((x - ccx) ** 2 + (y - (ccy - bh * 0.62)) ** 2)
    sm = np.clip(w * 0.32 - rr + 0.5, 0, 1)[..., None]
    sc = np.stack([0.96 - 0.25 * (rr / (w * 0.32)), 0.88 - 0.25 * (rr / (w * 0.32)), 0.66 - 0.2 * (rr / (w * 0.32))], -1)
    img[:] = img * (1 - sm) + sc * sm
    return img

def to_u8(img):
    return (np.clip(img, 0, 1) ** (1 / 1.0) * 255 + 0.5).astype(np.uint8)

def font(kind, size):
    p = {'title': '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
         'ital': '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
         'reg': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
         'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'}[kind]
    return ImageFont.truetype(p, size)
