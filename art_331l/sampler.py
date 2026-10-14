# Every Number but Three — a wall of small embroidery hoops: for k = 1..K, the smallest graph whose busiest
# pair of vertices is joined by exactly k simple paths, each path one silk thread between two coral knots.
import json, numpy as np, networkx as nx, argparse, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import silk

ap = argparse.ArgumentParser()
ap.add_argument('--W', type=int, default=4096)
ap.add_argument('--cols', type=int, default=7)
ap.add_argument('--K', type=int, default=49)
ap.add_argument('--out', default='sampler.png')
a = ap.parse_args()
d = json.load(open('math_paths/census.json'))['census']
S = a.W / 4096.0
cols = a.cols; rows = (a.K + cols - 1) // cols
tile = int(560 * S); gapx = int((a.W - cols * tile) / (cols + 1))
top = int(560 * S); lab = int(70 * S)
H = top + rows * (tile + lab) + int(120 * S)
ground = silk.linen(H, a.W, period=max(2.0, 8.0 * S), base=(0.990, 0.983, 0.972))
img = ground.copy()
R = tile * 0.40; wring = tile * 0.035

def layout(k):
    e = d[str(k)]; J = lambda x: json.loads(x) if isinstance(x, str) else x
    edges = J(e['edges']); u, v = J(e['pair']); paths = J(e['paths'])
    G = nx.Graph(); G.add_edges_from(edges)
    best = None
    n = G.number_of_nodes()
    for seed in range(24):
        rng = np.random.default_rng(seed)
        init = {i: rng.uniform(-0.6, 0.6, 2) for i in range(n)}
        hd = (1.0, 0.75, 0.55)[seed % 3]
        init[u] = np.array([0.0, -hd]); init[v] = np.array([0.0, hd])
        pos = nx.spring_layout(G, pos=init, fixed=[u, v], iterations=400, k=0.9, seed=seed)
        P = np.array([pos[i] for i in range(n)])
        sc = 1e9
        for i in range(n):
            for j in range(i + 1, n): sc = min(sc, np.linalg.norm(P[i] - P[j]))
        for (x, y) in edges:
            A, B = P[x], P[y]
            for i in range(n):
                if i in (x, y): continue
                t = np.clip(np.dot(P[i] - A, B - A) / np.dot(B - A, B - A), 0, 1)
                sc = min(sc, 1.6 * np.linalg.norm(P[i] - (A + t * (B - A))))
        sc /= np.abs(P).max()
        sc -= 0.15 * abs(P[:, 0].mean()) / np.abs(P).max()
        if best is None or sc > best[0]: best = (sc, P)
    P = best[1]
    P = P - np.array([(P[:, 0].max() + P[:, 0].min()) / 2, 0.0])
    P = P / np.max(np.linalg.norm(P, axis=1)) * R * 0.74
    return P, edges, u, v, paths

def chaikin(p, it=4):
    for _ in range(it):
        q = [p[0]]
        for i in range(len(p) - 1):
            q.append(0.75 * p[i] + 0.25 * p[i + 1]); q.append(0.25 * p[i] + 0.75 * p[i + 1])
        q.append(p[-1]); p = np.array(q)
    return p

t0 = time.time()
lx, ly, lz = -0.55, -0.62, 0.56
rad = max(0.8, 1.7 * S)
for idx in range(a.K):
    k = idx + 1
    r_, c_ = divmod(idx, cols)
    x0 = gapx + c_ * (tile + gapx); y0 = top + r_ * (tile + lab)
    cx, cy = x0 + tile / 2, y0 + tile / 2
    sub = img[y0:y0 + tile, x0:x0 + tile].copy()
    lcx, lcy = tile / 2, tile / 2
    # inside the hoop: slightly brighter, taut linen
    yy, xx = np.mgrid[0:tile, 0:tile].astype(np.float32)
    rr = np.sqrt((xx - lcx) ** 2 + (yy - lcy) ** 2)
    inside = np.clip(R - rr + 0.5, 0, 1)[..., None]
    sub = sub * (1 - inside) + np.minimum(sub * 1.006, 1) * inside
    knots = []
    if str(k) in d:
        P, edges, u, v, paths = layout(k)
        P = P + np.array([lcx, lcy])
        sig = np.array([np.mean([P[w][0] for w in p]) + 1e-3 * len(p) for p in paths])
        rank = np.argsort(np.argsort(sig))
        # per-edge spacing so the busiest edge carries a bundle of width <= 0.16 R
        load = {}
        for p in paths:
            for i in range(len(p) - 1):
                e = tuple(sorted((p[i], p[i + 1]))); load[e] = load.get(e, 0) + 1
        sp = min(6.0 * S, 0.42 * R / max(k, 1))
        acc = np.zeros((tile, tile, 3), np.float32); alp = np.zeros((tile, tile), np.float32); cov = np.zeros((tile, tile), np.float32)
        order = np.random.default_rng(k).permutation(len(paths))
        for pi in order:
            p = paths[pi]; o = (rank[pi] - (k - 1) / 2) * sp
            ctrl = [P[p[0]]]
            for i in range(len(p) - 1):
                A, B = P[p[i]], P[p[i + 1]]; dv = (B - A) / np.linalg.norm(B - A)
                nr = np.array([-dv[1], dv[0]])
                if nr[0] < -1e-9 or (abs(nr[0]) < 1e-9 and nr[1] < 0): nr = -nr
                if i > 0:
                    ctrl.append(A + 0.5 * (nr + prev_n) * o)
                ctrl.append(A + (B - A) * 0.2 + nr * o); ctrl.append(A + (B - A) * 0.8 + nr * o)
                prev_n = nr
            ctrl.append(P[p[-1]])
            pts = chaikin(np.array(ctrl), 5)
            col = silk.wheel(rank[pi] / max(k - 1, 1)) if k > 1 else silk.wheel(0.55)
            silk.draw_polyline(acc, alp, cov, pts.astype(np.float64), rad, col.astype(np.float64), 0.9, lx, ly, lz,
                               30 * S + 3, 0.30, 8.0)
        sub = silk.composite(sub, acc, alp, cov, shadow_dx=2.5 * S + 0.5, shadow_dy=4 * S + 0.5, shadow_blur=3 * S + 0.6)
        for w in range(len(P)):
            knots.append((P[w], w in (u, v)))
    else:
        # the missing number: two coral knots and nothing between them
        knots = [(np.array([lcx, lcy - R * 0.55]), True), (np.array([lcx, lcy + R * 0.55]), True)]
    for q, end in knots:
        rk = (15 if end else 9) * S + 1
        d_ = np.sqrt((xx - q[0]) ** 2 + (yy - q[1]) ** 2)
        sh = gaussian_filter(np.clip(rk + 0.5 - np.sqrt((xx - q[0] - 3 * S) ** 2 + (yy - q[1] - 4 * S) ** 2), 0, 1), 3 * S + 0.5)
        sub *= (1 - 0.22 * sh[..., None] * np.array([1, 1, 0.5]))
        msk = np.clip(rk + 0.5 - d_, 0, 1)[..., None]
        t = np.clip(d_ / rk, 0, 1); nz = np.sqrt(np.clip(1 - t * t, 0, 1))
        ang = np.arctan2(yy - q[1], xx - q[0]); bumps = 0.5 + 0.5 * np.sin(6 * ang + 8 * t)
        hl = np.exp(-(((xx - q[0] + rk * 0.35) ** 2 + (yy - q[1] + rk * 0.4) ** 2) / (rk * 0.32) ** 2))
        base = silk.CORAL if end else np.array([0.74, 0.70, 0.80])
        kn = base[None, None, :] * (0.62 + 0.38 * nz - 0.08 * bumps)[..., None] + 0.33 * hl[..., None]
        sub = sub * (1 - msk) + kn * msk
    sub = silk.hoop(sub, lcx, lcy, R, wring, seed=k)
    img[y0:y0 + tile, x0:x0 + tile] = sub
    if k % 7 == 0: print(k, time.time() - t0, flush=True)

im = Image.fromarray(silk.to_u8(img)); dr = ImageDraw.Draw(im)
ink = tuple(int(c * 255) for c in silk.INK); soft = tuple(int(0.30 * 255 + 0.70 * c * 255) for c in silk.INK)
coral = tuple(int(c * 255) for c in silk.CORAL)
for idx in range(a.K):
    k = idx + 1; r_, c_ = divmod(idx, cols)
    x0 = gapx + c_ * (tile + gapx); y0 = top + r_ * (tile + lab)
    f = silk.font('title' if k != 3 else 'ital', int(46 * S))
    txt = str(k) if k != 3 else '3 — never'
    w = dr.textlength(txt, font=f)
    dr.text((x0 + tile / 2 - w / 2, y0 + tile - int(4 * S)), txt, font=f, fill=coral if k == 3 else ink)
X0 = int(0.05 * a.W); Y0 = int(150 * S)
dr.text((X0, Y0), 'Every Number but Three', font=silk.font('title', int(124 * S)), fill=ink)
dr.text((X0, Y0 + int(160 * S)), 'for each k, the smallest graph whose busiest pair of vertices is joined by exactly k simple paths — one silk thread per path',
        font=silk.font('ital', int(56 * S)), fill=ink)
dr.text((X0, Y0 + int(245 * S)), 'coral knots: the busiest pair.  No graph has exactly three (any block richer than a cycle already gives four); every k ≥ 4 occurs.',
        font=silk.font('reg', int(46 * S)), fill=soft)
im.save(a.out)
print('done', time.time() - t0)
