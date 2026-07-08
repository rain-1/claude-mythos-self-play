"""PRIME MIRRORS — symmetric runs of consecutive primes as nested luminous arcs.

From the live MathOverflow front-page question (2026-07-08):
"Are there symmetric runs of consecutive primes of arbitrary length?"

A run of consecutive primes is symmetric when its gap sequence is a palindrome.
Each run is drawn as nested semicircular bridges (one arc per mirrored pair,
radius = true distance to centre). Foreground specimens (length >= 10) are
coloured spectrally by radius fraction — every palindrome a small rainbow.
Distant specimens take one hue from an indigo->gold ramp by TIGHTNESS
(span / expected span (k-1)·ln c): remarkable dense runs burn warm.
Odd-length runs carry a pearl (their centre IS a prime). All placed in
perspective on a night plane; four million short runs pile into the horizon.

Usage: python3 prime_mirrors.py <size> <out.png> [gain]
"""
import numpy as np, sys, os, time
from scipy.ndimage import gaussian_filter
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spectra import cmf, XYZ2RGB

t0 = time.time()
S    = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
OUT  = sys.argv[2] if len(sys.argv) > 2 else "art_x61t/variants/mirrors_proto.png"
GAIN = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
rng = np.random.default_rng(11)
sc = S/2560.0

p = np.load("art_x61t/data/primes.npy")
E = np.load("art_x61t/data/runs_even.npz"); ei, em = E["idx"], E["m"]
O = np.load("art_x61t/data/runs_odd.npz");  oi, om = O["idx"], O["m"]

canvas = np.zeros((S, S, 3), dtype=np.float32)
LW = np.array([0.2126, 0.7152, 0.0722])
YH = 0.235*S
KP = 0.80*S

# ---- tightness ramp: indigo -> teal -> gold -> ember (equal luminance) ----
ANCH = np.array([[0.30, 0.38, 1.55],
                 [0.35, 1.05, 1.25],
                 [1.50, 1.05, 0.45],
                 [1.80, 0.55, 0.22]], dtype=np.float32)
ANCH /= (ANCH @ LW.astype(np.float32))[:, None]
def ramp(u):
    u = np.clip(np.asarray(u, np.float32), 0, 1)*(len(ANCH)-1)
    i = np.minimum(u.astype(np.int32), len(ANCH)-2)
    f = (u-i)[:, None]
    return ANCH[i]*(1-f) + ANCH[i+1]*f

def lam_rgb(t):
    lam = 434.0 + 218.0*np.asarray(t, dtype=np.float64)
    xyz = cmf(lam)
    rgb = (XYZ2RGB @ xyz).T
    mn = np.minimum(rgb.min(axis=-1), 0)
    rgb = rgb - mn[..., None]
    lum = rgb @ LW + 1e-9
    return (rgb/lum[..., None]).astype(np.float32)

def splat(x, y, rgbw):
    ok = (x >= 0) & (x < S-1) & (y >= 0) & (y < S-1)
    x, y, rgbw = x[ok], y[ok], rgbw[ok]
    x0 = x.astype(np.int32); y0 = y.astype(np.int32)
    fx = (x-x0).astype(np.float32); fy = (y-y0).astype(np.float32)
    for dx, dy, w in ((0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)),
                      (0,1,(1-fx)*fy), (1,1,fx*fy)):
        np.add.at(canvas, (y0+dy, x0+dx), rgbw*w[:, None])

def radii_even(idx, mm):
    run0 = p[(idx[:, None] + np.arange(-mm+1, mm+1)[None, :])].astype(np.float64)
    return run0[:, mm:] - ((run0[:, 0] + run0[:, -1])/2)[:, None]

def radii_odd(idx, mm):
    run0 = p[(idx[:, None] + np.arange(-mm, mm+1)[None, :])].astype(np.float64)
    return run0[:, mm+1:] - run0[:, mm][:, None]

def tightness_u(rad, idx, klen):
    """0 = loosest, 1 = tightest (percentile within class)"""
    span = 2*rad[:, -1]
    expect = (klen-1)*np.log(p[idx].astype(np.float64))
    t = span/expect
    r_ = np.argsort(np.argsort(-t))          # tightest -> highest rank
    return (r_/(len(t)-1+1e-9)).astype(np.float32)

# lateral clumping for the horizon sea: inverse-CDF of positive 1-D fBm
xn = gaussian_filter(rng.standard_normal(4096).astype(np.float32), 60)
xn = np.exp(0.75*xn/xn.std()); cdf = np.cumsum(xn); cdf /= cdf[-1]
def clumped_x(n, mix=1.0):
    u = rng.random(n)
    xc = np.interp(u, cdf, np.linspace(0, 1, len(cdf)))
    return (mix*xc + (1-mix)*u)*1.06*S - 0.03*S

def zln(n, mu, sig):    # lognormal depth
    return np.exp(rng.normal(np.log(mu), sig, n))

def draw_class(idx, mm, kind, zmu, zsig, base_r, gain, npts, reflect=0.0,
               pearl=False, spectral=False, rankx=False, clump=0.6):
    n = len(idx)
    if n == 0:
        return
    rad = radii_odd(idx, mm) if kind == "odd" else radii_even(idx, mm)
    klen = 2*mm + (1 if kind == "odd" else 0)
    z = zln(n, zmu, zsig)
    x = clumped_x(n, mix=clump)
    if rankx:
        cv = p[idx].astype(np.float64)
        r_ = np.argsort(np.argsort(cv))
        x = ((r_+0.5)/n + rng.normal(0, 0.014, n))*0.99*S
    y = YH + KP/z
    tfrac = (rad/rad[:, -1:]).astype(np.float32)
    disp = (base_r*sc/z[:, None])*tfrac
    npts = max(6, int(npts*S/1280))
    phi = np.linspace(0, np.pi, npts)
    cxp = x[:, None, None] + disp[:, :, None]*np.cos(phi)[None, None, :]
    cyp = y[:, None, None] - disp[:, :, None]*np.sin(phi)[None, None, :]
    if spectral:
        col = lam_rgb(tfrac.ravel())
    else:
        u = tightness_u(rad, idx, klen)
        col = np.repeat(ramp(u), mm, axis=0)
    colp = np.repeat(col, npts, axis=0)
    wgt = (gain/z[:, None]**0.85)*(1.38 - 0.72*tfrac)*(np.pi*disp/npts)
    wp = np.repeat(wgt.ravel(), npts)[:, None]
    splat(cxp.ravel(), cyp.ravel(), colp*wp)
    if reflect > 0:
        ry = y[:, None, None] + (y[:, None, None]-cyp)*0.5
        splat(cxp.ravel(), ry.ravel(), colp*wp*reflect)
    if pearl:
        m = 4
        px_ = np.repeat(x, m) + rng.normal(0, 0.9*sc, n*m)
        py_ = np.repeat(y, m) + rng.normal(0, 0.9*sc, n*m)
        pw = np.repeat(gain*2.8/z**0.85, m)[:, None]/m
        splat(px_, py_, np.array([1.0, 0.88, 0.62], np.float32)[None, :]*pw)
    print(f"  {kind} len{klen} n={n} {time.time()-t0:.1f}s", flush=True)

# ---------- the sea: len3 + len4 -> horizon ----------
for (idx0, kind) in ((oi[om == 1], "odd"), (ei[em == 2], "even")):
    n = min(len(idx0), 420_000)
    sel = rng.choice(len(idx0), n, replace=False)
    z = zln(n, 260, 1.15)
    x = clumped_x(n, mix=0.85)
    y = YH + KP/z + rng.normal(0, 1.1*sc, n)
    w = (GAIN*0.013/np.maximum(z/260, 0.25)**0.7).astype(np.float32)
    idxs = idx0[sel]
    mm0 = 1 if kind == "odd" else 2
    rad = radii_odd(idxs, 1) if kind == "odd" else radii_even(idxs, 2)
    u = tightness_u(rad, idxs, 3 if kind == "odd" else 4)
    col = ramp(u)*np.array([1.12, 0.97, 0.74], np.float32)
    splat(x, y, col*w[:, None])
print(f"sea {time.time()-t0:.1f}s", flush=True)

# ---------- classes, far to near (lognormal z -> soft edges) ----------
draw_class(oi[om == 2], 2, "odd",  30, 0.55, 30, GAIN*0.045, 10)
sel6 = ei[em == 3]
n6 = min(len(sel6), 130_000)
sel6 = sel6[rng.choice(len(sel6), n6, replace=False)]
draw_class(sel6,        3, "even", 30, 0.55, 30, GAIN*0.045, 10)
draw_class(oi[om == 3], 3, "odd",  8.5, 0.42, 42, GAIN*0.075, 24,
           reflect=0.05, pearl=True)
draw_class(ei[em == 4], 4, "even", 8.5, 0.42, 42, GAIN*0.075, 24, reflect=0.05)
draw_class(oi[om == 4], 4, "odd",  4.0, 0.33, 58, GAIN*0.11, 60,
           reflect=0.08, pearl=True, spectral=False)
draw_class(ei[em == 5], 5, "even", 4.0, 0.33, 58, GAIN*0.11, 60, reflect=0.08)
draw_class(ei[em == 6], 6, "even", 2.15, 0.26, 82, GAIN*0.14, 120,
           reflect=0.16, spectral=True, rankx=True)
peer14 = ei[em == 7][p[ei[em == 7]] != 593566933]   # hero drawn separately
draw_class(peer14, 7, "even", 1.62, 0.20, 112, GAIN*0.17, 240,
           reflect=0.20, spectral=True, rankx=True)

# ---------- hero specimen: centre 593566935, gaps 34 2 4 2 42 12 4 12 42 2 4 2 34
hero_c2 = 2*593566935
cand = ei[em == 7]
hc = None
for i in cand:
    if int(p[i]) + int(p[i+1]) == hero_c2:
        hc = i
        break
if hc is not None:
    hr = radii_even(np.array([hc]), 7)[0]
    hx, hy = 0.345*S, 1.045*S            # centre below the frame: a colossal gate
    tf = (hr/hr[-1]).astype(np.float32)
    disph = (0.46*S)*tf
    nph = int(1600*S/1280)
    phi = np.linspace(0, np.pi, nph)
    colh = lam_rgb(tf)
    offs = np.array([-4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5])
    offw = np.array([0.25, 0.55, 0.9, 1.0, 0.9, 0.55, 0.25])
    for j in range(7):
        wj = GAIN*0.135*(1.38-0.72*tf[j])*(np.pi*disph[j]/nph)
        for off, ow in zip(offs, offw):              # wide soft luminous stroke
            xs = hx + (disph[j]+off*sc)*np.cos(phi)
            ys = hy - (disph[j]+off*sc)*np.sin(phi)
            splat(xs, ys, np.tile(colh[j], (nph, 1))*(wj*ow))
    print(f"hero gate planted {time.time()-t0:.1f}s", flush=True)

# ---------- tone ----------
img = gaussian_filter(canvas, (0.65*sc, 0.65*sc, 0))
lum = img @ LW.astype(np.float32)
thr = np.percentile(lum, 99.7)
mask = np.clip((lum-thr)/(thr+1e-9), 0, None)[..., None]*img
img = img + 0.50*gaussian_filter(mask, (2.2*sc, 2.2*sc, 0)) \
          + 0.17*gaussian_filter(mask, (8*sc, 8*sc, 0))
yv = (np.arange(S, dtype=np.float32)/S)[:, None, None]
horiz = np.exp(-0.5*np.clip((YH/S - yv)/0.05, 0, None)**2)*(yv < YH/S + 0.02)
img = img + horiz*np.array([0.034, 0.027, 0.016], np.float32) \
          + (0.0038 + 0.0032*(1-yv))*np.array([0.06, 0.08, 0.20], np.float32)

x = 1 - np.exp(-2.4*img)
out = (255*np.clip(x, 0, 1)**(1/2.1)).astype(np.uint8)
Image.fromarray(out).save(OUT)
print(f"saved {OUT} {time.time()-t0:.1f}s")
