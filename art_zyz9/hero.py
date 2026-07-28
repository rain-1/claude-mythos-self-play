"""THE SECOND SHEET - Gamma_0(2) flame field, two cusp families, seven rungs.
Chart: x = Re tau in [-1/2,1/2], y = ln Im tau."""
import numpy as np, sys, time
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from artkit import filmic, to_img, wide_bloom

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
SS = 2 if FINAL >= 2048 else 1
S = FINAL * SS
rs = S / 2400.0

IM_MIN, IM_MAX = 0.0045, 4.75
Y0, Y1 = np.log(IM_MIN), np.log(IM_MAX)
X0, X1 = -0.5, 0.5

def reduce_gamma02(tau, maxit=64):
    t = tau.copy()
    steps = np.zeros(t.shape, np.int32)
    for _ in range(maxit):
        shift = np.round(np.real(t))
        t = t - shift
        moved = shift != 0
        m1 = np.abs(2*t - 1) < 1 - 1e-15
        t = np.where(m1, t/(1 - 2*t), t)
        m2 = (~m1) & (np.abs(2*t + 1) < 1 - 1e-15)
        t = np.where(m2, t/(2*t + 1), t)
        act = moved | m1 | m2
        steps += act.astype(np.int32)
        if not act.any(): break
    return t, steps

def t2A(tau):
    tw = -1/(2*tau)
    te = np.where(np.imag(tw) > np.imag(tau), tw, tau)
    te = np.real(te) + 1j*np.minimum(np.imag(te), 40.0)   # cap: avoid overflow->NaN
    q = np.exp(2j*np.pi*te)
    prod = np.ones_like(q)
    for m in range(1, 26, 2):
        prod = prod * (1 - q**m)**24
    f = prod / q
    return f + 4096.0/f + 24.0

tt = t2A(np.array([1j*np.sqrt(58)/2, 1j*np.sqrt(22)/2, 1j*np.sqrt(2)/2]))
assert abs(tt[0].real - (396**4-104)) < 2e3
assert abs(tt[1].real - 2508952) < 1e-3
assert abs(tt[2].real - 152) < 1e-9
print("t2A engine matches certificates")

t0 = time.time()
imR   = np.zeros((S,S), np.float32)
imF   = np.zeros((S,S), np.float32)
steps = np.zeros((S,S), np.float32)
skel  = np.zeros((S,S), np.float32)
logt  = np.zeros((S,S), np.float32)
CH = max(1, 2**22 // S)
ys = np.exp(np.linspace(Y1, Y0, S))
xs = np.linspace(X0, X1, S)
for r0 in range(0, S, CH):
    r1 = min(S, r0+CH)
    tau = (xs[None,:] + 1j*ys[r0:r1,None]).astype(np.complex128)
    tr, st = reduce_gamma02(tau)
    imR[r0:r1] = np.imag(tr)
    imF[r0:r1] = np.imag(-1/(2*tr))
    steps[r0:r1] = st
    tv = t2A(tr)
    at = np.abs(tv)
    skel[r0:r1] = np.abs(np.imag(tv)) / (at + 1e-9)
    logt[r0:r1] = np.log10(at + 1e-30)
print("field done %.1fs" % (time.time()-t0))

# ---------- compose ----------
rgb = np.zeros((S,S,3), np.float32)
red = steps >= 1                       # pixels that actually reduced (the storm)
haze = np.exp(-steps/30.0)

# flames (only where reduction happened)
fI = np.where(red, np.maximum(imR - 0.5, 0), 0)
fO = np.maximum(imF - 0.5, 0)          # valid everywhere (fundamental-domain neck included)
def tone_flame(f):
    p = np.percentile(f[f>0], 97.0) if (f>0).any() else 1.0
    return (np.minimum(f/p, 2.4))**1.05
fIt = tone_flame(fI); fOt = tone_flame(fO)
COL_I = np.array([0.95, 0.72, 0.34])   # ember gold
COL_O = np.array([0.30, 0.75, 0.85])   # teal
rgb += (1.05*fIt*haze)[...,None]*COL_I[None,None,:]
rgb += (1.15*fOt*haze)[...,None]*COL_O[None,None,:]

# deep ground: subtle petrol by |log t| everywhere reduced
base = np.tanh(np.abs(logt)/9.0)
rgb += np.where(red, 0.045*base, 0)[...,None]*np.array([0.12,0.20,0.36])[None,None,:]

# sky (unreduced): near-black indigo gradient, brightening faintly with log|t|
sky = ~red
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
g = (yy/S)
skyglow = np.where(sky, 0.020 + 0.030*(1-g)*np.tanh(logt/12.0), 0)
rgb += skyglow[...,None]*np.array([0.30,0.38,0.62])[None,None,:]

# t-real web
web = np.exp(-(skel/0.011)**2) * haze**0.35
rgb += (0.52*web)[...,None]*np.array([0.62,0.74,0.92])[None,None,:]

# ---------- digit rungs: ticks where log10|t(iy)| crosses integers ----------
def ypix(y_im): return (Y1 - np.log(y_im))/(Y1-Y0)*S
def xpix(x):    return (x - X0)/(X1-X0)*S
tick = np.zeros((S,S), np.float32)
merid = t2A(1j*ys)                      # t on the meridian, per row
l10 = np.log10(np.abs(merid))
for k in range(3, 11):
    i = np.argmin(np.abs(l10 - k))
    if 0 < i < S-1:
        halfw = 0.052*S*(0.6 + 0.05*k)
        band = np.exp(-((yy - i)/(0.75*rs))**2) * np.exp(-((xx - S/2)/halfw)**4)
        tick += band*0.16
rgb += tick[...,None]*np.array([0.75,0.82,0.95])[None,None,:]

# ---------- rung stars ----------
RUNGS = [(1,152),(2,544),(3,2200),(5,20632),(9,614552),(11,2508952),(29,24591257752)]
star = np.zeros((S,S), np.float32); ring = np.zeros((S,S), np.float32)
for m, val in RUNGS:
    cx, cy = xpix(0.0), ypix(np.sqrt(2*m)/2)
    rad = (1.5 + 2.3*np.log10(val)) * rs
    d2 = (xx-cx)**2 + (yy-cy)**2
    amp = 1.35 if m == 29 else 0.62
    star += amp*np.exp(-d2/(2*(rad*0.26)**2)) + amp*0.42*np.exp(-d2/(2*rad**2))
    if m == 29:
        rr = np.sqrt(d2)
        ring += np.exp(-((rr - 1.8*rad)/(1.2*rs))**2)*0.9
rgb += star[...,None]*np.array([1.0,0.76,0.36])[None,None,:]
rgb += ring[...,None]*np.array([1.0,0.86,0.58])[None,None,:]

# bloom
lum = rgb.max(-1)
bl = wide_bloom(np.maximum(lum-0.7,0).astype(np.float32), 22*rs)
rgb += bl[...,None]*np.array([0.95,0.8,0.55])[None,None,:]*0.42

out = filmic(np.nan_to_num(rgb), 1.28)**0.95
img = to_img(out)

# rung labels (after tonemap, before footer)
imgW = img.size[0]
d2 = ImageDraw.Draw(img)
try:
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", max(9, int(0.0105*imgW)))
except OSError:
    fl = ImageFont.load_default()
LABELS = {1:"152",2:"544",3:"2200",5:"20632",9:"614552",11:"2508952",29:"24591257752 = 396^4-104"}
for m, val in RUNGS:
    cx, cy = xpix(0.0), ypix(np.sqrt(2*m)/2)
    rad = (1.5 + 2.3*np.log10(val)) * rs
    col = (247,216,150) if m == 29 else (150,160,185)
    dy = -0.006*imgW
    if m == 11: dy -= 0.006*imgW
    if m == 9:  dy += 0.006*imgW
    d2.text((cx + rad*2.1 + 0.008*imgW, cy + dy), LABELS[m], font=fl, fill=col)

# ---------- footer text ----------
W = img.size[0]
FH = int(0.088*W)
draw = ImageDraw.Draw(img, 'RGBA')
draw.rectangle([0, W-FH, W, W], fill=(4,6,12,216))
try:
    fs = max(10, int(0.0096*W))
    f_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fs)
    f_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", fs)
except OSError:
    f_mono = f_bold = ImageFont.load_default()
pad = int(0.018*W); ly = W-FH+pad//1
lines = [
 ("THE SECOND SHEET", f_bold, (238,205,140)),
 ("e^{pi sqrt58} = 24591257751.999999822213241469576192...   miss = 4372q + 96256q^2 + 1240002q^3 + ...   (q = e^{-pi sqrt58}; three terms match the miss to 34 digits)", f_mono, (176,188,210)),
 ("T_2A = q^-1 + 4372q + ... :  4372 = 4371+1   96256 = 96255+1   1240002 = 1139374+96255+4371+1+1   (Baby Monster irreps; decompositions unique)", f_mono, (176,188,210)),
 ("1/pi = (2sqrt2/9801) SUM (4k)!(1103+26390k)/(k!)^4 396^{4k} -- eight digits of pi per term; 26390 = 5*7*13*58, 58 = 2*29; h(-232) = 2 = genus count", f_mono, (176,188,210)),
]
for txt, fnt, col in lines:
    draw.text((pad, ly), txt, font=fnt, fill=col)
    ly += int(fs*1.55)

if SS > 1: img = img.resize((FINAL,FINAL), Image.LANCZOS)
img.save("hero_proto.png" if FINAL < 2048 else "hero.png")
print("saved %.1fs" % (time.time()-t0))
