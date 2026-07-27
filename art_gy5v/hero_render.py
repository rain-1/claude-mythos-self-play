"""THE GREAT GUIDE -- random harmonic series: genealogy -> weather -> law -> digits."""
import numpy as np, sys, math
from scipy.ndimage import gaussian_filter, grey_dilation
from kit import splat_points, line_splat, wide_bloom, filmic, to_img, text_layer
from PIL import Image as PImage

rs = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
SS = 2
S = int(640*rs); H = W = S*SS

XR = 3.30
def px(x): return (x/XR*0.5 + 0.5)*W

Y_ROOT = 0.040*H
Y_TREE1 = 0.560*H
Y_FOG1 = 0.640*H
Y_SEA = 0.870*H          # sea floor / land bottom
NT = 20
NFOG_END = 70
Hn = np.concatenate([[0], np.cumsum(1.0/np.arange(1, 3001))])
P = 0.80
def ytree(n): return Y_ROOT + (n**P)/(NT**P)*(Y_TREE1 - Y_ROOT)

acc = np.zeros((H, W, 3))

STOPS = np.array([
 [1.00,0.92,0.66],[1.00,0.70,0.36],[0.94,0.44,0.26],[0.72,0.26,0.34],
 [0.44,0.27,0.57],[0.26,0.28,0.62]])
def lvlcol(t):
    t = np.clip(t, 0, 1)*(len(STOPS)-1)
    i = np.minimum(t.astype(int), len(STOPS)-2)
    f = (t - i)[..., None]
    return STOPS[i]*(1-f) + STOPS[i+1]*f

# ---- tree edges, ink fading as levels crowd ----
d = np.load('tree_edges.npz')
INK = 5200.0*rs*rs
star_x, star_y, star_m = [], [], []
for n in range(1, NT+1):
    par, chi, mas = d[f'par{n}'], d[f'chi{n}'], d[f'mas{n}']
    x0, y0 = px(par), np.full(len(par), ytree(n-1))
    x1, y1 = px(chi), np.full(len(chi), ytree(n))
    nmid = 14.0 + 1.0*np.log2(max(rs, 1.0))
    fade = 1.0/(1.0 + np.exp((n - nmid)/1.4))
    fade = 0.06 + 0.94*fade
    buf = np.zeros((H, W))
    xm, ym = 0.5*(x0+x1), 0.5*(y0+y1)
    line_splat(buf, x0, y0, xm, ym, mas*INK*fade*0.62, H, W, samples_per_px=1.1)
    line_splat(buf, xm, ym, x1, y1, mas*INK*fade*0.38, H, W, samples_per_px=1.1)
    col = lvlcol(np.array([(n-1)/(NT+7)]))[0]
    acc += buf[:, :, None]*col[None, None, :]
    if n <= 16:
        u, cnt = np.unique(chi, return_counts=True)
        dup = u[cnt > 1]
        if len(dup):
            ux, um = [], []
            for v in dup:
                mm = chi == v
                ux.append(v); um.append(mas[mm].sum())
            um = np.array(um)
            um = um/um.sum()*1.0          # per-level star budget = 1 unit
            star_x += [px(np.array(ux))]; star_y += [np.full(len(ux), ytree(n))]
            star_m += [um]
if star_x:
    sx = np.concatenate(star_x); sy = np.concatenate(star_y); sm = np.concatenate(star_m)
    st = np.zeros((H, W))
    splat_points(st, sx, sy, sm*90.0*rs*rs, H, W)
    st = gaussian_filter(st, 1.6*SS*rs)
    acc += st[:, :, None]*np.array([1.0,0.95,0.80])[None, None, :]*1.0

st = np.zeros((H, W))
splat_points(st, np.array([px(0)]), np.array([Y_ROOT]), np.array([150.0*SS*SS*rs*rs]), H, W)
st = gaussian_filter(st, 3.2*SS*rs)
acc += st[:, :, None]*np.array([1.0,0.93,0.70])[None, None, :]*1.2

# ---- fog band n=23..70, interpolated in n, fading into the law ----
f = np.load('fog_rows.npz')
rows_, ns_ = f['rows'].astype(np.float64), f['ns']
sel = ns_ <= NFOG_END + 10
rows_, ns_ = rows_[sel], ns_[sel]
ftr = np.load('fog_tree_rows.npz')
tree_rows = np.array([ftr[f'r{n}'] for n in range(15, 23)]).astype(np.float64)
rows_ = np.concatenate([tree_rows, rows_], axis=0)
ns_ = np.concatenate([np.arange(15, 23), ns_])
fx = np.linspace(-4, 4, rows_.shape[1])
Y_FOGTOP = ytree(15)
yy = np.arange(int(Y_FOGTOP), int(Y_FOG1))
frac = (yy - Y_FOGTOP)/(Y_FOG1 - Y_FOGTOP)
nwant = 15 + frac*(NFOG_END - 15)
xcanvas = np.linspace(-XR, XR, W)
fogimg = np.zeros((len(yy), W))
for i, nv in enumerate(nwant):
    j = np.searchsorted(ns_, nv)
    j0, j1 = max(0, min(j-1, len(ns_)-1)), min(j, len(ns_)-1)
    t = 0.0 if j1 == j0 else np.clip((nv - ns_[j0])/(ns_[j1] - ns_[j0]), 0, 1)
    # smooth the two source rows slightly before lerp to soften atomic slabs
    prof = (1-t)*rows_[j0] + t*rows_[j1]
    fogimg[i] = np.interp(xcanvas, fx, prof)
from scipy.ndimage import gaussian_filter1d
fogimg = gaussian_filter1d(fogimg, 2.0*SS*rs, axis=0)
# normalize by a stable mid-fog scale, not the global spike
sc = np.percentile(fogimg[len(yy)//2], 99.0)
fogimg /= max(sc, 1e-12)
fogimg = np.clip(fogimg, 0, 3.0)
# crossfade in at the top (over levels 15..23), fade to void at the bottom
NMID = 14.0 + 1.0*np.log2(max(rs, 1.0))
fin = np.clip((nwant - (NMID - 1.5))/4.0, 0, 1)**1.2
fout = np.clip((1.0 - frac)/0.22, 0, 1)**0.8
gain = np.linspace(0.42, 0.30, len(yy))*fin*fout
tcol = np.clip((nwant - 1)/(NT + 7), 0, 1)
fogcol = lvlcol(tcol)
acc[int(Y_FOGTOP):int(Y_FOGTOP)+len(yy), :, :] += (fogimg*gain[:, None])[:, :, None]*fogcol[:, None, :]*0.9

# ---- the law: luminous curve over dark land ----
rc = np.load('rho_curve.npy'); rxs, rrho = rc[0], rc[1]
prof = np.interp(xcanvas, rxs, rrho)
pmax = prof.max()
Y_LAW0 = Y_FOG1 + 0.012*H         # top of law band (rho max maps here)
law_y = Y_SEA - (prof/pmax)*(Y_SEA - Y_LAW0)
rowgrid = np.arange(H)[:, None]
land = (rowgrid >= law_y[None, :]) & (rowgrid <= Y_SEA)
depth = np.clip((rowgrid - law_y[None, :])/(0.10*H), 0, 1)
landc = np.array([0.07,0.22,0.25])
acc += land[:, :, None]*landc[None, None, :]*(0.85 - 0.50*depth)[:, :, None]
# curve stroke
edge = np.zeros((H, W))
line_splat(edge, np.arange(W-1).astype(float), law_y[:-1],
           np.arange(1, W).astype(float), law_y[1:], 1.0, H, W, mass_per_length=True)
edge = grey_dilation(edge, size=(max(1, int(1.3*SS*rs)),)*2)
acc += edge[:, :, None]*np.array([0.62,1.0,0.90])[None, None, :]*0.75

CYAN = np.array([0.45,1.0,0.95])
y18 = Y_SEA - (0.125/pmax)*(Y_SEA - Y_LAW0)
ln = np.zeros((H, W))
line_splat(ln, np.array([0.0]), np.array([y18]), np.array([float(W)]), np.array([y18]),
           1.0, H, W, mass_per_length=True)
ln = grey_dilation(ln, size=(max(1, int(0.7*SS*rs)),)*2)
acc += ln[:, :, None]*CYAN[None, None, :]*0.22
for sgn, amp in ((2.0, 1.0), (-2.0, 0.45)):
    xp = px(sgn)
    ln = np.zeros((H, W))
    line_splat(ln, np.array([xp]), np.array([Y_ROOT*1.0]), np.array([xp]), np.array([y18]),
               1.0, H, W, mass_per_length=True)
    ln = grey_dilation(ln, size=(max(1, int(0.7*SS*rs)),)*2)
    acc += ln[:, :, None]*CYAN[None, None, :]*0.26*amp
    st = np.zeros((H, W))
    splat_points(st, np.array([xp]), np.array([y18]), np.array([130.0*SS*SS*rs*rs*amp]), H, W)
    st = gaussian_filter(st, 2.8*SS*rs)
    acc += st[:, :, None]*CYAN[None, None, :]*1.05*amp

# ---- level rail + axis marks (drawn as text later) ----
# ---- digit wall footer ----
digits_rho = "0.124999999999999999999999999999999999999999" 
digits_tail = "7642168357552"
digits_18  = "0.125000000000000000000000000000000000000000"
tail_18    = "0000000000000"
fs = int(11.5*SS*rs); yA = 0.905*H; yB = yA + 1.55*fs
xw = 0.028*W
tl = text_layer(H, W, [
  (xw, yA, digits_18 + tail_18, fs, (0.30, 0.52, 0.55), {'mono': True}),
  (xw, yB, digits_rho, fs, (0.95, 0.80, 0.45), {'mono': True}),
])
# ember tail: measure width of prefix
from PIL import ImageFont, ImageDraw, Image as PI
fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fs)
wpre = fnt.getbbox(digits_rho)[2]
tl += text_layer(H, W, [
  (xw + wpre, yB, digits_tail, fs, (1.0, 0.38, 0.22), {'mono': True}),
  (xw, yA - 2.1*fs, "1/8", fs, (0.30, 0.52, 0.55), {'mono': True}),
  (xw + fnt.getbbox("1/8  ")[2], yA - 2.1*fs, "\u03c1(2)", fs, (0.95, 0.80, 0.45), {'mono': True}),
])

# ---- bloom ----
lum = acc.sum(axis=2)
nz = lum[lum > 0.02*lum.max()]
th = np.percentile(nz, 98.0)
mask = np.clip((lum - th)/(lum.max() - th + 1e-9), 0, 1)
bl = wide_bloom(lum*mask, 13*SS*rs)
acc += bl[:, :, None]*np.array([1.0,0.85,0.65])[None, None, :]*0.4
acc += gaussian_filter(lum, 2.0*SS*rs)[:, :, None]*0.16*np.array([1.0,0.95,0.9])[None, None, :]

grad = np.linspace(0, 1, H)[:, None]*np.ones((1, W))
acc += (0.014 + 0.020*grad)[:, :, None]*np.array([0.30,0.36,0.72])[None, None, :]

img = filmic(acc, k=1.35, gamma=0.90)

def sup(k):
    S_ = {'0':'\u2070','1':'\u00b9','2':'\u00b2','3':'\u00b3','4':'\u2074','5':'\u2075',
          '6':'\u2076','7':'\u2077','8':'\u2078','9':'\u2079','-':'\u207b'}
    return ''.join(S_[c] for c in str(k))
fs2 = int(8.0*SS*rs); fm2 = int(6.4*SS*rs)
IV = (0.72, 0.78, 0.92); CY = (0.55, 0.95, 0.90); DIM = (0.44, 0.49, 0.65); GD = (0.95, 0.82, 0.50)
draws = [
  (0.030*W, 0.028*H, "T H E   G R E A T   G U I D E", int(11*SS*rs), (0.95, 0.88, 0.70)),
  (0.030*W, 0.028*H + 2.0*fs2, "the random harmonic series  X = \u03a3 \u00b1 1/n,  fair independent signs", fm2, IV),
  (0.030*W, 0.028*H + 3.5*fs2, "every sign-history drawn; brightness = probability; the tree becomes weather, the weather becomes law", fm2, DIM),
  (0.030*W, 0.028*H + 5.0*fs2, "\u201ccustom, then, is the great guide of human life\u201d \u2014 Hume", fm2, DIM),
  (0.970*W, 0.028*H, "knots: different histories, same sum \u2014 1/2 = 1/3 + 1/6", fm2, DIM, {'anchor':'ra'}),
  (0.970*W, 0.028*H + 1.6*fs2, "the walls of the world recede like H\u2099 = \u03a3 1/k", fm2, DIM, {'anchor':'ra'}),
]
for nlab in (1, 3, 6, 10, 15, 20):
    draws.append((0.008*W, ytree(nlab) - 0.6*fm2, f"n={nlab}", fm2, DIM))
draws += [
  (0.008*W, Y_FOG1 - 1.6*fm2, "n=70", fm2, DIM),
  (0.008*W, (Y_FOG1 + 0.02*H), "n\u2192\u221e : the density \u03c1", fm2, CY),
  (px(2.0) + 0.008*W, 0.115*H, "x = 2", fm2, CY),
  (px(2.0) - 0.012*W, y18 + 1.2*fm2, "\u03c1(2) \u2245 1/8 \u2014 for forty-two digits", fs2, CY, {'anchor':'ra'}),
  (px(-2.0) - 0.008*W, 0.115*H, "\u22122", fm2, (0.40, 0.62, 0.60), {'anchor':'ra'}),
  (0.030*W, 0.968*H, "\u03c1(2) \u2212 1/8 = \u22122.3578\u00d710" + sup(-43) + "   \u00b7   \u03c1(x) = (1/\u03c0)\u222b\u2080\u221e cos(xt) \u220f\u2099 cos(t/n) dt   \u00b7   75-digit quadrature vs FFT: two methods agree   \u00b7   Schmuland 2003", fm2, DIM),
]
tl2 = text_layer(H, W, draws)
img = np.clip(img + tl*1.0 + tl2, 0, 1)
out = to_img(img).resize((S, S), PImage.LANCZOS)
out.save('hero_proto.png' if rs < 3 else 'great_guide.png')
print("saved", S)
