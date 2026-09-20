"""render_lattice.py — 'The Circle a Lattice Can Draw': the 576 integer points of x^2+y^2 = 41^3 13^3 5^2 17^2
as beads; four chord families (one per Gaussian prime), each enveloping its own inner circle.
Coral: the circle itself, which in a world of whole-number points exists only where its points are.
Strip: the record circles — the first n whose circle carries more points than any before.
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import lattice_circle as L
from pastel import Sheet, PIG, absorb, polyline_density, text_density, finish, wrap, discs_density, draw_lines_density

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
OUT = sys.argv[2] if len(sys.argv) > 2 else f'lattice_{SIZE}.png'
SS = 2
W = H = SIZE * SS
rs = SIZE / 1024.0 * SS

PRIMES, EXPS = [41, 13, 5, 17], [3, 3, 1, 1]
FAMPIG = {41: 'orchid', 13: 'lavender', 5: 'cornflower', 17: 'aqua'}


def r2_count(n):
    """number of integer points on x^2+y^2=n (by enumeration, n small)"""
    c = 0
    m = int(n ** 0.5) + 1
    for x in range(-m, m + 1):
        y2 = n - x * x
        if y2 < 0:
            continue
        y = int(round(y2 ** 0.5))
        if y * y == y2:
            c += 1 if y == 0 else 2
    return c


def main():
    t0 = time.time()
    pts, n, pis = L.points_on_circle(PRIMES, EXPS)
    xy = np.array(list(pts.values()), float)
    r = np.sqrt(n)
    fams = L.chord_families(pts, PRIMES, EXPS)
    sheet = Sheet(W, H, seed=9)
    R = 0.385 * H
    cx, cy = 0.5 * W, 0.435 * H
    def to_px(P):
        P = np.asarray(P, float) / r
        return np.c_[cx + P[:, 0] * R, cy - P[:, 1] * R]
    # chord families: string art, constant mass per chord
    for p, f in zip(PRIMES, fams):
        A = to_px([a for a, b in f]); B = to_px([b for a, b in f])
        segs = np.c_[A, B]
        d = draw_lines_density(W, H, segs, 1.5 * rs, sigma=0.3 * rs)
        sheet.wash(np.clip(d, 0, 2.5) * 0.62, FAMPIG[p])
        # the envelope pools: a faint glaze of the family's disc between its envelope and the rim
        print('family', p, len(f), time.time() - t0)
    # deep families: the DOUBLE turns of 41 and of 13 (two steps along a chain), whose envelopes lie deep inside
    double = {}
    for j, pig in ((0, 'apricot'), (1, 'blush')):
        f2 = []
        for (ks, u), (x, y) in pts.items():
            if ks[j] + 2 <= EXPS[j]:
                ks2 = list(ks); ks2[j] += 2
                f2.append(((x, y), pts[(tuple(ks2), u)]))
        A = to_px([a for a, b in f2]); B = to_px([b for a, b in f2])
        d = draw_lines_density(W, H, np.c_[A, B], 1.3 * rs, sigma=0.3 * rs)
        sheet.wash(np.clip(d, 0, 2.5) * 0.70, pig)
        Ad = np.array([a for a, b in f2], float); Bd = np.array([b for a, b in f2], float)
        dd = np.abs(Ad[:, 0] * Bd[:, 1] - Ad[:, 1] * Bd[:, 0]) / np.linalg.norm(Bd - Ad, axis=1)
        double[PRIMES[j]] = dict(chords=len(f2), env_ratio=float(dd.mean() / r), cos_2arg=float(np.cos(2 * np.angle(pis[j]))))
    double41 = double
    print('double turn', double41)
    # the beads
    Q = to_px(xy)
    beads = discs_density(W, H, Q[:, 0], Q[:, 1], np.full(len(Q), 1.9 * rs), np.ones(len(Q)), sigma=0.5 * rs)
    sheet.wash(np.clip(beads, 0, 1) * 0.62, 'ink')
    # coral: the circle itself, thin, under the beads' feet
    th = np.linspace(0, 2 * np.pi, 4000)
    circ = np.c_[cx + R * np.cos(th), cy - R * np.sin(th)]
    cd = polyline_density(W, H, circ, 1.6 * rs, closed=True)
    sheet.wash(np.clip(cd, 0, 1) * 0.8, 'coral')
    sheet.wash(gaussian_filter(np.clip(cd, 0, 1), 5 * rs) * 0.10, 'coral')
    # strip: record circles (A071383): n with more points than any smaller n
    recs = [1, 5, 25, 65, 325, 1105, 4225, 5525, 27625, 71825, 138125, 160225, 801125]
    ns = len(recs)
    cellw = 0.072 * W
    x0 = 0.5 * W - 0.5 * cellw * ns
    ysr = 0.855 * H
    sr = 0.30 * cellw
    sb = np.zeros((H, W), np.float32); sc = np.zeros((H, W), np.float32)
    labels = []
    for j, m in enumerate(recs):
        ccx = x0 + (j + 0.5) * cellw
        P = []
        mm = int(m ** 0.5) + 1
        for x in range(-mm, mm + 1):
            y2 = m - x * x
            if y2 < 0:
                continue
            y = int(round(y2 ** 0.5))
            if y * y == y2:
                P.append((x, y))
                if y:
                    P.append((x, -y))
        P = np.array(P, float) / np.sqrt(m)
        Qs = np.c_[ccx + P[:, 0] * sr, ysr - P[:, 1] * sr]
        sb += discs_density(W, H, Qs[:, 0], Qs[:, 1], np.full(len(Qs), 1.5 * rs), np.ones(len(Qs)), sigma=0.4 * rs)
        circs = np.c_[ccx + sr * np.cos(th), ysr - sr * np.sin(th)]
        sc += polyline_density(W, H, circs, 0.8 * rs, closed=True)
        labels.append((str(len(P)), ccx, ysr + sr + 9 * rs, 8.5 * rs, 'mono', 'mm'))
    sheet.wash(np.clip(sb, 0, 1) * 0.8, 'ink')
    sheet.wash(np.clip(sc, 0, 1) * 0.55, 'coral')
    sheet.wash(text_density(W, H, labels) * 0.7, 'ink')
    # caption
    sheet.caption_strip(0.90, 0.985, 0.5)
    title = 'The Circle a Lattice Can Draw'
    sub = (f'In a world of whole-number points a circle exists only where x² + y² = n has solutions. This one, '
           f'n = 41³·13³·5·17 = {n:,}, has {len(pts)} of them, spread more evenly than chance. Multiplying a point by a '
           'Gaussian prime over its conjugate turns it onto another point of the same circle; the chords of each turn '
           'touch one inner circle — four primes, four circles, and two deeper ones (apricot, blush) from turning twice by 41 or by 13 — drawn by nothing but the points. Below: the circles '
           'that first carried 4, 8, 12, … points.')
    lines = wrap(sub, 10.5 * rs, 'italic', 0.84 * W)
    items = [(title, W / 2, 0.918 * H, 26 * rs, 'serif_bold', 'mm')]
    for i, ln in enumerate(lines):
        items.append((ln, W / 2, 0.947 * H + i * 13.0 * rs, 10.5 * rs, 'italic', 'mm'))
    sheet.wash(text_density(W, H, items) * 0.92, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), OUT)
    ang = np.arctan2(xy[:, 1], xy[:, 0])
    cert = dict(n=n, count=len(pts), discrepancy=L.discrepancy(ang), random_scale=1 / np.sqrt(len(pts)),
                records=[(m, r2_count(m)) for m in recs], double_turn_41=double41)
    json.dump(cert, open(OUT.replace('.png', '_cert.json'), 'w'), indent=1)
    print(json.dumps(cert)); print('done', time.time() - t0)


if __name__ == '__main__':
    main()
