"""THE SHORE NEAREST ONE -- harmonic knapsack (MO 511838): kelp columns, record stars, lcm lighthouse."""
import numpy as np, sys, re
from math import lcm
from scipy.ndimage import gaussian_filter, grey_dilation
from kit import splat_points, line_splat, wide_bloom, filmic, to_img, text_layer
from PIL import Image as PImage

rs = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
SS = 2
S = int(640*rs); H = W = S*SS

records = {2:(2,1),3:(6,1),4:(12,1),5:(60,1),6:(60,1),7:(420,2),8:(840,4),9:(2520,1),10:(2520,1),
           11:(27720,7),12:(27720,7),13:(360360,5),14:(360360,5),15:(360360,5),16:(720720,7),
           17:(12252240,7),18:(12252240,7),19:(232792560,110),20:(232792560,68),21:(232792560,68),
           22:(232792560,48),23:(5354228880,39),24:(5354228880,39),25:(26771144400,34),
           26:(26771144400,34),27:(80313433200,102),28:(80313433200,102)}

N0, N1 = 2, 28
YMAX = 11.4          # -log10 distance axis top
XPAD = 0.075*W
def pxn(n): return XPAD + (n - N0)/(N1 - N0)*(W - 2*XPAD)
Y_BOT, Y_TOP = 0.845*H, 0.075*H
def py(v): return Y_BOT - v/YMAX*(Y_BOT - Y_TOP)

acc = np.zeros((H, W, 3))

# ---- kelp columns from bandsfine files ----
KELP = np.array([0.10,0.55,0.48])
KELP_HI = np.array([0.55,0.95,0.75])
import os
COLS = [n for n in (4,6,8,9,12,14,16,18,20,22,24,26,28) if os.path.exists(f'shore/bandsfine_{n}.txt')]
kelp_layer = np.zeros((H, W))
for n in COLS:
    lines = open(f'shore/bandsfine_{n}.txt').read().strip().split('\n')
    m = re.match(r'# n=(\d+) L=(\d+) bpd=(\d+)', lines[0])
    L, BPD = int(m.group(2)), int(m.group(3))
    dat = np.array([[int(v) for v in l.split()] for l in lines[1:]])
    cnt, tot = dat[:,1].astype(float), np.maximum(dat[:,2].astype(float), 1)
    frac = cnt/tot
    present = cnt > 0
    logL = np.log10(L)
    val = np.where(present, 0.10 + 0.90*frac**0.55, 0.0)
    xc = pxn(n)
    wcol = (pxn(3) - pxn(2))*0.40
    for j in range(len(val)):
        if val[j] <= 0: continue
        v_hi = logL - j/BPD
        v_lo = logL - (j+1)/BPD
        yy0, yy1 = int(py(v_hi)), int(py(v_lo))
        if yy1 <= yy0: yy1 = yy0 + 1
        if yy1 < 0 or yy0 > H: continue
        kelp_layer[max(yy0,0):min(yy1,H), int(xc-wcol):int(xc+wcol)] = np.maximum(
            kelp_layer[max(yy0,0):min(yy1,H), int(xc-wcol):int(xc+wcol)], val[j])
kelp_layer = gaussian_filter(kelp_layer, 1.0*SS*rs)
tfield = np.clip((Y_BOT - np.arange(H))/(Y_BOT - Y_TOP), 0, 1)
col3 = KELP[None, :]*(1-tfield[:, None]) + KELP_HI[None, :]*tfield[:, None]
acc += kelp_layer[:, :, None]*col3[:, None, :]*0.85

# ---- record staircase + stars ----
GOLD = np.array([1.0,0.80,0.38])
ns = np.array(sorted(records))
gv = np.array([np.log10(records[n][0]/records[n][1]) for n in ns])
xs_, ys_ = pxn(ns.astype(float)), py(gv)
ln = np.zeros((H, W))
line_splat(ln, xs_[:-1], ys_[:-1], xs_[1:], ys_[1:], 1.0, H, W, mass_per_length=True)
ln = grey_dilation(ln, size=(max(1, int(0.9*SS*rs)),)*2)
acc += ln[:, :, None]*GOLD[None, None, :]*0.5
st = np.zeros((H, W))
splat_points(st, xs_, ys_, np.full(len(xs_), 60.0*SS*SS*rs*rs), H, W)
st = gaussian_filter(st, 2.0*SS*rs)
acc += st[:, :, None]*GOLD[None, None, :]*1.1

# ---- lcm lighthouse ceiling ----
SILVER = np.array([0.80,0.88,1.0])
lv = np.array([np.log10(lcm(*range(1, n+1))) for n in ns])
lx, ly = pxn(ns.astype(float)), py(lv)
ln = np.zeros((H, W))
# staircase: horizontal then vertical segments
for i in range(len(ns)-1):
    line_splat(ln, np.array([lx[i]]), np.array([ly[i]]), np.array([lx[i+1]]), np.array([ly[i]]),
               1.0, H, W, mass_per_length=True)
    if ly[i+1] != ly[i]:
        line_splat(ln, np.array([lx[i+1]]), np.array([ly[i]]), np.array([lx[i+1]]), np.array([ly[i+1]]),
                   1.0, H, W, mass_per_length=True)
ln = grey_dilation(ln, size=(max(1, int(0.8*SS*rs)),)*2)
acc += ln[:, :, None]*SILVER[None, None, :]*0.55
# beam glow at jumps (prime powers)
jumps = [i+1 for i in range(len(ns)-1) if lv[i+1] > lv[i] + 1e-9]
jx, jy = lx[jumps], ly[jumps]
st = np.zeros((H, W))
splat_points(st, jx, jy, np.full(len(jumps), 40.0*SS*SS*rs*rs), H, W)
st = gaussian_filter(st, 2.2*SS*rs)
acc += st[:, :, None]*SILVER[None, None, :]*0.8

# ---- open-water wedge between records and ceiling ----
nn_f = np.linspace(N0, N1, W)
rec_y = np.interp(nn_f, ns.astype(float), ys_*0 + gv)   # in v units
ceil_v = np.interp(nn_f, ns.astype(float), lv)
rowv = (Y_BOT - np.arange(H)[:, None])/(Y_BOT - Y_TOP)*YMAX
wedge = (rowv > np.interp(nn_f, ns.astype(float), gv)[None, :]) & (rowv < ceil_v[None, :])
rng = np.random.default_rng(7)
noise = rng.random((H, W))*0.5 + 0.5
acc += wedge[:, :, None]*np.array([0.16,0.22,0.42])[None, None, :]*0.10*noise[:, :, None]

# ---- exact-hit floor: d=0 (sums = lcm exactly achievable? no: sums < 1). baseline ----
ln = np.zeros((H, W))
line_splat(ln, np.array([0.0]), np.array([Y_BOT*1.0]), np.array([float(W)]), np.array([Y_BOT*1.0]),
           1.0, H, W, mass_per_length=True)
ln = grey_dilation(ln, size=(max(1, int(0.6*SS*rs)),)*2)
acc += ln[:, :, None]*np.array([0.35,0.45,0.55])[None, None, :]*0.4

# ---- sea reflection below baseline ----
above = acc[:int(Y_BOT), :, :]
refl = above[::-1, :, :]
n_refl = H - int(Y_BOT)
refl = refl[:n_refl]
refl = gaussian_filter(refl, (5.0*SS*rs, 1.2*SS*rs, 0))
fade = np.linspace(0.30, 0.02, n_refl)[:, None, None]
acc[int(Y_BOT):int(Y_BOT)+n_refl, :, :] += refl*fade*np.array([0.7,0.9,1.1])[None,None,:]
# horizon glow
hg = np.exp(-((np.arange(H) - Y_BOT)/(0.02*H))**2)[:, None]
acc += hg[:, :, None]*np.array([0.25,0.45,0.55])[None,None,:]*0.16

# ---- bloom + bg ----
lum = acc.sum(axis=2)
nz = lum[lum > 0.02*lum.max()]
th = np.percentile(nz, 97.5)
mask = np.clip((lum - th)/(lum.max() - th + 1e-9), 0, 1)
bl = wide_bloom(lum*mask, 13*SS*rs)
acc += bl[:, :, None]*np.array([0.9,0.95,0.85])[None, None, :]*0.4
acc += gaussian_filter(lum, 2.0*SS*rs)[:, :, None]*0.15*np.array([0.9,1.0,0.95])[None, None, :]

grad = np.linspace(0, 1, H)[:, None]*np.ones((1, W))
acc += (0.015 + 0.022*grad)[:, :, None]*np.array([0.25,0.40,0.60])[None, None, :]

img = filmic(acc, k=1.35, gamma=0.90)

def sup(k):
    S_ = {'0':'\u2070','1':'\u00b9','2':'\u00b2','3':'\u00b3','4':'\u2074','5':'\u2075',
          '6':'\u2076','7':'\u2077','8':'\u2078','9':'\u2079','-':'\u207b'}
    return ''.join(S_[c] for c in str(k))
fs = int(8.0*SS*rs); fm = int(6.3*SS*rs)
IV = (0.72,0.78,0.92); GD = (0.98,0.82,0.45); CY = (0.55,0.95,0.90); DIM = (0.45,0.50,0.66); SL = (0.75,0.82,0.95)
draws = [
  (0.035*W, 0.035*H, "T H E   S H O R E   N E A R E S T   O N E", int(11*SS*rs), (0.95,0.88,0.70)),
  (0.035*W, 0.035*H + 2.0*fs, "sums \u03a3 1/a\u1d62 < 1 with denominators \u2264 n, repetition allowed \u2014 how close can they come?", fm, IV),
  (0.035*W, 0.035*H + 3.5*fs, "every reachable sum charted by its distance to 1;  gold = the record;  silver = the 1/lcm(1..n) lighthouse", fm, DIM),
  (0.035*W, 0.035*H + 5.0*fs, "MathOverflow 511838, asked this week \u2014 the asymptotic law of the gap is OPEN", fm, DIM),
]
for dec in (1,2,3,4,5,6,7,8,9,10):
    draws.append((0.012*W, py(dec) - 0.7*fm, "10"+sup(-dec), fm, DIM))
for n in (4,6,8,9,12,14,16,18,20,22,24,26,28):
    draws.append((pxn(n), Y_BOT + 1.0*fm, str(n), fm, (0.62,0.66,0.60), {'anchor':'ma'}))
draws += [
  (pxn(12) + 0.008*W, py(np.log10(3960)) - 2.0*fm, "1/3960 \u2014 the question's own example, reproduced", fm, GD),
  (pxn(9) - 0.008*W, py(np.log10(2520)) - 1.6*fm, "1/2520 = 1/lcm \u2014 perfect", fm, GD, {'anchor':'ra'}),
  (pxn(25) - 0.010*W, py(np.log10(787386600)) + 1.2*fm, "1/787 386 600", fm, GD, {'anchor':'ra'}),
  (pxn(22) + 0.014*W, py(10.3), "the lighthouse: 1/lcm(1..n)", fm, SL, {'anchor':'ra'}),
  (pxn(20), py(8.9), "open water", fs, (0.55,0.62,0.85)),
  (0.5*W, 0.955*H, "records n=2..28 exact (bit-packed unbounded-knapsack DP over lcm(1..n) states, up to 8.0\u00d710\u00b9\u2070);  champion at n=25:  1/9+1/10+1/11+3/13+3/19+2/21+1/22+2/23+1/24+1/25 = 1 \u2212 1/787386600", fm, (0.5,0.55,0.68), {'anchor':'ma'}),
]
tl = text_layer(H, W, draws)
img = np.clip(img + tl, 0, 1)
out = to_img(img).resize((S, S), PImage.LANCZOS)
out.save('shore_proto.png' if rs < 2 else 'shore_nearest_one.png')
print("saved", S)
