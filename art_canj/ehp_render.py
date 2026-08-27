"""Piece 2 (2560²) — THE PRICE OF LEAVING THE CIRCLE  (MO 514645)
Left: the regular 17-gon of diameter 2 with its binding cage — the n active
diameter chords (a star polygon), each at the SAME exact tension
mu = (n-1)/16 — and its softest escape attempt: the k=2 ellipse mode drawn
as displacement silk (declared exaggeration).  The attempt costs; brightness
fades as the deformation leaves the orbit.
Right: the stiffness harp — the full cone-restricted Lagrangian spectrum
lambda(k, n) for odd n = 5..61, threaded by wavenumber; every string strictly
below the flatness horizon (lambda = 0): the polygon is a strict local
maximizer, with quadratic price c_n = |lambda_max| ~ 0.80 n.
"""
import numpy as np, json
from PIL import Image, ImageDraw, ImageFont
from ehp_dispersion import full_analysis

SS = 2
W = H = 2560
Ws, Hs = W * SS, H * SS
buf = np.zeros((Hs, Ws, 3), np.float32)

def splat(x, y, sigma, color, amp):
    r = int(3 * sigma) + 1
    x0, y0, x1, y1 = int(x)-r, int(y)-r, int(x)+r+1, int(y)+r+1
    xa, ya, xb, yb = max(x0,0), max(y0,0), min(x1,Ws), min(y1,Hs)
    if xb <= xa or yb <= ya: return
    gy = np.arange(ya, yb) - y
    gx = np.arange(xa, xb) - x
    g = np.exp(-(gy[:,None]**2 + gx[None,:]**2) / (2*sigma**2))
    for k in range(3):
        buf[ya:yb, xa:xb, k] += amp * color[k] * g

def line_glow(p0, p1, color, amp, width):
    d = np.hypot(p1[0]-p0[0], p1[1]-p0[1])
    n_samp = max(int(d / (width*0.5)), 2)
    for t in np.linspace(0, 1, n_samp):
        splat(p0[0]+t*(p1[0]-p0[0]), p0[1]+t*(p1[1]-p0[1]),
              width, color, amp/n_samp * d/width * 0.7)

GOLD  = np.array([1.00, 0.80, 0.40])
EMBER = np.array([1.00, 0.62, 0.24])
CYAN  = np.array([0.45, 0.88, 0.95])
STEEL = np.array([0.36, 0.52, 0.70])
WHITE = np.array([1.00, 0.95, 0.85])
BG    = np.array([0.010, 0.014, 0.028])

# ---------------- left: polygon + cage + mode silk ----------------
n = 17
P, mu, ev, ks, modes = full_analysis(n)
soft = modes[:, -1]; soft /= np.linalg.norm(soft)
lam = ev[-1]
CX, CY, RAD = 680*SS, 1070*SS, 560*SS
R0 = 1.0/np.cos(np.pi/(2*n))
def to_px(Q):
    return np.stack([CX + Q[:,0]/R0*RAD, CY - Q[:,1]/R0*RAD], 1)

# mode silk: ghosts of P + s*soft, s in [-smax, smax], exaggeration
EX = 0.95
for s in np.linspace(0.08, 1, 20):
    Q = P + (s*EX) * soft.reshape(-1,2)
    px = to_px(Q)
    w = np.exp(-1.6*s)
    col = EMBER*(0.35+0.65*s) + STEEL*(0.65-0.65*s)
    for i in range(n):
        j = (i+1) % n
        line_glow(px[i], px[j], col, amp=0.42*w, width=1.5*SS)
# undeformed polygon: crisp steel ring
pxu = to_px(P)
for i in range(n):
    j = (i+1) % n
    line_glow(pxu[i], pxu[j], STEEL*1.2, amp=0.9, width=1.8*SS)

# the diameter cage: active pairs, all tension mu = (n-1)/16
k1, k2 = (n-1)//2, (n+1)//2
px0 = to_px(P)
for i in range(n):
    for kk in (k1,):
        j = (i+kk) % n
        line_glow(px0[i], px0[j], GOLD, amp=0.72, width=1.7*SS)
# vertices
for i in range(n):
    splat(px0[i][0], px0[i][1], 5.5*SS, WHITE, 2.2)
    splat(px0[i][0], px0[i][1], 16*SS, GOLD, 0.7)

# ---------------- right: stiffness harp ----------------
data = json.load(open('ehp_dispersion.json'))
data = [d for d in data if d['n'] <= 61]
X0, X1 = 1480*SS, 2460*SS
Y0, Y1 = 340*SS, 2080*SS      # lambda = 0 at Y0, lambda_min at Y1
lam_min = -60.0
def hx(nv): return X0 + (nv - 5) / (61 - 5) * (X1 - X0)
def hy(l): return Y0 + (l / lam_min) * (Y1 - Y0)   # l negative -> down

# flatness horizon
line_glow((X0 - 30*SS, Y0), (X1 + 20*SS, Y0), CYAN, amp=2.0, width=2.0*SS)

# dispersion curves: top branch per wavenumber k
maxk = 12
FLOOR = -60.0
branch = {}
for d in data:
    nv = d['n']
    for l, k in zip(d['ev'], d['ks']):
        if k > maxk: continue
        key = (nv, k)
        if key not in branch or l > branch[key]:
            branch[key] = l
curves = {}
for (nv, k), l in sorted(branch.items()):
    curves.setdefault(k, []).append((nv, l))
for k, pts in sorted(curves.items(), reverse=True):
    pts = [(nv, l) for nv, l in pts if l >= FLOOR]
    if len(pts) < 2: continue
    t = min(k, maxk) / maxk
    col = STEEL*(1-t)*1.1 + EMBER*t
    if k == 2: col = GOLD
    for a, b in zip(pts[:-1], pts[1:]):
        line_glow((hx(a[0]), hy(a[1])), (hx(b[0]), hy(b[1])), col,
                  amp=1.15 if k==2 else 0.42, width=(2.0 if k==2 else 1.4)*SS)
    for (nv, l) in pts:
        splat(hx(nv), hy(l), (2.4 if k==2 else 1.6)*SS, col,
              1.2 if k==2 else 0.4)
# faint dust: the rest of the spectrum above the floor
for d in data:
    for l, k in zip(d['ev'], d['ks']):
        if l < FLOOR or (d['n'], k) in branch and abs(branch[(d['n'],k)]-l)<1e-12:
            continue
        splat(hx(d['n']), hy(l), 1.2*SS, STEEL*0.8, 0.12)
# lambda-axis ticks
for lt in (-10, -20, -30, -40, -50):
    line_glow((X0-26*SS, hy(lt)), (X0-6*SS, hy(lt)), STEEL, amp=0.8, width=1.4*SS)

# ---------------- compose ----------------
buf += BG[None,None,:]
from scipy.ndimage import gaussian_filter, zoom as ndzoom
lum = buf.mean(2)
thr = np.percentile(lum, 99.0)
mask = np.clip((lum-thr)/(lum.max()-thr+1e-9), 0, 1)
small = (buf*mask[:,:,None])[::4,::4]
bl = np.stack([gaussian_filter(small[:,:,k], 12) for k in range(3)], 2)
buf = buf + 1.1*ndzoom(bl, (4,4,1), order=1)[:Hs,:Ws]

img = 1 - np.exp(-1.5*buf)
img = np.clip(img, 0, 1)**(1/1.9)
img = img + (np.random.rand(Hs,Ws,1)-0.5)/255.0
im = Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((W,H), Image.LANCZOS)

def load_font(path, size):
    try: return ImageFont.truetype(path, size)
    except Exception: return ImageFont.load_default()
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_t = load_font(FB, 74); f_s = load_font(FR, 34); f_c = load_font(FR, 27)
f_l = load_font(FB, 34)
d = ImageDraw.Draw(im)
gold=(255,212,138); dim=(150,166,192); cyn=(150,214,228)
def ctext(x,y,s,f,fill):
    bb=d.textbbox((0,0),s,font=f); d.text((x-(bb[2]-bb[0])/2,y),s,font=f,fill=fill)

ctext(W/2, 56, "THE PRICE OF LEAVING THE CIRCLE", f_t, gold)
ctext(W/2, 150, "the regular odd polygon is a strict local maximizer of the product of pairwise distances at fixed diameter  ·  MO 514645", f_s, dim)

ctext(680, 1830, "the 17-gon of diameter 2 in its cage of 17 taut diameters —", f_c, dim)
ctext(680, 1872, "every chord at the same tension μ = (n−1)/16, proved via p′/p at a vertex of zⁿ−Rⁿ", f_c, gold)
ctext(680, 1914, "silk: the softest escape, the k = 2 ellipse mode (exaggerated) — even it pays quadratically", f_c, dim)

ctext(1965, 300, "λ = 0 — the horizon of flatness", f_c, cyn)
ctext(1965, 1980, "the stiffness harp: dispersion branches λ_k(n) of the", f_c, dim)
ctext(1965, 2022, "cone-restricted Lagrangian Hessian, odd n = 5 … 61", f_c, dim)
ctext(1965, 2064, "gold = the softest string, always k = 2: λ_max ≈ −0.80·n", f_c, gold)
ctext(1965, 2106, "no string ever touches the horizon", f_c, cyn)
d.text((1500, 360), "n = 5", font=f_c, fill=dim)
d.text((2380, 360), "61", font=f_c, fill=dim)

ctext(W/2, 2320, "log Δ(n-gon) − log Δ(r) ≥ |λ_max(n)|·dist(r, orbit)² for nearby feasible r — verified n ≤ 201; Monte-Carlo along the softest mode: 5.476 ≥ 4.751 at n = 9", f_c, dim)
ctext(W/2, 2362, "an answer-shaped computation for a question that asked what is known: strict quadratic stability, with the constant", f_c, (110,126,152))

im.save('ehp_2560.png')
print("saved; lam_max(17) =", lam, " mu =", mu.mean())
