"""render_coxeter.py — n runners: every 2-face of the permutohedron as a glaze, Coxeter-plane view.

Each 2-face (an ordered partition with n−2 blocks: a three-way tie = hexagon, two two-way ties =
square) is a convex polygon in the projection; it is rasterised with an anti-aliased signed
distance (min over its edges) and added as pigment density, so the picture is a Beer–Lambert stack
of 16 800 translucent tiles for n = 7.
usage: render_coxeter.py n S out.png [key=val]
"""
import sys, numpy as np
from coxeter import faces2
from sorbet import Sheet, PIG, absorb, finish, text_mask

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

WHEEL = ['strawberry', 'peach', 'butter', 'lime', 'mint', 'sky', 'periwinkle', 'lilac', 'bubblegum']


def wheel_ab(h):
    n = len(WHEEL); x = (h % 1.0) * n; i = int(x) % n; t = x - int(x)
    return (1 - t) * absorb(WHEEL[i]) + t * absorb(WHEEL[(i + 1) % n])


def raster(acc, pts, val, edge_acc=None, ew=1.0):
    """add val*coverage of convex polygon pts (k,2) [x,y] into acc (H,W) (or (H,W,3) with val rgb)"""
    H, W = acc.shape[:2]
    x0, y0 = np.floor(pts.min(0)).astype(int) - 2
    x1, y1 = np.ceil(pts.max(0)).astype(int) + 2
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W), min(y1, H)
    if x1 <= x0 or y1 <= y0:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32) + 0.5
    # orientation
    a = pts; b = np.roll(pts, -1, 0)
    area = np.sum(a[:, 0] * b[:, 1] - b[:, 0] * a[:, 1])
    sgn = 1 if area > 0 else -1
    d = np.full(xs.shape, np.inf, np.float32)
    for (ax, ay), (bx, by) in zip(a, b):
        ex, ey = bx - ax, by - ay
        L = np.hypot(ex, ey) + 1e-9
        s = sgn * ((xs - ax) * ey - (ys - ay) * ex) / L     # >0 inside (for ccw in y-down coords)
        d = np.minimum(d, -s)
    cov = np.clip(d + 0.5, 0, 1)
    if acc.ndim == 3:
        acc[y0:y1, x0:x1] += cov[..., None] * val
    else:
        acc[y0:y1, x0:x1] += cov * val
    if edge_acc is not None:
        edge_acc[y0:y1, x0:x1] += np.clip(1 - np.abs(d) / ew, 0, 1) * (d > -ew)


def main():
    n, S, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    mode = P('mode', 'pos')
    F = faces2(n)
    w = np.exp(2j * np.pi * np.arange(n) / n)
    rot = np.exp(1j * P('rot', np.pi / 2))
    Z = [np.asarray(poly) @ w * rot for _, _, _, poly in F]
    cen = np.mean([z.mean() for z in Z])
    Z = [z - cen for z in Z]
    R = max(np.abs(z).max() for z in Z)
    cx, cy, sc = S / 2, S * P('cy', 0.455), S * P('scale', 0.43) / R
    A = np.zeros((S, S, 3), np.float32)
    E = np.zeros((S, S), np.float32)
    dens = P('dens', 0.05)
    ew = max(0.8, S * P('ew', 0.00045))
    for (kind, T, pos, poly), z in zip(F, Z):
        pts = np.stack([cx + sc * z.real, cy - sc * z.imag], 1)
        if mode == 'pos':
            h = (np.mean(pos) + 1) / (n) * P('span', 0.9) + P('h0', 0.0)
        elif mode == 'dir':
            ang = np.angle(sum(w[r] for B in T for r in B) * rot)
            h = (ang / (2 * np.pi)) % 1 + P('h0', 0.0)
        elif mode == 'last':      # hue = who finishes last (the runner pulling hardest)
            v0 = np.asarray(poly[0]); last = [r for r in range(n) if max(np.asarray(p)[r] for p in poly) == n - 1]
            vec = sum(np.exp(2j * np.pi * r / n) for r in last) * rot
            h = (np.angle(vec) / (2 * np.pi)) % 1 + P('h0', 0.0)
        elif mode == 'ang':
            c = z.mean()
            h = (np.angle(c) / (2 * np.pi)) * P('fold', 1.0) + P('h0', 0.0) + P('rad', 0.0) * abs(c) / R
        else:
            h = (0.62 if kind == 'hex' else 0.05)
        wt = P('whex', 1.0) if kind == 'hex' else P('wsq', 0.7)
        raster(A, pts, dens * wt * wheel_ab(h), E, ew)
    np.save(out.replace('.png', '_A.npy'), A.astype(np.float16)); np.save(out.replace('.png', '_E.npy'), E.astype(np.float16))
    sh = Sheet(S, S, seed=3)
    sh.wash_rgb(A)
    lin = develop(sh, E)
    lin.save(out)


def develop(sh, E):
    from PIL import Image
    dmax = P('dmax', 1.7)
    A = dmax * (1 - np.exp(-sh.A / dmax))
    lin = np.clip(sh.paper * np.exp(-A), 0, 1)
    e = np.clip(P('edge', 0.35) * E, 0, 1)[..., None]
    lin = lin + (1 - lin) * e                          # face edges as light seams (glass leading)
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    return Image.fromarray(np.clip(srgb * 255 + 0.5, 0, 255).astype(np.uint8))


if __name__ == '__main__':
    main()
