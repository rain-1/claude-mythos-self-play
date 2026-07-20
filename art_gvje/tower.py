"""PANEL 2 (2560x2560): 'The Rose of 65535' - GF(2^16)* as one cyclic orbit.
angle = discrete log (g=258), radius = log2(value)/16 (continuous size of the integer).
Verified structure: 65535 = 3*5*17*257 (the four Fermat primes); the order-255
subgroup IS the integers 1..255; Frobenius doubles the dlog.
"""
import numpy as np, sys, time
from nim import nmul
from render_common import filmic, ramp, fast_bloom, save
from scipy.ndimage import gaussian_filter

S = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
rs = S / 2560.0
t0 = time.time()

dlog = np.load('dlog.npy')
N = 65535
v = np.arange(1, 65536)
k_of_v = dlog[1:]
val_at_k = np.zeros(N, dtype=np.int64)
val_at_k[k_of_v] = v

R_OUT = S * 0.47
def rad_of_val(val):
    return R_OUT * (np.log2(val) / 16.0) ** 0.92

theta = 2*np.pi*np.arange(N)/N - np.pi/2
r_at_k = rad_of_val(val_at_k)
X = S/2 + r_at_k*np.cos(theta)
Y = S/2 + r_at_k*np.sin(theta)

def line_splat(acc, x0, y0, x1, y1, mass, samples_per_px=1.1, chunk=4_000_000):
    L = np.hypot(x1-x0, y1-y0)
    ns = np.maximum(2, (L*samples_per_px).astype(np.int64))
    idx = np.repeat(np.arange(len(x0)), ns)
    cum = np.concatenate([[0], np.cumsum(ns)])
    tpar = (np.arange(int(ns.sum())) - cum[idx]) / ns[idx]
    xs = x0[idx] + (x1-x0)[idx]*tpar
    ys = y0[idx] + (y1-y0)[idx]*tpar
    ms = (mass[idx] if hasattr(mass,'__len__') else np.full(len(idx), mass)) / ns[idx]
    xf = np.floor(xs).astype(np.int64); yf = np.floor(ys).astype(np.int64)
    fx = xs-xf; fy = ys-yf
    for dx, dy, w in [(0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)), (0,1,(1-fx)*fy), (1,1,fx*fy)]:
        gx = xf+dx; gy = yf+dy
        ok = (gx>=0)&(gx<S)&(gy>=0)&(gy<S)
        np.add.at(acc, (gy[ok], gx[ok]), ms[ok]*w[ok])

# --- orbit curtain, colored by mean depth of the segment ---
# split segments into 3 depth classes for coloring: both deep (val small), mixed, both generic
curtain_cool = np.zeros((S, S)); curtain_warm = np.zeros((S, S))
x1r, y1r = np.roll(X,-1), np.roll(Y,-1)
depth = np.minimum(np.log2(val_at_k), np.log2(np.roll(val_at_k,-1))) / 16.0   # min of endpoints
warm_sel = depth < 0.5
line_splat(curtain_cool, X[~warm_sel], Y[~warm_sel], x1r[~warm_sel], y1r[~warm_sel], mass=4.2*rs)
line_splat(curtain_warm, X[warm_sel], Y[warm_sel], x1r[warm_sel], y1r[warm_sel], mass=7.5*rs)
print('curtain', time.time()-t0, flush=True)

# --- dust beads ---
dust = np.zeros((S, S))
bl = np.floor(np.log2(val_at_k)).astype(int) + 1
cnt_b = np.bincount(bl, minlength=17)
mass_bead = (2*np.pi*np.maximum(r_at_k, 3)) / np.maximum(cnt_b[bl],1) * 0.04 * rs
np.add.at(dust, (np.clip(Y,0,S-1).astype(int), np.clip(X,0,S-1).astype(int)), mass_bead)

# --- Frobenius cardioid chords on the subfield dial ring ---
frob = np.zeros((S, S))
sub = np.arange(2, 256)
th_a = 2*np.pi*dlog[sub]/N - np.pi/2
sq = nmul(sub, sub)
th_b = 2*np.pi*dlog[sq]/N - np.pi/2
r_sub = rad_of_val(255.99)
fx0 = S/2 + r_sub*np.cos(th_a); fy0 = S/2 + r_sub*np.sin(th_a)
fx1 = S/2 + r_sub*np.cos(th_b); fy1 = S/2 + r_sub*np.sin(th_b)
line_splat(frob, fx0, fy0, fx1, fy1, mass=np.full(len(sub), 3.0*rs))
# faint dial ring itself
tt = np.linspace(0, 2*np.pi, 3000, endpoint=False)
line_splat(frob, S/2+r_sub*np.cos(tt), S/2+r_sub*np.sin(tt),
           S/2+r_sub*np.cos(np.roll(tt,-1)), S/2+r_sub*np.sin(np.roll(tt,-1)), mass=0.4*rs)

# --- Fermat gears ---
gears = np.zeros((S, S))
for p in [3, 5, 17, 257]:
    ks = np.arange(p) * (N // p)
    gx = S/2 + rad_of_val(val_at_k[ks].astype(float))*np.cos(2*np.pi*ks/N - np.pi/2)
    gy = S/2 + rad_of_val(val_at_k[ks].astype(float))*np.sin(2*np.pi*ks/N - np.pi/2)
    np.add.at(gears, (np.clip(gy,0,S-1).astype(int), np.clip(gx,0,S-1).astype(int)), 1.0)

img = np.zeros((S, S, 3))
cn = curtain_cool / max(np.percentile(curtain_cool[curtain_cool>0], 92), 1e-9)
img += np.clip(cn,0,2.2)[...,None] * np.array([0.28, 0.40, 0.72]) * 0.62
wn = curtain_warm / max(np.percentile(curtain_warm[curtain_warm>0], 85), 1e-9)
img += np.clip(wn,0,2.5)[...,None] * np.array([1.0, 0.75, 0.35]) * 1.15
dn = dust / max(np.percentile(dust[dust>0], 97), 1e-9)
img += np.clip(dn,0,3)[...,None] * np.array([1.0, 0.82, 0.48]) * 0.45
fn = frob / max(np.percentile(frob[frob>0], 96), 1e-9)
img += np.clip(fn,0,2.5)[...,None] * np.array([0.30, 0.90, 1.0]) * 0.8
gb = gaussian_filter(gears, 2.2*rs)*26 + gaussian_filter(gears, 0.9)*7
img += gb[...,None] * np.array([0.95, 0.95, 1.0]) * 0.75
st = np.zeros((S,S)); st[S//2, S//2] = 1
img += (gaussian_filter(st, 8*rs)*900 + gaussian_filter(st, 1.6)*50)[...,None] * np.array([1.0,0.95,0.8])

lum = img @ np.array([0.35,0.5,0.15])
img += fast_bloom(np.clip(lum-0.8,0,None), 12*rs)[...,None]*np.array([0.8,0.85,1.0])*0.5
save(filmic(img, k=1.3, gamma=0.9), f'tower_{S}.png')
print('done', time.time()-t0)
