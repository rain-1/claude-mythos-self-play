"""THE DYNASTY OF CHAMPIONS — 4096^2 hero.
All 148 Collatz delay-record trajectories in (steps-remaining, log2 value):
shared water piles up (brightness = how many champions ride the same river),
hue = age of the water (which champion first used it), sources as stars
(revolutions blaze white, four-thirds heirs are gold beads), an ordinary-fog
ecology behind, and the ratio ladder with its 4/3 atom as an inset.

python3 hero_render.py [FINAL]   (default 1024 proto; 4096 final)
"""
import numpy as np, json, sys, math
from PIL import Image, ImageDraw, ImageFont

FINAL = int(sys.argv[1]) if len(sys.argv)>1 else 1024
SS = 2
S = FINAL*SS
rs = FINAL/1024.0

D = np.load('hero_paths.npz'); F = np.load('hero_fog.npz')
ltype = json.load(open('hero_ltype.json'))
lens, T, Y = D['lens'], D['t'], D['y']
share, dd, logn = D['share'], D['d'], D['logn']
flens, FT, FY = F['lens'], F['t'], F['y']

tmax = float(T.max())*1.02
ymax = float(max(Y.max(), FY.max()))*1.04
# layout: annotation band at bottom
BAND = int(0.118*S)
x0, x1 = 0.035*S, 0.985*S
y0, y1 = 0.030*S, S - BAND - 0.02*S     # y0 top

def to_px(t, y):
    px = x1 - (t/tmax)*(x1-x0)
    py = y0 + (1.0 - y/ymax)*(y1-y0)
    return px, py

def splat_lines(t, y, ink, w, age=None, k=0.0, step=0.7):
    """sample polyline every ~step px, bilinear deposit of w per sample."""
    px, py = to_px(t, y)
    dx, dy = np.diff(px), np.diff(py)
    seglen = np.hypot(dx, dy)
    nsub = np.maximum(1, np.ceil(seglen/step).astype(np.int32))
    tot = int(nsub.sum())
    idx = np.repeat(np.arange(len(dx)), nsub)
    # fractional position within each segment
    cs = np.concatenate(([0], np.cumsum(nsub)))
    frac = (np.arange(tot) - cs[idx]) / nsub[idx]
    X = px[idx] + dx[idx]*frac
    Yp = py[idx] + dy[idx]*frac
    wgt = np.full(tot, w, np.float32) * (seglen[idx]/nsub[idx] + 1e-9)
    xi = np.floor(X).astype(np.int64); yi = np.floor(Yp).astype(np.int64)
    fx = (X - xi).astype(np.float32); fy = (Yp - yi).astype(np.float32)
    for ddx, ddy, ww in ((0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)):
        gx, gy = xi+ddx, yi+ddy
        m = (gx>=0)&(gx<S)&(gy>=0)&(gy<S)
        np.add.at(ink, (gy[m], gx[m]), (wgt*ww)[m])
        if age is not None:
            np.minimum.at(age, (gy[m], gx[m]), np.where(ww[m]>0.05, k, np.inf))

ink = np.zeros((S,S), np.float32)
age = np.full((S,S), np.inf, np.float32)
fog = np.zeros((S,S), np.float32)

# fog first
o=0
for L in flens:
    splat_lines(FT[o:o+L], FY[o:o+L], fog, 1.0, step=1.4)
    o+=L
print('fog splatted')

# champions, oldest first
o=0
starts=[]
for kk, L in enumerate(lens):
    t, yy = T[o:o+L], Y[o:o+L]
    splat_lines(t, yy, ink, 1.0, age=age, k=float(kk))
    starts.append((t[0], yy[0]))
    o+=L
print('champions splatted')

# --- tone & color ---
img = np.zeros((S,S,3), np.float32)
# fog: steel blue, log-graded atmosphere
fgl = np.log1p(fog)
fg = 1.0 - np.exp(-fgl*0.30)
fogcol = np.array([0.13, 0.19, 0.30], np.float32)
img += fg[...,None]*fogcol[None,None,:]*0.55

# champions: luminance from log multiplicity, hue from age
mult = ink
nz = mult[mult>0]
p99 = np.percentile(nz, 99.5) if nz.size else 1.0
base = np.log1p(mult*1.7)/np.log1p(p99*1.7)
lum = 1.0 - np.exp(-2.9*base)
a = np.where(np.isfinite(age), age, 0.0)/max(1,len(lens)-1)
# 4-anchor ramp avoiding white midspace: gold -> amber -> teal -> cyan
anch = np.array([[1.00,0.74,0.24],[0.95,0.52,0.20],[0.25,0.55,0.60],[0.42,0.82,1.00]],np.float32)
pos  = np.array([0.0, 0.35, 0.70, 1.0], np.float32)
col = np.empty((S,S,3), np.float32)
for i in range(3):
    col[...,i] = np.interp(a, pos, anch[:,i])
img += lum[...,None]*col

# the mouth: every river reaches (t=0, y=0) — one gold sea-glow
mx, my = to_px(np.array([0.0]), np.array([0.0]))
yy, xx = np.ogrid[:S,:S]
rr2 = ((xx-mx[0])**2 + (yy-my[0])**2)/ (0.06*S)**2
img += np.exp(-rr2)[...,None]*np.array([1.0,0.75,0.35],np.float32)[None,None,:]*0.5

# --- sources: stars ---
star = np.zeros((S,S,3), np.float32)
def add_star(px, py, rad, color, amp):
    r = int(max(2, rad*3))
    yy, xx = np.ogrid[-r:r+1, -r:r+1]
    g = np.exp(-(xx*xx+yy*yy)/(2*rad*rad)).astype(np.float32)
    x0i, y0i = int(px)-r, int(py)-r
    xa, ya = max(0,x0i), max(0,y0i)
    xb, yb = min(S, x0i+2*r+1), min(S, y0i+2*r+1)
    if xb<=xa or yb<=ya: return
    sub = g[ya-y0i:yb-y0i, xa-x0i:xb-x0i]
    star[ya:yb, xa:xb, :] += amp*sub[...,None]*np.asarray(color,np.float32)[None,None,:]

for kk,(t_s, y_s) in enumerate(starts):
    px, py = to_px(np.array([t_s]), np.array([y_s])); px, py = float(px[0]), float(py[0])
    lt = ltype[kk]
    sh = share[kk]
    if kk==0: continue
    if lt=='founder' and sh<0.5:
        add_star(px, py, 3.4*SS*rs, (1.0,0.98,0.92), 1.1)      # revolution: white blaze
        add_star(px, py, 1.2*SS*rs, (1.0,1.0,1.0), 1.6)
    elif lt=='four-thirds':
        add_star(px, py, 1.7*SS*rs, (1.0,0.78,0.26), 0.55)     # heir: gold bead
    elif lt=='double':
        add_star(px, py, 1.5*SS*rs, (1.0,0.58,0.18), 0.5)      # doubling: amber
    else:
        add_star(px, py, 1.4*SS*rs, (0.9,0.82,0.6), 0.35)
print('stars added')

# bloom the stars (downsample-blur-upsample)
from scipy.ndimage import gaussian_filter, zoom
ds = 4
small = star[::ds, ::ds]
bl = gaussian_filter(small, (14*rs/ds*SS, 14*rs/ds*SS, 0))
bloom = np.kron(bl, np.ones((ds,ds,1),np.float32))[:S,:S]
img += star + 0.55*bloom

# --- inset: ratio ladder, top-left panel ---
links = json.load(open('links.json'))
iw, ih = int(0.30*S), int(0.175*S)
ix, iy = int(0.045*S), int(0.045*S)
pan = np.zeros((ih, iw, 3), np.float32)
pan[:] = np.array([0.012,0.016,0.028])
rr = [min(2.2, float(r)) for *_, r, _t in links]
tt = [_t for *_, _t in links]
for j,(r,typ) in enumerate(zip(rr,tt)):
    px = int(j/(len(rr)-1)*(iw-1))
    py = int((1 - (r-1.0)/1.25)*(ih-1))
    py = max(0,min(ih-1,py))
    colr = (1.0,0.80,0.30) if typ=='four-thirds' else ((1.0,0.62,0.22) if typ=='double' else (0.55,0.80,1.0))
    r0 = max(1,int(1.6*SS*rs))
    yyi, xxi = np.ogrid[-3*r0:3*r0+1, -3*r0:3*r0+1]
    g = np.exp(-(xxi*xxi+yyi*yyi)/(2*r0*r0)).astype(np.float32)
    ya,yb=max(0,py-3*r0),min(ih,py+3*r0+1); xa,xb=max(0,px-3*r0),min(iw,px+3*r0+1)
    pan[ya:yb, xa:xb,:] += 0.9*g[ya-(py-3*r0):yb-(py-3*r0), xa-(px-3*r0):xb-(px-3*r0)][...,None]*np.asarray(colr)[None,None,:]
# 4/3 line
lypx = int((1-(4/3-1.0)/1.25)*(ih-1))
pan[lypx-max(1,int(SS*rs/2)):lypx+max(1,int(SS*rs/2)), :, :] += np.array([0.5,0.42,0.2])[None,None,:]*0.55
# ratio=2 faint line
ly2 = int((1-(2.0-1.0)/1.25)*(ih-1))
pan[ly2, :, :] += np.array([0.3,0.2,0.12])[None,:]*0.5
img[iy:iy+ih, ix:ix+iw, :] = img[iy:iy+ih, ix:ix+iw, :]*0.05 + pan

img = np.clip(img, 0, 1)**(1/1.35)
img8 = (np.clip(img,0,1)*255 + np.random.uniform(-0.5,0.5,img.shape)).clip(0,255).astype(np.uint8)
out = Image.fromarray(img8).resize((FINAL, FINAL), Image.LANCZOS)

# --- annotation band ---
d2 = ImageDraw.Draw(out)
def font(sz, bold=False):
    try:
        p = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else '')
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()
bandy = FINAL - BAND//SS
d2.rectangle([0, bandy, FINAL, FINAL], fill=(6,7,10))
fs = max(9, int(12.5*rs))
mx0 = int(0.035*FINAL)
d2.text((mx0, bandy+int(0.008*FINAL)), 'THE DYNASTY OF CHAMPIONS', font=font(int(27*rs), True), fill=(255,214,120))
caps = [
 'All 148 Collatz delay-record trajectories (A006877, to 1.47e19) in (steps remaining, log2 value); every river ends in the gold sea at 1.',
 'Brightness = how many champions share the water; hue = its age (old gold, new cyan). A champion rides its predecessor’s river for',
 '93–99% of its length: if n≡1 (mod 3) the heir (4n−1)/3 → 4n → 2n → n buys 3 delay for a 4/3 climb — the crown’s cheapest move.',
 'White blazes: revolutions (new rivers, <50% shared). Gold beads: exact heirs — 33/147 links, the atom at 4/3 in the inset ladder.',
 'Records recomputed from scratch, verified to 1e11 (exact A006877 match, both conventions).  MO 514605 · 2026-08-24.']
ytxt = bandy+int(0.040*FINAL)
for c in caps:
    d2.text((mx0, ytxt), c, font=font(fs), fill=(158,168,190)); ytxt += int(fs*1.42)
d2.text((int(0.045*FINAL)+5, int(0.045*FINAL/1.0)//SS*2+5), 'R(k+1)/R(k)  — lines at 4/3 and 2', font=font(fs), fill=(130,160,200))

out.save('hero_%d.png' % FINAL)
print('saved hero_%d.png' % FINAL)
