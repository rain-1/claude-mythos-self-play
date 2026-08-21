#!/usr/bin/env python3
"""THE DESERT BETWEEN — the quartic oval of MO 514415, its one small door,
and the combed emptiness below.

Top: the real oval D^2 = -Q(r); gold star = the seed point (e = 14489).
Below the axis: depth = log10(denominator q).  Comb rows q <= 360 lit by
their exact quadratic-residue survivor density; the sieve-swept haze down to
the certified line q = 3*10^5 (hyperellratpoints: EMPTY); the seed's plumb
bead hangs just past the last lamppost at q = 1,242,748.
Right: the height ladder n^2*39.84 with e-digit rungs 5 / 73 / 212 / 420 and
the gold threshold e = 10^20 -- only the seed lives below it.
"""
import numpy as np, json, sys
from scipy.ndimage import gaussian_filter
import artlib

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
SS   = int(sys.argv[2]) if len(sys.argv) > 2 else 1
OUT  = sys.argv[3] if len(sys.argv) > 3 else 'desert_prev.png'
S = SIZE*SS
rs = S/2560.0

GOLD  = np.array([1.00, 0.78, 0.30])
EMBER = np.array([1.00, 0.45, 0.18])
ICE   = np.array([0.55, 0.85, 1.00])
VIOL  = np.array([0.62, 0.40, 0.95])
SAND  = np.array([0.85, 0.70, 0.45])

C = [35534992, 3306770731944, 15172317493269316128,
     1093490321304049798772416, 18958669594580211381729967107]
def Qval(r):
    return (((C[0]*r + C[1])*r + C[2])*r + C[3])*r + C[4]
R_LO, R_HI = -43694.688550255774, -28782.776780479772
R_SEED = -48044056139/1242748

buf = artlib.canvas(S)

# ---------- layout ----------
xl, xr = 0.07*S, 0.80*S          # main panel horizontal span
def x_of_r(r): return xl + (r - R_LO)/(R_HI - R_LO)*(xr - xl)
y_axis = 0.315*S                  # the rational line (surface of the desert)
oval_h = 0.21*S                   # oval max half-height above axis
y_depth0, y_depth1 = y_axis, 0.865*S   # depth panel: log10 q in [0, 7]
def y_of_logq(lq): return y_depth0 + (lq/7.0)*(y_depth1 - y_depth0)

# ---------- the oval ----------
rr = np.linspace(R_LO, R_HI, 4200)
Dv = np.sqrt(np.maximum(-np.array([float(Qval(float(x))) for x in rr]), 0.0))
Dmax = Dv.max()
yy_up = y_axis - (Dv/Dmax)*oval_h
yy_dn = y_axis + (Dv/Dmax)*0.055*S     # faint mirror below the axis (into the ground)
pts_up = np.stack([x_of_r(rr), yy_up], 1)
artlib.polyline(buf, pts_up, VIOL*0.85 + ICE*0.15, amp=0.16*rs, step=0.6)
artlib.polyline(buf, np.stack([x_of_r(rr), yy_dn], 1), VIOL*0.35, amp=0.05*rs, step=0.7)
# oval interior: true 2-D soft fill (the possible region)
ytop_arr = y_axis - (Dv/Dmax)*oval_h
x_pix = np.arange(S)
Dv_at = np.interp(x_pix, x_of_r(rr), (Dv/Dmax)*oval_h, left=0, right=0)
yy2 = np.arange(int(y_axis - oval_h - 4), int(y_axis)+1)
sub = np.zeros((len(yy2), S), np.float32)
for i, y in enumerate(yy2):
    depth = (y_axis - y)
    insideo = depth < Dv_at
    t = np.where(Dv_at > 0, depth/np.maximum(Dv_at, 1e-9), 1.0)
    sub[i] = np.where(insideo, (1 - t**2)**1.4 * 0.065 + 0.018*np.exp(-((Dv_at-depth)/(9*rs))**2), 0.0)
for c in range(3):
    buf[yy2[0]:yy2[-1]+1, :, c] += sub*(VIOL*0.7 + ICE*0.3)[c]
del sub

# the rational line (surface)
artlib.polyline(buf, np.array([[xl-8*rs, y_axis],[xr+8*rs, y_axis]]), SAND*0.8, amp=0.10*rs, step=0.6)

# ---------- seed star on the oval ----------
xs_seed = x_of_r(R_SEED)
Dseed = np.sqrt(-float(Qval(R_SEED)))
ys_seed = y_axis - Dseed/Dmax*oval_h
artlib.star(buf, xs_seed, ys_seed, GOLD, amp=7.0*rs*rs, rad=9.0*rs)

# ---------- comb rows: exact survivor densities ----------
rows = json.load(open('sieve_rows.json'))
rng = np.random.default_rng(7)
for (qd, npts, nsurv) in rows:
    lq = np.log10(qd) if qd > 1 else 0.0
    y = y_of_logq(lq)
    dens = nsurv/max(npts,1)
    b = (dens/0.00135)**0.75 if dens > 0 else 0.0     # max row density ~0.00135
    n_dust = min(int(nsurv*0.05) + (10 if nsurv else 0), 1400)
    if n_dust and qd > 1:
        xs = xl + rng.random(n_dust)*(xr-xl)
        ys = y + rng.normal(0, 0.5*rs, n_dust)
        artlib._splat_points(buf, xs, ys, 0.22*rs*min(b,1.4) + 0.02*rs, SAND, 1.0)
    artlib.polyline(buf, np.array([[xl, y],[xr, y]]), SAND*min(b,1.1),
                    amp=(0.030 + 0.085*min(b,1.3))*rs, step=0.9)

# ---------- swept haze from q=360 to 3e5 ----------
y_a, y_b = y_of_logq(np.log10(360)), y_of_logq(np.log10(3e5))
yy, xx = np.mgrid[0:S, 0:S]
band = np.clip((yy - y_a)/(y_b - y_a), 0, 1)
rake = 0.75 + 0.45*np.sin(xx*(2*np.pi/(3.1*rs*4)))**2
soft = np.clip((yy - (y_a-6*rs))/(12*rs), 0, 1)*np.clip(((y_b+6*rs) - yy)/(12*rs), 0, 1)
haze = np.where((xx > xl) & (xx < xr), 0.075*(1 - 0.40*band)*soft, 0.0)
grain = rng.random((S, S))*0.5 + 0.75
for c in range(3):
    buf[:,:,c] += haze*grain*rake*(ICE*0.80 + SAND*0.20)[c]
del soft
del yy, xx, band, haze, grain, rake

# certified sweep line (ice)
y_sw = y_of_logq(np.log10(3e5))
artlib.polyline(buf, np.array([[xl, y_sw],[xr, y_sw]]), ICE, amp=0.55*rs, step=0.6)

# ---------- the seed's plumb ----------
y_seed_depth = y_of_logq(np.log10(1242748))
artlib.polyline(buf, np.array([[xs_seed, y_axis],[xs_seed, y_seed_depth]]),
                GOLD*0.55, amp=0.06*rs, step=0.7)
artlib.star(buf, xs_seed, y_seed_depth, GOLD, amp=8.0*rs*rs, rad=10.0*rs)

# 2G plumbs: true r positions; their denominators (41 and 110 digits) exit the frame
for r2g in (-29990.77098537705, -43667.886879580285):
    artlib.polyline(buf, np.array([[x_of_r(r2g), y_of_logq(6.72)],[x_of_r(r2g), S*1.01]]),
                    VIOL*0.7, amp=0.07*rs, step=0.7)
    artlib.star(buf, x_of_r(r2g), y_of_logq(6.72), VIOL, amp=1.6*rs*rs, rad=4.5*rs)

# ---------- height ladder (right margin) ----------
lx = 0.868*S
y_top, y_bot = 0.10*S, 0.865*S
hmax = 4.4**2*39.84
def y_of_h(h): return y_top + (h/hmax)*(y_bot - y_top)
artlib.polyline(buf, np.array([[lx, y_of_h(0)],[lx, y_bot]]), np.array([0.5,0.5,0.6])*0.7, amp=0.05*rs, step=0.7)
digs = {1:5, 2:73, 3:212, 4:420}
for n in (1,2,3,4):
    h = n*n*39.84442622
    y = y_of_h(h)
    cc = GOLD if n == 1 else (VIOL if n >= 3 else ICE)
    artlib.polyline(buf, np.array([[lx-14*rs, y],[lx+14*rs, y]]), cc, amp=0.22*rs, step=0.6)
    artlib.star(buf, lx, y, cc, amp=3.0*rs*rs, rad=5.5*rs)
# e = 10^20 threshold: interpolate in digits space between rung1(5 digits) and rung2(73)
h_thresh = 39.84*(1 + (20-5)/(73-5)*3)      # crude linear-in-digits between n^2*h: h in [39.84,159.4]
y_th = y_of_h(h_thresh)
artlib.polyline(buf, np.array([[lx-22*rs, y_th],[lx+22*rs, y_th]]), GOLD, amp=0.16*rs, step=0.6)

artlib.bloom(buf, sigmas=(2*max(rs,0.5), 9*rs, 30*rs), weights=(1.0, 0.30, 0.14))
img = artlib.tonemap(buf, k=1.35, gamma=0.93)

if SS > 1:
    from PIL import Image
    im = Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((SIZE,SIZE), Image.LANCZOS)
    img = np.asarray(im).astype(np.float32)/255.0
F = SIZE
yl1, yl2, yl3, yl4 = [ (0.10 + (n*n*39.84442622/hmax)*(0.865-0.10)) for n in (1,2,3,4) ]
ylth = 0.10 + (39.84*(1 + (20-5)/(73-5)*3)/hmax)*(0.865-0.10)
ylth += 0.013
texts = [
 (F*0.5, F*0.045, "T H E   D E S E R T   B E T W E E N", int(F*0.021), (0.93,0.90,0.82), True, 'mm'),
 (F*0.5, F*0.075, "a⁴+b⁴+c⁴+d⁴ = (a+27b+27c+27d)⁴  ·  the rational points of one quartic oval  ·  MathOverflow 514415, zero answers", int(F*0.0095), (0.62,0.63,0.68), False, 'mm'),
 (F*0.325, F*0.105, "D² = −(35534992·r⁴ + … + 18958669594580211381729967107)   ·   the window  −43694.7 < r < −28782.8   is all the room the equation allows", int(F*0.0072), (0.50,0.52,0.58), False, 'mm'),
 (F*0.035, F*0.330, "q = 1", int(F*0.0075), (0.55,0.50,0.42), False, 'lm'),
 (F*0.035, F*0.610, "combed rows: every rational r = p/q, brightness = exact survivor density of the 9-modulus square sieve", int(F*0.0072), (0.55,0.50,0.42), False, 'lm'),
 (F*0.035, F*0.760, "hyperellratpoints: certified EMPTY to q = 300,000", int(F*0.0078), (0.62,0.80,0.92), False, 'lm'),
 (F*0.035, F*0.800, "the seed hangs just past the last lamppost:  r = −48044056139 / 1242748  →  13355⁴+8010⁴+9498⁴+1530⁴ = 14489⁴,  e = a+27(b+c+d) exactly", int(F*0.0072), (0.85,0.72,0.42), False, 'lm'),
 (F*0.845, F*0.055, "the ladder of heights", int(F*0.0080), (0.62,0.63,0.68), False, 'lm'),
 (F*0.845, F*0.082, "ĥ(nG) = n²·39.844", int(F*0.0070), (0.50,0.52,0.58), False, 'lm'),
 (F*0.882, F*yl1, "n=1 · e = 14489 · 5 digits", int(F*0.0066), (0.85,0.72,0.42), False, 'lm'),
 (F*0.882, F*ylth, "e = 10²⁰ — the horizon", int(F*0.0066), (0.85,0.72,0.42), False, 'lm'),
 (F*0.882, F*yl2, "n=2 · 73 digits", int(F*0.0066), (0.62,0.80,0.92), False, 'lm'),
 (F*0.882, F*yl3, "n=3 · 212 digits", int(F*0.0066), (0.70,0.58,0.92), False, 'lm'),
 (F*0.882, F*yl4, "n=4 · 420 digits", int(F*0.0066), (0.70,0.58,0.92), False, 'lm'),
 (F*0.5, F*0.900, "the Jacobian has rank ≥ 1 (2-descent bound 3, trivial torsion) · the seed is divisible by no k ≤ 6: it is a generator, height ĥ = 39.844 · effort-5 descent finds nothing smaller", int(F*0.0072), (0.58,0.60,0.66), False, 'mm'),
 (F*0.5, F*0.917, "between the seed and its double lies a desert of sixty-eight decimal digits — any new solution with e < 10²⁰ must enter by a second generator of height < 66, and none is anywhere to be found", int(F*0.0072), (0.58,0.60,0.66), False, 'mm'),
 (F*0.5, F*0.934, "every identity above is verified in exact arithmetic: the seed, its double (73 digits), its triple (212 digits) all satisfy a⁴+b⁴+c⁴+d⁴ = (a+27b+27c+27d)⁴ on the nose", int(F*0.0072), (0.58,0.60,0.66), False, 'mm'),
]
img = artlib.bake_text(img, texts, F)
artlib.save(img, OUT)
print("saved", OUT)
