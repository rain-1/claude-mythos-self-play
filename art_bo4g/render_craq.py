"""render_craq.py — EVERY CRACK ENDS ON AN OLDER ONE: a dried film as a pastel mosaic.

Reads craq.c's output.  Cells = connected components of intact triangles at the end; each cell is tinted by
the strain at which it was born (the moment it was cut off from its parent, found by adding the bonds back in
reverse break order); the film is drawn in its DEFORMED position, so the gaps between cells are the real crack
openings (older cracks are wider).  Ink: the crack faces.  Coral: the very first crack.
    python3 render_craq.py cache/craq_320.bin <final_px>
"""
import sys, struct
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from pastel import *

path = sys.argv[1]
FINAL = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
SS = 2
Wp = Hp = FINAL * SS
rs = FINAL / 1024 * SS

with open(path, 'rb') as f:
    W, H, nbroken = struct.unpack('iii', f.read(12))
    eps_end = struct.unpack('d', f.read(8))[0]
    ux = np.frombuffer(f.read(8 * W * H), np.float64).reshape(H, W)
    uy = np.frombuffer(f.read(8 * W * H), np.float64).reshape(H, W)
    brk = np.frombuffer(f.read(4 * W * H * 3), np.int32).reshape(H, W, 3)
    brk_eps = np.frombuffer(f.read(8 * W * H * 3), np.float64).reshape(H, W, 3)
print('lattice', W, H, 'broken', nbroken, 'eps_end', eps_end)
I, J = np.mgrid[0:H, 0:W]
X0 = J + 0.5 * (I & 1); Y0 = I * np.sqrt(3) / 2
X = X0 + ux; Y = Y0 + uy

# triangles: for node (i,j): up-triangle (i,j),(i,j+1),(i+1,jl+1)  and down-triangle (i,j),(i+1,jl+1),(i+1,jl)
# bonds: b0 (i,j)-(i,j+1); b1 (i,j)-(i+1,jl); b2 (i,j)-(i+1,jl+1)
def nb(i, j, b):
    if b == 0: return i, j + 1
    jl = j - 1 + (i & 1)
    return i + 1, jl + (1 if b == 2 else 0)

tris = []   # (nodes(3), bonds(3) as flat bond ids)
bid = lambda i, j, b: (i * W + j) * 3 + b
for i in range(H - 1):
    for j in range(W):
        jl = j - 1 + (i & 1)
        # up triangle: (i,j),(i,j+1),(i+1,jl+1): bonds b0(i,j), b2(i,j), b1(i,j+1)
        if j + 1 < W and 0 <= jl + 1 < W:
            tris.append(((i, j), (i, j + 1), (i + 1, jl + 1), bid(i, j, 0), bid(i, j, 2), bid(i, j + 1, 1)))
        # down triangle: (i,j),(i+1,jl),(i+1,jl+1): bonds b1(i,j), b2(i,j), b0(i+1,jl)
        if 0 <= jl and jl + 1 < W:
            tris.append(((i, j), (i + 1, jl), (i + 1, jl + 1), bid(i, j, 1), bid(i, j, 2), bid(i + 1, jl, 0)))
print('triangles', len(tris))
brk_flat = brk.reshape(-1)
eps_flat = brk_eps.reshape(-1)
# ---- cells from a raster of the cracks (the graph itself keeps a few unstrained ligament bonds across
# every crack, so graph components would not separate the cells): draw every broken bond's dual segment
# (centroid to centroid) in the REST lattice at 4 px per unit, 1.3 units wide, and label the complement.
from collections import defaultdict
from scipy.ndimage import label as nd_label
bond_tris = defaultdict(list)
for k, t in enumerate(tris):
    for b in t[3:]:
        bond_tris[b].append(k)
ntri = len(tris)
q = 4
cent0 = np.array([((X0[t[0]] + X0[t[1]] + X0[t[2]]) / 3, (Y0[t[0]] + Y0[t[1]] + Y0[t[2]]) / 3) for t in tris])
RW, RH = int(W * q) + 8, int(H * np.sqrt(3) / 2 * q) + 8
rim = Image.new('L', (RW, RH), 0)
rd = ImageDraw.Draw(rim)
for b, ks in bond_tris.items():
    if brk_flat[b] < 0 or len(ks) < 2:
        continue
    rd.line([(cent0[ks[0], 0] * q + 4, cent0[ks[0], 1] * q + 4), (cent0[ks[1], 0] * q + 4, cent0[ks[1], 1] * q + 4)],
            fill=255, width=int(1.3 * q))
# the film's own rim closes the edge cells
rd.rectangle([X0.min() * q + 4, Y0.min() * q + 4, X0.max() * q + 4, Y0.max() * q + 4], outline=255, width=int(1.3 * q))
crack = np.asarray(rim) > 0
from scipy.ndimage import binary_closing
yy0, xx0 = np.mgrid[-6:7, -6:7]
disc = (yy0 ** 2 + xx0 ** 2) <= (1.5 * q) ** 2
crack = binary_closing(crack, structure=disc)      # seal the pinholes left by unbroken ligament bonds
lab, ncell = nd_label(~crack)
# drop the crumbs (fragments smaller than ~6 nodes) into the crack so their nodes join the nearest real cell
sizes = np.bincount(lab.ravel())
small = sizes < 6 * q * q * 0.87
small[0] = True
lab[small[lab]] = 0
lab, ncell = nd_label(lab > 0)
idx = distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
def cell_at(i, j, lab=lab, idx=idx):
    yy_ = int(Y0[i, j] * q + 4); xx_ = int(X0[i, j] * q + 4)
    yy_ = min(max(yy_, 0), RH - 1); xx_ = min(max(xx_, 0), RW - 1)
    l = lab[yy_, xx_]
    if l == 0:
        l = lab[idx[0][yy_, xx_], idx[1][yy_, xx_]]
    return l - 1
node_cell_arr = np.zeros((H, W), np.int64)
for i in range(H):
    for j in range(W):
        node_cell_arr[i, j] = cell_at(i, j)
cell_idx = np.array([node_cell_arr[t[0]] for t in tris])
print('cells', ncell)
# tint of a cell = the age of its walls: the mean strain at which the broken bonds touching its nodes broke
# (early cells have old walls; the last slivers are bounded by the youngest cracks)
NS = 16
cell_sum = np.zeros(ncell); cell_cnt = np.zeros(ncell)
for i in range(H):
    for j in range(W):
        for b in range(3):
            o = brk[i, j, b]
            if o < 0: continue
            ii, jj = nb(i, j, b)
            if not (0 <= ii < H and 0 <= jj < W): continue
            for c in (node_cell_arr[i, j], node_cell_arr[ii, jj]):
                cell_sum[c] += brk_eps[i, j, b]; cell_cnt[c] += 1
wall_eps = np.where(cell_cnt > 0, cell_sum / np.maximum(cell_cnt, 1), eps_end)
birth = np.clip(((wall_eps - wall_eps.min()) / max(wall_eps.max() - wall_eps.min(), 1e-9)) * (NS - 1), 0, NS - 1).astype(int)
print('wall age range', wall_eps.min(), wall_eps.max(), 'bins', np.bincount(birth, minlength=NS))
# ---- draw: each node's hexagon (the centroids of its six triangles), filled with its cell's pigment ---
# The two faces of a crack are the hexagons of the nodes on either side; they meet at the crack's midline
# when the crack is closed and separate by the real displacement when it has opened.
sheet = Sheet(Wp, Hp, seed=31)
margin = 0.06
sc = (1 - 2 * margin) * Wp / max(X.max() - X.min(), Y.max() - Y.min())
offx = margin * Wp - X.min() * sc + 0.5 * ((1 - 2 * margin) * Wp - (X.max() - X.min()) * sc)
offy = margin * Hp - Y.min() * sc + 0.5 * ((1 - 2 * margin) * Hp - (Y.max() - Y.min()) * sc)
PX = X * sc + offx; PY = Y * sc + offy
fam = ['lemon', 'apricot', 'blush', 'orchid', 'lavender', 'cornflower', 'aqua', 'mint']
rank = (birth + 0.5 * np.random.default_rng(1).random(ncell)) / NS
rng = np.random.default_rng(4)
h = rank * (len(fam) - 1)
i0 = np.floor(h).astype(int); i1 = np.minimum(i0 + 1, len(fam) - 1); fr = h - i0
dens_cell = 0.6 + 0.35 * rng.random(ncell)
# triangle centroids and, per node, the list of its triangles in angular order
cent = np.array([((PX[t[0]] + PX[t[1]] + PX[t[2]]) / 3, (PY[t[0]] + PY[t[1]] + PY[t[2]]) / 3) for t in tris])
node_tris = defaultdict(list)
for k, t in enumerate(tris):
    for nd in t[:3]:
        node_tris[nd].append(k)
# node's cell: majority over its intact triangles
layers = {name: Image.new('F', (Wp, Hp), 0.0) for name in fam}
draws = {name: ImageDraw.Draw(layers[name]) for name in fam}
node_cell = {}
for nd, ks in node_tris.items():
    if len(ks) < 3:
        continue
    c = node_cell_arr[nd]
    node_cell[nd] = c
    # order the centroids by angle around the node
    px, py = PX[nd], PY[nd]
    ang = np.arctan2(cent[ks, 1] - py, cent[ks, 0] - px)
    order_ = np.argsort(ang)
    poly = [(cent[ks[o], 0], cent[ks[o], 1]) for o in order_]
    # only keep the part of the hexagon on this node's side: triangles whose cell differs are still drawn
    # (their centroid is the crack's midline), which is what makes the faces meet when closed
    w0, w1 = (1 - fr[c]) * dens_cell[c], fr[c] * dens_cell[c]
    if w0 > 0: draws[fam[i0[c]]].polygon(poly, fill=float(w0))
    if w1 > 0: draws[fam[i1[c]]].polygon(poly, fill=float(w1))
for name in fam:
    a = np.asarray(layers[name], np.float32)
    if a.max() > 0:
        sheet.wash(a, name, granulate=0.10, edge=0.30, seed=5)
# crack lines in ink: the dual edge of every broken bond (centroid to centroid across the bond)
first = []
ink = np.zeros((Hp, Wp), np.float32)
ages = {}
for b, ks in bond_tris.items():
    if brk_flat[b] < 0 or len(ks) < 2:
        continue
    seg = (cent[ks[0], 0], cent[ks[0], 1], cent[ks[1], 0], cent[ks[1], 1])
    age = (eps_end - eps_flat[b]) / eps_end          # 1 = the oldest crack
    band = min(3, int(age * 4))
    ages.setdefault(band, []).append(seg)
    if brk_flat[b] < nbroken * 0.02:
        first.append(seg)
for band, segs in ages.items():
    wdt = (0.9 + 0.9 * band) * rs
    ink += draw_lines_density(Wp, Hp, segs, max(1.0, wdt), sigma=0.6 * rs)
if first:
    co = draw_lines_density(Wp, Hp, first, max(1.0, 3.5 * rs), sigma=0.9 * rs)
    ink = ink * (1 - 0.85 * np.clip(co, 0, 1))
    sheet.wash(np.clip(co, 0, 1) * 1.4, 'coral')
sheet.wash(np.clip(ink, 0, 1) * 0.8, 'ink')
sheet.caption_strip(0.90, 0.985, f=0.55)
title = 'Every Crack Ends on an Older One'
sub = ('A drying film on an elastic bed, %d cells: each new crack runs until it meets an earlier one, and meets it '
       'at a right angle; the tint is the strain at which each cell was born, the coral is the first crack.' % ncell)
size_t = int(44 * rs); size_s = int(23 * rs)
items = [(title, Wp / 2, Hp * 0.925, size_t, 'serif_bold', 'mm')]
for i, ln in enumerate(wrap(sub, size_s, 'italic', 0.84 * Wp)):
    items.append((ln, Wp / 2, Hp * (0.953 + 0.025 * i), size_s, 'italic', 'mm'))
sheet.wash(text_density(Wp, Hp, items), 'ink')
img = sheet.develop()
finish(img, (FINAL, FINAL), 'cache/craq_%s_%d.png' % (path.split('/')[-1].replace('.bin', ''), FINAL))
