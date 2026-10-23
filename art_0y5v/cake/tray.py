# The tray: nine petits fours, each cut fairly into three. Colour = congruence class.
import numpy as np, json, sys, time
sys.path.insert(0, '../math_fair')
from PIL import Image
from shapes import all_shapes
from petit import render
from cake import look, tonemap
from build_petit import shape_row, piece_rows
W = int(sys.argv[1]); out = sys.argv[2]; spp = int(sys.argv[3]) if len(sys.argv) > 3 else 1
lin = lambda c: (np.array(c, float)/255.)**2.2
D = json.load(open('../math_fair/partitions.json'))
SH = {s.name: s for s in all_shapes()}
names = ['triangle', 'square', 'pentagon',
         'ellipse_b0.8', 'disc', 'hexagon',
         'halfdisc', 'reuleaux', 'rect_1.5']
k = 0.315; Hc = 0.24; sp = 0.98
# fondant box: three per cake, rotating through the sorbet colours; twins share
FON = lin([[246, 168, 190], [255, 196, 160], [255, 226, 140], [176, 226, 186], [160, 210, 240],
           [196, 180, 246], [240, 176, 226], [255, 178, 168], [168, 228, 214], [255, 150, 138]])
S = np.zeros((9, 64)); PCS = np.zeros((9, 3, 12))
def sol_for(n):
    d = D[n]
    if n == 'halfdisc':
        return [c for c in d['chord_solutions'] if c['pairwise_noncongruent']][0]
    return d['best_noncongruent_Y']
for i, n in enumerate(names):
    sh = SH[n]; sol = sol_for(n)
    gx, gy = (i % 3 - 1) * sp, (1 - i // 3) * sp * 0.92
    # centroid of the shape (from its dense boundary)
    B = np.array(D[n]['boundary']); x, y = B[:, 0], B[:, 1]
    cr = x*np.roll(y, -1) - np.roll(x, -1)*y; A = cr.sum()/2
    cen = np.array([((x + np.roll(x, -1))*cr).sum(), ((y + np.roll(y, -1))*cr).sum()])/(6*A)
    if n.startswith('ellipse'):
        S[i] = shape_row('ellipse', None, gx, gy, Hc, ab=(sh.a*k, sh.b*k))
        inside = lambda p, a=sh.a*k, b=sh.b*k: np.hypot(p[0]/a, p[1]/b) - 1
    else:
        prims = []
        for e in sh.elems:
            if e['kind'] == 'seg':
                P = (e['P'] - cen)*k; u = e['u']; nrm = np.array([u[1], -u[0]])
                prims.append([0, nrm[0], nrm[1], nrm @ P])
            else:
                C = (e['C'] - cen)*k; prims.append([1, C[0], C[1], e['R']*k])
        # dedupe identical discs (the disc is one arc)
        uniq = []
        for p in prims:
            if not any(np.allclose(p, q) for q in uniq): uniq.append(p)
        S[i] = shape_row('prims', uniq, gx, gy, Hc)
        def inside(p, uniq=uniq):
            v = -1e9
            for t, a, b, c in uniq:
                v = max(v, a*p[0] + b*p[1] - c if t == 0 else np.hypot(p[0]-a, p[1]-b) - c)
            return v
    pieces = [(np.array(p) - cen)*k for p in sol['pieces']]
    cp = [tuple(sorted(q)) for q in sol['congruent_pairs']]
    base = (i*3) % 9
    cols = [base, (base+1) % 9, (base+2) % 9]
    for a, b in cp:
        cols[b] = cols[a]
    if n == 'disc':
        cols = [0, 0, 0]
        a, b = cp[0]; cols[a] = cols[b] = 0
        odd = [j for j in range(3) if j not in cp[0]][0]; cols[odd] = 5
        cols[a] = cols[b] = 9
    PCS[i] = piece_rows(pieces, inside, 0.05, cols, 0.022)
    print(n, 'pairs', cp, 'cols', cols, 'cuts', [int((r[3:5] != 0).any()) + 1 for r in PCS[i]])
T = np.array([1.55, 1.42, *lin([228, 238, 252]), *lin([252, 236, 240])])
LC = lin([[255, 238, 210], [255, 226, 232], [240, 232, 255]])
L = np.array([-0.5, -0.45, 0.74]); L /= np.linalg.norm(L)
cam = look([0, -3.9, 3.8], [0, -0.32, -0.05], 40)
t = time.time(); img = render(W, W, cam, S, PCS, T, FON, LC, L, spp, 5); print('render', time.time() - t)
np.save(out.replace('.png', '.npy'), img.astype(np.float32))
Image.fromarray(tonemap(img, 0.85)).save(out)
