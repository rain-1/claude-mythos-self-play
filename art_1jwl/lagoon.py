"""lagoon.py — 'The Channel Closes at the Twelfth Sheet'
Sheet n (n = 1 nearest) is cut from one strip of paper with one cell per integer s in [-T_n, T_n],
T_n = 1^3 + ... + n^3.  Paper stands at s exactly when s = ±1 ± 8 ± 27 ... ± n^3 for some signs, and
it stands as high as the number of sign choices that give s.  Where no sum lands there is water.
usage: lagoon.py SIZE out.png [N]"""
import sys, numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, 'math_balance')
from dist import dists
from papercut import Box, rgb, mix, SERIF, SERIF_I, SERIF_B

def sheet_profile(c, T, x0, x1, hmax, u, rng, gamma=0.5, strip=3.0):
    """c[s+T] = number of representations.  Returns per-pixel-column (top height, present) arrays
    as a list of rectangles (xa, xb, h) in pixels."""
    ncell = 2 * T + 1; cw = (x1 - x0) / ncell; cmax = c.max()
    rects = []
    if cw >= strip * u:                      # every cell is its own tooth, exact
        nz = np.nonzero(c)[0]
        # merge runs of adjacent equal-height cells
        i = 0
        while i < len(nz):
            j = i
            while j + 1 < len(nz) and nz[j + 1] == nz[j] + 1 and c[nz[j + 1]] == c[nz[i]]: j += 1
            rects.append((x0 + nz[i] * cw, x0 + (nz[j] + 1) * cw, hmax * (c[nz[i]] / cmax) ** gamma))
            i = j + 1
        return rects
    # cells are thinner than a blade can cut: strips of width `strip`, standing with probability =
    # the fraction of their cells that are attainable (0 and 1 are kept exact), as high as the mean count
    c = c[::2]; ncell = len(c)             # only sums of the parity of T can occur: count those cells alone
    ns = int(round((x1 - x0) / (strip * u))); ns += (ns + 1) % 2          # odd, so one strip is centred on 0
    edges = np.linspace(0, ncell, ns + 1)
    cs = np.concatenate([[0], np.cumsum(c)]); ps = np.concatenate([[0], np.cumsum(c > 0)])
    lo = np.floor(edges[:-1] + 1e-9).astype(int); hi = np.ceil(edges[1:] - 1e-9).astype(int); hi = np.maximum(hi, lo + 1)
    frac = (ps[hi] - ps[lo]) / (hi - lo); mean = (cs[hi] - cs[lo]) / np.maximum(ps[hi] - ps[lo], 1)
    thr = rng.uniform(0.08, 0.92, ns); thr = np.minimum(thr, thr[::-1])     # symmetric dither, like the sums
    stand = (frac > 0) & ((frac >= 1.0) | (frac >= thr))
    h = hmax * (mean / cmax) ** gamma
    sw = (x1 - x0) / ns
    i = 0
    while i < ns:
        if not stand[i]: i += 1; continue
        rects.append((x0 + i * sw, x0 + (i + 1) * sw, h[i])); i += 1
    return rects

def rect_mask(S, rects, base, round_px=0.0):
    """mask of teeth rising from y = base; exact area-coverage antialiasing in x and y"""
    top = np.full(S, 0.0, np.float32); cov = np.zeros(S, np.float32); hsum = np.zeros(S, np.float32)
    for xa, xb, h in rects:
        ia, ib = int(np.floor(xa)), int(np.ceil(xb))
        for i in range(max(ia, 0), min(ib, S)):
            w = min(i + 1, xb) - max(i, xa)
            if w > 0: cov[i] += w; hsum[i] += w * h
    hcol = np.where(cov > 0, hsum / np.maximum(cov, 1e-6), 0)
    y = np.arange(S, dtype=np.float32)[:, None] + 0.5
    m = np.clip(y - (base - hcol[None, :]) + 0.5, 0, 1) * np.clip(base - y + 0.5, 0, 1)
    return (m * np.clip(cov, 0, 1)[None, :]).astype(np.float32)

def main():
    S = int(sys.argv[1]); out = sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 26
    u = S / 4096.0
    B = Box(S, seed=7)
    X0, X1, Y0, Y1 = 300 * u, 3796 * u, 280 * u, 3500 * u      # the window
    x, y = B.grid()
    rng = np.random.default_rng(11)
    # ---------- sky: five torn bands of paper, darkest on top ------------------------------
    sky = ['#2a2f5e', '#494a86', '#8a6d9c', '#d48f96', '#f3b98c', '#f8dcae']
    yh = 2330 * u                                              # horizon
    B.lay(B.rect(X0 - 40 * u, Y0 - 40 * u, X1 + 40 * u, Y1 + 40 * u), rgb(sky[0]), 1, shadow=0, k=0)
    band_y = [760, 1250, 1640, 1960, 2180]
    for i, by in enumerate(band_y):
        # each band is a lower, nearer sheet with a slow torn edge
        ph = rng.uniform(0, 6.28, 4)
        edge = by * u + (38 * np.sin(x / (610 * u) + ph[0]) + 21 * np.sin(x / (233 * u) + ph[1]) + 9 * np.sin(x / (71 * u) + ph[2]) + 3.5 * np.sin(x / (19 * u) + ph[3])) * u * (1.0 - 0.12 * i)
        m = np.clip(y - edge + 0.5, 0, 1)
        B.lay(m, rgb(sky[i + 1]), 2 + i, shadow=0.30, reach=7, soft=5, edge=0.7, k=i + 1)
    zsky = 2 + len(band_y)
    # ---------- moon (a hole punched... no: a disc of cream paper) and two thin clouds --------
    mx, my, mr = 2790 * u, 900 * u, 172 * u
    B.lay(B.disc(mx, my, mr), rgb('#f7edcf'), zsky + 1, shadow=0.42, reach=8, soft=4, edge=0.9, k=2)
    def cloud(cx, cy, L, col, z):
        t = (x - cx) / L
        th = (26 * u) * np.clip(1 - t * t, 0, 1) ** 0.6 * (1 + 0.35 * np.sin(x / (63 * u) + cy) + 0.2 * np.sin(x / (29 * u)))
        m = np.clip(th - np.abs(y - cy - 9 * u * np.sin(x / (170 * u))) + 0.5, 0, 1) * (np.abs(t) < 1)
        B.lay(m.astype(np.float32), rgb(col), z, shadow=0.36, reach=9, soft=4, edge=0.8, k=3)
    cloud(2560 * u, 1010 * u, 520 * u, '#b9a3c4', zsky + 2)
    cloud(1050 * u, 1420 * u, 610 * u, '#e9b7b0', zsky + 2)
    cloud(3200 * u, 1730 * u, 420 * u, '#f6cfa6', zsky + 2)
    # stars: pinpricks of cream paper in the two darkest skies
    srng = np.random.default_rng(3); stars = np.zeros((S, S), np.float32)
    for _ in range(70):
        sx, sy = srng.uniform(X0 + 30 * u, X1 - 30 * u), srng.uniform(Y0 + 30 * u, 1150 * u); r = srng.choice([3.2, 4.2, 5.5, 7.5], p=[.45, .3, .18, .07]) * u
        if np.hypot(sx - mx, sy - my) < mr + 60 * u: continue
        if sy > 700 * u + 0.0 and srng.uniform() < 0.5: continue
        stars = np.maximum(stars, np.clip(r - np.hypot(x - sx, y - sy) + 0.5, 0, 1))
    B.lay(stars, rgb('#f7edcf'), zsky + 1, shadow=0.3, reach=3, soft=1.5, edge=0.5, k=2)
    # ---------- the sheets --------------------------------------------------------------------
    D = list(dists(3, N))
    def base(n):  # y of the foot of sheet n: perspective spacing
        return yh + (Y1 - yh) / (1 + 0.40 * (n - 1)) ** 0.93
    def height(n):
        if n <= 11: return (250 + 16 * (n - 1)) * u
        return (430 + 82 * (n - 12)) * u
    near = np.array([rgb('#161a36'), rgb('#1f2750'), rgb('#2c3a68'), rgb('#3d4a7c'), rgb('#55528c'), rgb('#6f5a94'), rgb('#8a6699'), rgb('#a8789f'), rgb('#c68ea4'), rgb('#dfa8a8'), rgb('#efc2b0'), rgb('#f6d8bf')])
    def sheet_col(n):
        t = ((n - 1) / (N - 1)) ** 0.85 * (len(near) - 1); i = min(int(t), len(near) - 2)
        return mix(near[i], near[i + 1], t - i) * (1.0 + 0.035 * (1 if n % 2 else -1) * (n >= 12))
    water_far, water_mid, water_near = rgb('#f2c7a2'), rgb('#7d9db9'), rgb('#234a72')
    def water_col(n):
        t = ((n - 1) / (N - 1)) ** 0.5
        return mix(water_near, water_mid, t / 0.55) if t < 0.55 else mix(water_mid, water_far, (t - 0.55) / 0.45)
    z0 = zsky + 3
    drng = np.random.default_rng(5)
    for n in range(N, 0, -1):
        nn, T, c = D[n - 1]
        zn = z0 + (N - n) * 1.0
        rects = sheet_profile(c, T, X0, X1, height(n), u, np.random.default_rng(100 + n))
        m = rect_mask(S, rects, base(n))
        col = sheet_col(n)
        B.lay(m, col, zn, shadow=0.50, reach=8, soft=3.2, edge=1.0 if n < 14 else 0.8, k=n, ao=0.26 if n >= 6 else 0.12, ao_soft=16.0)
        if n == 12:   # the first sheet with paper standing exactly at 0: one red post
            cw = (X1 - X0) / (2 * T + 1); xc = (X0 + X1) / 2; hw = max(cw / 2, 5.0 * u)
            h0 = height(n) * (c[T] / c.max()) ** 0.5
            top = base(n) - h0 - 70 * u
            B.lay(B.rect(xc - hw, top, xc + hw, base(n)), rgb('#d8412b'), zn + 0.5, shadow=0.45, reach=5, soft=2, edge=1.0, k=1)
            B.lay(B.poly([(xc + hw, top), (xc + hw + 74 * u, top + 24 * u), (xc + hw, top + 48 * u)]), rgb('#d8412b'), zn + 0.5, shadow=0.45, reach=5, soft=2, edge=1.0, k=1)
        # the water in front of this sheet, down to the foot of the next nearer one
        yb = base(n - 1) if n > 1 else Y1 + 40 * u
        wm = B.rect(X0 - 40 * u, base(n) - 0.5, X1 + 40 * u, yb + 1)
        wc = np.broadcast_to(water_col(n), B.img.shape).copy()
        # thin lighter ripples cut along the strip
        rip = (np.sin((y - base(n)) / (7.5 * u * (1 + 14.0 / n)) * 6.283 + 1.3 * np.sin(x / (140 * u) + n)) > 0.93)
        wc = wc + (1 - wc) * (0.10 * rip)[..., None]
        B.lay(wm, wc, zn - 0.5, shadow=0.0, edge=0, tex=0.8, k=n + 2)
        # cast the sheet's shadow / reflection onto its own water: a darker band at the foot
        refl = rect_mask(S, [(xa, xb, min(h * 0.55, (yb - base(n)) * 0.9)) for xa, xb, h in rects], base(n))
        refl = np.flipud(refl) if False else refl
        # mirror below the base line
        Hpx = int(round(base(n)))
        mir = np.zeros_like(refl); span = min(Hpx, S - Hpx)
        mir[Hpx:Hpx + span] = refl[Hpx - span:Hpx][::-1]
        mir *= wm
        B.img *= (1 - 0.30 * mir)[..., None]
    # ---------- mat, caption -------------------------------------------------------------------
    B.mat(X0, Y0, X1, Y1)
    cap = [((X0 + X1) / 2, 3622 * u, "The Channel Closes at the Twelfth Sheet", SERIF, 104 * u, 'ma'),
           ((X0 + X1) / 2, 3766 * u, "Every sheet is the set of sums  ±1³ ± 2³ ± … ± n³ : paper where a sum lands, as tall as the number of ways; water where none does.", SERIF_I, 50 * u, 'ma'),
           ((X0 + X1) / 2, 3834 * u, "The first sheet is the two quays (±1). Zero stays open water through sheet eleven; the red post is the first sum that is exactly 0.", SERIF_I, 50 * u, 'ma'),
           ((X0 + X1) / 2, 3926 * u, "n = 1 … %d,  one cell per integer  ·  cut paper, six skies, one lamp at upper left" % N, SERIF, 40 * u, 'ma')]
    B.ink(B.text_mask(cap), '#4a4640', 0.88)
    B.save(out)

if __name__ == "__main__":
    main()
