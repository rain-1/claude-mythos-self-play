"""render_appell.py — 'Where Two Roads Meet' : zeros of the moment polynomials Q_n(x;q)=E[(x+X)^n]
for the symmetric three-atom law X∈{−1,0,1}, P(±1)=q, as q runs from 0 (the constant law, every
zero at the origin) to 1/2 (every zero on the imaginary axis).  MO 514900.

Three materials: pale pigment = where ANY law on the atoms {−1,0,1} can put a zero of Q_n
(0 ∈ conv{(x−1)^n, x^n, (x+1)^n}); pigment roads = the actual zero paths of the symmetric law;
coral rings = the double zeros (theorem: x = ±i cot(πk/(n−1)), q = 1/(2+2|cos(πk/(n−1))|^{1−n})).
Pigment = degree n (hierarchy as palette).
"""
import numpy as np, sys, json, time
from numpy.polynomial import polynomial as P
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
from pastel import Sheet, PIG, CYCLE, absorb, polyline_density, text_density, finish, draw_lines_density, discs_density
import appell

def track_roads(n, qs):
    """root paths: (len(qs), n) complex, matched greedily between consecutive q"""
    Z = np.zeros((len(qs), n), complex)
    prev = None
    for i, q in enumerate(qs):
        r = P.polyroots(appell.Qn_coeffs(n, q))
        if prev is None:
            Z[i] = r
        else:
            # greedy matching by distance
            used = np.zeros(n, bool); out = np.zeros(n, complex)
            D = np.abs(prev[:, None] - r[None, :])
            for _ in range(n):
                k = np.argmin(np.where(used[None, :], np.inf, D)); a, b = divmod(k, n)
                out[a] = r[b]; used[b] = True; D[a, :] = np.inf
            Z[i] = out
        prev = Z[i]
    return Z

def region_mask(n, X):
    """0 ∈ conv{(x−1)^n, x^n, (x+1)^n} — vectorised triangle test (normalised to avoid overflow)"""
    A = (X - 1) ** n; B = X ** n; C = (X + 1) ** n
    s = np.maximum(np.maximum(np.abs(A), np.abs(B)), np.abs(C)) + 1e-300
    A, B, C = A / s, B / s, C / s
    def cross(u, v):
        return u.real * v.imag - u.imag * v.real
    d1 = cross(B - A, -A); d2 = cross(C - B, -B); d3 = cross(A - C, -C)
    neg = (d1 < 0) | (d2 < 0) | (d3 < 0); pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
    return ~(neg & pos)

def render(FINAL=2560, SS=2, nmin=4, nmax=12, R=4.2, tag='appell', caption=True):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    sheet = Sheet(W, H, seed=5)
    cx, cy = W * 0.5, H * 0.47
    scale = 0.5 * W / R
    def to_px(z):
        return np.stack([cx + scale * z.real, cy - scale * z.imag], 1)
    ns = list(range(nmin, nmax + 1))
    ROADPIG = ['apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']
    pig_of = {n: ROADPIG[(n - nmin) % len(ROADPIG)] for n in ns}
    # --- the possible: regions, pale, computed at half resolution
    h2, w2 = H // 2, W // 2
    yy, xx = np.mgrid[:h2, :w2]
    X = ((xx + 0.5) * 2 - cx) / scale + 1j * (cy - (yy + 0.5) * 2) / scale
    from scipy.ndimage import zoom
    for n in ns:
        m = region_mask(n, X).astype(np.float32)
        m = gaussian_filter(m, 1.2)
        m = zoom(m, 2, order=1)[:H, :W]
        # edge pooling: pigment gathers at the region's rim
        b = gaussian_filter(m, 2.5 * rs); gy, gx = np.gradient(b); e = np.hypot(gx, gy)
        e = e / (e.max() + 1e-9)
        d = 0.07 * m + 0.0 * e
        sheet.wash(d.astype(np.float32), pig_of[n], granulate=0.25, seed=100 + n)
        print(f'  region n={n} area frac {m.mean():.3f}  {time.time()-t0:.0f}s', flush=True)
    # --- the actual: zero roads of the symmetric law (each n in its pigment, plus ink underlay)
    s_ = np.linspace(0.002, 1.0, 5000)
    qs = 0.5 * s_ ** 3
    roads_ink = np.zeros((H, W), np.float32)
    lw = 2.0 * rs
    n_dp = 0
    dp_all = []
    for n in ns:
        Z = track_roads(n, qs)
        dens = np.zeros((H, W), np.float32)
        for j in range(n):
            pts = to_px(Z[:, j])
            ok = (np.abs(pts[:, 0] - cx) < 0.55 * W) & (np.abs(pts[:, 1] - cy) < 0.55 * H)
            # split into runs inside the frame
            idx = np.where(ok)[0]
            if len(idx) < 2: continue
            cuts = np.where(np.diff(idx) > 1)[0]
            for seg in np.split(idx, cuts + 1):
                if len(seg) >= 2:
                    dens += polyline_density(W, H, pts[seg], lw, weight=1.0)
        dens = np.clip(gaussian_filter(dens, 0.6 * rs), 0, 1)
        sheet.wash(dens * 1.6, pig_of[n])
        roads_ink += dens
        # rungs: chords between a zero and its mirror image across the axis at evenly spaced q
        rungs = []
        for i in np.linspace(40, len(qs) - 1, 46).astype(int):
            zi = Z[i]
            for j in range(n):
                if zi[j].real > 1e-6:
                    m_ = np.argmin(np.abs(zi - (-np.conj(zi[j]))))
                    if abs(zi[m_] - (-np.conj(zi[j]))) < 1e-6 * (1 + abs(zi[j])):
                        p0 = to_px(np.array([zi[j]]))[0]; p1 = to_px(np.array([zi[m_]]))[0]
                        rungs.append([p0[0], p0[1], p1[0], p1[1]])
        if rungs:
            rd = draw_lines_density(W, H, np.array(rungs), 0.9 * rs)
            rd = np.clip(gaussian_filter(rd, 0.5 * rs), 0, 1)
            sheet.wash(rd * 0.55, pig_of[n])
            roads_ink += 0.25 * rd
        # double points
        for k, q, xdp in appell.double_points(n):
            dp_all.append((n, k, q, xdp)); n_dp += 1
        print(f'  roads n={n}  {time.time()-t0:.0f}s', flush=True)
    sheet.wash(np.clip(roads_ink, 0, 1) * 0.34, 'ink')
    # --- the theorem: coral rings at every double zero (inside the frame)
    yy, xx = np.ogrid[:H, :W]
    rings = np.zeros((H, W), np.float32)
    shown = 0
    for (n, k, q, xdp) in dp_all:
        p = to_px(np.array([xdp]))[0]
        if not (0 < p[0] < W and 0 < p[1] < H): continue
        rad = (7.0 + 1.1 * (nmax - n)) * rs
        rr = np.hypot(xx - p[0], yy - p[1])
        rings += np.clip(1 - np.abs(rr - rad) / (1.7 * rs), 0, 1)
        shown += 1
    sheet.wash(np.clip(rings, 0, 1) * 1.6, 'coral')
    # the origin: the constant law, where every zero begins (coral bead + ink ring)
    rr = np.hypot(xx - cx, yy - cy)
    sheet.wash(np.exp(-(rr / (5.5 * rs)) ** 2).astype(np.float32) * 1.5, 'coral')
    sheet.wash(np.clip(1 - np.abs(rr - 12 * rs) / (1.5 * rs), 0, 1).astype(np.float32) * 0.9, 'ink')
    # the imaginary axis, hairline
    ax = np.exp(-((xx - cx) / (0.9 * rs)) ** 2) * (yy > 0.02 * H) * (yy < 0.905 * H)
    sheet.wash(ax.astype(np.float32) * 0.30, 'ink')
    # small legend: n → pigment swatches along the bottom right
    sw = []
    for i, n in enumerate(ns):
        x0 = W * 0.73 + i * W * 0.018; y0 = H * 0.905
        d = np.zeros((H, W), np.float32)
        d[int(y0):int(y0 + 0.010 * H), int(x0):int(x0 + 0.014 * W)] = 1.0
        sheet.wash(gaussian_filter(d, 0.8 * rs) * 0.9, pig_of[n])
    sheet.wash(text_density(W, H, [(f'n = {nmin}', W * 0.73, H * 0.898, 0.010 * W, 'italic', 'lb'),
                                   (f'{nmax}', W * 0.73 + (len(ns) - 1) * W * 0.018 + 0.014 * W, H * 0.898, 0.010 * W, 'italic', 'rb')]) * 1.5, 'ink')
    if caption:
        sheet.caption_strip(0.925, 0.995, 0.5)
        ts_ = 0.030 * W; is_ = 0.0125 * W
        items = [('Where Two Roads Meet', W * 0.5, H * 0.945, ts_, 'serif_bold', 'mm'),
                 ('Zeros of E[(x+X)ⁿ] for X taking the values −1, 0, 1 with P(X=±1) = q, as q runs from 0 (every zero at the origin) to ½ (every zero on the axis).',
                  W * 0.5, H * 0.9705, is_, 'italic', 'mm'),
                 (f'Pale: where any law on these atoms may put a zero.  Coral: where two roads meet and the polynomial has a double zero — {shown} of them here, the first at n = 4, q = 1/18, x = ±i/√3.',
                  W * 0.5, H * 0.986, is_, 'italic', 'mm')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert = dict(nmin=nmin, nmax=nmax, frame=R, double_points_total=n_dp, double_points_shown=shown,
                first=dict(n=4, q='1/18', x='±i/√3', Q4='(3x²+1)²/9'))
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(cert, f'done {time.time()-t0:.0f}s')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--nmax', type=int, default=14)
    ap.add_argument('--R', type=float, default=4.6)
    ap.add_argument('--tag', default='proto_appell')
    a = ap.parse_args()
    render(FINAL=a.final, SS=a.ss, nmax=a.nmax, R=a.R, tag=a.tag)
