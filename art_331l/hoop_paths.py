# Every simple path between opposite corners of an m×m grid, embroidered: each path one silk thread,
# bundled per edge (slot = rank of the path's lateral swing), rounded turns at the nodes, in a hoop.
import numpy as np, sys, time, argparse
from paths import grid_paths
import silk

ap = argparse.ArgumentParser()
ap.add_argument('--W', type=int, default=1024)
ap.add_argument('--m', type=int, default=5)
ap.add_argument('--hue', default='swing')       # swing | length
ap.add_argument('--order', default='random')    # random | long_first | short_first
ap.add_argument('--wmax', type=float, default=0.40)  # max bundle width / edge length
ap.add_argument('--gamma', type=float, default=0.55)
ap.add_argument('--rad', type=float, default=1.25)   # thread radius in px at 4096
ap.add_argument('--opac', type=float, default=0.85)
ap.add_argument('--disc', type=float, default=0.75)
ap.add_argument('--rdisc', type=float, default=1330)
ap.add_argument('--fillet', type=float, default=0.32)
ap.add_argument('--weave', type=int, default=1)
ap.add_argument('--samp', type=int, default=24)
ap.add_argument('--needle', type=int, default=1)
ap.add_argument('--out', default='proto.png')
ap.add_argument('--caption', type=int, default=1)
a = ap.parse_args()

W = H = a.W; S = W / 4096.0
m = a.m
P = grid_paths(m)
n = len(P)
print(n, 'paths')
# geometry: grid rotated 45°, corner 0 at top, corner N-1 at bottom
cx, cy = W * 0.5, H * 0.445
R_hoop = 1480 * S
half_diag = 1250 * S
L = half_diag * 2 / ((m - 1) * np.sqrt(2)) * np.sqrt(2) / 2 * np.sqrt(2)  # edge length in px
L = 2 * half_diag / ((m - 1) * np.sqrt(2))
def pos(v):
    x, y = v % m, v // m
    u = (x - y) / np.sqrt(2); w = (x + y) / np.sqrt(2)
    return np.array([cx + u * L, cy - half_diag + w * L])

# lateral swing signature: mean (x - y) over the path's vertices (screen-right is positive)
sig = np.array([np.mean([(v % m) - (v // m) for v in p]) for p in P])
lens = np.array([len(p) - 1 for p in P])
rank_sig = np.argsort(np.argsort(sig + 1e-6 * lens))
# edges
from collections import defaultdict
users = defaultdict(list)
for i, p in enumerate(P):
    for k in range(len(p) - 1):
        e = (min(p[k], p[k + 1]), max(p[k], p[k + 1]))
        users[e].append(i)
cmax = max(len(v) for v in users.values())
print('max edge load', cmax, 'edges', len(users))
slot = {}
for e, us in users.items():
    us_sorted = sorted(us, key=lambda i: (sig[i], lens[i], i))
    c = len(us)
    Wb = a.wmax * L * (c / cmax) ** a.gamma
    for r, i in enumerate(us_sorted):
        slot[(e, i)] = (r - (c - 1) / 2) * (Wb / max(c, 1))
def normal(d):
    nrm = np.array([-d[1], d[0]])
    if nrm[0] < 0 or (abs(nrm[0]) < 1e-9 and nrm[1] < 0): nrm = -nrm
    return nrm
# constant lane per path (global swing rank) -> clean nested mitred turns; then a square->disc warp
ap_lane = a.wmax  # lane width in edge units
lane = (rank_sig / (n - 1) - 0.5) * ap_lane
def gxy(v): return np.array([v % m, v // m], float)
def nrm_g(d):  # normal in grid coords, pointing screen-right (towards +x-y)
    nr = np.array([-d[1], d[0]])
    if nr[0] - nr[1] < 0: nr = -nr
    return nr
def warp(q):
    # q in grid coords (0..m-1)^2 -> screen; elliptical square->disc map blended with the square
    X = q[:, 0] / (m - 1) * 2 - 1; Y = q[:, 1] / (m - 1) * 2 - 1
    Xd = X * np.sqrt(np.clip(1 - Y * Y / 2, 0, 1)); Yd = Y * np.sqrt(np.clip(1 - X * X / 2, 0, 1))
    Xb = a.disc * Xd + (1 - a.disc) * X / np.sqrt(2) * 1.12; Yb = a.disc * Yd + (1 - a.disc) * Y / np.sqrt(2) * 1.12
    u = (Xb - Yb) / np.sqrt(2); w = (Xb + Yb) / np.sqrt(2)
    return np.stack([cx + u * a.rdisc * S, cy + w * a.rdisc * S], -1)
def thread(i):
    p = P[i]; o = lane[i]
    corners = [gxy(p[0])]
    ds = [gxy(p[k + 1]) - gxy(p[k]) for k in range(len(p) - 1)]
    for k in range(1, len(p) - 1):
        n1, n2 = nrm_g(ds[k - 1]), nrm_g(ds[k])
        if abs(np.dot(ds[k - 1], ds[k])) > 0.5: corners.append(gxy(p[k]) + o * n1)
        else: corners.append(gxy(p[k]) + o * (n1 + n2))
    corners.append(gxy(p[-1]))
    # polyline with fillets
    f = a.fillet
    pts = [corners[0]]
    for k in range(1, len(corners) - 1):
        c = corners[k]; d1 = ds[k - 1]; d2 = ds[k]
        if abs(np.dot(d1, d2)) > 0.5:
            pts.append(c); continue
        A = c - d1 * f; B = c + d2 * f
        t = np.linspace(0, 1, 9)[:, None]
        pts.extend(list((1 - t) ** 2 * A + 2 * (1 - t) * t * c + t * t * B))
    pts.append(corners[-1])
    pts = np.array(pts)
    # resample densely so the warp curves the straights
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1)); s = np.concatenate([[0], np.cumsum(seg)])
    ss = np.linspace(0, s[-1], max(8, int(s[-1] * a.samp)))
    q = np.stack([np.interp(ss, s, pts[:, 0]), np.interp(ss, s, pts[:, 1])], -1)
    # endpoints: lanes fan out of the pin -> pull first/last bit to the pin smoothly
    if not a.weave: return warp(q)
    # split into per-node pieces (nearest path vertex), tag kind for the basket-weave order
    V = np.array([gxy(v) for v in p])
    near = np.argmin(np.abs(q[:, None, :] - V[None, :, :]).max(-1) + 1e-6 * np.arange(len(V))[None, :], 1)
    near = np.maximum.accumulate(near)
    pieces = []
    W_ = warp(q)
    st = 0
    for j in range(1, len(q) + 1):
        if j == len(q) or near[j] != near[st]:
            k = near[st]; v = p[k]
            par = ((v % m) + (v // m)) & 1
            if 0 < k < len(p) - 1:
                d1, d2 = ds[k - 1], ds[k]
                if abs(np.dot(d1, d2)) > 0.5: kind = 0 if d1[0] != 0 else 2   # x-straight / y-straight
                else: kind = 1
            else: kind = 1
            if par: kind = 2 - kind
            pieces.append((kind, W_[st:min(j + 1, len(q))]))
            st = j
    return pieces
def pos(v): return warp(gxy(v)[None, :])[0]
if a.hue == 'swing':
    tq = rank_sig / (n - 1)
else:
    tq = (lens - lens.min()) / (lens.max() - lens.min())
cols = np.array([silk.wheel(t) for t in tq])
rng = np.random.default_rng(7)
if a.order == 'random': order = rng.permutation(n)
elif a.order == 'long_first': order = np.argsort(-lens + 0.01 * rng.random(n))
else: order = np.argsort(lens + 0.01 * rng.random(n))

ground = silk.linen(H, W, period=max(2.0, 5.0 * S * 1.6))
# fabric outside the hoop: slightly cooler, gentle folds
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
outside = np.clip((rr - R_hoop) / (6 * S), 0, 1)[..., None]
folds = 1 - 0.025 * np.clip((rr - R_hoop) / (1500 * S), 0, 1)
ground = ground * (1 - outside) + ground * folds[..., None] * np.array([0.99, 0.99, 0.995], np.float32) * outside

acc = np.zeros((H, W, 3), np.float32); alp = np.zeros((H, W), np.float32); cov = np.zeros((H, W), np.float32)
lx, ly, lz = -0.55, -0.62, 0.56
t0 = time.time()
rad = max(0.55, a.rad * S)
if a.weave:
    allp = []
    for i in order:
        for kind, pts in thread(i): allp.append((kind, i, pts))
    allp.sort(key=lambda t: t[0])
    layers = []
    for kind in range(3):
        acc = np.zeros((H, W, 3), np.float32); alp = np.zeros((H, W), np.float32); cov = np.zeros((H, W), np.float32)
        for (kd, i, pts) in allp:
            if kd != kind: continue
            c = cols[i] * (0.95, 0.98, 1.0)[kind]
            silk.draw_polyline(acc, alp, cov, pts, rad, c.astype(np.float64), a.opac, lx, ly, lz,
                               40 * S + 3, 0.30, 8.0)
        layers.append((acc, alp, cov))
        print('layer', kind, time.time() - t0, flush=True)
else:
  for j, i in enumerate(order):
    pts = thread(i)
    silk.draw_polyline(acc, alp, cov, pts, rad, cols[i].astype(np.float64), a.opac, lx, ly, lz,
                       40 * S + 3, 0.30, 8.0)
    if j % 2000 == 0: print(j, time.time() - t0, flush=True)
if a.weave:
    img = ground
    for li, (acc, alp, cov) in enumerate(layers):
        k = 1.0 if li == 0 else 1.6
        img = silk.composite(img, acc, alp, cov, shadow_dx=4 * S * k * 1.5, shadow_dy=6 * S * k * 1.5,
                             shadow_blur=(5 * S * k + 0.6) * 1.5, shadow_k=0.30 if li == 0 else 0.42)
    del layers
else:
    img = silk.composite(ground, acc, alp, cov, shadow_dx=3 * S * 1.5, shadow_dy=5 * S * 1.5, shadow_blur=4 * S * 1.5 + 0.6)
# pins (French knots) at the two corners in coral, small knots at other nodes? (only endpoints)
for v in (0, m * m - 1):
    q = pos(v); rk = 34 * S
    d = np.sqrt((xx - q[0]) ** 2 + (yy - q[1]) ** 2)
    sh = np.clip(rk + 0.5 - np.sqrt((xx - q[0] - 6 * S) ** 2 + (yy - q[1] - 9 * S) ** 2), 0, 1)
    from scipy.ndimage import gaussian_filter
    sh = gaussian_filter(sh, 6 * S + 0.5)
    img *= (1 - 0.25 * sh[..., None] * np.array([1, 1, 0.5]))
    msk = np.clip(rk + 0.5 - d, 0, 1)[..., None]
    t = np.clip(d / rk, 0, 1)
    # knot texture: little loops
    ang = np.arctan2(yy - q[1], xx - q[0])
    bumps = 0.5 + 0.5 * np.sin(7 * ang + 9 * t)
    nz = np.sqrt(np.clip(1 - t * t, 0, 1))
    hl = np.exp(-(((xx - q[0] + rk * 0.35) ** 2 + (yy - q[1] + rk * 0.4) ** 2) / (rk * 0.3) ** 2))
    knot = silk.CORAL[None, None, :] * (0.62 + 0.38 * nz - 0.08 * bumps)[..., None] + 0.35 * hl[..., None]
    img = img * (1 - msk) + knot * msk
img = silk.hoop(img, cx, cy, R_hoop, 95 * S)
if a.needle:
    from scipy.ndimage import gaussian_filter, shift as ndshift
    # needle lying on the linen, lower right, eye toward the hoop; a loose coral thread back to the 'there' knot
    E = np.array([3600.0, 2860.0]) * S; T = np.array([3900.0, 3480.0]) * S
    dvec = (T - E) / np.linalg.norm(T - E); nv = np.array([-dvec[1], dvec[0]])
    K = pos(m * m - 1)
    # thread: from knot, sag down and around, up into the eye (cubic through two handles)
    c1 = K + np.array([150, 420]) * S; c2 = E + np.array([-520, 560]) * S
    t = np.linspace(0, 1, 400)[:, None]
    p1 = (1 - t) ** 3 * K + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t * t * c2 + t ** 3 * (E + dvec * 30 * S)
    # tail beyond the eye: short loose end
    t2 = np.linspace(0, 1, 120)[:, None]
    q0 = E + dvec * 30 * S; q3 = E + np.array([210, -170]) * S
    p2 = (1 - t2) ** 3 * q0 + 3 * (1 - t2) ** 2 * t2 * (q0 - dvec * 160 * S + nv * 60 * S) + 3 * (1 - t2) * t2 * t2 * (q3 + np.array([-40, 150]) * S) + t2 ** 3 * q3
    acc = np.zeros((H, W, 3), np.float32); alp = np.zeros((H, W), np.float32); cov = np.zeros((H, W), np.float32)
    for pp in (p2, p1):
        silk.draw_polyline(acc, alp, cov, pp.astype(np.float64), 5.0 * S + 0.6, silk.CORAL.astype(np.float64), 1.0,
                           lx, ly, lz, 22 * S + 2, 0.35, 8.0)
    img = silk.composite(img, acc, alp, cov, shadow_dx=10 * S, shadow_dy=14 * S, shadow_blur=8 * S + 0.6, shadow_k=0.35)
    # needle body: capsule tapering to the tip, steel shading across, long specular streak
    L_ = np.linalg.norm(T - E)
    rel = np.stack([xx - E[0], yy - E[1]], -1)
    al = rel @ dvec; ac = rel @ nv
    tt = np.clip(al / L_, 0, 1)
    rr_ = 9.5 * S * np.where(tt < 0.78, 1.0, np.clip((1 - tt) / 0.22, 0, 1) ** 0.8) + 0.3
    inside = (al > -9 * S) & (al < L_) & (np.abs(ac) < rr_ + 1)
    cover = np.clip(rr_ + 0.5 - np.abs(ac), 0, 1) * inside
    # rounded eye end
    de = np.sqrt((xx - E[0]) ** 2 + (yy - E[1]) ** 2)
    cover = np.maximum(cover, np.clip(9.5 * S + 0.5 - de, 0, 1) * (al <= 0))
    # eye slot (hole shows the linen/thread below)
    slot = (al > 12 * S) & (al < 52 * S) & (np.abs(ac) < 3.0 * S)
    cover = cover * (1 - slot)
    shd = ndshift(gaussian_filter(cover, 6 * S + 0.5), (16 * S, 10 * S), order=1)
    img = img * (1 - 0.30 * shd[..., None] * np.array([1, 1, 0.55]))
    xn = np.clip(ac / np.maximum(rr_, 1e-3), -1, 1)
    steel = 0.78 + 0.16 * np.sqrt(np.clip(1 - xn * xn, 0, 1)) - 0.10 * xn
    streak = np.exp(-((xn + 0.35) / 0.18) ** 2) * 0.28
    ncol = np.stack([steel * 0.93 + streak, steel * 0.94 + streak, steel * 0.99 + streak], -1)
    img = img * (1 - cover[..., None]) + ncol * cover[..., None]
    # the thread passing through the eye drawn again on top inside the slot region only
    msk = slot[..., None] * (alp[..., None] > 0)
    img = np.where(msk, acc + (1 - alp[..., None]) * img, img)
out = silk.to_u8(img)
from PIL import Image, ImageDraw
im = Image.fromarray(out)
if a.caption:
    dr = ImageDraw.Draw(im)
    ink = tuple(int(c * 255) for c in silk.INK)
    x0 = int(300 * S); y0 = int(3640 * S)
    dr.text((x0, y0), 'Every Way from Here to There', font=silk.font('title', int(118 * S)), fill=ink)
    dr.text((x0, y0 + int(150 * S)), f'all {n:,} self-avoiding paths between opposite corners of the {m}×{m} grid, one silk thread each',
            font=silk.font('ital', int(62 * S)), fill=ink)
    dr.text((x0, y0 + int(235 * S)), 'each thread keeps one lane, ranked by how far its path swings (hue, left to right); at every crossing the bundles weave over and under; coral knots: here, there',
            font=silk.font('reg', int(46 * S)), fill=tuple(int(0.30 * 255 + 0.70 * c * 255) for c in silk.INK))
im.save(a.out)
print('done', time.time() - t0)
