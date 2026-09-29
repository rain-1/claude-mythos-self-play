"""The Bee's Ledger — sunburst of the prefix tree of bee numbers (MO 515588)."""
import numpy as np, sys, time
from sorbet import *
S = int(sys.argv[1]); K = int(sys.argv[2]); out = sys.argv[3]
SS = 2
N = S * SS
t0 = time.time()
raw = np.fromfile('tree_26.bin', np.uint8); rawA = np.fromfile('ang_26.bin', np.uint8); rawD = np.fromfile('dst_26.bin', np.uint8)
lev, angl, dstl, off = [None], [None], [None], 0
for j in range(1, 27):
    n_ = 1 << (j - 1); lev.append(raw[off:off + n_]); angl.append(rawA[off:off + n_]); dstl.append(rawD[off:off + n_]); off += n_
LUT = np.stack([absorb(wheel_tint(i / 256 + 0.08)) for i in range(256)])
HEADP = ['butter', 'lime', 'sky', 'periwinkle', 'bubblegum', 'peach']  # heading 30,90,...,330 deg
absH = np.stack([absorb(p) for p in HEADP])            # (6,3)
cx, cy = N / 2, 0.455 * N
R0, R1 = 0.07 * N, 0.415 * N
P = float(sys.argv[4]) if len(sys.argv) > 4 else 0.75
DK = float(sys.argv[5]) if len(sys.argv) > 5 else 1.4
def rad(j):  # ring j spans rad(j-1)..rad(j), j = 2..K (depth 1 is the centre disc)
    return R0 + (R1 - R0) * ((j - 1) / (K - 1)) ** P
# box-filtered ring textures: absorbance per node, averaged down to <= MAXB bins per ring
MAXB = 1 << 17
TEX = {}
for jj in range(2, K + 1):
    v = lev[jj]; alive = ((v >= 1) & (v <= 6)).astype(np.float32)
    dens = DK * (0.55 + 0.9 * dstl[jj] / 255.0) * alive
    t = dens[:, None] * LUT[angl[jj]]
    n_ = len(t)
    if n_ > MAXB: t = t.reshape(MAXB, n_ // MAXB, 3).mean(1)
    TEX[jj] = (t.astype(np.float32), len(t))
sh = Sheet(N, N, seed=3)
A = np.zeros((N, N, 3), np.float32)
CH = 512
for y0 in range(0, N, CH):
    yy, xx = np.mgrid[y0:min(N, y0 + CH), 0:N].astype(np.float32)
    dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
    r = np.hypot(dx, dy)
    frac = ((np.arctan2(dx, -dy) / (2 * np.pi)) % 1.0)          # clockwise from top
    # ring index
    u = np.clip((r - R0) / (R1 - R0), 0, 1)
    jf = 1 + (K - 1) * u ** (1 / P)
    j = np.ceil(jf).astype(np.int32)
    inside = (r > R0) & (r < R1)
    a = np.zeros(r.shape + (3,), np.float32)
    for jj in range(2, K + 1):
        m = inside & (j == jj)
        if not m.any(): continue
        tex, M = TEX[jj]
        idx = np.minimum((frac[m] * M).astype(np.int64), M - 1)
        rin, rout = rad(jj - 1), rad(jj)
        t = (r[m] - rin) / (rout - rin)
        gapw = max(0.6 * SS, 0.10 * (rout - rin))
        edge = np.clip(np.minimum(r[m] - rin, rout - r[m]) / gapw, 0, 1)
        if jj > 11: edge = np.ones_like(edge)
        a[m] = edge[:, None] * tex[idx]
    A[y0:y0 + CH] = a
sh.wash_rgb(A)
del A
# the centre: all bee flights of DEPTH_C bits on a honeycomb, beads hued like the rings
DEPTH_C = 9
HD = [(np.cos(np.radians(30 + 60 * h)), np.sin(np.radians(30 + 60 * h))) for h in range(6)]
walks = []
def fly(path, h, depth):
    if depth == DEPTH_C:
        walks.append(list(path)); return
    for turn in (-1, +1):               # right (0), left (1)
        h2 = (h + turn) % 6
        p = (round(path[-1][0] + HD[h2][0], 6), round(path[-1][1] + HD[h2][1], 6))
        if p in path: continue
        fly(path + [p], h2, depth + 1)
fly([(0.0, 0.0), (round(HD[5][0], 6), round(HD[5][1], 6))], 5, 1)
print('centre walks', len(walks))
edge = R0 * 0.80 / 7.2
tocan = lambda p: (cx + edge * p[0], cy - edge * p[1])
comb = []
for i in range(-12, 13):
    for jj in range(-12, 13):
        qx = np.sqrt(3) * (i + 0.5 * jj); qy = 1.5 * jj      # hex centres (edge 1) in bee coords
        comb.append([tocan((qx + np.cos(np.pi / 6 + t * np.pi / 3) * 1, qy + np.sin(np.pi / 6 + t * np.pi / 3))) for t in range(7)])
# shift: bee vertices sit at hex corners; start vertex (0,0) must be a corner -> offset centres by (0,1)
comb = [[(x, y + edge) for (x, y) in c] for c in comb]   # hex centre (0,-1) has its top vertex at the start (0,0)
rr = np.hypot(*np.meshgrid(np.arange(N) - cx, np.arange(N) - cy)).astype(np.float32)
fade = np.clip((R0 * 0.93 - rr) / (0.12 * R0), 0, 1)
sh.wash(0.55 * fade * lines(N, N, comb, max(1, round(N / 3000)), sigma=0.5 * SS), 'honey')
wl = lines(N, N, [[tocan(p) for p in w_] for w_ in walks], max(1, round(N / 2600)), sigma=0.5 * SS)
sh.wash(0.22 * fade * wl, 'plum')
for w_ in walks:
    ex, ey = w_[-1]; ai = int((np.arctan2(ey, ex) / (2 * np.pi) % 1) * 255.999)
    X_, Y_ = tocan(w_[-1])
    sh.wash(0.5 * discs(N, N, [X_], [Y_], [edge * 0.30], sigma=0.4 * SS), wheel_tint(ai / 256 + 0.08)) if False else None
# beads batched by hue bin
bins = {}
for w_ in walks:
    ex, ey = w_[-1]; ai = int((np.arctan2(ey, ex) / (2 * np.pi) % 1) * 255.999) // 8
    bins.setdefault(ai, []).append(tocan(w_[-1]))
for ai, pts in bins.items():
    pts = np.array(pts)
    sh.wash(0.9 * fade * discs(N, N, pts[:, 0], pts[:, 1], [edge * 0.28] * len(pts), sigma=0.5 * SS), wheel_tint((ai * 8 + 4) / 256 + 0.08))
# coral: the walk of 32 = 100000b — first edge, then five right turns: a hexagon back to the start
hx = [(0.0, 0.0)]; h = 5; hx.append(HD[5])
for k in range(5):
    h = (h - 1) % 6; hx.append((hx[-1][0] + HD[h][0], hx[-1][1] + HD[h][1]))
sh.wash(1.2 * lines(N, N, [[tocan(p) for p in hx]], max(2, round(N / 1100)), sigma=0.6 * SS), 'coral')
sh.wash(1.3 * discs(N, N, [cx], [cy], [edge * 0.22], sigma=0.5 * SS), 'plum')
# paper ghost honeycomb (fades toward the disc)
big = N / 70
gl = []
for i in range(-60, 61):
    for jj in range(-50, 51):
        qx = cx + big * np.sqrt(3) * (i + 0.5 * jj); qy = cy + big * 1.5 * jj
        if -big < qx < N + big and -big < qy < N + big:
            gl.append([(qx + big * np.cos(np.pi / 6 + t * np.pi / 3), qy + big * np.sin(np.pi / 6 + t * np.pi / 3)) for t in range(4)])
g = lines(N, N, gl, max(1, round(N / 2400)), sigma=0.6 * SS)
g *= np.clip((rr - R1 * 1.03) / (0.08 * N), 0, 1)
sh.wash(0.22 * g, 'honey')
del rr
# caption
T1 = "The Bee's Ledger"
T2 = "every number whose binary digits fly a honeycomb without crossing their own path, to 26 bits"
T3 = "hue = where the bee is;  gaps = bees that met themselves;  coral = 32 = 100000, the first to fail"
txt = [(T1, N / 2, 0.905 * N, 0.030 * N, 'serif_bold', 'mm'),
       (T2, N / 2, 0.940 * N, 0.0165 * N, 'italic', 'mm'),
       (T3, N / 2, 0.965 * N, 0.0120 * N, 'mono', 'mm')]
sh.wash(1.25 * text_mask(N, N, txt), 'ink')
img = sh.develop(dmax=1.5)
finish(img, S, out)
print('done', time.time() - t0)
