"""Seven islands, thirteen bridges: the 7-vertex graph of MO 516850 (triangular prism plus a
vertex joined to the four corners of one rectangular face) as a woodblock seascape.
usage: python3 islands.py SIZE OUT [bridgemask(int, 13 bits) ] [seed]"""
import sys, numpy as np
from PIL import ImageDraw
from scipy import ndimage as ndi
from hanga import Sheet, INK, fbm, stroke, bezier, SERIF_B, SERIF_I, SERIF

EDGES = [(0, 1), (0, 5), (0, 6), (1, 3), (1, 4), (2, 3), (2, 4), (2, 5), (2, 6), (3, 4), (3, 6), (4, 5), (5, 6)]
#           x     y(waterline)  w     h    far?
ISL = {0: (0.215, 0.405, 0.150, 0.070, 1), 1: (0.775, 0.390, 0.165, 0.080, 1),
       5: (0.330, 0.560, 0.185, 0.095, 0), 4: (0.665, 0.535, 0.185, 0.100, 0),
       2: (0.500, 0.705, 0.200, 0.085, 0),
       6: (0.185, 0.815, 0.215, 0.110, 0), 3: (0.825, 0.805, 0.215, 0.115, 0)}
SUN = (0.585, 0.200, 0.064)
HILL_DX = {6: -0.11, 3: 0.11, 5: -0.07, 4: 0.07, 2: 0.0, 0: 0.0, 1: 0.0}   # hills stand back from the landings
FRAME = (0.055, 0.055, 0.945, 0.905)      # x0,y0,x1,y1 of the picture
HORIZON = 0.300


def footprint(i, grow=1.0, n=90):
    x, y, w, h, far = ISL[i]; t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rng = np.random.default_rng(50 + i)
    r = 1 + 0.07 * np.sin(3 * t + rng.random() * 6) + 0.05 * np.sin(5 * t + rng.random() * 6)
    return np.c_[x + 0.5 * w * grow * r * np.cos(t), y + 0.5 * w * 0.26 * grow * r * np.sin(t)]


def _anchors():
    """shore point of island i facing island j: on a flank, never behind the hill, and
    bridges leaving the same flank are spread apart (phi = angle below the flank direction)"""
    nb = {i: [] for i in ISL}
    for i, j in EDGES: nb[i].append(j); nb[j].append(i)
    out = {}
    for i in ISL:
        xi, yi, wi = ISL[i][:3]; sides = {1: [], -1: []}
        for j in nb[i]:
            xj, yj = ISL[j][:2]; dx = xj - xi; dy = (yj - yi) / 0.26
            sd = (1 if dx >= 0 else -1) if abs(dx) >= 0.06 else (1 if xi > 0.5 else -1)
            phi = np.arctan2(dy, abs(dx) if abs(dx) >= 0.06 else 0.02)
            sides[sd].append([max(phi, -0.70 if ISL[i][4] or i == 2 else (-1.05 if sd * HILL_DX[i] < 0 else -0.5)), j])
        for sd, lst in sides.items():
            lst.sort()
            for k in range(1, len(lst)): lst[k][0] = max(lst[k][0], lst[k - 1][0] + 0.72)
            for phi, j in lst:
                phi = min(phi, 1.75)
                out[i, j] = np.array([xi + sd * 0.5 * wi * 0.97 * np.cos(phi), yi + 0.5 * wi * 0.26 * 0.97 * np.sin(phi)])
    return out


_ANCH = None


def anchor(i, j):
    global _ANCH
    if _ANCH is None: _ANCH = _anchors()
    return _ANCH[i, j]


CAMBER = {(3, 6): 0.035, (0, 1): 0.05, (4, 5): 0.10}


def bridge_path(i, j):
    p0 = anchor(i, j); p2 = anchor(j, i); mid = (p0 + p2) / 2; L = np.hypot(*(p2 - p0))
    d = (p2 - p0) / L
    up = np.array([0, -1.0]); side = np.array([np.sign(mid[0] - 0.5) or 1.0, 0])
    horiz = abs(d[0])
    cam = CAMBER.get((i, j), 0.16)
    c = mid + up * cam * L * horiz ** 2 + side * 0.13 * L * (1 - horiz ** 2)
    return bezier(p0, c, p2, 90)


def mound(i, n=160):
    """hill profile polygon (normalised)"""
    x, y, w, h, far = ISL[i]; rng = np.random.default_rng(7 + i)
    t = np.linspace(-1, 1, n); prof = np.zeros(n)
    for k in range(3):
        c = rng.uniform(-0.5, 0.5); sg = rng.uniform(0.35, 0.6); a = rng.uniform(0.6, 1.0)
        prof = np.maximum(prof, a * np.exp(-((t - c) / sg) ** 2))
    prof = prof / prof.max() * np.clip(1 - t ** 2, 0, 1) ** 0.42
    prof += 0.025 * np.sin(11 * t + i) * (1 - t ** 2)
    bw = (0.40 if far or i == 2 else 0.33) * w; x = x + HILL_DX[i] * w
    top = np.c_[x + bw * t, y - 0.010 - h * prof]
    base = np.c_[x + bw * t[::-1], y - 0.010 + 0.035 * w * np.sqrt(np.clip(1 - t[::-1] ** 2, 0, 1))]
    return np.r_[top, base], top


def pine(d, s, x, y, sz, rng, layer):
    """layer 'f' foliage pads, 't' trunk"""
    lean = rng.uniform(-0.25, 0.25)
    tip = (x + lean * sz, y - 1.0 * sz)
    if layer == 't':
        pts = [(x, y), (x + 0.6 * lean * sz + 0.06 * sz, y - 0.5 * sz), tip]
        stroke(d, [(a * s, b * s) for a, b in pts], [0.10 * sz * s, 0.075 * sz * s, 0.05 * sz * s])
        rng.random(8)
    else:
        for k, (ox, oy, r) in enumerate([(0, 0.02, 0.36), (-0.34, 0.22, 0.30), (0.36, 0.30, 0.28), (-0.05, -0.16, 0.22)]):
            cx = tip[0] + (ox + rng.uniform(-.06, .06)) * sz; cy = tip[1] + oy * sz
            rx = sz * r * rng.uniform(0.9, 1.15); ry = rx * 0.40
            d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=255)


def reach(present, root=2):
    comp = {root}; grew = True
    while grew:
        grew = False
        for k, (a, b) in enumerate(EDGES):
            if present >> k & 1 and ((a in comp) != (b in comp)): comp |= {a, b}; grew = True
    return comp


def render(size, out, present=(1 << 13) - 1, seed=3, title=True, ss=2, pseed=None):
    S = Sheet(size, seed if pseed is None else pseed, ss=ss); s = size * S.ss; rng = np.random.default_rng(seed)
    home = reach(present); whole = len(home) == 7
    x0, y0, x1, y1 = FRAME
    frame = S.mask(lambda d: d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], fill=255))
    sea_all = S.mask(lambda d: d.rectangle([x0 * s, HORIZON * s, x1 * s, y1 * s], fill=255))
    foot = S.mask(lambda d: [d.polygon(S.px(footprint(i)), fill=255) for i in ISL]) * frame
    foam = S.mask(lambda d: [d.polygon(S.px(footprint(i, 1.10)), fill=255) for i in ISL])
    mounds = {i: mound(i) for i in ISL}
    mmask = {i: S.mask(lambda d, i=i: d.polygon(S.px(mounds[i][0]), fill=255)) for i in ISL}
    allm = np.clip(sum(mmask.values()), 0, 1)

    # mist bands (suyari-gasumi): rounded bars of bare paper
    bars = [(0.055, 0.255, 0.36, 0.019), (0.25, 0.286, 0.42, 0.015), (0.70, 0.232, 0.30, 0.017),
            (0.40, 0.345, 0.26, 0.014), (0.055, 0.480, 0.17, 0.012), (0.83, 0.655, 0.12, 0.011),
            (0.47, 0.455, 0.13, 0.010)]
    def draw_mist(d):
        for bx, by, bl, bh in bars:
            d.rounded_rectangle([bx * s, (by - bh / 2) * s, (bx + bl) * s, (by + bh / 2) * s], radius=bh * s / 2, fill=255)
    mist = S.mask(draw_mist); clear = (1 - mist) * frame

    # ---- sky ----
    sky = frame * (1 - sea_all) * clear
    S.block(sky, INK['sky'], strength=0.55, k=0)
    S.block(sky, INK['peach'], strength=0.85, bokashi=S.grad_y(HORIZON + 0.01, 0.165, 1.2), k=1)
    S.block(sky, INK['rose'], strength=0.55, bokashi=S.grad_y(HORIZON + 0.02, 0.235, 1.0), k=1)
    S.block(sky, INK['prussian'], strength=0.95, bokashi=S.grad_y(y0 - 0.01, 0.185, 1.3), k=2)
    S.block(sky, INK['indigo'], strength=0.75, bokashi=S.grad_y(y0 - 0.005, 0.095, 1.0), k=2)
    sx_, sy_, sr_ = SUN
    sun = S.mask(lambda d: d.ellipse([(sx_ - sr_) * s, (sy_ - sr_) * s, (sx_ + sr_) * s, (sy_ + sr_) * s], fill=255))
    if whole: S.block(sun * clear * frame, INK['vermilion'], strength=0.92, rim=0.10, k=3)
    else: S.block(sky, INK['plum'], strength=0.50, bokashi=S.grad_y(HORIZON + 0.02, 0.10, 0.8), k=1)

    # ---- sea ----
    sea = sea_all * (1 - foam) * (1 - allm) * clear
    S.block(sea, INK['aqua'], strength=0.80, k=4)
    S.block(sea, INK['prussian'], strength=0.90, bokashi=S.grad_y(y1 + 0.02, 0.60, 1.5), k=5)
    S.block(sea, INK['prussian'], strength=0.55, bokashi=S.grad_y(HORIZON - 0.002, HORIZON + 0.05, 1.0), k=5)
    S.block(sea, INK['indigo'], strength=0.55, bokashi=S.grad_y(y1 + 0.01, 0.80, 1.2), k=5)
    # ripples: a second, darker blue block of little double arcs, denser toward the viewer
    def draw_ripples(d):
        n = 0
        while n < 1500:
            y = HORIZON + 0.015 + (y1 - HORIZON - 0.02) * rng.random() ** 0.8; x = x0 + (x1 - x0) * rng.random()
            dep = (y - HORIZON) / (y1 - HORIZON); L = 0.008 + 0.030 * dep * rng.uniform(0.6, 1.2)
            t = np.linspace(0, 1, 16); wv = np.sin(np.pi * t) ** 0.8
            pts = np.c_[x + L * (t - 0.5) * 2, y - 0.16 * L * np.sin(2 * np.pi * t) * 0 - 0.10 * L * np.abs(np.sin(2 * np.pi * t))]
            stroke(d, pts * s, (0.0012 + 0.0022 * dep) * s * (0.25 + wv)); n += 1
    rip = S.mask(draw_ripples) * sea
    S.block(rip, INK['prussian'], strength=0.62, grain=0.05, rim=0, k=5)
    # reflected sun: a few vermilion dashes under the sun
    def draw_glit(d):
        for k in range(20):
            y = HORIZON + 0.010 + 0.075 * (k / 20) ** 1.3 + rng.uniform(-0.002, 0.002)
            L = rng.uniform(0.012, 0.05) * (1 - 0.5 * k / 26); x = SUN[0] + rng.uniform(-0.03, 0.03)
            stroke(d, np.array([[x - L, y], [x + L, y]]) * s, 0.0032 * s)
    if whole: S.block(S.mask(draw_glit) * sea, INK['vermilion'], strength=0.55, rim=0, k=3)
    else: S.block(sea, INK['plum'], strength=0.30, k=1)

    # ---- islands: sand skirt, hills (far = slate, near = moss with pine-green tops) ----
    S.block(foot, INK['sand'], strength=0.95, k=1)
    S.block(foot * (1 - allm), INK['ochre'], strength=0.50, bokashi=None, k=1, rim=0.5)
    for i in sorted(ISL, key=lambda i: ISL[i][1]):
        x, y, w, h, far = ISL[i]; m = mmask[i] * clear
        if i not in home:        # cut off from the shrine island: printed without its colour
            S.block(m, INK['grey'], strength=0.75, k=2)
            S.block(m, INK['sumi'], strength=0.30, bokashi=S.grad_y(y - h - 0.01, y - 0.25 * h, 1.0), k=2)
        elif far:
            S.block(m, INK['slate'], strength=0.80, k=2)
            S.block(m, INK['indigo'], strength=0.55, bokashi=S.grad_y(y - h - 0.01, y - 0.25 * h, 1.0), k=2)
        else:
            S.block(m, INK['moss'], strength=0.95, k=3)
            S.block(m, INK['pine'], strength=0.85, bokashi=S.grad_y(y - h - 0.015, y - 0.30 * h, 1.1), k=3)
            S.block(m, INK['ochre'], strength=0.55, bokashi=S.grad_y(y + 0.02, y - 0.22 * h, 1.0), k=1)

    # ---- bridges ----
    live = [e for k, e in enumerate(EDGES) if present >> k & 1]
    gone = [e for k, e in enumerate(EDGES) if not present >> k & 1]
    paths = {e: bridge_path(*e) for e in EDGES}
    def depth(p): return np.clip((p[:, 1].mean() - HORIZON) / (y1 - HORIZON), 0.1, 1)
    def deckw(e): return (0.0050 + 0.0085 * depth(paths[e])) 
    def draw_piles(d, es, stub=False):
        for e in es:
            p = paths[e]; wd = deckw(e); L = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
            n = max(3, int(L[-1] / (wd * 3.3)))
            for q in np.linspace(0, L[-1], n + 2)[1:-1]:
                k = np.searchsorted(L, q); a = p[min(k, len(p) - 1)]
                hgt = wd * (2.6 if not stub else 1.5)
                for off in (-0.33, 0.33):
                    stroke(d, np.array([[a[0] + off * wd * 1.1, a[1]], [a[0] + off * wd * 1.25, a[1] + hgt]]) * s, wd * 0.30 * s)
    def draw_decks(d, es):
        for e in es: stroke(d, paths[e] * s, deckw(e) * s)
    def draw_rails(d, es):
        for e in es:
            p = paths[e]; wd = deckw(e); tg = np.gradient(p, axis=0); tg /= np.hypot(*tg.T)[:, None] + 1e-12
            nr = np.c_[-tg[:, 1], tg[:, 0]]; horiz = abs(p[-1, 0] - p[0, 0]) / (np.hypot(*(p[-1] - p[0])) + 1e-9)
            for off in (-0.5, 0.5):
                stroke(d, (p + off * wd * nr) * s, max(1.5, wd * 0.16 * s))
            L = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
            for qq in np.linspace(0, L[-1], max(4, int(L[-1] / (wd * 1.15)))):
                k = min(np.searchsorted(L, qq), len(p) - 1); a = p[k]
                if horiz > 0.75:
                    stroke(d, np.array([[a[0], a[1] - 0.5 * wd], [a[0], a[1] - 0.95 * wd]]) * s, max(1.2, wd * 0.12 * s))
                else:      # planks across a deck seen from above
                    stroke(d, np.array([a - 0.5 * wd * nr[k], a + 0.5 * wd * nr[k]]) * s, max(1.0, wd * 0.07 * s))
            if horiz > 0.75:
                q = p + np.array([0, -0.95 * wd]); stroke(d, q * s, max(1.5, wd * 0.15 * s))
    hide = 1 - allm * 0.0
    piles = S.mask(lambda d: draw_piles(d, live)); decks = S.mask(lambda d: draw_decks(d, live))
    rails = S.mask(lambda d: draw_rails(d, live))
    S.block(piles * (1 - decks) * clear, INK['sumi'], strength=0.80, rim=0, k=0)
    S.img[:] = S.img * (1 - decks[..., None] * clear[..., None]) + decks[..., None] * clear[..., None] * np.array([0.955, 0.92, 0.84], np.float32)  # carve the deck out of the sea block
    S.block(decks * clear, INK['vermilion'], strength=0.93, rim=0.12, k=3)
    S.key(rails * clear, strength=0.9)
    if gone:   # a washed-out bridge leaves its piles
        stubs = S.mask(lambda d: draw_piles(d, gone, True))
        S.block(stubs * clear * (1 - foot), INK['sumi'], strength=0.55, rim=0, k=0)

    # ---- trees, torii, key lines on the islands ----
    trees = []
    for i in ISL:
        x, y, w, h, far = ISL[i]; top = mounds[i][1]; r2 = np.random.default_rng(90 + i)
        if far: continue
        for k in r2.choice(np.arange(30, len(top) - 30, 14), 3 if i != 2 else 2, replace=False):
            trees.append((top[k, 0], top[k, 1] + 0.008, w * r2.uniform(0.15, 0.21), np.random.default_rng(int(r2.integers(1e9))), i in home))
    import copy
    trk = S.mask(lambda d: [pine(d, s, x, y, sz, copy.deepcopy(r), 't') for x, y, sz, r, hm in trees])
    fol = S.mask(lambda d: [pine(d, s, x, y, sz, copy.deepcopy(r), 'f') for x, y, sz, r, hm in trees])
    folh = S.mask(lambda d: [pine(d, s, x, y, sz, copy.deepcopy(r), 'f') for x, y, sz, r, hm in trees if hm])
    S.block(trk * (1 - fol), INK['sumi'], strength=0.85, rim=0, k=0)
    S.img[:] = S.img * (1 - 0.92 * fol[..., None]) + 0.92 * fol[..., None] * np.array([0.90, 0.90, 0.80], np.float32)
    S.block(folh, INK['pine'], strength=0.97, rim=0.3, k=4)
    S.block(folh, INK['indigo'], strength=0.35, k=4)
    S.block(fol * (1 - folh), INK['grey'], strength=0.95, rim=0.3, k=4)
    # torii on the middle island (the vertex joined to four)
    tx, ty, tw = ISL[2][0] + 0.005, ISL[2][1] + 0.016, 0.030
    def draw_torii(d):
        for sx in (-1, 1):
            stroke(d, np.array([[tx + sx * 0.36 * tw, ty], [tx + sx * 0.30 * tw, ty - 0.92 * tw]]) * s, 0.10 * tw * s)
        stroke(d, np.array([[tx - 0.62 * tw, ty - 0.96 * tw], [tx, ty - 0.90 * tw], [tx + 0.62 * tw, ty - 0.96 * tw]]) * s, 0.13 * tw * s)
        stroke(d, np.array([[tx - 0.45 * tw, ty - 0.68 * tw], [tx + 0.45 * tw, ty - 0.68 * tw]]) * s, 0.08 * tw * s)
    tor = S.mask(draw_torii)
    S.img[:] = S.img * (1 - tor[..., None]) + tor[..., None] * np.array([0.955, 0.92, 0.84], np.float32)
    S.block(tor, INK['vermilion'], strength=0.95, rim=0.1, k=3)
    # key block: hill outlines + contour hatching, shore line
    def draw_key(d):
        for i in ISL:
            x, y, w, h, far = ISL[i]; top = mounds[i][1]; lw = (0.0016 if far else 0.0024) * s
            n = len(top); wv = lw * (0.6 + 0.6 * np.sin(np.linspace(0, np.pi, n)))
            stroke(d, top * s, wv)
            if not far:
                r2 = np.random.default_rng(300 + i)
                for k in range(9):       # short strata strokes near the waterline
                    u = r2.uniform(-0.8, 0.8); px_ = x + HILL_DX[i] * w + 0.28 * w * u; py_ = y - 0.012 - r2.uniform(0.04, 0.30) * h
                    L = r2.uniform(0.02, 0.06) * w
                    stroke(d, np.array([[px_ - L, py_ + 0.002], [px_, py_], [px_ + L, py_ + 0.003]]) * s, lw * 0.6)
            if not far:                   # a ridge falling from the summit
                kk = int(np.argmin(top[:, 1])); r3 = np.random.default_rng(700 + i)
                for sgn in (-1, 1):
                    L = r3.uniform(0.35, 0.6) * h; tt = np.linspace(0, 1, 12)
                    rx = top[kk, 0] + sgn * (0.05 * w * tt + 0.03 * w * tt ** 2) * r3.uniform(0.6, 1.4); ry = top[kk, 1] + 0.004 + L * tt ** 1.2
                    stroke(d, np.c_[rx, ry] * s, lw * 0.75 * (1 - 0.7 * tt))
            fp = footprint(i); fp = np.r_[fp, fp[:1]]
            stroke(d, fp * s, lw * 0.45)
    S.key(S.mask(draw_key) * clear * (1 - fol * 0.9), strength=0.85)

    # boats: paper sails
    boats = [(0.52, 0.585, 0.020), (0.905, 0.50, 0.015), (0.10, 0.60, 0.017), (0.44, 0.365, 0.010), (0.60, 0.87, 0.026)]
    def draw_sail(d):
        for bx, by, bs in boats:
            d.polygon(S.px([(bx - 0.05 * bs, by - 0.2 * bs), (bx - 0.02 * bs, by - 1.5 * bs), (bx + 0.62 * bs, by - 0.25 * bs)]), fill=255)
    def draw_hull(d):
        for bx, by, bs in boats:
            d.polygon(S.px([(bx - 0.75 * bs, by - 0.18 * bs), (bx + 0.85 * bs, by - 0.18 * bs), (bx + 0.55 * bs, by + 0.10 * bs), (bx - 0.5 * bs, by + 0.10 * bs)]), fill=255)
            stroke(d, np.array([[bx - 0.05 * bs, by - 0.15 * bs], [bx - 0.02 * bs, by - 1.6 * bs]]) * s, 0.07 * bs * s)
    sail = S.mask(draw_sail) * clear; hull = S.mask(draw_hull) * clear
    S.img[:] = S.img * (1 - sail[..., None]) + sail[..., None] * np.array([0.965, 0.94, 0.87], np.float32)
    S.block(hull, INK['sumi'], strength=0.85, rim=0, k=0)
    # birds
    def draw_birds(d):
        for bx, by, bs in [(0.30, 0.175, 0.011), (0.335, 0.158, 0.009), (0.355, 0.182, 0.008), (0.39, 0.150, 0.007),
                           (0.27, 0.150, 0.007)]:
            stroke(d, np.array([[bx - bs, by - 0.35 * bs], [bx - 0.4 * bs, by - 0.5 * bs], [bx, by],
                                [bx + 0.4 * bs, by - 0.5 * bs], [bx + bs, by - 0.35 * bs]]) * s, [1, 2.2, 2.6, 2.2, 1] * np.array(0.0009 * s))
    S.key(S.mask(draw_birds), strength=0.85)

    # frame line, cartouche, seal, caption
    def draw_frame(d):
        d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=255, width=int(0.0022 * s))
    S.key(S.mask(draw_frame), strength=0.9)
    if title:
        # seal: the graph itself, cut in a vermilion square
        cx, cy, cw = 0.905, 0.094, 0.050
        def gpos(i):
            x, y = ISL[i][:2]; return (cx + (x - 0.5) * cw * 1.05, cy + (y - 0.60) * cw * 1.65)
        def draw_seal(d):
            d.rounded_rectangle([(cx - cw / 2) * s, (cy - cw / 2) * s, (cx + cw / 2) * s, (cy + cw / 2) * s], radius=0.004 * s, fill=255)
            for i, j in EDGES:
                d.line([tuple(np.array(gpos(i)) * s), tuple(np.array(gpos(j)) * s)], fill=0, width=int(0.0016 * s))
            for i in ISL:
                gx, gy = gpos(i); r = 0.0030
                d.ellipse([(gx - r) * s, (gy - r) * s, (gx + r) * s, (gy + r) * s], fill=0)
        seal = S.mask(draw_seal)
        S.img[:] = S.img * (1 - seal[..., None] * 0.9) + seal[..., None] * 0.9 * np.array([0.955, 0.92, 0.84], np.float32)
        S.block(seal, INK['vermilion'], strength=0.95, rim=0.25, speckle=0.22, k=3)
        cap = S.text_mask([(x0, 0.928, 'Seven Islands, Thirteen Bridges', SERIF_B, 0.0215, 'ls'),
                           (x0, 0.957, 'Toss a coin for every bridge. In exactly half of the 8192 outcomes you can still walk everywhere.',
                            SERIF_I, 0.0152, 'ls'),
                           (x1, 0.928, 'MO 516850', SERIF, 0.0125, 'rs')])
        S.key(cap, strength=0.88, rough=0.25)
    if out: S.save(out)
    return S


if __name__ == '__main__':
    size = int(sys.argv[1]); out = sys.argv[2]
    present = int(sys.argv[3], 0) if len(sys.argv) > 3 else (1 << 13) - 1
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    render(size, out, present, seed)
