import numpy as np, sys, time, json
from PIL import Image
from scipy import ndimage as ndi
import quill as Q, mandala as M, tiles as T

def teardrop(L, Wd, m=1.3, n=240):
    t = np.linspace(0, 2*np.pi, n, endpoint=False)
    x = np.cos(t); y = np.sin(t)*np.abs(np.sin(t/2))**m
    # tip at x=+1 -> put tip at origin, round end at -L
    return np.c_[(x-1)/2*L, y*Wd/2]

def build(tsv, k=2, Wout=1600, seed=0, gens=3, pmax=10**6, stretch=1.0):
    rec = M.load(tsv)
    leaves, anc, main = M.ancestry(rec, gens, pmax)
    W = Wout*k; Hh = W
    H, A = T.card((Hh, W), seed)
    yy = np.linspace(0, 1, Hh)[:, None, None]
    A[:] = (np.array((0.88,0.90,0.99))*(1-yy)+np.array((0.99,0.89,0.90))*yy).astype(np.float32)
    G = np.zeros((Hh, W), np.float32)
    cx, cy = W/2, Hh/2
    R = 0.43*W
    # round white card
    yy2, xx2 = np.mgrid[0:Hh, 0:W]
    rr = np.sqrt((xx2+.5-cx)**2+((yy2+.5-cy))**2)
    card = np.clip(R*1.04+0.5-rr, 0, 1).astype(np.float32)
    A[:] = A*(1-card[...,None]) + np.array([0.992,0.99,0.985],np.float32)*card[...,None]
    del yy2, xx2
    # angular layout: leaves grouped by main parent (gen 2), groups ordered by their gen-1 parent
    kids = {}
    for p in anc:
        if p in main: kids.setdefault(main[p], []).append(p)
    def gen(p): return rec[p][1]
    def nleaves(p):
        return 1 if gen(p) == gens else sum(nleaves(c) for c in kids.get(p, []))
    roots = sorted([p for p in anc if gen(p) == 0], key=lambda p: -nleaves(p))
    ang = {}
    order = []
    def walk(p):
        cs = sorted(kids.get(p, []), key=lambda c: (gen(c), c))
        if gen(p) == gens: order.append(p); return
        for c in cs:
            if gen(c) == gen(p)+1 or gen(c) > gen(p): walk(c)
    for r in roots: walk(r)
    nl = len(order)
    for i, p in enumerate(order): ang[p] = 2*np.pi*(i+0.5)/nl - np.pi/2
    def mean_ang(p):
        if p in ang: return ang[p]
        a = [mean_ang(c) for c in kids.get(p, []) if gen(c) > gen(p)]
        if not a:
            return None
        v = np.mean(np.exp(1j*np.array(a)))
        ang[p] = np.angle(v); return ang[p]
    for r in roots: mean_ang(r)
    orphans = [p for p in anc if p not in ang]
    for g_ in sorted(set(gen(p) for p in orphans)):
        taken = [ang[p] for p in anc if p in ang and gen(p) == g_]
        for j, p in enumerate(sorted(o for o in orphans if gen(o) == g_)):
            # largest angular gap among this ring
            ts = np.sort(np.mod(np.array(taken), 2*np.pi)) if taken else np.array([0.0])
            gaps = np.diff(np.r_[ts, ts[0]+2*np.pi])
            i = np.argmax(gaps); ang[p] = ts[i] + gaps[i]/2; taken.append(ang[p])
    print('orphans', orphans)
    # spread each inner ring to a minimum angular separation (order preserved, circular)
    def spread(nodes, sep, iters=400):
        if len(nodes) < 2: return
        nodes = sorted(nodes, key=lambda p: ang[p] % (2*np.pi))
        a = np.array([ang[p] % (2*np.pi) for p in nodes])
        sep = min(sep, 2*np.pi/len(nodes)*0.98)
        for _ in range(iters):
            d = np.diff(np.r_[a, a[0]+2*np.pi])
            bad = d < sep
            if not bad.any(): break
            for i in np.nonzero(bad)[0]:
                j = (i+1) % len(a); push = (sep-d[i])/2*0.5
                a[i] -= push; a[j] += push
        for p, v in zip(nodes, a): ang[p] = v
    rad = {0: 0.075*R, 1: 0.215*R, 2: 0.40*R, 3: 0.56*R}
    for g_, sep_px in ((2, 0.115*R), (1, 0.115*R), (0, 0.2*R)):
        nodes = [p for p in anc if gen(p) == g_]
        spread(nodes, sep_px/rad[g_])
    ks = k*Wout/1200; hgt = 22*ks; sw = 2.1*ks
    # palette: hue walk around the wheel by gen-2 group
    WHEEL = [(1.0,0.62,0.62),(1.0,0.74,0.56),(1.0,0.86,0.52),(0.80,0.92,0.60),(0.62,0.90,0.78),
             (0.60,0.84,1.0),(0.72,0.74,1.0),(0.86,0.70,0.98),(1.0,0.68,0.86)]
    g2 = sorted([p for p in anc if gen(p) == 2], key=lambda p: (ang[p] + np.pi/2) % (2*np.pi))
    gcol = {p: WHEEL[i % len(WHEEL)] for i, p in enumerate(g2)}
    def colof(p):
        if gen(p) == 3: return gcol[main[p]]
        if gen(p) == 2: return gcol[p]
        if gen(p) == 1: return (1.0, 0.93, 0.80)
        return (1.0, 0.82, 0.50)
    pos = {p: (cx+rad[gen(p)]*np.cos(ang[p]), cy+rad[gen(p)]*np.sin(ang[p])) for p in anc}
    # stems first (lower), then coils
    for p in anc:
        if p not in main: continue
        q = main[p]
        a0, a1 = ang[q], ang[p]
        r0 = rad[gen(q)] + (0.035*R if gen(q) < 2 else 0.07*R)
        r1 = rad[gen(p)] - (0.03*R if gen(p) < 3 else 0.0)
        p0 = np.array([cx+r0*np.cos(a0), cy+r0*np.sin(a0)])
        p2 = np.array([cx+r1*np.cos(a1), cy+r1*np.sin(a1)])
        rm = (r0+r1)/2
        p1 = np.array([cx+rm*np.cos(a1), cy+rm*np.sin(a1)])
        M.stem(H, A, M.bezier(p0, p1, p2), sw, hgt*0.9, tuple(np.array(colof(p))**1.4))
    # leaves: teardrops, tip inward
    L = 0.37*R; Wd = 2*np.pi*(rad[3]+0.8*L)/nl*0.93
    lr = np.array([np.log(rec[p][0])/np.log(p) for p in order])
    lrn = (lr-lr.min())/(lr.max()-lr.min()+1e-9)
    print('log s/log p range', lr.min(), lr.max())
    for i, p in enumerate(order):
        a = ang[p]
        L = (0.31+0.10*lrn[i])*R
        tip = np.array([cx+rad[3]*np.cos(a), cy+rad[3]*np.sin(a)])
        poly = M.place(teardrop(L, Wd/0.77), tip[0], tip[1], a+np.pi)
        pole = tip + (L*0.70)*np.array([np.cos(a), np.sin(a)])
        M.coil_shape(H, A, poly, pitch=4.2*ks, sw=sw*0.9, hgt=hgt, col=colof(p), pole=pole, G=G, gild=False)
    # gen-2: eyes (marquise), gen-1: larger tight coils, gen-0: gilded tight coils
    for p in anc:
        g = gen(p)
        if g == 2:
            a = ang[p]; c = np.array(pos[p])
            poly = M.place(np.c_[np.cos(np.linspace(0,2*np.pi,200,endpoint=False))*0.075*R,
                                 np.sin(np.linspace(0,2*np.pi,200,endpoint=False))**1*0.042*R*np.abs(np.sin(np.linspace(0,2*np.pi,200,endpoint=False)))**0.3], c[0], c[1], a)
            M.coil_shape(H, A, poly, pitch=4.4*ks, sw=sw, hgt=hgt*1.05, col=colof(p), pole=tuple(c), G=G, gild=True)
        elif g == 1:
            M.tight_coil(H, A, pos[p][0], pos[p][1], 0.04*R, sw, hgt*1.1, colof(p), G=G)
        elif g == 0:
            M.tight_coil(H, A, pos[p][0], pos[p][1], 0.048*R, sw, hgt*1.15, colof(p), G=G)
    # outer ring frame
    t = np.linspace(0, 2*np.pi, 721)
    ring = np.c_[cx+R*0.99*np.cos(t), cy+R*0.99*np.sin(t)]
    Q.stroke(H, A, np.hstack([ring[:-1], ring[1:]]), sw*1.6, hgt*1.05, (0.97,0.94,0.88))
    H += card*3.5*ks
    if stretch != 1.0:
        H = ndi.zoom(H, (stretch, 1), order=1); G = ndi.zoom(G, (stretch, 1), order=1)
        A = np.stack([ndi.zoom(A[..., c], (stretch, 1), order=1) for c in range(3)], -1)
    return H, A, G, dict(leaves=order, anc=sorted(anc), main=main, rec={p: rec[p] for p in anc}, ang={p: float(ang[p]) for p in anc})

if __name__ == '__main__':
    Wout = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    k = 2
    t = time.time()
    tilt = 24
    H, A, G, info = build('../math_digits/cap_12357_L11.tsv', k=k, Wout=Wout, stretch=1/np.cos(np.radians(tilt)))
    print('build', time.time()-t); t = time.time()
    img = Q.render(H, A, tilt_deg=tilt, spp=4, out_w=Wout, light=(-0.65,0.30,0.70), amb=(0.62,0.62,0.70),
                   sun=(0.75,0.72,0.68), G=G)
    print('render', time.time()-t)
    Image.fromarray(Q.tonemap(img)).save(f'proto/mandala_{Wout}.png')
