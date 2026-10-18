"""Quilled optimal posets n=1..11: elements = tight coils, covers = strips on edge."""
import numpy as np, json, sys, time, itertools
from PIL import Image
from scipy import ndimage as ndi
import quill as Q, mandala as M, tiles as T, sampler as SM

def components(n, cov):
    par = list(range(n))
    def f(a):
        while par[a] != a: a = par[a]
        return a
    for a, b in cov: par[f(a)] = f(b)
    comps = {}
    for v in range(n): comps.setdefault(f(v), []).append(v)
    return list(comps.values())

def layout(comp, cov, rng):
    cs = [(a, b) for a, b in cov if a in comp]
    if not cs:
        return {comp[0]: (0.0, 0.5)}
    lo = sorted({a for a, b in cs} | {v for v in comp if all(v != b for _, b in cs) and all(v != a for a, _ in cs)})
    up = sorted({b for a, b in cs})
    lo = [v for v in comp if v not in up]
    best = None
    for perm_lo in (itertools.permutations(lo) if len(lo) <= 6 else [rng.permutation(lo) for _ in range(500)]):
        xl = {v: i for i, v in enumerate(perm_lo)}
        # top elements at barycentres, then ordered and spaced
        bc = sorted(up, key=lambda u: np.mean([xl[a] for a, b in cs if b == u]))
        for perm_up in [bc]:
            xu = {}
            for i, u in enumerate(perm_up):
                xu[u] = np.mean([xl[a] for a, b in cs if b == u])
            # spread top to min spacing 1 preserving order
            vals = [xu[u] for u in perm_up]
            for it in range(50):
                for i in range(1, len(vals)):
                    if vals[i] - vals[i-1] < 1.0:
                        d = (1.0 - (vals[i]-vals[i-1]))/2; vals[i-1] -= d; vals[i] += d
            xu = dict(zip(perm_up, vals))
            cr = 0
            for (a, b), (c, d) in itertools.combinations(cs, 2):
                if (xl[a]-xl[c])*(xu[b]-xu[d]) < 0: cr += 1
            L = sum(abs(xl[a]-xu[b]) for a, b in cs)
            sc = cr*10 + L
            if best is None or sc < best[0]: best = (sc, dict(xl), dict(xu))
    _, xl, xu = best
    pos = {v: (float(x), 1.0) for v, x in xl.items()}
    pos.update({v: (float(x), 0.0) for v, x in xu.items()})
    m = min(p[0] for p in pos.values())
    return {v: (p[0]-m, p[1]) for v, p in pos.items()}

def is_fence(comp, cov):
    cs = [(a, b) for a, b in cov if a in comp]
    deg = {v: 0 for v in comp}
    for a, b in cs: deg[a] += 1; deg[b] += 1
    return all(d <= 2 for d in deg.values())

COOLS = [(0.62,0.84,1.0),(0.64,0.92,0.80),(0.76,0.74,1.0),(0.86,0.72,0.98),(0.60,0.90,0.92),(0.78,0.92,0.64)]
FENCE_COL = {1: (1.0,0.88,0.58), 2: (0.70,0.90,0.74), 4: (0.62,0.84,1.0), 6: (0.78,0.74,1.0), 8: (0.90,0.72,0.98)}
WARM = (1.0, 0.64, 0.62)

def build(opt, k=2, Wout=3200, Hout=3200, tilt=26, seed=0):
    rng = np.random.default_rng(seed)
    cs_ = np.cos(np.radians(tilt))
    W = Wout*k; Hh = int(Hout*k/cs_)
    H, A = T.card((Hh, W), seed)
    yy = np.linspace(0, 1, Hh)[:, None, None]
    A[:] = (np.array((0.86,0.88,0.99))*(1-yy)+np.array((0.99,0.87,0.90))*yy).astype(np.float32)
    G = np.zeros((Hh, W), np.float32)
    plate = np.zeros((Hh, W), np.float32)
    rows = [[1,2,3,4],[5,6,7],[8,9],[10,11]]
    u = 0.057*W          # horizontal unit between elements
    vh = 0.075*W/cs_     # vertical distance between levels (world, stretched)
    rc = 0.019*W         # coil radius
    ks = k*Wout/1200; hgt = 22*ks; sw = 2.1*ks
    pad = 0.026*W; cgap = 0.85*u
    labels = []
    row_h = vh + 2*rc/cs_ + 2*pad/cs_
    gap_y = 0.04*W/cs_
    top0 = 0.035*W/cs_
    for ri, row in enumerate(rows):
        cards = []
        for n in row:
            P = opt[str(n)]['posets'][0]
            cov = [tuple(c) for c in P['covers']]
            comps = components(n, cov)
            comps.sort(key=lambda c: (-len(c), c))
            lays = [layout(c, cov, rng) for c in comps]
            widths = [max(p[0] for p in l.values()) for l in lays]
            wtot = sum(widths) + cgap/u*(len(comps)-1)
            cards.append((n, P, cov, comps, lays, widths, wtot))
        cw = [c[6]*u + 2*pad + 2*rc for c in cards]
        gx = 0.035*W
        total = sum(cw) + gx*(len(cards)-1)
        x = (W - total)/2
        oy = top0 + ri*(row_h + gap_y)
        for (n, P, cov, comps, lays, widths, wtot), w in zip(cards, cw):
            m = SM.rounded_rect(plate.shape, x, oy, x+w, oy+row_h, 12*ks)
            plate = np.maximum(plate, m)
            A[:] = A*(1-m[..., None]) + np.array([0.992,0.99,0.985],np.float32)*m[..., None]
            labels.append((n, P, x+w/2, oy+row_h))
            cx = x + pad + rc
            for comp, lay, wd in zip(comps, lays, widths):
                fence = is_fence(comp, cov)
                sz = len(comp)
                col = FENCE_COL.get(sz, COOLS[sz % 6]) if fence else WARM
                pos = {v: (cx + p[0]*u, oy + pad/cs_ + rc/cs_ + p[1]*vh) for v, p in lay.items()}
                for a, b in cov:
                    if a in comp:
                        pa, pb = np.array(pos[a]), np.array(pos[b])
                        d = pb-pa; d /= np.linalg.norm(d)
                        M.stem(H, A, np.array([pa+d*rc*0.9, pb-d*rc*0.9]), sw*1.1, hgt*0.95, tuple(np.array(col)**1.5))
                for v, p in pos.items():
                    # tight coil, stretched vertically so it reads round after the tilt
                    t = np.linspace(0, 2*np.pi, 120, endpoint=False)
                    poly = np.c_[p[0]+rc*np.cos(t), p[1]+rc/cs_*np.sin(t)]
                    M.coil_shape(H, A, poly, pitch=sw*1.9, sw=sw, hgt=hgt*1.1, col=col, wall=sw*1.5, pole=p, G=G, gild=True)
                cx += wd*u + cgap
            x += w + gx
    H += plate*3.5*ks
    return H, A, G, labels, cs_

if __name__ == '__main__':
    Wout = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    opt = json.load(open('../math_poset/optimal.json'))
    t = time.time()
    H, A, G, labels, cs_ = build(opt, Wout=Wout, Hout=Wout)
    print('build', time.time()-t)
    img = Q.render(H, A, tilt_deg=26, spp=4, out_w=Wout, light=(-0.65,0.30,0.70), amb=(0.62,0.62,0.70),
                   sun=(0.75,0.72,0.68), G=G)
    Image.fromarray(Q.tonemap(img)).save(f'proto/posets_{Wout}.png')
    json.dump([(n, P['desc'], P['e'], P['aut'], x/2, y/2*cs_) for n, P, x, y in labels], open(f'proto/posets_labels_{Wout}.json','w'))
