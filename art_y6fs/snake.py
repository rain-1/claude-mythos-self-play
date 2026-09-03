"""The Snake That Sees Every Room — snake-in-the-box with bounded covering radius (MO 514865).
A snake is an induced path in the hypercube Q_n. The question: is there a universal D such that
Q_n has a D-dense snake (every vertex within distance D of it) for every n?
We search: exhaustive for n <= 5 (min covering radius over ALL snakes), randomised DFS with a
coverage heuristic for n = 6..9, and draw the n = 8 snake on a 16x16 Karnaugh map.

usage: python3 snake.py SIZE [out]
"""
import sys, math, time, json, random
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from pastel import *


def dist_to_set(n, S):
    """BFS distances from set S in Q_n"""
    N = 1 << n
    d = np.full(N, -1, np.int64)
    fr = list(S)
    for v in fr: d[v] = 0
    k = 0
    while fr:
        nf = []
        for v in fr:
            for i in range(n):
                u = v ^ (1 << i)
                if d[u] < 0:
                    d[u] = k + 1; nf.append(u)
        fr = nf; k += 1
    return d


def covering_radius(n, path):
    return int(dist_to_set(n, path).max())


def exhaustive_min_D(n):
    """min covering radius over all snakes starting at 0 (all snakes are equivalent under symmetry to one starting at 0)"""
    N = 1 << n
    best = [n, None, 0]
    nbr = [[v ^ (1 << i) for i in range(n)] for v in range(N)]
    onpath = np.zeros(N, bool)
    blocked = np.zeros(N, np.int64)   # count of path vertices adjacent (excluding the current head)
    path = [0]
    onpath[0] = True
    count = [0]

    def rec():
        count[0] += 1
        D = covering_radius(n, path)
        if D < best[0] or (D == best[0] and len(path) > len(best[1] or [])):
            best[0] = D; best[1] = list(path)
        head = path[-1]
        for u in nbr[head]:
            if onpath[u]: continue
            # u must not be adjacent to any path vertex other than head
            ok = True
            for w in nbr[u]:
                if onpath[w] and w != head:
                    ok = False; break
            if not ok: continue
            onpath[u] = True; path.append(u)
            rec()
            path.pop(); onpath[u] = False
    rec()
    return best[0], best[1], count[0]


def heuristic_min_D(n, restarts=400, seed=1, time_budget=60.0):
    """iterated local search for a 1-dense (dominating) snake: greedy growth toward uncovered
    vertices, then repeatedly cut the snake at a random point and regrow; accept when the number
    of uncovered vertices does not increase. Returns (D, path) for the best snake found."""
    rng = random.Random(seed)
    N = 1 << n
    nbr = [[v ^ (1 << i) for i in range(n)] for v in range(N)]

    def grow(path, onpath, cov, temp):
        while True:
            head = path[-1]
            cands = []
            for u in nbr[head]:
                if onpath[u]: continue
                if any(onpath[w] and w != head for w in nbr[u]): continue
                gain = (cov[u] == 0) + sum(cov[w] == 0 for w in nbr[u])
                cands.append((gain + rng.random() * temp, u))
            if not cands: break
            cands.sort(reverse=True)
            u = cands[0][1]
            path.append(u); onpath[u] = 1
            cov[u] += 1
            for w in nbr[u]: cov[w] += 1

    def state_from(path):
        onpath = bytearray(N); cov = np.zeros(N, np.int64)
        for v in path:
            onpath[v] = 1; cov[v] += 1
            for w in nbr[v]: cov[w] += 1
        return onpath, cov

    t0 = time.time()
    best = None
    while time.time() - t0 < time_budget:
        path = [0]; onpath, cov = state_from(path)
        grow(path, onpath, cov, 0.9)
        unc = int((cov == 0).sum())
        cur = (unc, -len(path), list(path))
        # local search
        for it in range(400):
            if cur[0] == 0: break
            cut = rng.randint(1, max(1, len(cur[2]) - 1))
            p2 = cur[2][:cut]
            onpath, cov = state_from(p2)
            grow(p2, onpath, cov, rng.choice([0.3, 0.9, 1.5]))
            unc2 = int((cov == 0).sum())
            if (unc2, -len(p2)) <= (cur[0], cur[1]):
                cur = (unc2, -len(p2), list(p2))
        D = covering_radius(n, cur[2])
        key = (D, cur[0], -len(cur[2]))
        if best is None or key < best[0]:
            best = (key, list(cur[2]))
        if D == 1:
            break
    return best[0][0], best[1]


def gray(k):
    return [i ^ (i >> 1) for i in range(1 << k)]


def render(SIZE, out, reuse=None):
    SS = 2
    W = H = SIZE * SS
    results = {}
    if reuse:
        prev = json.load(open(reuse))
        results = {int(k): v for k, v in prev.items() if k != 'drawn'}
        path = prev['drawn']['path']
        print('reusing search results from', reuse)
    else:
        for n in range(2, 6):
            t0 = time.time()
            D, path, cnt = exhaustive_min_D(n)
            results[n] = dict(D=D, length=len(path), snakes_from_0=cnt, method='exhaustive')
            print('n=%d exhaustive: min covering radius %d (snake of %d vertices), %d snakes enumerated, %.1fs' % (n, D, len(path), cnt, time.time() - t0))
        paths = {}
        for n in range(6, 11):
            t0 = time.time()
            D, path = heuristic_min_D(n, seed=n, time_budget={6: 20, 7: 40, 8: 150, 9: 150, 10: 150}[n])
            results[n] = dict(D=D, length=len(path), method='heuristic', uncovered_at_1=int((dist_to_set(n, path) > 1).sum()))
            paths[n] = path
            print('n=%d heuristic: covering radius %d (snake of %d vertices, %d rooms farther than 1), %.1fs' % (
                n, D, len(path), results[n]['uncovered_at_1'], time.time() - t0))
        path = paths[8]
    n = 8
    # verify inducedness of the drawn snake
    S = set(path)
    for a, v in enumerate(path):
        for i in range(n):
            u = v ^ (1 << i)
            if u in S:
                b = path.index(u)
                assert abs(a - b) == 1, 'not induced'
    d = dist_to_set(n, path)
    print('n=8 snake verified induced; distance histogram', np.bincount(d).tolist())
    # nested torus map: Q_8 = Q_2^4; each 2-bit pair is a 4-cycle drawn as a 4-position ring
    # (Gray order 00,01,11,10) so EVERY hypercube edge is a step of 1 (mod 4) in exactly one of
    # four coordinates: block row, block col, row in block, col in block.
    g2 = {0: 0, 1: 1, 3: 2, 2: 3}
    def coords(v):
        return g2[(v >> 6) & 3], g2[(v >> 4) & 3], g2[(v >> 2) & 3], g2[v & 3]
    def cell(v):
        br, bc, r, c = coords(v)
        return br * 4 + r, bc * 4 + c
    G = 16
    margin = 0.10 * W
    gap = 0.35   # gap between blocks in cell units
    cs = (W - 2 * margin) / (G + 3 * gap)
    def centre(v):
        br, bc, r, c = coords(v)
        return margin + (bc * (4 + gap) + c + 0.5) * cs, margin + (br * (4 + gap) + r + 0.5) * cs
    def key_pos(v):
        return coords(v)
    sheet = Sheet(W, H, seed=17)
    # every room is tinted by the snake room that sees it (the first along the snake, if several):
    # hue = position along the snake, so the map is the snake's territories
    owner = np.full(256, -1, np.int64)
    for a, v in enumerate(path):
        owner[v] = a
    snake_index = {v: a for a, v in enumerate(path)}
    for v in range(256):
        if v not in snake_index:
            cands = [snake_index[v ^ (1 << i)] for i in range(n) if (v ^ (1 << i)) in snake_index]
            owner[v] = min(cands) if cands else -1
    hue = np.where(owner >= 0, owner / max(1, len(path)), 0.0)
    i0, i1, tt = hue_to_pigments(hue)
    for p in range(len(CYCLE)):
        im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
        any_ = False
        for v in range(256):
            w = (1 - tt[v]) * (i0[v] == p) + tt[v] * (i1[v] == p)
            if w <= 0.02: continue
            any_ = True
            x, y = centre(v)
            pad = 0.07 * cs
            far = d[v] >= 2
            dr.rounded_rectangle([x - cs / 2 + pad, y - cs / 2 + pad, x + cs / 2 - pad, y + cs / 2 - pad], radius=0.18 * cs,
                                 fill=float(w * (0.25 if far else 1.0)))
        if not any_: continue
        Dm = gaussian_filter(np.asarray(im, np.float32), 0.8 * SS)
        sheet.wash(Dm * 0.6, CYCLE[p], granulate=0.3, edge=0.25, seed=70 + p)
    # rooms beyond distance 1 (none for this snake) would be left as bare paper with an ink ring
    for v in range(256):
        if d[v] >= 2:
            x, y = centre(v)
            im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
            dr.rounded_rectangle([x - cs / 2 + 0.07 * cs, y - cs / 2 + 0.07 * cs, x + cs / 2 - 0.07 * cs, y + cs / 2 - 0.07 * cs],
                                 radius=0.18 * cs, outline=1.0, width=max(1, int(0.05 * cs)))
            sheet.wash(gaussian_filter(np.asarray(im, np.float32), 0.6 * SS) * 0.6, 'ink')
    # the snake: ink thread through cell centres; non-grid-adjacent steps as arcs
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    lw = int(round(0.16 * cs))
    for a in range(len(path) - 1):
        x0, y0 = centre(path[a]); x1, y1 = centre(path[a + 1])
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1.2 * cs:
            dr.line([(x0, y0), (x1, y1)], fill=1.0, width=lw)
        else:
            # a wrap-around or between-block step: a thinner, lighter arc bulging away from the map centre
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            nx, ny = -(y1 - y0) / L, (x1 - x0) / L
            sgn = 1 if (nx * (mx - W / 2) + ny * (my - H / 2)) > 0 else -1
            b = min(0.16 * L, 1.0 * cs) * sgn
            pts = []
            for t in np.linspace(0, 1, 40):
                bx = (1 - t) * x0 + t * x1 + nx * b * 4 * t * (1 - t)
                by = (1 - t) * y0 + t * y1 + ny * b * 4 * t * (1 - t)
                pts.append((bx, by))
            dr.line(pts, fill=0.5, width=max(1, int(lw * 0.5)), joint='curve')
    Dl = gaussian_filter(np.asarray(im, np.float32), 0.6 * SS)
    sheet.wash(Dl / (Dl.max() + 1e-9) * 0.9, 'ink')
    # snake vertices: coral beads with ink centre; head and tail bigger
    xs = [centre(v)[0] for v in path]; ys = [centre(v)[1] for v in path]
    rs = [0.30 * cs] * len(path); rs[0] = rs[-1] = 0.40 * cs
    Db = discs_density(W, H, xs, ys, rs, [1.0] * len(path), sigma=0.8 * SS)
    sheet.wash(Db / (Db.max() + 1e-9) * 1.0, 'coral')
    Dc = discs_density(W, H, xs, ys, [0.09 * cs] * len(path), [1.0] * len(path), sigma=0.5 * SS)
    sheet.wash(Dc / (Dc.max() + 1e-9) * 0.8, 'ink')
    # bit labels: block coordinates (2 bits) outside, in-block coordinates on the first block
    items = []
    gl = ['00', '01', '11', '10']
    for k in range(4):
        items.append((gl[k], margin + (k * (4 + gap) + 2) * cs, margin - 0.7 * cs, 0.0095 * W, 'mono', 'mm'))
        items.append((gl[k], margin - 0.9 * cs, margin + (k * (4 + gap) + 2) * cs, 0.0095 * W, 'mono', 'mm'))
    sheet.caption_strip(0.905, 0.985)
    hist = np.bincount(d)
    items += [("The Snake That Sees Every Room", 0.05 * W, 0.935 * H, 0.030 * W, 'serif_bold', 'ls'),
              ("an induced path of %d rooms in the 8-cube; every one of the 256 rooms is within %d door%s of it (%s)" % (
                  len(path), d.max(), 's' if d.max() > 1 else '', ', '.join('%d at distance %d' % (c, k) for k, c in enumerate(hist))),
               0.05 * W, 0.962 * H, 0.0135 * W, 'italic', 'ls')]
    T = text_density(W, H, items)
    sheet.wash(T * 0.85, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), out)
    results['drawn'] = dict(n=8, path=path, dist_hist=hist.tolist())
    return results


if __name__ == '__main__':
    SIZE = int(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else 'snake_%d.png' % SIZE
    reuse = sys.argv[3] if len(sys.argv) > 3 else None
    res = render(SIZE, out, reuse)
    json.dump({str(k): v for k, v in res.items()}, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
