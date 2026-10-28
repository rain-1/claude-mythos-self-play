# Patchwork satin quilt of the gravitational allocation: usage python3 quilt.py SIZE R SEED out.png [hl]
import numpy as np, sys, math, time
from numba import njit, prange
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
from gef import coeffs, field, zeros, basins, lic, fval, field_pts
import os

PAL = np.array([[1.00, 0.80, 0.66], [0.99, 0.72, 0.76], [0.94, 0.72, 0.90], [0.80, 0.74, 0.98], [0.68, 0.82, 0.99],
                [0.64, 0.92, 0.88], [0.80, 0.95, 0.68], [1.00, 0.91, 0.64]])

@njit(parallel=True, cache=True)
def shadow(h, lx, ly, lz, maxd):
    H, W = h.shape; S = np.ones((H, W), np.float32)
    for y in prange(H):
        for x in range(W):
            z0 = h[y, x]; occ = 0.0
            for k in range(1, maxd):
                px = x + lx * k; py = y - ly * k
                if px < 0 or py < 0 or px >= W - 1 or py >= H - 1: break
                zz = z0 + lz * k
                hh = h[int(py), int(px)]
                if hh > zz:
                    occ = max(occ, min(1.0, (hh - zz) * 0.6))
                    if occ >= 1: break
            S[y, x] = 1 - occ
    return S

def trace_line(V, x, y, W, sgn, step, maxn):
    pts = [(x, y)]
    for i in range(maxn):
        ix, iy = int(x + .5), int(y + .5)
        if ix < 1 or iy < 1 or ix >= W - 1 or iy >= W - 1: break
        vx, vy = V[iy, ix]
        n = math.hypot(vx, vy) + 1e-12
        x += sgn * step * vx / n; y -= sgn * step * vy / n
        pts.append((x, y))
        if sgn < 0 and n < 0.05: break
    return pts

def main():
    S = int(sys.argv[1]); R = float(sys.argv[2]); seed = int(sys.argv[3]); out = sys.argv[4]
    margin = int(S * 0.06); cap = int(S * 0.0)
    Wf = S - 2 * margin                       # fabric square
    t = time.time()
    ext = float(os.environ.get('EXT', '1.0'))
    Wv, Rv = Wf, R
    Wf = int(round(Wv * ext)); Wf += (Wf - Wv) % 2; R = Rv * Wf / Wv
    if os.environ.get('MODE') == 'poisson':
        rng0 = np.random.default_rng(seed); Rb = Rv * 3.0
        npts = rng0.poisson(Rb * Rb)                 # intensity 1/pi on a disc of radius Rb
        rr0 = Rb * np.sqrt(rng0.random(npts)); th0 = 2 * np.pi * rng0.random(npts)
        Pt = rr0 * np.exp(1j * th0)
        U, V = field_pts(Pt, Wf, R)
        U = U - np.float32(np.median(U)) - np.float32(0.3)
        print('U range', np.percentile(U, [1, 50, 99]))
        Z = Pt[(np.abs(Pt.real) < R * 1.02) & (np.abs(Pt.imag) < R * 1.02)]
    else:
        K = int(R * R + 8 * R + 40); c = coeffs(K, seed)
        U, V = field(c, Wf, R); Z = zeros(c, U, R, Wf)
    px = Wf / (2 * R)
    ZL = np.full((Wf, Wf), -1, np.int32)
    zc = [((z.real + R) * px - 0.5, (R - z.imag) * px - 0.5) for z in Z]
    yy, xx = np.mgrid[0:Wf, 0:Wf]
    for k, (cx, cy) in enumerate(zc):
        r = max(2.0, 0.05 * px)
        x0, x1 = int(max(cx - r - 2, 0)), int(min(cx + r + 3, Wf)); y0, y1 = int(max(cy - r - 2, 0)), int(min(cy + r + 3, Wf))
        if x1 <= x0 or y1 <= y0: continue
        sub = (xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2 <= r * r
        ZL[y0:y1, x0:x1][sub] = k
    L = basins(V, ZL, Wf, 0.5, 8 * Wf)
    if Wf != Wv:
        off = (Wf - Wv) // 2
        U = np.ascontiguousarray(U[off:off + Wv, off:off + Wv]); V = np.ascontiguousarray(V[off:off + Wv, off:off + Wv])
        L = np.ascontiguousarray(L[off:off + Wv, off:off + Wv]); Wf = Wv; R = Rv
        zc = [(x - off, y - off) for (x, y) in zc]
        yy, xx = np.mgrid[0:Wf, 0:Wf]
    keep = sorted(set(np.unique(L).tolist()) - {-1})
    print('fields', time.time() - t, 'zeros', len(Z)); t = time.time()
    # fill unlabelled (paths leaving the square) by nearest label
    bad = L < 0
    if bad.any():
        idx = ndi.distance_transform_edt(bad, return_distances=False, return_indices=True)
        L = L[idx[0], idx[1]]
    nZ = len(Z)
    # adjacency + greedy colouring (largest-degree first), prefer colours far on the wheel from neighbours
    adj = [set() for _ in range(nZ)]
    for a, b in ((L[:, 1:], L[:, :-1]), (L[1:, :], L[:-1, :])):
        m = a != b
        for p, q in set(zip(a[m].tolist(), b[m].tolist())):
            adj[p].add(q); adj[q].add(p)
    col = -np.ones(nZ, int)
    rng = np.random.default_rng(seed)
    order = sorted(range(nZ), key=lambda k: -len(adj[k]))
    for k in order:
        used = {col[j] for j in adj[k] if col[j] >= 0}
        free = [cc for cc in range(len(PAL)) if cc not in used]
        col[k] = free[rng.integers(len(free))] if free else rng.integers(len(PAL))
    base = PAL[col[L]]
    # height = clamped potential, smooth
    if os.environ.get('MODE') == 'poisson':
        U = U - ndi.gaussian_filter(U, px * 1.2) + np.float32(0.25)
    h = 0.5 * np.log(np.exp(2 * np.minimum(U.astype(np.float64), 30)) + math.exp(-1.7))
    h = ndi.gaussian_filter(h, 1.0)
    amp = px * 0.30                            # height in pixels per unit of U
    hp = (h * amp).astype(np.float32)
    gy, gx = np.gradient(hp)
    # seams: boundaries pinch a little (piping groove) on top of the ridge
    edge = np.zeros_like(L, bool)
    edge[:, 1:] |= L[:, 1:] != L[:, :-1]; edge[1:, :] |= L[1:, :] != L[:-1, :]
    de = ndi.distance_transform_edt(~edge).astype(np.float32)
    groove = np.exp(-(de / (px * 0.018)) ** 2)
    hp2 = hp - groove * px * 0.025
    gy, gx = np.gradient(hp2)
    n = np.dstack([-gx, gy, np.ones_like(gx)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    Ld = np.array([-0.45, 0.55, 0.70]); Ld /= np.linalg.norm(Ld)
    ndl = n @ Ld
    diff = 0.56 + 0.46 * np.clip(ndl, -0.3, 1)
    # fibre direction = flow direction lifted to the surface
    vn = V / (np.linalg.norm(V, axis=2, keepdims=True) + 1e-9)
    T = np.dstack([vn[..., 0], vn[..., 1], -gx * vn[..., 0] + gy * vn[..., 1]])
    T /= np.linalg.norm(T, axis=2, keepdims=True)
    Hh = Ld + np.array([0, 0, 1.0]); Hh /= np.linalg.norm(Hh)
    th = T @ Hh
    sheen = np.clip(1 - th ** 2, 0, 1) ** 10
    noise = np.random.default_rng(seed + 1).random((Wf, Wf)).astype(np.float32)
    tex = lic(V, noise, Wf, int(max(8, px * 0.12)))
    tex = (tex - tex.mean()) / (tex.std() + 1e-9)
    print('lic', time.time() - t); t = time.time()
    sh = shadow(hp2, float(-Ld[0] / math.hypot(Ld[0], Ld[1])), float(Ld[1] / math.hypot(Ld[0], Ld[1])),
                float(Ld[2] / math.hypot(Ld[0], Ld[1])), int(px * 0.8))
    sh = ndi.gaussian_filter(sh, 2.0)
    light = diff * (0.78 + 0.22 * sh)
    img = base * light[..., None] * (1 + 0.035 * tex[..., None])
    img += (0.34 * sheen * (0.75 + 0.25 * np.clip(tex, -2, 2) / 2) * (0.5 + 0.5 * sh))[..., None] * np.array([1.0, 0.98, 0.96])
    # piping: a fine light seam line on the boundary
    pip = np.exp(-(de / (px * 0.006)) ** 2)
    img = img * (1 - 0.55 * pip[..., None]) + 0.55 * pip[..., None] * np.array([1.0, 0.98, 0.95])
    # tufting stitches: flow lines from each button out to its seams (traced uphill), drawn as dashed thread
    canvas = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    np.savez_compressed(out.replace('.png', '_data.npz'), L=L, Z=Z, col=col, R=R, px=px)
    st = Image.new('L', canvas.size, 0); d = ImageDraw.Draw(st)
    sw = max(1, int(round(px * 0.012))); dash = px * 0.07
    for k, (cx, cy) in enumerate(zc):
        if not (0 <= cx < Wf and 0 <= cy < Wf): continue
        for a in range(8):
            ang = 2 * math.pi * (a + 0.5) / 8 + 0.3 * k
            x = cx + math.cos(ang) * px * 0.16; y = cy + math.sin(ang) * px * 0.16
            pts = trace_line(V, x, y, Wf, -1, 1.0, int(px * 4))
            # stop where the line leaves its own patch
            acc = 0.0; on = True; seg = [pts[0]]
            for (p0, p1) in zip(pts[:-1], pts[1:]):
                ix, iy = int(p1[0] + .5), int(p1[1] + .5)
                if ix < 0 or iy < 0 or ix >= Wf or iy >= Wf or L[iy, ix] != k or de[iy, ix] < px * 0.05: break
                acc += math.hypot(p1[0] - p0[0], p1[1] - p0[1])
                if on: seg.append(p1)
                if acc > dash * (0.62 if on else 0.38):
                    if on and len(seg) > 1: d.line(seg, fill=255, width=sw)
                    on = not on; acc = 0.0; seg = [p1]
            if on and len(seg) > 1: d.line(seg, fill=255, width=sw)
    sa = np.asarray(st, np.float32) / 255
    sa = ndi.gaussian_filter(sa, 0.6)
    ssh = ndi.shift(sa, (px * 0.008, px * 0.006), order=1)
    img = np.asarray(canvas, np.float32) / 255
    img = img * (1 - 0.25 * ssh[..., None])
    thread = base * 0.55 + 0.45
    img = img * (1 - sa[..., None]) + sa[..., None] * thread * (0.85 + 0.15 * diff[..., None])
    # coral running stitch just inside the highlighted patch (the one whose button is nearest the centre)
    hlk = int(sys.argv[5]) if len(sys.argv) > 5 and int(sys.argv[5]) >= 0 else int(np.argmin([abs(z) for z in Z]))
    inside = (L == hlk)
    din = ndi.distance_transform_edt(inside)
    ring = (din > px * 0.07) & (din <= px * 0.07 + max(2.0, px * 0.022))
    # dash by arc length along the ordered contour of the ring's centre-line
    from skimage import measure
    from scipy.spatial import cKDTree
    cs = measure.find_contours(din.astype(np.float32), px * 0.07 + max(1.0, px * 0.011))
    cpts = max(cs, key=len)
    al = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(cpts, axis=0).T))])
    ys_, xs_ = np.nonzero(ring)
    _, nn = cKDTree(cpts).query(np.c_[ys_, xs_])
    per = px * 0.06
    on = (al[nn] % per) < 0.62 * per
    cm = np.zeros(din.shape, np.float32); cm[ys_[on], xs_[on]] = 1
    cm = ndi.gaussian_filter(cm, 0.6)
    coral = np.array([1.0, 0.45, 0.38])
    img = img * (1 - 0.2 * ndi.shift(cm, (px * 0.008, px * 0.006), order=1)[..., None])
    img = img * (1 - cm[..., None]) + cm[..., None] * coral * (0.85 + 0.2 * diff[..., None])
    area_hl = inside.sum() / px ** 2
    print('highlight', hlk, Z[hlk], 'area/pi', area_hl / math.pi)
    # pearl buttons
    yy2, xx2 = yy.astype(np.float32), xx.astype(np.float32)
    rb = px * 0.105
    for k, (cx, cy) in enumerate(zc):
        if not (-rb < cx < Wf + rb and -rb < cy < Wf + rb): continue
        x0, x1 = int(max(cx - 2 * rb, 0)), int(min(cx + 2 * rb + 2, Wf)); y0, y1 = int(max(cy - 2 * rb, 0)), int(min(cy + 2 * rb + 2, Wf))
        if x1 <= x0 or y1 <= y0: continue
        dx = (xx2[y0:y1, x0:x1] - cx) / rb; dy = (yy2[y0:y1, x0:x1] - cy) / rb
        r2 = dx * dx + dy * dy
        # contact shadow
        sdx = dx - 0.18; sdy = dy - 0.22
        csh = np.exp(-np.maximum(sdx * sdx + sdy * sdy - 0.8, 0) * 3.0) * 0.35
        sub = img[y0:y1, x0:x1]
        sub *= (1 - csh)[..., None]
        m = r2 < 1
        nz = np.sqrt(np.clip(1 - r2, 0, 1)); nxp = dx; nyp = -dy
        dl = np.clip(nxp * Ld[0] + nyp * Ld[1] + nz * Ld[2], 0, 1)
        hv = (nxp * Hh[0] + nyp * Hh[1] + nz * Hh[2])
        spec = np.clip(hv, 0, 1) ** 60
        irid = 0.5 + 0.5 * np.cos(6.0 * nz[..., None] + np.array([0, 2.1, 4.2])[None, None, :])
        pearl = (0.80 + 0.06 * irid) * (0.70 + 0.30 * dl)[..., None] + 0.9 * spec[..., None]
        pearl = pearl * 0.92 + 0.08 * PAL[col[k]]
        a = np.clip((1 - np.sqrt(r2)) * rb, 0, 1)[..., None]
        sub[:] = sub * (1 - a) + a * pearl
    # fabric onto the backdrop with a soft drop shadow and a bound edge
    out_img = np.ones((S, S, 3), np.float32) * np.array([0.975, 0.965, 0.975])
    mask = np.zeros((S, S), np.float32); mask[margin:margin + Wf, margin:margin + Wf] = 1
    ds = ndi.gaussian_filter(ndi.shift(mask, (S * 0.006, S * 0.004), order=0), S * 0.006)
    out_img *= (1 - 0.22 * ds)[..., None]
    out_img[margin:margin + Wf, margin:margin + Wf] = img
    # binding: a narrow satin border
    bw = int(px * 0.06)
    bind = np.zeros((S, S), bool); bind[margin:margin + Wf, margin:margin + Wf] = True
    inner = np.zeros((S, S), bool); inner[margin + bw:margin + Wf - bw, margin + bw:margin + Wf - bw] = True
    bnd = bind & ~inner
    yb, xb = np.nonzero(bnd)
    dd = np.minimum.reduce([xb - margin, margin + Wf - 1 - xb, yb - margin, margin + Wf - 1 - yb]) / bw
    out_img[yb, xb] = np.array([0.99, 0.97, 0.96]) * (0.80 + 0.20 * np.sin(np.pi * np.clip(dd, 0, 1)))[:, None]
    im = Image.fromarray((np.clip(out_img, 0, 1) * 255).astype(np.uint8))
    if len(sys.argv) > 6:
        label(im, S, margin, Wf, area_hl / math.pi)
    im.save(out)
    print('done', time.time() - t)

def label(im, S, margin, Wf, ahl=1.0):
    d = ImageDraw.Draw(im)
    lw, lh = int(S * 0.335), int(S * 0.128)
    x0 = margin + Wf - lw - int(S * 0.035); y0 = margin + Wf - lh - int(S * 0.035)
    # shadow
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rectangle([x0 + 6, y0 + 9, x0 + lw + 6, y0 + lh + 9], fill=90)
    from PIL import ImageFilter
    sh = sh.filter(ImageFilter.GaussianBlur(S * 0.004))
    im.paste((60, 50, 70), (0, 0), sh)
    d.rectangle([x0, y0, x0 + lw, y0 + lh], fill=(252, 249, 242))
    # stitched border
    ins = int(S * 0.006); dl = int(S * 0.006)
    for (a, b) in (((x0 + ins, y0 + ins), (x0 + lw - ins, y0 + ins)), ((x0 + ins, y0 + lh - ins), (x0 + lw - ins, y0 + lh - ins)),
                   ((x0 + ins, y0 + ins), (x0 + ins, y0 + lh - ins)), ((x0 + lw - ins, y0 + ins), (x0 + lw - ins, y0 + lh - ins))):
        L_ = math.hypot(b[0] - a[0], b[1] - a[1]); n = int(L_ / dl)
        for i in range(0, n, 2):
            p = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
            q = (a[0] + (b[0] - a[0]) * min(i + 1.2, n) / n, a[1] + (b[1] - a[1]) * min(i + 1.2, n) / n)
            d.line([p, q], fill=(255, 140, 120), width=max(2, int(S * 0.0016)))
    ink = (92, 77, 102)
    fb = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', int(S * 0.021))
    fi = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf', int(S * 0.0128))
    fs = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', int(S * 0.0108))
    tx = x0 + int(S * 0.018); ty = y0 + int(S * 0.016)
    d.text((tx, ty), sys.argv[6], font=fb, fill=ink)
    ty += int(S * 0.031)
    for i, line in enumerate(sys.argv[7].replace('AREA', f'{ahl:.4f}').split('|')):
        d.text((tx, ty), line, font=fi if i == 0 else fs, fill=ink)
        ty += int(S * 0.0175)

if __name__ == '__main__':
    main()
