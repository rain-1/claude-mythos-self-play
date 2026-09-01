"""THE COMB AND THE STORM — paper marbling by a real fluid (2560²).

Pigment bands laid on the bath, gently raked (exact shear combs), then
advected by the Kelvin-Helmholtz vortex-sheet roll-up (Krasny delta-blob
Birkhoff-Rott).  Rendering is BACKWARD: each pixel is traced back through
the stored velocity frames (RK2, linear time interp), through the inverse
comb, and reads its pigment from the initial bands — infinite-resolution
marbling of an honest Navier-free fluid.
"""
import numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont
from pastel import Watercolor, stroke_polyline, PIGMENTS
from scipy.ndimage import gaussian_filter

SS = 2
FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 900
W = H = FINAL * SS

meta = json.load(open('marble_meta_a.json'))
frames = np.load('marble_frames_a.npy')      # (F,2,g,g)
sheets = np.load('marble_sheet_a.npy')       # (F,2,N)
F, _, g, _ = frames.shape
ys = meta['yspan']
dt_frame = meta['dt'] * meta['ksave']

# canvas -> fluid coords: x in [0,2pi), y in [-YV, YV]
YV = 1.45
px = (np.arange(W, dtype=np.float32) + 0.5) / W * 2 * np.pi
py = (np.arange(H, dtype=np.float32) + 0.5) / H * 2 * YV - YV
X, Y = np.meshgrid(px, py)
X = X.astype(np.float32); Y = Y.astype(np.float32)

def sample_vel(fi, x, y):
    """Bilinear sample of frame fi at fluid coords (periodic x, clamped y)."""
    U = frames[fi, 0]; V = frames[fi, 1]
    gx = x / (2 * np.pi) * g
    gy = (y + ys) / (2 * ys) * (g - 1)
    gx0 = np.floor(gx).astype(np.int32); fx = gx - gx0
    gy0 = np.floor(gy).astype(np.int32)
    np.clip(gy0, 0, g - 2, out=gy0)
    fy = np.clip(gy - gy0, 0, 1).astype(np.float32)
    gx0m = np.mod(gx0, g); gx1m = np.mod(gx0 + 1, g)
    def bi(A):
        return ((A[gy0, gx0m] * (1 - fx) + A[gy0, gx1m] * fx) * (1 - fy) +
                (A[gy0 + 1, gx0m] * (1 - fx) + A[gy0 + 1, gx1m] * fx) * fy)
    return bi(U), bi(V)

# ---- backward trace ---------------------------------------------------------
x, y = X.copy(), Y.copy()
for fi in range(F - 1, 0, -1):
    # RK2 midpoint backward over [fi-1, fi]
    u1, v1 = sample_vel(fi, x, y)
    xm = x - 0.5 * dt_frame * u1; ym = y - 0.5 * dt_frame * v1
    xm = np.mod(xm, 2 * np.pi).astype(np.float32)
    um, vm = sample_vel(fi - 1, xm, ym)   # midpoint in time ~ fi-1/2; use fi-1
    x = np.mod(x - dt_frame * um, 2 * np.pi).astype(np.float32)
    y = (y - dt_frame * vm).astype(np.float32)
    if fi % 20 == 0:
        print(f"  back to frame {fi}", flush=True)

# ---- inverse combs ----------------------------------------------------------
# comb: at t=0 we raked DOWN with teeth at x = c_k: y += A*lam^2/(lam^2+(x-c)^2)
# inverse: y -= .  Two gentle passes, coarse then fine.
def uncomb(x, y, teeth, A, lam):
    for c in teeth:
        dx = np.angle(np.exp(1j * (x - c))).astype(np.float32)  # periodic dist
        y = y - A * lam * lam / (lam * lam + dx * dx)
    return y

y = uncomb(x, y, np.linspace(0, 2 * np.pi, 9, endpoint=False), 0.22, 0.24)
y = uncomb(x, y, np.linspace(0.35, 2 * np.pi + 0.35, 27, endpoint=False), -0.06, 0.07)

# ---- pigment bands ----------------------------------------------------------
BANDS = ['sky', 'rose', 'butter', 'seafoam', 'lilac', 'peach', 'periwinkle']
bandw = 0.34
wc = Watercolor(H, W, seed=31)
t = y / bandw
k = np.floor(t).astype(np.int64)
frac = (t - k).astype(np.float32)
# soft band edges
edge = 0.16
wgt_hi = np.clip((frac - (1 - edge)) / edge, 0, 1) * 0.5
wgt_lo = np.clip(((edge) - frac) / edge, 0, 1) * 0.5
for bi, pig in enumerate(BANDS):
    sel_main = (np.mod(k, len(BANDS)) == bi).astype(np.float32) * (1 - wgt_hi - wgt_lo)
    sel_up = (np.mod(k + 1, len(BANDS)) == bi).astype(np.float32) * wgt_hi
    sel_dn = (np.mod(k - 1, len(BANDS)) == bi).astype(np.float32) * wgt_lo
    dens = 0.62 * (sel_main + sel_up + sel_dn)
    # stretching-based darkening: pigment thins where the flow stretched it
    wc.wash(dens, pig, granulate=0.10)

# ---- the sheet itself, faint graphite filament ------------------------------
sx, sy = sheets[-1]
keep = np.abs(sy) < YV * 0.98
ink = np.zeros((H, W), np.float32)
pxs = sx / (2 * np.pi) * W
pys = (sy + YV) / (2 * YV) * H
run = [ ]
def flush_run(run):
    if len(run) > 3:
        stroke_polyline(ink, np.array(run, np.float32), 1.0 * SS, amp=0.30)
for i in range(len(sx)):
    if keep[i]:
        if run and abs(pxs[i] - run[-1][0]) > 0.2 * W:
            flush_run(run); run = []
        run.append((pxs[i], pys[i]))
    else:
        flush_run(run); run = []
flush_run(run)
wc.wash(ink, 'graphite')

# ---- label ------------------------------------------------------------------
img = Image.new('L', (W, H), 0)
dr = ImageDraw.Draw(img)
try:
    f_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(0.026 * H))
    f_sub = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(0.0105 * H))
except Exception:
    f_title = f_sub = ImageFont.load_default()
title = "The Comb and the Storm"
sub1 = "paper marbling by an honest fluid: pigment bands raked by exact shears, then rolled by the"
sub2 = "Kelvin–Helmholtz instability of a vortex sheet (Birkhoff–Rott, δ-regularized) — every pixel traced back through the storm"
bb = dr.textbbox((0, 0), title, font=f_title)
label_w = max(bb[2], dr.textbbox((0, 0), sub2, font=f_sub)[2]) + int(0.03 * W)
label_h = int(0.075 * H)
lx0 = (W - label_w) // 2; ly0 = int(0.905 * H)
dr.text(((W - bb[2]) / 2, ly0 + 0.006 * H), title, fill=255, font=f_title)
for i, s in enumerate((sub1, sub2)):
    bb2 = dr.textbbox((0, 0), s, font=f_sub)
    dr.text(((W - bb2[2]) / 2, ly0 + 0.040 * H + i * 0.014 * H), s, fill=255, font=f_sub)
tf = np.asarray(img, dtype=np.float32) / 255.0
# paper-colored reserve behind the label: SUBTRACT existing density there
lab_mask = np.zeros((H, W), np.float32)
lab_mask[ly0 - int(0.008 * H):ly0 + label_h, lx0:lx0 + label_w] = 1.0
lab_mask = gaussian_filter(lab_mask, 6 * SS)
wc.D *= (1 - 0.88 * lab_mask)[..., None]
wc.wash(2.0 * gaussian_filter(tf, 0.6 * SS), 'ink')

wc.save(f'marble_{FINAL}.png', final_size=(FINAL, FINAL), dmax=2.4)
print('saved', FINAL)
