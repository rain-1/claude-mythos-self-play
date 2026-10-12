"""EVERY PEBBLE LOSES THE SAME — MO 515905.  One lattice, nine copies of one ellipse at nine
orientations; each pebble's lattice hull cut as a gem (min of facet planes), facet hue = edge
direction, coral slivers = what the hull loses to the true ellipse."""
import numpy as np, sys
from PIL import Image, ImageFilter
from hull import ellipse_pts, hull
from render_doors import wheel, PAPER

def render(S=3200, out='gems_raw.png', ss=2, Rl=9.3, a=1.0, b=0.5, seed=7, cap_frac=0.42):
    G = S*ss; sp = 41.0*ss*S/3200                       # lattice spacing in px
    rng = np.random.default_rng(seed)
    img = np.ones((G, G, 3))*PAPER
    yy, xx = np.mgrid[0:G, 0:G].astype(np.float32) + 0.5
    # lattice dots
    ox, oy = 0.37*sp, 0.61*sp
    fx = ((xx - ox)/sp) % 1; fy = ((yy - oy)/sp) % 1
    dd = np.hypot(np.minimum(fx, 1 - fx), np.minimum(fy, 1 - fy))*sp
    dot = np.clip(2.2*ss*S/3200 - dd + 0.5, 0, 1)
    img = img*(1 - 0.32*dot[..., None]) + 0.32*dot[..., None]*np.array([0.55, 0.50, 0.66])
    thetas = np.deg2rad(np.arange(9)*10.0)               # 0°,10°,…,80°
    cell = G/3
    shadow = np.zeros((G, G), np.float32); layers = []
    for i, th in enumerate(thetas):
        cxp = cell*(i % 3 + 0.5) + rng.uniform(-0.03, 0.03)*cell
        cyp = cell*(i//3 + 0.47) + rng.uniform(-0.03, 0.03)*cell
        # lattice coordinates of the pebble centre -> translation t
        lx, ly = (cxp - ox)/sp, (cyp - oy)/sp            # lattice points at integer (lx,ly)
        t = np.array([-(lx % 1), -(ly % 1)])              # lattice points relative to centre: Z^2 + t
        # y axis flips: work in a frame with y up
        P = ellipse_pts(a, b, th, Rl, (t[0] % 1, (-(ly % 1)) % 1))
        # reconstruct pts in px: points p (x right, y up) relative to centre
        P = ellipse_pts(a, b, th, Rl, (t[0] % 1, (ly % 1) % 1))
        H = hull(P)
        layers.append((cxp, cyp, th, H, P))
    full_img = img; full_sh = shadow
    for (cxp, cyp, th, H, P) in layers:
        rad = int(Rl*a*sp*1.15) + 8
        y0, y1, x0, x1 = int(cyp) - rad, int(cyp) + rad, int(cxp) - rad, int(cxp) + rad
        img = full_img[y0:y1, x0:x1]; shadow = full_sh[y0:y1, x0:x1]
        xx_, yy_ = xx[y0:y1, x0:x1], yy[y0:y1, x0:x1]
        X = (xx_ - cxp)/sp; Y = -(yy_ - cyp)/sp             # lattice units, y up
        # ellipse inside / distance
        c, s = np.cos(th), np.sin(th)
        u = (X*c + Y*s)/(Rl*a); v = (-X*s + Y*c)/(Rl*b)
        q = np.sqrt(u*u + v*v)
        gq = np.sqrt((c*u/(Rl*a) - s*v/(Rl*b))**2 + (s*u/(Rl*a) + c*v/(Rl*b))**2)/np.maximum(q, 1e-6)
        de = (q - 1)/np.maximum(gq, 1e-9)*sp              # signed px distance to the ellipse
        # facet planes
        n = len(H); E = np.roll(H, -1, 0) - H
        L = np.hypot(E[:, 0], E[:, 1]); N = np.stack([E[:, 1], -E[:, 0]], 1)/L[:, None]   # outward (ccw hull)
        if np.mean(N[:, 0]*H[:, 0] + N[:, 1]*H[:, 1]) < 0: N = -N
        dist = np.full(X.shape, np.inf, np.float32); idx = np.zeros(X.shape, np.int16)
        for k in range(n):
            d = (H[k, 0] - X)*N[k, 0] + (H[k, 1] - Y)*N[k, 1]
            m = d < dist; dist[m] = d[m]; idx[m] = k
        inside = dist > 0
        dpx = dist*sp
        cap = cap_frac*Rl*b*sp                            # table starts at this depth
        tab = dpx > cap
        # facet normals: slope toward edge; crown angle
        slope = 0.75
        nx = np.where(tab, 0, N[idx, 0]*slope); ny = np.where(tab, 0, N[idx, 1]*slope)
        nz = np.ones_like(nx); nn = np.sqrt(nx**2 + ny**2 + nz**2)
        Ld = np.array([-0.45, 0.55, 0.70]); Ld /= np.linalg.norm(Ld)
        lam = (nx*Ld[0] + ny*Ld[1] + nz*Ld[2])/nn
        Hv = Ld + np.array([0, 0, 1.0]); Hv /= np.linalg.norm(Hv)
        spec = np.clip((nx*Hv[0] + ny*Hv[1] + nz*Hv[2])/nn, 0, 1)**80
        ang = np.arctan2(N[idx, 1], N[idx, 0])
        hue = (ang/(2*np.pi)) % 1.0
        base = wheel(hue)
        par = (idx % 2).astype(np.float32)
        base = base*(1 - 0.06*par)[..., None] + 0.06*par[..., None]
        tabc = (0.80*np.array([1.0, 0.995, 1.0]) + 0.20*wheel(hue))*(1 - 0.035*par)[..., None] + 0.035*par[..., None]*0.9
        col = np.where(tab[..., None], tabc, base)
        col = col*((0.90 + 0.18*lam)*np.where(tab, 1.0, 0.95 + 0.08*np.clip(dpx/cap, 0, 1)))[..., None] + 0.55*spec[..., None]
        # facet seams: thin white lines where idx changes or at the table edge
        seam = np.zeros(X.shape, bool)
        seam[1:] |= idx[1:] != idx[:-1]; seam[:, 1:] |= idx[:, 1:] != idx[:, :-1]
        seam = seam & ~tab | (seam & tab)
        tedge = np.abs(dpx - cap) < 0.9*ss
        wire = (seam | tedge) & inside
        col = np.where(wire[..., None], col*np.where(tab, 0.8, 0.55)[..., None] + np.where(tab, 0.2, 0.45)[..., None], col)
        cov = np.clip(dpx/1.0 + 0.5, 0, 1)
        img = img*(1 - cov[..., None]) + cov[..., None]*col
        # coral slivers between hull and ellipse
        sl = np.clip(-de + 0.5, 0, 1)*(1 - cov)
        img = img*(1 - 0.85*sl[..., None]) + 0.85*sl[..., None]*np.array([0.98, 0.56, 0.52])
        # ellipse outline (plum hairline)
        ring = np.clip(0.9*ss - np.abs(de) + 0.5, 0, 1)
        img = img*(1 - 0.6*ring[..., None]) + 0.6*ring[..., None]*np.array([0.40, 0.33, 0.47])
        # hull vertices as white pearls
        for (hx, hy) in H:
            px, py = cxp + hx*sp, cyp - hy*sp
            r = 7.0*ss*S/3200
            ya, yb, xa, xb = int(py - 3*r), int(py + 3*r) + 1, int(px - 3*r), int(px + 3*r) + 1
            dd = np.hypot(xx_[ya-y0:yb-y0, xa-x0:xb-x0] - px, yy_[ya-y0:yb-y0, xa-x0:xb-x0] - py)
            pb = np.clip(r - dd + 0.5, 0, 1)
            img[ya-y0:yb-y0, xa-x0:xb-x0] = img[ya-y0:yb-y0, xa-x0:xb-x0]*(1 - pb[..., None]) + pb[..., None]*np.array([1.0, 0.99, 0.97])
        full_img[y0:y1, x0:x1] = img
        full_sh[y0:y1, x0:x1] = np.maximum(shadow, (q < 1).astype(np.float32))
    img = full_img; shadow = full_sh
    m = Image.fromarray((shadow*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(G*0.006))
    sh = np.roll(np.roll(np.asarray(m, np.float32)/255, int(G*0.005), 0), int(G*0.003), 1)*(1 - shadow)
    img = img*(1 - 0.18*sh[..., None]) + 0.18*sh[..., None]*np.array([0.78, 0.76, 0.92])
    im = Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8))
    if ss > 1: im = im.resize((S, S), Image.LANCZOS)
    im.save(out); return [len(l[3]) for l in layers]

if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    print(render(S, f'gems_raw_{S}.png', ss=2))
