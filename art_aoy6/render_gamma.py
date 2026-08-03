"""render_gamma.py — THE LEDGER OF HALVES (2560^2)

MO 513837 resolved: sum_{k<=N} (2 - 2^(k-N)) B_k = H_{2^N-1} exactly — the
dyadic weights are nothing but the harmonic series regrouped by odd part.
Chart: every integer n = 2^j * m (m odd) < 2^N at x = log2 m, y = j.
Brightness = 1/n (each row is literally half the row below: the ledger of
halves). The anti-diagonal j = N - log2 m is the frame's shoreline; above
it, the cyan ghosts are the halvings the frame cannot hold — their total
shortfall per column is exactly the 2^(k-N) in the poster's weights.
Bottom strip: digits of gamma gained per layer (log10 2 per layer, exact
error psi(2^N) - N ln2), with the Richardson-doubled staircase as ghost.
"""
import numpy as np
import mpmath as mp
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

SIZE = 2560
W = H = SIZE
rs = SIZE / 1024.0
NLAY = 20

# ---- geometry ----
FX0, FX1 = 90, W - 90            # field x range for log2 m in [0, NLAY]
Y_BOT = 2195                     # row j=0 baseline
ROW = 92                         # px per valuation step
def xf(l2m): return FX0 + l2m / NLAY * (FX1 - FX0)
def yf(j): return Y_BOT - j * ROW

img = np.zeros((H, W, 3))
acc_g = np.zeros((H, W))         # gold beads
acc_c = np.zeros((H, W))         # cyan ghosts

m = np.arange(1, 1 << NLAY, 2, dtype=np.int64)
k = np.int64(np.floor(np.log2(m))) + 1          # layer of m (bitlength)
l2m = np.log2(m.astype(np.float64))

def splat_points(acc, px, py, amp):
    x0 = np.floor(px).astype(np.int64); y0 = np.floor(py).astype(np.int64)
    fx = px - x0; fy = py - y0
    for dx, dy, wt in ((0, 0, (1-fx)*(1-fy)), (1, 0, fx*(1-fy)),
                       (0, 1, (1-fx)*fy), (1, 1, fx*fy)):
        xi = x0 + dx; yi = y0 + dy
        msk = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
        np.add.at(acc, (yi[msk], xi[msk]), (amp * wt)[msk])

print("splatting ledger ...")
for j in range(0, NLAY):
    live = (k - 1 + j) < NLAY            # n = 2^j m < 2^N
    n_log2 = l2m + j
    t = 1.0 - n_log2 / NLAY              # display luminance ramp (log of 1/n)
    lum = np.maximum(t, 0) ** 1.0 * 0.95 + 0.010
    dust = live & (m >= 64)              # m < 64 drawn as explicit pearls
    splat_points(acc_g, xf(l2m[dust]), np.full(dust.sum(), float(yf(j))),
                 lum[dust])
    # ghosts: the missing halvings continue the exponential decay upward
    dead = ~live & ((k - 1 + j) < NLAY + 4)
    if dead.any():
        gamp = 0.0042 * 0.5 ** (n_log2[dead] - NLAY)
        splat_points(acc_c, xf(l2m[dead]), np.full(dead.sum(), float(yf(j))),
                     gamp)

# large pearls for the brightest beads (n small): explicit gaussians
yy, xx = np.ogrid[0:H, 0:W]
for j in range(0, NLAY):
    for mm in range(1, 64, 2):
        if (mm << j) >= (1 << NLAY): continue
        n_log2 = np.log2(mm) + j
        t = 1.0 - n_log2 / NLAY
        r = 2.0 * rs * (0.33 + 0.95 * t ** 1.5)
        cx, cy = xf(np.log2(mm)), yf(j)
        sub = (slice(max(0, int(cy - 5 * r)), min(H, int(cy + 5 * r))),
               slice(max(0, int(cx - 5 * r)), min(W, int(cx + 5 * r))))
        rr2 = (xx[:, sub[1]] - cx) ** 2 + (yy[sub[0], :] - cy) ** 2
        acc_g[sub] += np.exp(-rr2 / (2 * r * r)) * (t ** 1.5 * 0.72 + 0.05)

# hanging chains: each bead connected to its halving above (ALL odd m)
chain = np.zeros((H, W))
xi_c = np.clip(xf(l2m).astype(np.int64), 0, W - 1)
for j in range(1, NLAY):
    livec = (k - 1 + j) < NLAY
    t_up = 1.0 - (l2m + j) / NLAY
    ampc = np.where(livec, np.minimum(2.0 ** (-(l2m + j)) * 26.0, 0.5), 0.0)
    chaincol = np.bincount(xi_c, weights=ampc, minlength=W)
    ys = np.arange(int(yf(j)), int(yf(j - 1)))
    chain[ys, :] += chaincol[None, :]
chain = gaussian_filter(chain, 0.9 * rs)
acc_g += chain * 0.9

acc_g = gaussian_filter(acc_g, 0.8 * rs)
acc_c = gaussian_filter(acc_c, 1.0 * rs)

C_gold = np.array([1.00, 0.76, 0.34])
C_gold_hi = np.array([1.00, 0.93, 0.72])
C_cyan = np.array([0.45, 0.78, 1.00])
g = np.clip(acc_g, 0, None)
gl = 1.0 - np.exp(-g * 2.1)
img += gl[..., None] * (C_gold * (1 - 0.55 * gl[..., None]) + C_gold_hi * 0.55 * gl[..., None]) * 1.25
cl = 1.0 - np.exp(-np.clip(acc_c, 0, None) * 1.9)
img += cl[..., None] * C_cyan * 0.62

# bloom the founding column (m=1: the powers of two) and bright shore
hot = np.where(gl > 0.62, gl - 0.62, 0)
def wide_bloom(layer, sigma):
    ds = max(1, int(sigma / 6))
    small = layer[::ds, ::ds]
    b = gaussian_filter(small, sigma / ds)
    return np.kron(b, np.ones((ds, ds)))[:H, :W]
img += (gaussian_filter(hot, 3 * rs) * 0.5 + wide_bloom(hot, 16 * rs) * 0.3)[..., None] * C_gold

# shoreline: the anti-diagonal j = N - log2 m
sh = np.zeros((H, W))
tt = np.linspace(0, NLAY, 3000)
sx = xf(tt); sy = yf(NLAY - tt)
for x_, y_ in zip(sx, sy):
    xi, yi = int(x_), int(y_)
    if 0 <= xi < W and 0 <= yi < H: sh[yi, xi] += 1.0
sh = gaussian_filter(sh, 1.3 * rs)
img += np.clip(sh, 0, 1.2)[..., None] * np.array([0.85, 0.92, 1.0]) * 0.55

# ---- bottom strip: digits staircase ----
mp.mp.dps = 80
ln2m = mp.log(2)
def E_of(NN): return mp.digamma(mp.mpf(2) ** NN) - NN * ln2m
digs = [float(-mp.log10(abs(E_of(NN)))) for NN in range(1, NLAY + 1)]
Es = [E_of(NN) for NN in range(0, NLAY + 1)]
digsR = [float(-mp.log10(abs(2 * Es[NN] - Es[NN - 1]))) for NN in range(1, NLAY + 1)]
S_Y0, S_Y1 = 2320, 2515          # strip rows
dmax = max(digsR) + 1
def sy_of(dig): return S_Y1 - dig / dmax * (S_Y1 - S_Y0)
stair = np.zeros((H, W))
stairR = np.zeros((H, W))
def draw_step(buf, NN, dig, amp=1.0):
    x_a, x_b = xf(NN - 1.0), xf(float(NN))
    y_ = sy_of(dig)
    n = int(x_b - x_a)
    xs = np.linspace(x_a, x_b, n)
    buf[int(y_), np.clip(xs.astype(int), 0, W - 1)] += amp
for NN in range(1, NLAY + 1):
    draw_step(stair, NN, digs[NN - 1], 1.0)
    draw_step(stairR, NN, digsR[NN - 1], 0.8)
stair = gaussian_filter(stair, 1.2 * rs)
stairR = gaussian_filter(stairR, 1.2 * rs)
img += np.clip(stair, 0, 1.5)[..., None] * np.array([1.0, 0.80, 0.40]) * 1.05
img += np.clip(stairR, 0, 1.5)[..., None] * np.array([0.55, 0.80, 1.0]) * 0.55

# ---- tone map ----
img = 1.0 - np.exp(-1.30 * img)
img = img ** (1 / 1.75)
img += (np.random.default_rng(11).random((H, W, 3)) - 0.5) / 255.0
img = np.clip(img, 0, 1)
out = Image.fromarray((img * 255).astype(np.uint8))

# ---- annotations ----
dr = ImageDraw.Draw(out)
try:
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    Fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
    Fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
    Fi = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 27)
except OSError:
    F = Fs = Fb = Fi = ImageFont.load_default()
gold = (255, 210, 130); cyan = (150, 205, 255); grey = (168, 168, 185)
tx = 1180; ty = 200
dr.text((tx, ty), "THE LEDGER OF HALVES", font=Fb, fill=gold)
dr.text((tx, ty + 78), "every n < 2²⁰ hangs at (log₂ odd part, how many times 2 divides n);", font=F, fill=grey)
dr.text((tx, ty + 120), "each row is exactly half the light of the row below.", font=F, fill=grey)
dr.text((tx, ty + 186), "MO 513837, resolved:  Σₖ (2 − 2ᵏ⁻ᴺ) Bₖ = H₂ᴺ₋₁   exactly —", font=F, fill=gold)
dr.text((tx, ty + 228), "the dyadic weights are the harmonic series regrouped by odd part;", font=F, fill=grey)
dr.text((tx, ty + 270), "the weight 2 − 2ᵏ⁻ᴺ is the chain of halvings the frame can hold,", font=F, fill=grey)
dr.text((tx, ty + 312), "and γ = lim ( H₂ᴺ₋₁ − N ln 2 ) is the classical limit in disguise.", font=F, fill=grey)
dr.text((tx, ty + 372), "the shoreline j = N − log₂ m: beyond it, the ghost halvings —", font=Fi, fill=cyan)
dr.text((tx, ty + 412), "their shortfall per column is exactly the missing 2ᵏ⁻ᴺ.", font=Fi, fill=cyan)
dr.text((FX0 + 8, yf(NLAY - 1) - 58), "m = 1: the powers of two", font=Fs, fill=gold)
dr.text((FX0 + 4, S_Y0 - 50), "digits of γ per layer:  −log₁₀|S_N − γ| = 0.301·N + 0.549…  (error = ψ(2ᴺ) − N ln 2 = −2⁻ᴺ⁻¹ − 4⁻ᴺ/12 − …)", font=Fs, fill=gold)
dr.text((xf(9.2), sy_of(digsR[-1] * 0.72)), "Richardson twin 2S_N − S_{N−1}: slope doubles", font=Fs, fill=cyan)
dr.text((xf(9.0), Y_BOT + 26), "odd numbers — the shore every integer hangs from", font=Fs, fill=(220, 190, 140))
out.save("art_aoy6/ledger_of_halves_2560.png")
print("saved art_aoy6/ledger_of_halves_2560.png")
