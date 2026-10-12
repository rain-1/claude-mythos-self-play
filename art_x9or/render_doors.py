"""THE THREE DOORS — a Riemann map built only from Brownian exit probabilities (MO 515949),
carrying the Farey / (2,3,∞) tessellation of the disc into a domain, as cloisonné enamel."""
import numpy as np, sys, argparse
from PIL import Image, ImageFilter
from conformal import solve_map, eval_F, disc_mobius, tiles

SHAPES = {
 'flower5': lambda s: 1 + 0.22*np.cos(5*s),
 'flower6': lambda s: 1 + 0.16*np.cos(6*s) + 0.05*np.cos(12*s),
 'cloud':   lambda s: 1 + 0.10*np.cos(2*s+0.4) + 0.09*np.cos(5*s+1) + 0.05*np.sin(7*s),
 'star5':   lambda s: 1 + 0.30*np.cos(5*s),
 'bean':    lambda s: 1 + 0.25*np.cos(2*s) + 0.12*np.cos(3*s+0.5),
 'clover':  lambda s: 1 + 0.28*np.cos(3*s) + 0.04*np.cos(6*s),
}
WHEEL = np.array([[246,150,170],[250,180,150],[252,220,140],[200,232,150],[150,224,200],
                  [150,204,240],[168,176,242],[204,164,236],[240,158,212]], float)/255.
def wheel(h):
    h = (h % 1.0)*len(WHEEL); i = np.floor(h).astype(int); fr = (h - i)[..., None]
    a = WHEEL[i % len(WHEEL)]; b = WHEEL[(i+1) % len(WHEEL)]
    return np.exp(np.log(a)*(1-fr) + np.log(b)*fr)
PAPER = np.array([0.992, 0.985, 0.975])
C3 = -2.0*np.exp(2j*np.pi*np.arange(3)/3)

def setup(shape, doors_deg):
    rf = SHAPES[shape] if isinstance(shape, str) else shape
    sol = solve_map(rf, 2048)
    sd = np.deg2rad(np.array(doors_deg, float)); zd = rf(sd)*np.exp(1j*sd)
    fd = (zd - sol['a'])*np.exp(-eval_F(sol, zd)); fd /= np.abs(fd)
    mob = disc_mobius(fd)
    return rf, sol, zd, mob

def wmap(sol, mob, z):
    return mob((z - sol['a'])*np.exp(-eval_F(sol, z)))

def strip(rf, sol, zd, mob, G, ext, y0, y1, ss, S, hoff, satg, cx=0.0, cy=0.0):
    """rows y0..y1 of the supersampled grid (with a 2-row halo), returns rgb rows + inside mask"""
    ya, yb = max(0, y0 - 2), min(G, y1 + 2)
    x = (np.arange(G) + 0.5)/G*2*ext - ext + cx
    yv = -((np.arange(ya, yb) + 0.5)/G*2*ext - ext) + cy
    X, Y = np.meshgrid(x, yv); Z = X + 1j*Y
    inside = np.abs(Z) < rf(np.angle(Z))
    zi = Z[inside]
    f = (zi - sol['a'])*np.exp(-eval_F(sol, zi))
    w = mob(f); r = np.abs(w); w = np.where(r >= 1, w/r*(1-1e-9), w)
    T = tiles(w)
    u = T[:, 0] + 1j*T[:, 1]; wr = T[:, 2] + 1j*T[:, 3]; depth = T[:, 4]; par = T[:, 6]; k = T[:, 7]
    # hyperbolic size of a pixel
    W = np.full(Z.shape, np.nan + 0j); W[inside] = w
    gx = np.gradient(W, axis=1); gy = np.gradient(W, axis=0)
    dwp = np.sqrt(np.abs(gx)**2 + np.abs(gy)**2)[inside]/np.sqrt(2)
    hp = 2*dwp/(1 - np.abs(w)**2)                        # hyperbolic length of one (supersampled) pixel
    hp = np.where(np.isfinite(hp), hp, 10.0)
    one = 1 - np.abs(wr)**2
    D3 = np.sort(np.array([np.arcsinh(np.abs(np.abs(wr - c)**2 - 3)/(np.sqrt(3)*one)) for c in C3]), 0)
    dmain = D3[0]; cuspw = (D3[0] + D3[1])/hp/ss              # local width between the two nearest sides, final px
    cfade = np.clip((cuspw - 2.5)/5.0, 0, 1); cfade = cfade*cfade*(3 - 2*cfade)
    dsub = np.min([np.arcsinh(2*np.abs(np.imag(wr*np.exp(-1j*th)))/one) for th in np.arange(3)*np.pi/3], 0)
    tilepx = 0.55/hp/ss                                  # tile inradius in final px
    ssm = lambda x: x*x*(3 - 2*x)
    fade = ssm(np.clip((tilepx - 1.2)/14.0, 0, 1))*ssm(np.clip((cuspw - 1.0)/23.0, 0, 1))
    fadesub = np.clip((tilepx - 4.0)/8.0, 0, 1)
    # colour: hue = direction of the tile centre in the disc (where you'll probably leave), sat = how sure
    hue = np.angle(u)/(2*np.pi) + hoff
    rr = np.abs(u)
    sat = np.clip(rr, 0, 1)**satg
    base = (1 - 0.86*sat[:, None])*PAPER + 0.86*sat[:, None]*wheel(hue)
    # smooth field for where tiles are sub-pixel (exit direction = arg w)
    smooth = (1 - 0.78*np.abs(w)[:, None]**satg)*PAPER + 0.78*(np.abs(w)[:, None]**satg)*wheel(np.angle(w)/(2*np.pi) + hoff)
    col = base*fade[:, None] + smooth*(1 - fade[:, None])
    col *= (1 - 0.035*par*fade)[:, None]                    # alternate reflections: a breath of two-tone
    # pillow height in hyperbolic units -> normals in px
    hgt = (1 - np.exp(-dmain/0.22))*cfade + (1-cfade)*0.6 - 0.25*np.exp(-dsub/0.05)*fadesub
    H = np.zeros(Z.shape); H[inside] = hgt
    Fd = np.zeros(Z.shape); Fd[inside] = fade
    hx = np.gradient(H, axis=1); hy = np.gradient(H, axis=0)
    # scale: dH/dpx comes out large where tiles are small; normalise by tile size
    TP = np.full(Z.shape, 1.0); TP[inside] = tilepx*ss
    nx = -hx*TP*0.9; ny = hy*TP*0.9
    L = np.array([-0.55, 0.65, 0.75]); L /= np.linalg.norm(L)
    nz = np.ones_like(nx); nn = np.sqrt(nx**2 + ny**2 + nz**2)
    lam = (nx*L[0] + ny*L[1] + nz*L[2])/nn
    Hh = L + np.array([0, 0, 1.0]); Hh /= np.linalg.norm(Hh)
    spec = np.clip((nx*Hh[0] + ny*Hh[1] + nz*Hh[2])/nn, 0, 1)**60
    shade = (0.87 + 0.21*lam)
    img = np.ones(Z.shape + (3,))*PAPER
    cimg = np.zeros(Z.shape + (3,)); cimg[inside] = col
    m9 = inside & (Fd > 0.9)
    if m9.sum() > 100 and __import__("os").environ.get("DBGSH"): print("meanshade", shade[m9].mean(), np.median(shade[m9]))
    SM = float(__import__("os").environ.get("SHM", "0.97"))
    sh = np.where(inside, SM + (shade - SM)*Fd, 1)
    img = np.where(inside[..., None], cimg*sh[..., None] + (0.55*spec*Fd)[..., None], img)
    # silver wires (constant px), main + sub
    dpx_main = dmain/hp; dpx_sub = dsub/hp
    wm = np.clip(0.95*ss - dpx_main + 0.5, 0, 1)*fade*cfade
    wsub = np.clip(0.45*ss - dpx_sub + 0.5, 0, 1)*fadesub*0.8
    wire = np.zeros(Z.shape); wire[inside] = np.maximum(wm, wsub)
    wirecol = np.array([1.0, 0.995, 1.0])
    img = img*(1 - wire[..., None]) + wire[..., None]*wirecol
    # rainbow rim: the exit direction along the boundary itself
    rimd = np.abs(np.abs(Z) - rf(np.angle(Z)))/(2*ext/G)
    rim = np.clip(1.6*ss*S/1000 - rimd + 0.5, 0, 1)
    zb = rf(np.angle(Z))*np.exp(1j*np.angle(Z))
    near = rim > 0
    rimcol = np.zeros(Z.shape + (3,))
    if near.any():
        wb = wmap(sol, mob, zb[near]*(1 - 1e-7))
        rimcol[near] = wheel(np.angle(wb)/(2*np.pi) + hoff)*0.62
    img = img*(1 - 0.9*rim[..., None]) + 0.9*rim[..., None]*rimcol
    c0 = y0 - ya
    return img[c0:c0 + (y1 - y0)], inside[c0:c0 + (y1 - y0)]

def brownian(rf, z0, rng, h=1.5e-3, maxn=4_000_000):
    pts = [z0]; z = z0
    while True:
        st = rng.normal(size=20000)*h + 1j*rng.normal(size=20000)*h
        path = z + np.cumsum(st)
        out = np.abs(path) >= rf(np.angle(path))
        if out.any():
            k = np.argmax(out); pts.append(path[:k+1]); break
        pts.append(path); z = path[-1]
    P = np.concatenate([np.atleast_1d(p) for p in pts])
    e = P[-1]; P[-1] = rf(np.angle(e))*np.exp(1j*np.angle(e))
    return P

def render(shape, S, ss=2, doors_deg=(90, 234, 18), hoff=0.0, out='x.png', ext=1.42, walkers=0, seed=1, satg=0.55, rows=256, cx=0.0, cy=0.0, H=None):
    rf, sol, zd, mob = setup(shape, doors_deg)
    G = S*ss; Hh = (H or S)*ss
    img = np.zeros((G, G, 3)); inside = np.zeros((G, G), bool)
    for y0 in range(0, G, rows):
        y1 = min(G, y0 + rows)
        img[y0:y1], inside[y0:y1] = strip(rf, sol, zd, mob, G, ext, y0, y1, ss, S, hoff, satg, cx, cy)
    img = np.where(inside[..., None], img, PAPER)
    # drop shadow
    m = Image.fromarray((inside*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(G*0.010))
    shadow = np.roll(np.roll(np.asarray(m, float)/255, int(G*0.009), 0), int(G*0.006), 1)
    shadow = np.where(inside, 0, shadow)
    img = img*(1 - 0.17*shadow[..., None]) + 0.17*shadow[..., None]*np.array([0.80, 0.78, 0.92])
    px = lambda z: (((z.real - cx) + ext)/(2*ext)*G, (ext - (z.imag - cy))/(2*ext)*G)
    rng = np.random.default_rng(seed)
    if walkers:
        # start at the conformal centre (all three exits equally likely): Newton on w(z)=0
        z0 = 0j
        for _ in range(30):
            e = 1e-6; w0 = wmap(sol, mob, np.array([z0]))[0]; d = (wmap(sol, mob, np.array([z0 + e]))[0] - w0)/e
            z0 = z0 - w0/d
        from PIL import ImageDraw
        lay = Image.new('L', (G, G), 0); dr = ImageDraw.Draw(lay)
        ends = []
        for k in range(walkers):
            P = brownian(rf, z0, rng)
            xs, ys = px(P)
            dr.line(list(zip(xs.tolist(), ys.tolist())), fill=255, width=max(1, int(1.3*ss*S/1000)))
            ends.append(P[-1])
        L = np.asarray(lay, float)[..., None]/255*0.75
        img = img*(1 - L) + L*np.array([0.36, 0.29, 0.42])
        for e in ends:
            we = wmap(sol, mob, np.array([e*(1 - 1e-6)]))[0]
            beadat(img, e, wheel(np.angle(we)/(2*np.pi) + hoff)*0.92, 7*ss*S/1000, G, ext, cx, cy)
        beadat(img, z0, np.array([1.0, 1.0, 1.0]), 8*ss*S/1000, G, ext, cx, cy, ringc=np.array([0.36, 0.29, 0.42]))
    for zz in zd:
        beadat(img, zz, np.array([0.97, 0.45, 0.42]), 10*ss*S/1000, G, ext, cx, cy)
    im = Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8))
    if ss > 1: im = im.resize((S, S), Image.LANCZOS)
    im.save(out)
    return im

def beadat(img, zz, col, rad, G, ext, cx, cy, ringc=np.array([1.0, 1.0, 1.0])):
    X0 = ((zz.real - cx) + ext)/(2*ext)*G; Y0 = (ext - (zz.imag - cy))/(2*ext)*G
    R = int(rad*2 + 6); xa, xb = int(X0) - R, int(X0) + R; ya, yb = int(Y0) - R, int(Y0) + R
    yy, xx = np.mgrid[ya:yb, xa:xb] + 0.5
    dd = np.hypot(xx - X0, yy - Y0)
    bead = np.clip(rad - dd + 0.5, 0, 1); ring = np.clip(rad*1.3 - dd + 0.5, 0, 1) - bead
    sub = img[ya:yb, xa:xb]
    gl = np.clip(1 - np.hypot(xx - X0 + rad*0.35, yy - Y0 + rad*0.35)/(rad*0.45), 0, 1)**2*0.6
    sub[:] = sub*(1 - ring[..., None]) + ring[..., None]*ringc
    sub[:] = sub*(1 - bead[..., None]) + bead[..., None]*(col*(1 - gl[..., None]) + gl[..., None])

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('shape'); ap.add_argument('--S', type=int, default=700)
    ap.add_argument('--ss', type=int, default=2); ap.add_argument('--doors', default='90,234,18'); ap.add_argument('--hoff', type=float, default=0)
    ap.add_argument('--out', default=None); ap.add_argument('--walkers', type=int, default=0); ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    ap2=0
    render(a.shape, a.S, a.ss, [float(v) for v in a.doors.split(',')], a.hoff, a.out or f'v_{a.shape}.png', walkers=a.walkers, seed=a.seed)
