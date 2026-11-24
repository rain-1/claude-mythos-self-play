"""sunprint.py SIZE out — 'The Room the Corner Leaves': six cyanotype exposures, one per assembly (n = 2..7; rows for 3..6, the best free arch for 7).

In the assembly's own frame the corridor turns round it.  For each of 360 moments of the turn the walls are laid
on the paper as an opaque mask and the lamp is lit for 1/360 of the time.  Doses add: the paper is darkest where
it was inside the corridor at EVERY moment (the largest sofa that could make this very same journey), and pales
with the fraction of the turn spent inside a wall.  The crates lie on the paper throughout and stay white."""
import sys, json, os, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
import cyano
from geom import Motion, load
from corner import width_fast

size = int(sys.argv[1]); out = sys.argv[2]
S = size / 1024.0
r2 = np.sqrt(2)
def skyline(h): h = np.asarray(h, float); n = len(h); return np.c_[np.arange(n) - (n - 1) / 2, h, np.zeros(n)]
def law(n): return (n + 4) * (r2 - 1) / 2
sets = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'math_corner', 'chosen.json')))
cols, rows = 2, 3
X0, X1, Y0, Y1 = 0.060, 0.940, 0.040, 0.825; gx, gy = 0.030, 0.052
pw = (X1 - X0 - gx * (cols - 1)) / cols; ph = (Y1 - Y0 - gy * (rows - 1)) / rows
boxes = [(X0 + c * (pw + gx), Y0 + r * (ph + gy), X0 + c * (pw + gx) + pw, Y0 + r * (ph + gy) + ph) for r in range(rows) for c in range(cols)]
sh = cyano.Sheet(size, seed=23, ss=2, coat_box=boxes)
PPW = 0.250 * pw * size          # pixels per corridor width — the same in every panel
dose = np.zeros((size, size), np.float32); obj = np.zeros((size, size), np.float32)
info = []
K = 360
for (key, b) in zip(['2', '3', '4', '5', '6', '7'], boxes):
    M = Motion(np.array(sets[key]['P']).reshape(-1, 3)); info.append((int(key), M.n / width_fast(M.P, 46080) ** 2, sets[key].get('kind', '')))
    tm = (M.t0 + M.t1) / 2 + (np.pi / 4)             # direction of the outer corner at mid-turn, in the assembly frame
    if M.sw: tm = (M.t0 + M.t1) / 2 + np.pi / 4
    up = np.array([np.cos(tm), np.sin(tm)])           # should point to the top of the sheet
    e1 = np.array([up[1], -up[0]]); e2 = up           # screen x, screen -y
    V = M.V.reshape(-1, 2); cen = (V.min(0) + V.max(0)) / 2
    # centre of the hull: bbox of the vertices in the (e1,e2) frame
    a = V @ e1; bq = V @ e2; ca, cb = (a.min() + a.max()) / 2, (bq.min() + bq.max()) / 2
    cx, cy = (b[0] + b[2]) / 2 * size, (b[1] + b[3]) / 2 * size - 0.03 * ph * size
    x0, x1, y0, y1 = [int(v * size) for v in (b[0], b[2], b[1], b[3])]
    x0 -= int(20 * S); x1 += int(20 * S); y0 -= int(12 * S); y1 += int(12 * S)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    A = (xx - cx) / PPW * M.w + ca; Bv = -(yy - cy) / PPW * M.w + cb       # assembly-frame coords along e1, e2
    gxw = A * e1[0] + Bv * e2[0]; gyw = A * e1[1] + Bv * e2[1]
    acc = np.zeros(gxw.shape, np.float32)
    for t in np.linspace(M.t0, M.t1, K):
        c, s = np.cos(t), np.sin(t)
        Xv = c * M.V[..., 0] + s * M.V[..., 1]; Yv = -s * M.V[..., 0] + c * M.V[..., 1]
        hx, hy = Xv.max(), Yv.max()
        P_ = c * gxw + s * gyw - hx + M.w; Q_ = -s * gxw + c * gyw - hy + M.w
        acc += ((P_ <= M.w) & (Q_ <= M.w) & ((P_ >= 0) | (Q_ >= 0)))
    acc /= K
    dose[y0:y1, x0:x1] = np.maximum(dose[y0:y1, x0:x1], acc)
    hull_area = float((acc > 0.9995).sum()) / PPW ** 2
    info[-1] = info[-1] + (hull_area,)
    # the crates
    im = Image.new('L', (size * 2, size * 2), 0); d = ImageDraw.Draw(im)
    for q in M.V:
        pts = [((cx + ((p @ e1) - ca) / M.w * PPW) * 2, (cy - ((p @ e2) - cb) / M.w * PPW) * 2) for p in q]
        d.polygon(pts, fill=255)
    obj = np.maximum(obj, np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255)
    print(key, 'area %.4f hull %.4f' % (M.area, hull_area), flush=True)
# penumbra: the mask stood a little off the paper
dose = ndi.gaussian_filter(dose, 1.1 * S)
# tone curve: a short flash with the walls removed (so the brushed coat shows), then the 360 timed exposures
sh.lay(obj, opacity=0.975, height=0.5, halo=0.10)
sh.dose = 0.115 + 0.30 * dose ** 1.5 + 0.60 * (dose > 0.999) * 1.0
sh.dose = ndi.gaussian_filter(sh.dose, 0.6 * S) * sh.T
sh.develop(k=3.0)
# ---- pencil -------------------------------------------------------------------------------------------
names = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven'}
for (n, area, kind, hull), b in zip(info, boxes):
    sh.text('%s  ·  crates %.4f  ·  room %.3f' % (names[n], area, hull), ((b[0] + b[2]) / 2, b[3] + 0.027), 13.0)
sh.text('The Room the Corner Leaves', (0.5, 0.893), 30)
sh.text('The crates lay on the paper while the corner was turned round them, the lamp lit for a 360th of the time at each of 360 moments.', (0.5, 0.927), 14.2)
sh.text('Darkest blue was never inside a wall: all the room there was on that journey.  White is what was actually carried.  Lane 1 wide; areas in square paces.', (0.5, 0.952), 13.4)
sh.text('a row of n:  lane (n+4)(\u221a2\u22121)/2,  crates 4n(3+2\u221a2)/(n+4)\u00b2, most at four  \u2014  until seven go in two storeys', (0.5, 0.977), 12.4, italic=False)
n_ = size; st = np.zeros((n_, n_), np.float32); x0, y0, w_ = int(0.912 * n_), int(0.876 * n_), int(0.030 * n_)
st[y0:y0 + w_, x0:x0 + w_] = 1; q = 3 * n_ // 1024; st[y0 + q:y0 + w_ - q, x0 + q:x0 + w_ - q] = 0
sh.stamp(st); sh.text('L', ((x0 + w_ / 2) / n_, (y0 + w_ / 2) / n_), 22, italic=False, layer='red')
sh.develop(k=3.0); sh.save(out)
