"""shell.py -- 'A Shell with a Chamber for Every Prime'  (line engraving; Fable 5.2, day 10)

(p^2-1)/(p^2+1) = cos(theta_p) with tan(theta_p/2) = 1/p: the angle of the right triangle (p^2-1, 2p, p^2+1).
Start with an edge of length 1.  Chamber p is that triangle standing on what the last chamber left
(hypotenuse = previous leg), so the leg after all primes up to p is  prod_{q<=p} (q^2-1)/(q^2+1)  -> 2/5.
All corners are rational points.  The lip therefore winds inwards on the circle of radius 2/5 (red) and
never reaches it; it turns for ever (sum theta_p diverges like 2 log log p): a quarter turn by p = 3, half by 43,
three quarters by 5119, once round at p = 141,634,651.
Engraving: growth lines are the scaled copies t*(lip), 0<t<1 (level lines of the gauge G); tone = line width.
usage: shell.py SIZE out.png"""
import sys, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
S = int(sys.argv[1]); out = sys.argv[2]; u = S / 4096.0
N = 2 * 10**6
sv = np.ones(N + 1, bool); sv[:2] = False
for i in range(2, int(N**0.5) + 1):
    if sv[i]: sv[i * i::i] = False
pr = np.nonzero(sv)[0].astype(np.float64)
th = 2 * np.arctan(1 / pr); Phi = np.concatenate([[0.0], np.cumsum(th)])        # Phi[k] = direction of corner P_k
rk = np.concatenate([[1.0], np.cumprod((pr * pr - 1) / (pr * pr + 1))])           # |O P_k|
a0 = np.deg2rad(-38.0)                                                           # direction of the first edge (y up)
Pk = np.stack([rk * np.cos(a0 + Phi), rk * np.sin(a0 + Phi)], 1)
lo, hi = Pk[:400].min(0), Pk[:400].max(0); lo = np.minimum(lo, -0.41); hi = np.maximum(hi, 0.41)
bx0, by0, bx1, by1 = 0.13 * S, 0.085 * S, 0.87 * S, 0.775 * S
R = min((bx1 - bx0) / (hi[0] - lo[0]), (by1 - by0) / (hi[1] - lo[1]))
ox = (bx0 + bx1) / 2 - (lo[0] + hi[0]) / 2 * R; oy = (by0 + by1) / 2 + (lo[1] + hi[1]) / 2 * R
print('R = %.0f px; chambers drawn one by one while 0.4*R*theta > 1.2 px: p < %.0f' % (R, 0.8 * R / 1.2))
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
X = (xx + 0.5 - ox) / R; Y = -(yy + 0.5 - oy) / R
rho = np.hypot(X, Y); psi = np.mod(np.arctan2(Y, X) - a0, 2 * np.pi)
k = np.searchsorted(Phi, psi.ravel(), side='right').reshape(S, S)               # chamber index 1..len(pr); beyond = len+1
last = len(pr); beyond = k > last; kc = np.clip(k, 1, last)
ek = Phi[kc]; r_k = rk[kc]; thk = th[kc - 1]
G = np.where(beyond, rho / 0.4, rho * np.cos(ek - psi) / r_k).astype(np.float32)
r_loc = np.where(beyond, 0.4, r_k).astype(np.float32)                            # px scale of the gauge here
inside = G <= 1.0
aa = lambda d, w: np.clip(w * 0.5 - d + 0.5, 0, 1)
ink = np.zeros((S, S), np.float32)
# ---- growth lines: tone = width ----------------------------------------------------------------
J = int(round(0.4 * R / (13.0 * u)))
pitch = r_loc * R / J
frac = np.clip((psi - Phi[kc - 1]) / thk, 0, 1)                                  # 0 at the old wall, 1 at the new wall of the chamber
vis = np.clip(thk * rho * R / (10 * u), 0, 1) * ~beyond                           # chambers wide enough to be shaded one by one
lightang = np.deg2rad(128.0)
tone = 0.14 + 0.46 * G**1.7 + 0.16 * np.cos(psi + a0 - lightang) * G + 0.30 * vis * (1 - frac)**1.6 * (0.35 + 0.65 * G)
tone = np.clip(tone, 0.07, 0.86)
U = G * J
d = np.abs(U - np.round(U)) * pitch
ink = np.maximum(ink, aa(d, tone * pitch * 0.74) * inside * (G > 0.5 / J))
# ---- chamber walls: full for the first primes, then ticks as long as the gap allows --------------
wall = np.zeros((S, S), np.float32)
for j in (0, -1):                                                                # the two walls of the pixel's chamber
    kb = np.clip(kc + j, 0, last); ang = Phi[kb]; rb = rk[kb]
    gapang = th[np.clip(kb, 0, last - 1)]                                        # the chamber that begins at this wall
    dpx = rho * R * np.abs(np.sin(psi - ang))
    Lf = np.clip(7.0 * gapang, 0, 1); Lf = np.where(kb == 0, 1.0, Lf)
    w = np.clip(0.42 * gapang * 0.4 * R, 0, 2.6 * u); w = np.where(kb == 0, 3.6 * u, w)
    ok = (rho <= rb) & (rho >= rb * (1 - Lf)) & (np.cos(psi - ang) > 0) & ~beyond
    wall = np.maximum(wall, aa(dpx, w) * ok)
ink = np.maximum(ink, wall)
# ---- the lip (G = 1) --------------------------------------------------------------------------------
ink = np.maximum(ink, aa(np.abs(1 - G) * r_loc * R, 3.8 * u) * (G < 1.02))
ink *= (G <= 1.0 + 2.2 * u / (r_loc * R))
# ---- a little ground shadow: horizontal lines, swelling under the shell ------------------------------
shd = ndi.gaussian_filter(inside.astype(np.float32), 26 * u)
shd = np.roll(np.roll(shd, int(46 * u), 0), int(30 * u), 1) * ~inside
py_ = 15 * u; dl = np.abs((yy / py_) - np.round(yy / py_)) * py_
ink = np.maximum(ink, aa(dl, np.clip(shd * 1.5 - 0.06, 0, 0.62) * py_) * ~inside * (shd > 0.06))
# ---- red: the circle of radius 2/5 ---------------------------------------------------------------------
red = aa(np.abs(rho - 0.4) * R, 6.0 * u)
# ---- lettering -------------------------------------------------------------------------------------------
SER = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'; SERI = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
txt = Image.new('L', (S, S), 0); dr = ImageDraw.Draw(txt)
tp = lambda P, push=0.0: (ox + P[0] * R * (1 + push), oy - P[1] * R * (1 + push))
for i in range(1, 15):                                                          # p = 2 ... 43, where the half turn is reached
    mid = (Pk[i - 1] + Pk[i]) / 2; e = np.array([np.cos(a0 + Phi[i]), np.sin(a0 + Phi[i])])
    q = mid + e * (0.050 + 0.012 * (i > 9)); sz = max(30.0, 56.0 - 2.2 * i) * u
    dr.text((ox + q[0] * R, oy - q[1] * R), str(int(pr[i - 1])), font=ImageFont.truetype(SERI, int(sz)), fill=255, anchor='mm')
for pmark, lab in ((5119, '5119'),):
    i = int(np.searchsorted(pr, pmark)) + 1; e = np.array([np.cos(a0 + Phi[i]), np.sin(a0 + Phi[i])])
    q0 = e * (rk[i] + 0.012); q1 = e * (rk[i] + 0.040)
    dr.line([ox + q0[0] * R, oy - q0[1] * R, ox + q1[0] * R, oy - q1[1] * R], fill=255, width=max(1, int(2.4 * u)))
    q = e * (rk[i] + 0.072); dr.text((ox + q[0] * R, oy - q[1] * R), lab, font=ImageFont.truetype(SERI, int(36 * u)), fill=255, anchor='mm')
q = Pk[0] + np.array([np.cos(a0), np.sin(a0)]) * 0.035
dr.text((ox + q[0] * R, oy - q[1] * R), '1', font=ImageFont.truetype(SERI, int(44 * u)), fill=255, anchor='mm')
cy = 0.842 * S
dr.text((S / 2, cy), 'A Shell with a Chamber for Every Prime', font=ImageFont.truetype(SER, int(104 * u)), fill=255, anchor='mm')
dr.text((S / 2, cy + 112 * u), 'Chamber p is the right triangle with sides p² − 1, 2p, p² + 1, standing on the leg the last one left.  The first edge is 1; what is left', font=ImageFont.truetype(SERI, int(50 * u)), fill=235, anchor='mm')
dr.text((S / 2, cy + 176 * u), 'after 2, 3, 5, 7 ... is 3/5 · 4/5 · 12/13 · 24/25 ··· , so the lip closes on the red circle of radius two fifths and never touches it.', font=ImageFont.truetype(SERI, int(50 * u)), fill=235, anchor='mm')
dr.text((S / 2, cy + 262 * u), 'a quarter turn at the prime 3, half a turn at 43, three quarters at 5119, once round at 141,634,651; twice round near 10¹⁸⁸', font=ImageFont.truetype(SER, int(41 * u)), fill=225, anchor='mm')
ink = np.maximum(ink, np.asarray(txt, np.float32) / 255.0)
# ---- print ----------------------------------------------------------------------------------------------
rng = np.random.default_rng(3)
grain = ndi.gaussian_filter(rng.standard_normal((S // 2, S // 2)).astype(np.float32), 0.8)
grain = ndi.zoom(grain, 2, order=1)[:S, :S]
cloud = ndi.zoom(rng.standard_normal((S // 64 + 2, S // 64 + 2)).astype(np.float32), 64, order=3)[:S, :S]
paper = np.array([0.957, 0.940, 0.895], np.float32)[None, None, :] * (1 + 0.012 * grain + 0.014 * cloud)[..., None]
# plate mark: the paper is pressed down inside the plate
pm = np.zeros((S, S), np.float32); m0, m1, n0, n1 = int(0.045 * S), int(0.955 * S), int(0.040 * S), int(0.960 * S)
pm[n0:n1, m0:m1] = 1; pmb = ndi.gaussian_filter(pm, 3 * u); gy, gx = np.gradient(pmb)
paper *= (1 - 0.030 * pm - 2.2 * u * (gx + gy))[..., None]
INK = np.array([0.105, 0.115, 0.185], np.float32); RED = np.array([0.78, 0.20, 0.15], np.float32)
bite = np.clip(ink * (0.93 + 0.10 * grain), 0, 1)[..., None]
img = paper * (1 - bite) + INK * bite * (0.9 + 0.1 * paper)
rr = (0.93 * red)[..., None]; img = img * (1 - rr) + RED * (0.55 + 0.45 * img / paper) * rr      # letterpress red, printed last
# the seal
sx, sy, sw = int(0.888 * S), int(0.905 * S), int(0.026 * S)
img[sy:sy + sw, sx:sx + sw] = img[sy:sy + sw, sx:sx + sw] * 0.12 + RED * 0.88
sl = Image.new('L', (S, S), 0); ImageDraw.Draw(sl).text((sx + sw / 2, sy + sw / 2), '⅖', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(0.019 * S)), fill=255, anchor='mm')
sl = (np.asarray(sl, np.float32) / 255.0)[..., None]; img = img * (1 - sl) + paper * sl
Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)
