"""Hero: THE DRAWINGS THAT WERE ALWAYS THERE — dessins d'enfants garden.

All bicolored plane trees with <= 6 edges as their exact Shabat flowers:
pixel z -> P(z); the two preimage tints checker by sign(Im P); the tree
P^{-1}([0,1]) is inked from the traced edge paths; black/white vertices drawn.
Pastel watercolor register on warm paper.
"""
import numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont
from pastel import Watercolor, PIGMENTS, stroke_polyline, absorption

SS = 2
FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
W = H = FINAL * SS

sols = json.load(open('shabat_solutions_6.json'))
try:
    orbits = json.load(open('galois_orbits.json'))     # cls -> orbit index
except Exception:
    orbits = {}

# ---- layout: rows of medallions --------------------------------------------
rows = []   # each row: list of (n, sol)
r1 = [(1, s) for s in sols['1']] + [(2, s) for s in sols['2']] + [(3, s) for s in sols['3']]
rows.append(r1)
rows.append([(4, s) for s in sols['4']])
rows.append([(5, s) for s in sols['5']])
six = [(6, s) for s in sols['6']]
rows.append(six[:10]); rows.append(six[10:19]); rows.append(six[19:])

CHECKER = {1: ('sky', 'rose'), 2: ('periwinkle', 'peach'), 3: ('seafoam', 'lilac'),
           4: ('sky', 'butter'), 5: ('sage', 'rose'), 6: ('periwinkle', 'peach')}
# special Galois structures discovered by galois.py (certified):
#   cubic orbit of three  (2,2,1,1)|(3,2,1) & mirror  -> rose rim
#   Q(i) conjugate pair   (3,1,1,1)|(3,2,1) & mirror  -> periwinkle rim
#   split passport        (2,2,1,1)|(4,1,1) & mirror  -> sage rim (two Q-singletons)
SPECIAL_RIM = {
    ((2, 2, 1, 1), (3, 2, 1)): 'rose', ((3, 2, 1), (2, 2, 1, 1)): 'rose',
    ((3, 1, 1, 1), (3, 2, 1)): 'periwinkle', ((3, 2, 1), (3, 1, 1, 1)): 'periwinkle',
    ((2, 2, 1, 1), (4, 1, 1)): 'sage', ((4, 1, 1), (2, 2, 1, 1)): 'sage',
}

wc = Watercolor(H, W, seed=11)

title_h = int(0.075 * H)
garden_h = H - title_h
row_h = garden_h / len(rows)

def poly_from(sol):
    lam, mu = sol['lam'], sol['mu']
    a = np.array([complex(*z) for z in sol['a']])
    b = np.array([complex(*z) for z in sol['b']])
    c0 = complex(*sol['c0'])
    p = np.array([1.0 + 0j])
    for r, m in zip(a, lam):
        for _ in range(m):
            p = np.convolve(p, np.array([1.0, -r]))
    return p / c0, a, b, lam, mu

rng = np.random.default_rng(7)
base_diam = (garden_h / len(rows)) * 0.92
for ri, row in enumerate(rows):
    cnt = len(row)
    cell_w = W / cnt
    diam = min(min(row_h, cell_w) * 0.90, 1.18 * base_diam)
    for ci, (n, sol) in enumerate(row):
        cx = (ci + 0.5) * cell_w
        cy = title_h * 0.2 + (ri + 0.5) * row_h
        rad = diam / 2
        P, a, b, lam, mu = poly_from(sol)
        # principal-axis rotation: weighted root cloud's long axis horizontal
        wts = np.concatenate([np.array(lam, float), np.array(mu, float)])
        pts0 = np.concatenate([a, b])
        Cxx = np.sum(wts * pts0.real ** 2); Cyy = np.sum(wts * pts0.imag ** 2)
        Cxy = np.sum(wts * pts0.real * pts0.imag)
        theta = 0.5 * np.arctan2(2 * Cxy, Cxx - Cyy)
        rot = np.exp(-1j * theta)
        a = a * rot; b = b * rot
        # rebuild P after rotation
        Pr = np.array([1.0 + 0j])
        for r_, m_ in zip(a, lam):
            for _ in range(m_):
                Pr = np.convolve(Pr, np.array([1.0, -r_]))
        P = Pr / complex(*sol['c0']) * (1.0)  # c0 unchanged by |rot|=1? recompute:
        Pb = np.array([1.0 + 0j])
        for r_, m_ in zip(b, mu):
            for _ in range(m_):
                Pb = np.convolve(Pb, np.array([1.0, -r_]))
        c0r = (Pr - Pb)[-1]
        P = Pr / c0r
        allr = np.concatenate([a, b])
        zR = 1.55 * max(np.abs(allr).max(), 0.3)
        # bbox grid
        x0, x1 = int(cx - rad), int(cx + rad) + 1
        y0, y1 = int(cy - rad), int(cy + rad) + 1
        xs = (np.arange(x0, x1) - cx) / rad * zR
        ys = (np.arange(y0, y1) - cy) / rad * zR
        Z = xs[None, :] + 1j * ys[:, None]
        mask = (np.abs(Z) <= zR).astype(np.float32)
        Wv = np.polyval(P.astype(np.complex64), Z.astype(np.complex64))
        rr = np.abs(Z) / zR
        # equipotential-shaped fade: normalized log-potential; the flower's
        # boundary follows |P| level curves (petals pinch at critical points)
        aw = np.abs(Wv)
        rim_band = (rr > 0.88) & (rr <= 1.0)
        wrim = np.median(aw[rim_band]) if rim_band.any() else 10.0
        L = np.log1p(aw) / max(np.log1p(wrim), 1e-3)
        taper = np.clip(1.0 - 0.92 * L, 0, 1) ** 0.8 * mask
        taper = taper * np.clip(1.25 - rr ** 4, 0, 1) ** 0.6
        up = (Wv.imag > 0).astype(np.float32) * taper
        dn = (Wv.imag <= 0).astype(np.float32) * taper
        pig_up, pig_dn = CHECKER[n]
        # faint medallion ground wash (no cookie rim)
        ground = mask * np.clip(1.06 - rr ** 2.5, 0, 1)
        fld = np.zeros((H, W), np.float32)
        fld[y0:y1, x0:x1] = 0.09 * ground
        wc.wash(fld, 'butter', granulate=0.2, edge=0.2, edge_sigma=2.5 * SS)
        f2 = np.zeros((H, W), np.float32); f2[y0:y1, x0:x1] = 0.95 * up
        wc.wash(f2, pig_up, granulate=0.16, edge=0.25, edge_sigma=1.8 * SS)
        f3 = np.zeros((H, W), np.float32); f3[y0:y1, x0:x1] = 0.95 * dn
        wc.wash(f3, pig_dn, granulate=0.16, edge=0.25, edge_sigma=1.8 * SS)
        # rim ONLY for the special Galois passports (cubic trio / Q(i) pair /
        # split passport), drawn as a clean stroked circle
        rimp = SPECIAL_RIM.get((tuple(lam), tuple(mu)))
        if rimp is not None:
            th = np.linspace(0, 2 * np.pi, 400)
            ring = np.zeros((H, W), np.float32)
            circ = np.stack([cx + 1.035 * rad * np.cos(th),
                             cy + 1.035 * rad * np.sin(th)], 1)
            stroke_polyline(ring, circ, 2.6 * SS, amp=2.2)
            wc.wash(ring, rimp)
        # tree ink from traced paths (rotated with the frame)
        ink = np.zeros((H, W), np.float32)
        for path in sol['paths']:
            pz = np.array([complex(*p) for p in path]) * rot
            px = cx + pz.real / zR * rad
            py = cy + pz.imag / zR * rad
            stroke_polyline(ink, np.stack([px, py], 1), 1.1 * SS, amp=1.45)
        wc.wash(ink, 'ink')
        # vertices
        vert = np.zeros((H, W), np.float32)
        ring_ink = np.zeros((H, W), np.float32)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        for z, m in zip(a, lam):
            vx = cx + z.real / zR * rad; vy = cy + z.imag / zR * rad
            r0 = (2.0 + 1.05 * m) * SS
            d2 = (xx - vx) ** 2 + (yy - vy) ** 2
            vert[y0:y1, x0:x1] += 2.4 * np.exp(-d2 / (2 * (r0 / 1.8) ** 2))
        for z, m in zip(b, mu):
            vx = cx + z.real / zR * rad; vy = cy + z.imag / zR * rad
            r0 = (2.3 + 1.15 * m) * SS
            d = np.sqrt((xx - vx) ** 2 + (yy - vy) ** 2)
            ring_ink[y0:y1, x0:x1] += 2.6 * np.exp(-(d - r0 / 1.45) ** 2 / (2 * (1.0 * SS) ** 2))
        wc.wash(vert, 'ink')
        wc.wash(ring_ink, 'ink')

# ---- row labels -------------------------------------------------------------
lab_img = Image.new('L', (W, H), 0)
lab_d = ImageDraw.Draw(lab_img)
try:
    lab_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', int(0.011 * H))
except Exception:
    lab_font = ImageFont.load_default()
ROWLAB = ['one, two, three edges', 'four edges', 'five edges',
          'six edges', '', '']
for ri, lab in enumerate(ROWLAB):
    if not lab: continue
    ycen = title_h * 0.2 + (ri + 0.06) * row_h
    lab_d.text((int(0.012 * W), int(ycen)), lab, fill=255, font=lab_font)
lab_f = np.asarray(lab_img, dtype=np.float32) / 255.0
from scipy.ndimage import gaussian_filter as _gf
wc.wash(1.3 * _gf(lab_f, 0.6 * SS), 'clay')

# ---- title ------------------------------------------------------------------
def text_field(lines, cy_frac, size_px):
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', size_px)
        font2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(size_px * 0.44))
    except Exception:
        font = font2 = ImageFont.load_default()
    y = int(cy_frac * H)
    for i, ln in enumerate(lines):
        f = font if i == 0 else font2
        bb = d.textbbox((0, 0), ln, font=f)
        d.text(((W - bb[2]) / 2, y), ln, fill=255, font=f)
        y += int((bb[3] - bb[1]) * 1.75)
    fld = np.asarray(img, dtype=np.float32) / 255.0
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(fld, 0.6 * SS)

tf = text_field(["The Drawings That Were Always There",
                 "all fifty bipartite plane trees with at most six edges, drawn by their exact Shabat polynomials —",
                 "each flower is the checkering of the plane by P: rose-side to one half of the sky, blue-side to the other"],
                0.933, int(0.021 * H))
wc.wash(2.0 * tf, 'ink')

wc.save(f'dessins_hero_{FINAL}.png', final_size=(FINAL, FINAL), dmax=2.4)
print('saved', FINAL)
