"""gilbreath.py — 'The Triangle That Begins With One'.

Row 0: the primes.  Each row below: absolute differences of the row above (Gilbreath, 1958: the left
entry is 1 in every row — verified to 10^13 rows by Odlyzko, unproved).  Above the triangle the gaps
p_{j+1} - p_j stand as a skyline (row 1).  Entries > 2 are the crust: warm pigment by magnitude, dripping
down-left as stalactites and dying out within ~50 rows; below it a sea of 2s (aqua) and 0s (paper), which
is exactly Rule 90 (|a-b| on {0,2} is XOR), so the sea carries Sierpinski holes.  Coral: the column of
ones.  Ink beads: (n, j) where the SIGNED n-th difference sum_k (-1)^k C(n,k) p_{j+k} vanishes
(MathOverflow 515079).
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, finish, text_width, draw_lines_density

RAMP = ['apricot', 'blush', 'orchid', 'lavender', 'cornflower']   # by (value-4)/4: 4, 8, 12, 16, 20+


def primes_upto(LIM):
    sieve = np.ones(LIM // 2, dtype=bool); sieve[0] = False
    for i in range(1, int(LIM ** 0.5) // 2 + 1):
        if sieve[i]:
            p = 2 * i + 1; sieve[p * p // 2::p] = False
    return np.concatenate([[2], 2 * np.nonzero(sieve)[0] + 1]).astype(np.int64)


def render(FINAL=1024, SS=2, tag='proto_gil', cols=None, cw=1.8, rh=6.0, x0=0.075, y0=0.34, caption=True,
           sea_d=0.62, crust_d=2.0, fade=0.14, hole_edge=0.0, sky_d=0.75, gran=0.10, bead_d=1.2, coral_d=1.5, sky_h=0.24,
           zeros_nmax=24):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    cw_px, rh_px = cw * rs, rh * rs
    X0, Y0 = x0 * W, y0 * H
    rows = int((H * (0.90 if caption else 0.98) - Y0) / rh_px)
    if cols is None:
        cols = int((0.985 * W - X0) / cw_px)
    primes = primes_upto(60_000_000)
    need = cols + rows + zeros_nmax + 5
    P = primes[:need]
    # ---- Gilbreath rows
    G = P.copy(); tri = np.zeros((rows, cols), np.int64)
    firsts = []
    for n in range(rows):
        G = np.abs(G[1:] - G[:-1])
        tri[n] = G[:cols]; firsts.append(int(G[0]))
    gaps = tri[0]                       # row 1 of the triangle = the gaps (skyline)
    # ---- signed differences, zeros with j <= cols, n <= zeros_nmax
    D = P.copy(); zeros = []
    for n in range(1, zeros_nmax + 1):
        D = D[1:] - D[:-1]
        for j in np.nonzero(D[:cols] == 0)[0]:
            zeros.append((n, int(j) + 1))
    cert = dict(cols=cols, rows=rows, all_firsts_one=bool(all(f == 1 for f in firsts)),
                crust_depth=int(max(np.nonzero((tri > 2).any(1))[0]) + 1), max_entry=int(tri.max()),
                n_signed_zeros=len(zeros), sea_fraction_2=float((tri[100:] == 2).mean()), sea_fraction_0=float((tri[100:] == 0).mean()))
    print(cert)
    sheet = Sheet(W, H, seed=23)

    def cell_field(mask_or_val):
        """expand a (rows, cols) array to the canvas at cell size (nearest), positioned at X0, Y0"""
        F = np.zeros((H, W), np.float32)
        yy = np.arange(H); xx = np.arange(W)
        ri = np.floor((yy - Y0) / rh_px).astype(int); ci = np.floor((xx - X0) / cw_px).astype(int)
        okr = (ri >= 0) & (ri < rows); okc = (ci >= 0) & (ci < cols)
        sub = np.asarray(mask_or_val, np.float32)[np.clip(ri, 0, rows - 1)][:, np.clip(ci, 0, cols - 1)]
        sub[~okr] = 0; sub[:, ~okc] = 0
        yb = Y0 + rows * rh_px
        ramp = np.clip((yb - yy) / (fade * H), 0, 1)[:, None].astype(np.float32)
        return sub * ramp ** 0.7

    # ---- the sea: 2s in aqua (with a little cornflower granulation), 0s = paper
    sea = cell_field(tri == 2)
    sea = gaussian_filter(sea, 0.5 * rs)
    sheet.wash(sea * sea_d, 'aqua', granulate=gran, seed=31)
    sheet.wash(gaussian_filter(cell_field(tri == 2), 2.5 * rs) * 0.10, 'cornflower')
    # ---- the crust: warm by magnitude
    lv = np.where(tri > 2, (tri - 4) / 4.0, 0.0)     # 0 for 4, 1 for 8, 2 for 12 ...
    for k, pig in enumerate(RAMP):
        lo = k
        wgt = np.clip(1 - np.abs(lv - lo), 0, 1) * (tri > 2)
        if k == len(RAMP) - 1:
            wgt = np.clip(lv - lo + 1, 0, 1) * (tri > 2)
        f = gaussian_filter(cell_field(wgt), 0.45 * rs)
        sheet.wash(f * crust_d, pig, granulate=gran, seed=40 + k)
    # ---- the skyline of gaps above the triangle: bars of height gap/max * sky_h*H in ink-wash (sepia)
    gmax = gaps.max()
    bars = np.zeros((H, W), np.float32)
    xs = X0 + (np.arange(cols) + 0.5) * cw_px
    hts = gaps / gmax * sky_h * H
    segs = np.stack([xs, np.full(cols, Y0 - 0.5 * rs), xs, Y0 - hts], 1)
    bars = draw_lines_density(W, H, segs, max(1.0, cw_px * 0.62))
    bars = gaussian_filter(bars, 0.4 * rs)
    sheet.wash(bars * sky_d, 'sepia', granulate=gran * 0.6, seed=52)
    # baseline of the skyline: hairline ink
    sheet.wash(polyline_density(W, H, [(X0, Y0), (X0 + cols * cw_px, Y0)], 0.7 * rs) * 0.8, 'ink')
    # ---- zeros of the signed differences: ink beads at (row n-1?, col j): row index n-1 (row 0 = first difference)
    zx = [X0 + (j - 1 + 0.5) * cw_px for (n, j) in zeros]
    zy = [Y0 + (n - 1 + 0.5) * rh_px for (n, j) in zeros]
    r_b = 0.42 * min(cw_px, rh_px)
    sheet.wash(discs_density(W, H, zx, zy, [r_b] * len(zx), [1.0] * len(zx), sigma=0.35 * rs) * bead_d, 'ink')
    # ---- the column of ones in coral: a bead per row at column 0
    cy_ = Y0 + (np.arange(rows) + 0.5) * rh_px
    cx_ = np.full(rows, X0 + 0.5 * cw_px)
    cf = np.clip((Y0 + rows * rh_px - cy_) / (fade * H), 0, 1) ** 0.7
    sheet.wash(discs_density(W, H, cx_, cy_, [0.5 * cw_px] * rows, list(cf), sigma=0.35 * rs) * coral_d, 'coral')
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'The Triangle That Begins With One'
        sub = ("Primes on top; each row the differences of the last. The gaps erode to a sea of twos and zeros within fifty rows, "
               "and the left edge has read 1 for every row ever checked. Ink: where the signed difference is exactly zero.")
        fs = 0.0135 * H
        fs = min(fs, fs * 0.90 * W / max(1, text_width(sub, fs, 'italic')))
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, fs, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, v = a.split('=', 1)
        try:
            kw[k] = eval(v)
        except Exception:
            kw[k] = v
    render(**kw)
