"""render_page.py — 'The Leaf Told on a Page' (hero).
Left/top: the leaf, a hexagonal packing of equal coins tinted by where they sit.
Right/bottom: the same coins repacked so that every boundary angle sum is pi and four are pi/2 —
a page whose proportion is the leaf's conformal modulus. Coral rows: exact conformal images of
straight rows of the leaf (independent map); the coins agree with them to O(h).
"""
import numpy as np, json, sys, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P
from cpack_rect import build, Leaf, ExactMap, rect_map_setup, F_elliptic, Offset

INK = P.PIG['ink']


def coin_tints(W, region):
    ang = np.angle(W) / (2 * np.pi)
    i0, i1, t = P.hue_to_pigments(ang + 0.02)
    rmax = np.abs(region.boundary()).max()
    rad = np.abs(W) / rmax
    dens = 0.34 + 0.80 * rad ** 1.7
    absorb = np.zeros((len(W), 3), np.float32)
    for k in range(len(W)):
        tint = P.mix_tint(P.CYCLE[i0[k]], P.CYCLE[i1[k]], float(t[k]))
        absorb[k] = dens[k] * P.absorb(tint)
    return absorb


def draw_coins(Wd, Hd, X, Y, Rp, absorb, SS, gap=0.05, ink_min=1.6):
    chans = [Image.new('F', (Wd, Hd), 0.0) for _ in range(3)]
    drs = [ImageDraw.Draw(im) for im in chans]
    ink = Image.new('F', (Wd, Hd), 0.0); dink = ImageDraw.Draw(ink)
    for k in np.argsort(-Rp):
        r = Rp[k]
        if r < 0.5:
            continue
        rf = r * (1 - gap)
        for c in range(3):
            drs[c].ellipse([X[k] - rf, Y[k] - rf, X[k] + rf, Y[k] + rf], fill=float(absorb[k, c]))
        if r > ink_min * SS:
            wl = max(1.0, 0.030 * r + 0.30 * SS)
            dink.ellipse([X[k] - r, Y[k] - r, X[k] + r, Y[k] + r], outline=1.0, width=int(round(wl)))
    A = np.stack([np.asarray(im, np.float32) for im in chans], axis=-1)
    return A, np.asarray(ink, np.float32)


def render(pack, S=1024, SS=2, out='proto_page.png', seed=5, rows_every=4, row_dir=1):
    t0 = time.time()
    Wd, Hd = S * SS, S * SS
    sh = P.Sheet(Wd, Hd, seed=seed)
    mesh, z, r, corners, L1, L2 = pack['mesh'], pack['z'], pack['r'], pack['corners'], pack['L1'], pack['L2']
    W, bd = mesh['W'], mesh['boundary']
    region = pack['region']; h = mesh['h']
    absorb = coin_tints(W, region)
    # coins on the drawn rows (lattice index along the normal of the row direction) get more pigment
    dirs0 = {0: 1.0, 1: np.exp(1j * np.pi / 3), 2: np.exp(2j * np.pi / 3)}
    nrm0 = 1j * dirs0[row_dir]
    mrow = np.round((W * np.conj(nrm0)).real / (h * np.sqrt(3) / 2)).astype(int)
    onrow = (mrow % rows_every) == 0
    absorb = absorb * np.where(onrow, 1.45, 1.0)[:, None]
    # ---- placement
    rmax = np.abs(region.boundary()).max()
    leaf_c = np.array([0.30, 0.335]) * Wd
    s1 = 0.285 * Wd / rmax                      # px per source unit
    page_w = 0.44 * Wd
    s2 = page_w / L1
    page_h = L2 * s2
    page_o = np.array([0.50 * Wd, 0.885 * Hd])   # bottom-left corner of the page
    # keep page top below the leaf a little: allow overlap in the corner; fine
    src_px = lambda w: (leaf_c[0] + s1 * np.real(w), leaf_c[1] - s1 * np.imag(w))
    pag_px = lambda q: (page_o[0] + s2 * np.real(q), page_o[1] - s2 * np.imag(q))
    # ---- leaf coins
    X1, Y1 = src_px(W)
    A1, I1 = draw_coins(Wd, Hd, X1, Y1, np.full(len(W), 0.5 * h * s1), absorb * 1.05, SS)
    # ---- page coins
    X2, Y2 = pag_px(z)
    A2, I2 = draw_coins(Wd, Hd, X2, Y2, r * s2, absorb, SS)
    A = A1 + A2; I = np.maximum(I1, I2)
    del A1, A2
    g = P.noise(Hd, Wd, 1.6, seed + 11)
    A *= (1 + 0.15 * g)[..., None]
    tot = A.sum(-1)
    b = gaussian_filter(tot, 1.2 * SS)
    gy, gx = np.gradient(b); edge = np.hypot(gx, gy)
    nz = edge[edge > 0]
    if nz.size:
        edge /= (np.percentile(nz, 99) + 1e-9)
    A *= (1 + 0.30 * np.clip(edge, 0, 1))[..., None]
    A = gaussian_filter(A, [0.5 * SS, 0.5 * SS, 0])
    sh.A += A
    del A
    sh.wash(gaussian_filter(I, 0.45 * SS) * 0.85, INK)
    # ---- outlines: leaf boundary and page edge (thin ink)
    outl = Image.new('F', (Wd, Hd), 0.0); do = ImageDraw.Draw(outl)
    bdry = region.boundary(3000); bx, by = src_px(bdry)
    do.line(list(zip(bx.tolist(), by.tolist())) + [(float(bx[0]), float(by[0]))], fill=1.0, width=int(round(1.2 * SS)), joint='curve')
    cz = [0, L1, L1 + 1j * L2, 1j * L2]
    pxs = [pag_px(c) for c in cz]
    do.line([(float(x), float(y)) for x, y in pxs] + [(float(pxs[0][0]), float(pxs[0][1]))], fill=1.0, width=int(round(1.2 * SS)))
    sh.wash(gaussian_filter(np.asarray(outl, np.float32), 0.6 * SS) * 0.55, INK)
    # ---- coral rows: source straight rows (every k-th) and their exact images in the page
    region_c = pack['region_c']
    ex = ExactMap(region_c)
    thb = np.linspace(0, 2 * np.pi, 12000, endpoint=False); wbb = region_c.r(thb) * np.exp(1j * thb)
    p = ex(np.array([wbb[np.argmin(np.abs(wbb - W[c]))] for c in corners])); p /= np.abs(p)
    S_ = rect_map_setup(p)
    K, Kp = S_['K'], S_['Kp']
    # determine the symmetry that aligns exact rectangle to the discrete one (same recipe as the certificate)
    sym = pack['cert'].get('map_symmetry', (True, False, True))
    def exact_to_page(w):
        zex = F_elliptic(S_['m'](S_['T'](ex(w))), S_['k']) + K
        t = zex
        flipx, flipy, swap = sym
        if swap:
            t = t.imag + 1j * t.real
        Lx = 2 * K if not swap else Kp; Ly = Kp if not swap else 2 * K
        if flipx:
            t = (Lx - t.real) + 1j * t.imag
        if flipy:
            t = t.real + 1j * (Ly - t.imag)
        return t * (L1 / Lx)
    rows_im = Image.new('F', (Wd, Hd), 0.0); dr = ImageDraw.Draw(rows_im)
    dirs = {0: 1.0, 1: np.exp(1j * np.pi / 3), 2: np.exp(2j * np.pi / 3)}
    e = dirs[row_dir]; nrm = 1j * e
    spacing = h * np.sqrt(3) / 2
    ts = np.linspace(-1.8, 1.8, 700)
    nrow = 0
    for m in range(-60, 61):
        if m % rows_every:
            continue
        line = m * spacing * nrm + ts * e
        ins = region_c.inside(line)
        idx = np.where(ins)[0]
        if len(idx) < 6:
            continue
        for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
            if len(run) < 6:
                continue
            seg = line[run]
            # trim to the coin carrier: keep points at distance > 0.45h from the boundary roughly (no need)
            x, y = src_px(seg)
            dr.line(list(zip(x.tolist(), y.tolist())), fill=1.0, width=int(round(0.9 * SS)))
            # exact image
            sub = seg[::4]
            q = exact_to_page(sub)
            x2, y2 = pag_px(q)
            dr.line(list(zip(x2.tolist(), y2.tolist())), fill=1.0, width=int(round(1.0 * SS)), joint='curve')
            nrow += 1
    rd = gaussian_filter(np.asarray(rows_im, np.float32), 0.55 * SS)
    sh.wash(rd * 1.25, 'coral')
    # ---- caption
    c = pack['cert']
    sh.caption_strip(0.915, 0.99, 0.55)
    items = [("The Leaf Told on a Page", 0.5 * Wd, 0.935 * Hd, int(0.030 * Wd), 'serif_bold', 'mm'),
             (f"The same coins, each keeping its six neighbours; the sides are straight because every rim angle sums to π. "
              f"The page's proportion {L1/L2:.3f} is the leaf's own number (exact {c.get('modulus_exact', float('nan')) if not sym[2] else 1/c.get('modulus_exact', 1):.3f}); the coral rows are the true map.",
              0.5 * Wd, 0.968 * Hd, int(0.0118 * Wd), 'italic', 'mm')]
    sh.wash(P.text_density(Wd, Hd, items) * 1.1, INK)
    img = sh.develop()
    P.finish(img, (S, S), out)
    print(f'render {out} rows={nrow} {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    out = sys.argv[3] if len(sys.argv) > 3 else f'proto_page_{S}.png'
    pack = build(h, verbose=False, ncert=400)
    json.dump(pack['cert'], open(out.replace('.png', '_cert.json'), 'w'), indent=1, default=str)
    print(json.dumps({k: pack['cert'][k] for k in ('V', 'modulus_discrete', 'modulus_exact', 'modulus_rel_err', 'map_err_mean', 'map_err_relative_to_width', 'map_symmetry')}, default=str))
    render(pack, S=S, SS=2, out=out)
