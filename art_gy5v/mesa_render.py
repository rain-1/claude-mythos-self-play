"""THE EIGHTH TOWER -- Borwein integrals as nine towers in log-depth chart."""
import numpy as np, sys, math
from scipy.ndimage import gaussian_filter, grey_dilation, distance_transform_edt
from kit import splat_points, line_splat, wide_bloom, filmic, to_img, text_layer
from PIL import Image as PImage

rs = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
SS = 2
S = int(640*rs); H = W = S*SS

d = np.load('tower_profiles.npz')

YHI = 13.4
Y0, Y1 = 0.856*H, 0.068*H
def py(ylog): return Y0 + ylog*(Y1 - Y0)/YHI
CEILY = 12.55

NTOW = 9
MARG = 0.030*W
SLOTW = (W - 2*MARG)/NTOW
UX = SLOTW/2.62
def pxn(n, x): return MARG + (n + 0.5)*SLOTW + x*UX

WARM_LO = np.array([0.55,0.20,0.07]); WARM_MID = np.array([1.0,0.62,0.22]); WARM_HI = np.array([1.0,0.94,0.74])
COLD_LO = np.array([0.07,0.20,0.38]); COLD_MID = np.array([0.28,0.58,0.88]); COLD_HI = np.array([0.78,0.96,1.0])
CYAN = np.array([0.45,1.0,0.95]); GOLD = np.array([1.0,0.78,0.35])

def ramp3(t, lo, mid, hi):
    t = np.clip(t, 0, 1)[..., None]
    a = np.clip(t*2, 0, 1); b = np.clip(t*2-1, 0, 1)
    return np.where(t < 0.5, lo*(1-a) + mid*a, mid*(1-b) + hi*b)

acc = np.zeros((H, W, 3))

# decade gridlines
gw = max(1, int(SS*rs*0.6))
for dec in range(0, 14):
    y = int(py(dec))
    acc[y:y+gw, :, :] += np.array([0.13,0.15,0.26])*0.5
# heaven band
yh = int(py(CEILY))
acc[yh:yh+max(1,int(SS*rs*1.0)), :, :] += np.array([0.45,0.42,0.30])*0.7

rows = np.arange(H)[:, None]
capinfo = []
for n in range(9):
    x, y = d[f'x{n}'], d[f'y{n}']
    cold = n >= 7
    c0, c1 = int(pxn(n, -1.29)), int(pxn(n, 1.29))
    cols = np.arange(c0, c1)
    xu = (cols - pxn(n, 0))/UX
    yy = np.interp(np.abs(xu), x, y)
    isinf = ~np.isfinite(yy)
    ytop = np.where(np.isfinite(yy), py(np.minimum(yy, YHI)), -10.0)
    colmask = (rows >= ytop[None, :]) & (rows <= Y0)
    # edge-lit interior: EDT of mask
    sub = colmask.astype(np.uint8)
    dist = distance_transform_edt(sub)
    edgelight = np.exp(-dist/(9.0*SS*rs))
    alt = (np.clip((Y0 - rows)/(Y0 - py(13.0)), 0, 1.05)**1.25)*np.ones((1, len(cols)))
    lo, mid, hi = (COLD_LO, COLD_MID, COLD_HI) if cold else (WARM_LO, WARM_MID, WARM_HI)
    col = ramp3(alt, lo, mid, hi)
    # masonry striation per decade of ylog
    ylog_field = (Y0 - rows)/( (Y0-Y1)/YHI )*np.ones((1, len(cols)))
    stria = 1.0 + 0.09*np.cos(2*np.pi*ylog_field)
    body = colmask[:, :, None]*col*(0.13 + 0.60*edgelight[:, :, None])*stria[:, :, None]
    if cold:
        ymaxv = np.nanmax(np.where(np.isfinite(y), y, np.nan))
        capr = np.sqrt(((rows - py(ymaxv))/(0.09*H))**2 + ((np.arange(len(cols)) - len(cols)/2)[None, :]*1.0/(0.055*W))**2)
        body *= (1.0 + 1.8*np.exp(-capr**2))[:, :, None]
    # pillar core: columns where exact (inf) get an extra inner glow ramp
    if isinf.any():
        pill = colmask & isinf[None, :]
        body += pill[:, :, None]*col*0.30
    acc[:, c0:c1, :] += body
    # rim edges: split into left flank, right flank (never across plateau)
    ecol = (COLD_HI if cold else WARM_HI)
    edge = np.zeros((H, W))
    for side in (-1, 1):
        m = np.isfinite(yy) & ((xu*side) > 0)
        if isinf.any():
            # restrict to outside the plateau
            m &= np.abs(xu) >= np.abs(xu[isinf]).min()
        ex, ey = cols[m].astype(float), ytop[m]
        o = np.argsort(ex)
        ex, ey = ex[o], ey[o]
        if len(ex) > 1:
            line_splat(edge, ex[:-1], ey[:-1], ex[1:], ey[1:], 1.0, H, W, mass_per_length=True)
    if isinf.any():
        j = np.where(isinf)[0]
        for edgecol in (j.min(), j.max()):
            xpx = float(cols[edgecol])
            ystart = ytop[j.min()-1] if j.min() > 0 else Y0
            line_splat(edge, np.array([xpx]), np.array([min(float(Y0), float(ystart)+2*SS*rs)]),
                       np.array([xpx]), np.array([0.0]), 1.0, H, W, mass_per_length=True)
    edge = grey_dilation(edge, size=(max(1, int(1.1*SS*rs)),)*2)
    acc += edge[:, :, None]*ecol[None, None, :]*0.9
    if cold:
        ymax = np.nanmax(np.where(np.isfinite(y), y, np.nan))
        capinfo.append((n, ymax))
        st = np.zeros((H, W))
        splat_points(st, np.array([pxn(n, 0.0)]), np.array([py(ymax)]),
                     np.array([110.0*SS*SS*rs*rs]), H, W)
        st = gaussian_filter(st, 3.0*SS*rs)
        acc += st[:, :, None]*CYAN[None, None, :]*1.0
        # cap seal line
        sl = np.zeros((H, W))
        line_splat(sl, np.array([pxn(n, -0.30)]), np.array([py(ymax)]),
                   np.array([pxn(n, 0.30)]), np.array([py(ymax)]), 1.0, H, W, mass_per_length=True)
        sl = grey_dilation(sl, size=(max(1,int(0.9*SS*rs)),)*2)
        acc += sl[:, :, None]*CYAN[None, None, :]*0.5
    else:
        # burn-through at heaven band
        if isinf.any():
            j = np.where(isinf)[0]
            xc = (cols[j.min()] + cols[j.max()])/2.0
            st = np.zeros((H, W))
            splat_points(st, np.array([xc]), np.array([py(CEILY)]),
                         np.array([140.0*SS*SS*rs*rs*(1 + 0.15*(cols[j.max()]-cols[j.min()])/SLOTW*8)]), H, W)
            st = gaussian_filter(st, 6.0*SS*rs)
            acc += st[:, :, None]*np.array([1.0,0.92,0.70])[None, None, :]*0.85

# fuel bars
FB_Y = 0.8815*H
FBH = max(2, int(2.0*SS*rs))
unit = SLOTW*0.80
for n in range(9):
    s = sum(1.0/(2*k+1) for k in range(1, n+1))
    xl = pxn(n, 0) - unit*0.55
    cold = n >= 7
    ln = np.zeros((H, W))
    line_splat(ln, np.array([xl]), np.array([FB_Y]), np.array([xl + unit*min(s, 1.0)]),
               np.array([FB_Y]), 1.0, H, W, mass_per_length=True)
    ln = grey_dilation(ln, size=(FBH, FBH))
    acc += ln[:, :, None]*(COLD_MID if cold else WARM_MID)[None, None, :]*0.85
    if s > 1.0:
        ex = np.zeros((H, W))
        line_splat(ex, np.array([xl + unit]), np.array([FB_Y]), np.array([xl + unit*s]),
                   np.array([FB_Y]), 1.0, H, W, mass_per_length=True)
        ex = grey_dilation(ex, size=(FBH, FBH))
        acc += ex[:, :, None]*CYAN[None, None, :]*1.5
    tk = np.zeros((H, W))
    line_splat(tk, np.array([xl + unit]), np.array([FB_Y - 4.5*SS*rs]), np.array([xl + unit]),
               np.array([FB_Y + 4.5*SS*rs]), 1.0, H, W, mass_per_length=True)
    tk = grey_dilation(tk, size=(max(1,int(0.8*SS*rs)),)*2)
    acc += tk[:, :, None]*GOLD[None, None, :]*1.0

# bloom
lum = acc.sum(axis=2)
nz = lum[lum > 0.02*lum.max()]
th = np.percentile(nz, 97.0)
mask = np.clip((lum - th)/(lum.max() - th + 1e-9), 0, 1)
bl = wide_bloom(lum*mask, 15*SS*rs)
acc += bl[:, :, None]*np.array([1.0,0.85,0.6])[None, None, :]*0.45
acc += gaussian_filter(lum, 2.2*SS*rs)[:, :, None]*0.17*np.array([1.0,0.95,0.88])[None, None, :]

# background
grad = np.linspace(0, 1, H)[:, None]*np.ones((1, W))
acc += (0.016 + 0.026*grad)[:, :, None]*np.array([0.30,0.38,0.72])[None, None, :]

img = filmic(acc, k=1.30, gamma=0.90)

# ---- annotations ----
def sup(k):
    S_ = {'0':'\u2070','1':'\u00b9','2':'\u00b2','3':'\u00b3','4':'\u2074','5':'\u2075',
          '6':'\u2076','7':'\u2077','8':'\u2078','9':'\u2079','-':'\u207b'}
    return ''.join(S_[c] for c in str(k))
fs = int(7.5*SS*rs); fm = int(6.2*SS*rs)
IV = (0.72, 0.78, 0.92); GD = (0.98, 0.80, 0.42); CY = (0.55, 0.95, 0.90); DIM = (0.45, 0.50, 0.66)
draws = [
  (0.032*W, 0.912*H, "T H E   E I G H T H   T O W E R", int(10.5*SS*rs), (0.95, 0.88, 0.70)),
  (0.032*W, 0.912*H + 1.9*fs, "I(n) = \u222b\u2080\u221e \u220f\u2096 sinc(t/(2k+1)) dt = \u03c0/2 exactly for n = 0..6", fm, IV),
  (0.032*W, 0.912*H + 3.3*fs, "the eighth falls short by 2.31\u00d710" + sup(-11) + " \u2014 custom is not law", fm, IV),
  (0.968*W, 0.912*H, "tower height = \u2212log\u2081\u2080(1 \u2212 h\u2099(x))", fm, DIM, {'anchor':'ra'}),
  (0.968*W, 0.912*H + 1.4*fm, "h\u2099 = \U0001d7d9[\u22121,1] \u2217 box(1/3) \u2217 \u22ef \u2217 box(1/(2n+1))", fm, DIM, {'anchor':'ra'}),
  (0.968*W, 0.912*H + 2.8*fm, "an exact plateau h\u2099 \u2261 1 = a pillar of infinite height", fm, DIM, {'anchor':'ra'}),
  (0.968*W, 0.912*H + 4.2*fm, "gold bars: \u03a3 1/(2k+1) \u2014 the pillar dies when the sum passes 1", fm, DIM, {'anchor':'ra'}),
]
for dec in (1,2,3,4,6,8,10,12):
    draws.append((0.005*W, py(dec) - 0.7*fm, "10" + sup(-dec), fm, DIM))
labels = ['1','3','5','7','9','11','13','15','17']
for n in range(9):
    draws.append((pxn(n, 0), 0.8955*H, labels[n], fm, (0.80,0.75,0.65) if n < 7 else (0.55,0.75,0.95), {'anchor':'ma'}))
draws += [
  (pxn(7, 0) + 0.020*W, py(10.83) - 0.5*fs, "1 \u2212 h\u2087(0) = 1.47\u00d710" + sup(-11), fm, CY),
  (pxn(8, 0) - 0.020*W, py(7.92) - 0.5*fs, "1.19\u00d710" + sup(-8), fm, CY, {'anchor':'ra'}),
  (0.5*W, 0.980*H, "1 \u2212 h\u2087(0) = 6879714958723010531 / 467807924720320453655260875000   \u00b7   exact rational box-convolution, verified from scratch   \u00b7   Borwein & Borwein 2001", fm, (0.52,0.56,0.70), {'anchor':'ma'}),
]
tl = text_layer(H, W, draws)
img = np.clip(img + tl, 0, 1)
out = to_img(img).resize((S, S), PImage.LANCZOS)
out.save('mesa_proto.png' if rs < 2 else 'eighth_tower.png')
print("saved", S, "caps:", capinfo)
