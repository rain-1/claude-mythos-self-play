"""Hero: a random domino tiling as glossy candy bars, tied by one baker's-twine path that
enters each domino by one half and leaves by the other.  Top-down relief render (numba)."""
import numpy as np, numba as nb, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, '..')

WHEEL = np.array([[1.00,0.60,0.66],[1.00,0.74,0.58],[1.00,0.90,0.60],[0.80,0.93,0.62],[0.62,0.92,0.80],
                  [0.60,0.84,0.98],[0.70,0.74,0.99],[0.84,0.72,0.98],[1.00,0.70,0.88]], np.float64)
def wheel(t):
    t = np.asarray(t, float) % 1.0 * len(WHEEL); i = np.floor(t).astype(int) % len(WHEEL); f = (t - i)[..., None]
    f = f * f * (3 - 2 * f)
    return WHEEL[i] * (1 - f) + WHEEL[(i + 1) % len(WHEEL)] * f

@nb.njit(parallel=True, cache=True)
def dominoes(S, x0, y0, u, idx, cen, half, col, H):
    """height + albedo of rounded pillow dominoes."""
    n = idx.shape[0]
    h = np.zeros((S, S), np.float32); alb = np.ones((S, S, 3), np.float32); msk = np.zeros((S, S), np.float32)
    gap = 0.055; rad = 0.17; bev = 0.20
    for py in nb.prange(S):
        for px in range(S):
            gx = (px + 0.5 - x0) / u; gy = (py + 0.5 - y0) / u
            c = int(math.floor(gx)); r = int(math.floor(gy))
            if c < 0 or r < 0 or c >= n or r >= n: continue
            d = idx[r, c]
            qx = abs(gx - cen[d, 0]) - (half[d, 0] - gap - rad); qy = abs(gy - cen[d, 1]) - (half[d, 1] - gap - rad)
            sd = math.sqrt(max(qx, 0.0) ** 2 + max(qy, 0.0) ** 2) + min(max(qx, qy), 0.0) - rad
            if sd >= 0: continue
            t = min(-sd / bev, 1.0)
            prof = math.sqrt(1 - (1 - t) ** 2)
            # slight overall crown so the top is not dead flat
            crown = 0.06 * (1 - (2 * (gx - cen[d, 0]) / (2 * half[d, 0])) ** 2) * (1 - (2 * (gy - cen[d, 1]) / (2 * half[d, 1])) ** 2)
            tl = (gx - cen[d, 0]) if half[d, 0] > half[d, 1] else (gy - cen[d, 1])
            groove = 0.0
            if half[d, 0] != half[d, 1]: groove = 0.16 * math.exp(-(tl / 0.035) ** 2)
            h[py, px] = H * (prof * (0.9 - groove) + crown) * u
            msk[py, px] = min(-sd * u / 1.2, 1.0)
            for k in range(3): alb[py, px, k] = col[d, k]
    return h, alb, msk

@nb.njit(cache=True)
def tube(S, pts, rc, hbase):
    """swept sphere along dense polyline pts (pixels); returns height above base, arc index, lateral offset."""
    hh = np.zeros((S, S), np.float32); ti = -np.ones((S, S), np.int32); lat = np.zeros((S, S), np.float32)
    m = pts.shape[0]; R = int(rc) + 2
    for i in range(m):
        cx = pts[i, 0]; cy = pts[i, 1]
        j = min(i + 1, m - 1); k = max(i - 1, 0)
        tx = pts[j, 0] - pts[k, 0]; ty = pts[j, 1] - pts[k, 1]; tn = math.sqrt(tx * tx + ty * ty) + 1e-9; tx /= tn; ty /= tn
        for py in range(max(int(cy) - R, 0), min(int(cy) + R + 1, S)):
            for px in range(max(int(cx) - R, 0), min(int(cx) + R + 1, S)):
                dx = px + 0.5 - cx; dy = py + 0.5 - cy; d2 = dx * dx + dy * dy
                if d2 < rc * rc:
                    z = math.sqrt(rc * rc - d2)
                    if z > hh[py, px]:
                        hh[py, px] = z; ti[py, px] = i; lat[py, px] = (dx * (-ty) + dy * tx) / rc
    return hh, ti, lat

def fillet(P, rad, step):
    """P: lattice polyline (k,2) in pixels with unit-cell corners; round each corner by radius rad; resample every `step` px."""
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        d1 = (b - a) / np.linalg.norm(b - a); d2 = (c - b) / np.linalg.norm(c - b)
        if abs(d1 @ d2) > 0.99: out.append(b); continue
        p1 = b - d1 * rad; p2 = b + d2 * rad; ctr = p1 + d2 * rad
        a1 = math.atan2(*(p1 - ctr)[::-1]); a2 = math.atan2(*(p2 - ctr)[::-1])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for s in np.linspace(0, 1, 12):
            out.append(ctr + rad * np.array([math.cos(a1 + da * s), math.sin(a1 + da * s)]))
    out.append(P[-1]); out = np.array(out)
    seg = np.linalg.norm(np.diff(out, axis=0), axis=1); L = np.concatenate([[0], np.cumsum(seg)])
    s = np.arange(0, L[-1], step)
    return np.stack([np.interp(s, L, out[:, 0]), np.interp(s, L, out[:, 1])], 1), s

def blur(a, r):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(a.astype(np.float32), r, mode='nearest')

def shift(a, dx, dy):
    b = np.zeros_like(a); S = a.shape[0]
    b[dy:, dx:] = a[:S - dy, :S - dx]; return b

def font(name, sz): return ImageFont.truetype(f'/usr/share/fonts/truetype/{name}', int(sz))

def render(npz, S=1024, outname='proto.png', seedc=0, cycles=1.0, hue0=0.0):
    D = np.load(npz); idx = D['idx']; cells = D['cells'].astype(float); path = D['path']; n = idx.shape[0]; ND = len(cells)
    B = 0.80 * S; u = B / n; x0 = (S - B) / 2; y0 = 0.06 * S
    cen = np.zeros((ND, 2)); half = np.zeros((ND, 2))
    for d in range(ND):
        (r1, c1), (r2, c2) = cells[d]
        cen[d] = ((c1 + c2) / 2 + 0.5, (r1 + r2) / 2 + 0.5); half[d] = (1.0, 0.5) if r1 == r2 else (0.5, 1.0)
    col = np.tile(np.array([0.975, 0.972, 0.985]), (ND, 1))
    order = -np.ones(ND, int); order[path] = np.arange(len(path))
    col[path] = wheel(hue0 + cycles * np.arange(len(path)) / len(path))
    h, alb, msk = dominoes(S, x0, y0, u, idx, cen, half, col.astype(np.float32), 0.20)
    # path polyline: black cell -> white cell of each domino in order (cells stored (black, white) as (r,c))
    P = []
    for d in path:
        (rb, cb), (rw, cw) = cells[d]
        P.append((x0 + (cb + 0.5) * u, y0 + (rb + 0.5) * u)); P.append((x0 + (cw + 0.5) * u, y0 + (rw + 0.5) * u))
    P = np.array(P)
    pts, sarc = fillet(P, 0.30 * u, 0.6)
    rc = 0.085 * u
    th, ti, lat = tube(S, pts, rc, 0.0)
    # shading -------------------------------------------------------------
    Lv = np.array([-0.42, -0.55, 0.72]); Lv /= np.linalg.norm(Lv)
    Hv = Lv + np.array([0, 0, 1.0]); Hv /= np.linalg.norm(Hv)
    def shade(hf, k=1.0):
        gy, gx = np.gradient(hf * k)
        nz = 1 / np.sqrt(gx * gx + gy * gy + 1); nx = -gx * nz; ny = -gy * nz
        dif = np.clip(nx * Lv[0] + ny * Lv[1] + nz * Lv[2], 0, 1)
        sp = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)
        return dif, sp, nz
    paper = np.empty((S, S, 3), np.float32); paper[:] = (0.992, 0.985, 0.975)
    rng = np.random.default_rng(3)
    paper += (blur(rng.normal(0, 1, (S, S)), 0.7 * S / 1024)[..., None] * 0.006).astype(np.float32)
    # domino shadow on paper
    so = max(int(0.07 * u), 1)
    sh = blur(shift(msk, so, int(so * 1.3)), 0.09 * u) * 0.55 + blur(msk, 0.05 * u) * 0.25
    shadow_tint = np.array([0.62, 0.60, 0.80])
    img = paper * (1 - sh[..., None] * (1 - shadow_tint))
    dif, sp, nz = shade(h, 1.0)
    lit = 0.80 + 0.30 * (dif - Lv[2]) / (1 - Lv[2] + 1e-9) * 0.9
    lit = 0.70 + 0.40 * dif
    dom = alb * lit[..., None] + (1 - alb) * 0.10            # lifted shadows keep it pastel
    # soft sky fill in the bevels facing away
    dom = dom * (1 - 0.10 * (1 - nz)[..., None]) + 0.10 * (1 - nz)[..., None] * np.array([0.72, 0.74, 0.95])
    gl = np.clip((sp - 0.975) / 0.02, 0, 1) ** 1.5 * 0.75    # crisp window gloss on the bevel
    dom = dom + gl[..., None] * (1 - dom)
    # twine shadow on the dominoes / paper
    tm = (th > 0).astype(np.float32)
    ts = blur(shift(tm, max(int(0.045 * u), 1), max(int(0.06 * u), 1)), 0.035 * u) * 0.50
    dom = dom * (1 - ts[..., None] * (1 - np.array([0.55, 0.50, 0.72])))
    img = img * (1 - ts[..., None] * (1 - shadow_tint) * (1 - msk[..., None]))
    img = img * (1 - msk[..., None]) + dom * msk[..., None]
    # twine: two-ply twist, coral and white
    difT, spT, nzT = shade(th, 1.0)
    arc = sarc[np.clip(ti, 0, len(sarc) - 1)]
    ph = arc / (rc * 3.2) + lat * 0.75
    ply = 0.5 + 0.5 * np.sin(2 * np.pi * ph)
    plyw = np.clip((ply - 0.5) / 0.12 + 0.5, 0, 1)
    coral = np.array([0.98, 0.42, 0.40]); white = np.array([0.995, 0.975, 0.955])
    tcol = white * (1 - plyw[..., None]) + coral * plyw[..., None]
    groove = 1 - 0.22 * np.exp(-((ply - 0.5) / 0.10) ** 2)     # darker seam between plies
    tl = (0.50 + 0.58 * difT) * groove
    tw = tcol * tl[..., None]
    tg = np.clip((spT - 0.97) / 0.025, 0, 1) ** 2 * 0.45
    tw = tw + tg[..., None] * (1 - tw)
    ta = np.clip(th / (0.35 * rc), 0, 1)[..., None]
    img = img * (1 - ta) + tw * ta
    img = np.clip(img, 0, 1)
    # endpoints: coral beads
    im = Image.fromarray((img ** (1 / 1.0) * 255 + 0.5).astype(np.uint8))
    return im, dict(S=S, u=u, x0=x0, y0=y0, B=B, P=P, n=n, ND=ND, L=len(path))

def bead(im, x, y, r, colr=(250, 108, 102)):
    ss = 4; R = int(r * ss * 2.2); t = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    yy, xx = np.mgrid[0:2 * R, 0:2 * R]; dx = (xx - R) / (r * ss); dy = (yy - R) / (r * ss); d2 = dx * dx + dy * dy
    z = np.sqrt(np.clip(1 - d2, 0, 1)); dif = np.clip(-0.42 * dx - 0.55 * dy + 0.72 * z, 0, 1)
    c = np.array(colr) / 255.0; rgb = c[None, None] * (0.55 + 0.55 * dif[..., None])
    hl = np.exp(-(((dx + 0.33) ** 2 + (dy + 0.40) ** 2) / 0.035)); rgb = rgb + hl[..., None] * (1 - rgb) * 0.9
    a = np.clip((1 - np.sqrt(d2)) * r * ss / 1.5, 0, 1)
    shd = np.exp(-(((dx - 0.25) ** 2 + (dy - 0.33) ** 2) / 0.9)) * 0.38 * (1 - a)
    out = np.zeros((2 * R, 2 * R, 4)); out[..., :3] = np.clip(rgb, 0, 1) * a[..., None] + np.array([0.45, 0.40, 0.62]) * (1 - a[..., None])
    out[..., 3] = np.maximum(a, shd)
    t = Image.fromarray((out * 255).astype(np.uint8), 'RGBA').resize((2 * R // ss, 2 * R // ss), Image.LANCZOS)
    im.paste(t, (int(x - R / ss), int(y - R / ss)), t)

def caption(im, info, title, line1, line2):
    S = info['S']; d = ImageDraw.Draw(im); ink = (92, 77, 102)
    y = info['y0'] + info['B'] + 0.022 * S; x = info['x0']
    d.text((x, y), title, font=font('liberation/LiberationSerif-Bold.ttf', 0.034 * S), fill=ink)
    d.text((x, y + 0.045 * S), line1, font=font('liberation/LiberationSerif-Italic.ttf', 0.0172 * S), fill=ink)
    d.text((x, y + 0.072 * S), line2, font=font('dejavu/DejaVuSansMono.ttf', 0.0096 * S), fill=(132, 118, 146))

if __name__ == '__main__':
    npz = sys.argv[1]; S = int(sys.argv[2]); out = sys.argv[3]
    cyc = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0; hue0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
    im, info = render(npz, S, out, cycles=cyc, hue0=hue0)
    P = info['P']; bead(im, *P[0], 0.17 * info['u']); bead(im, *P[-1], 0.17 * info['u'])
    caption(im, info, 'Enter by One Half, Leave by the Other',
            f"A uniformly random domino tiling of the {info['n']}×{info['n']} board, and one string that never splits a domino: {info['L']} of {info['ND']} tied.",
            f"colour = order along the string · white = the {info['ND']-info['L']} left out (best of a long search) · worst case over ALL tilings, exact: 7 of 8 (4×4), 16 of 18 (6×6)")
    im.save(out); print('saved', out, info['L'], info['ND'])
