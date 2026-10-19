"""Frame a square render as a round porthole in a gold ring on paper, with caption."""
import sys
import numpy as np
from PIL import Image
from brooch import tonemap
from caption import caption

def frame(img, W, H, cy_frac=0.44, R_frac=0.40):
    S = img.shape[0]
    out = np.ones((H, W, 3), np.float32) * np.array([0.992, 0.985, 0.975], np.float32)
    cx, cy = W / 2, H * cy_frac
    R = R_frac * W
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.sqrt(dx * dx + dy * dy)
    # shadow
    rs = np.sqrt((dx - 0.02 * R) ** 2 + (dy - 0.03 * R) ** 2)
    t = np.clip((rs - R * 1.06) / (0.08 * R), 0, None)
    sh = np.where(rs < R * 1.06, 1.0, np.exp(-t * t * 1.4))
    out -= sh[..., None] * np.array([0.09, 0.12, 0.05], np.float32)
    # window content
    ox, oy = int(cx - S / 2), int(cy - S / 2)
    inside = r < R
    sub = np.zeros_like(out)
    sub[oy:oy + S, ox:ox + S] = img
    out = np.where(inside[..., None], sub, out)
    # inner glass shadow at the rim
    rim = np.exp(-((R - r) / (0.03 * R)) ** 2) * inside
    out *= (1 - 0.18 * rim)[..., None]
    # gold ring: convex profile
    ring = (r >= R) & (r < R * 1.06)
    q = (r - R) / (0.06 * R)
    nr = (q - 0.5) * 1.6
    ang = np.arctan2(-dy, dx)
    nx = nr * np.cos(ang); ny = nr * np.sin(ang)
    lx, ly = -0.5, 0.42
    L = 0.75 + 0.45 * np.clip(nx * lx + ny * ly, -1, 1) + 0.35 * np.exp(-((nx * lx + ny * ly) - 0.6) ** 2 * 8)
    gold = np.array([0.98, 0.80, 0.50], np.float32)
    g = gold[None, None, :] * (0.42 + 0.5 * L[..., None]) + np.maximum(L - 1.0, 0)[..., None] * 0.6
    out = np.where(ring[..., None], g, out)
    return out

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    img = np.load(src)
    W, H = int(sys.argv[3]), int(sys.argv[4])
    out = frame(img, W, H)
    im = Image.fromarray(tonemap(out, 1.0))
    caption(im, sys.argv[5], sys.argv[6], sys.argv[7], int(H * 0.885), line3=sys.argv[8] if len(sys.argv) > 8 else None)
    im.save(dst)
