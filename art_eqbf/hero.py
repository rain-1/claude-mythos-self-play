"""HERO -- The Veil Where Two Pasts Flee.
Base-plane slice through the collision image q*=(-1/4,0,0) of the Alpoge map.
Every pixel is a 'present' (a,b,c); its pasts are the roots of
P(T)=cT^3-2T^2+bT-2a via x=2/P'(t).  The cyan veil is the discriminant locus:
crossing it, two pasts merge in t and flee to +-infinity in x -- the map never
folds (det DF = -2 everywhere), it forgets at infinity.  Cusps = triple roots.
"""
import numpy as np, field, kit
from scipy.ndimage import gaussian_filter, zoom as ndzoom
import sys

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2
S = FINAL * SS
rs = FINAL / 1024.0

u0, u1 = -0.68, 1.12
v0, v1 = -1.8, 1.8   # aspect 1:2  -> use H = S, W = S (window equal, anisotropic ok? keep square canvas, window 1.8x3.6)
H = W = S
uu = (np.linspace(u0, u1, W, dtype=np.float32)[None, :] * np.ones((H, 1), np.float32))
vv = (np.linspace(v1, v0, H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32))
a, b, c = field.slice_abc(uu, vv)
D = field.disc(a, b, c)
U = np.log(np.abs(D) + 1e-14)

# ---- root-dependent fields on a coarse grid, upsampled ----
CO = 4 if S > 2048 else 2
hc, wc = H // CO, W // CO
ac = a[::CO, ::CO].astype(np.float64)
bc = b[::CO, ::CO].astype(np.float64)
cc = c[::CO, ::CO].astype(np.float64)
del a, b, c
t = field.roots_grid(ac, bc, cc)
pp = field.pprime(t, ac, bc, cc)
x = 2.0 / (pp + 1e-300)
absx = np.abs(x)
absx[~np.isfinite(absx)] = 0.0
# escape atmosphere: how far the three pasts have run
esc_c = np.log1p(np.sum(np.minimum(absx, 1e6), axis=-1))
# sheet-phase (outside chamber): geometry of the complex pair vs the real root
imt = np.abs(np.imag(t))
pair_q = np.max(imt, axis=-1)
i_real = np.argmin(imt, axis=-1)
t_real = np.take_along_axis(np.real(t), i_real[..., None], -1)[..., 0]
i_pair = np.argmax(imt, axis=-1)
p_re = np.take_along_axis(np.real(t), i_pair[..., None], -1)[..., 0]
phase_c = np.arctan2(pair_q, p_re - t_real) / np.pi   # in (0,1)

def up(f):
    z = ndzoom(f, CO, order=1)
    return z[:H, :W]
esc = up(esc_c); phase = up(phase_c)
esc = np.clip(esc / np.percentile(esc, 99.0), 0, 1.6)

buf = np.zeros((H, W, 3), np.float32)
inside = D > 0

# 1. base atmosphere: two regimes, lit by the escape field (the wind of flight)
# presence of the pasts: flare as they flee, extinguish where they pass beyond sight
en = np.clip(esc / 1.9, 0, 2.5) ** 1.5 * np.exp(-(esc / 2.75) ** 4)
warm_lo = np.array([0.115, 0.055, 0.023]); warm_hi = np.array([0.85, 0.34, 0.09])
cool_lo = np.array([0.016, 0.036, 0.070]); cool_hi = np.array([0.10, 0.30, 0.38])
glow_in = warm_lo + en[..., None] * warm_hi
glow_out = cool_lo + 0.75 * en[..., None] * cool_hi
buf += np.where(inside[..., None], glow_in, glow_out)
# sheet-phase iridescence outside the chamber (honestly anti-symmetric)
irid = kit.ramp(phase, [(0.0, (0.02, 0.10, 0.16)), (0.5, (0.05, 0.07, 0.18)), (1.0, (0.14, 0.05, 0.15))])
buf += np.where(inside[..., None], 0.0, 1.0) * irid * 0.65

# 2. graded equipotential rings of U = log|Delta| (histogram-equalized level -> dusk ramp)
qs = np.quantile(U, np.linspace(0.001, 0.999, 512))
lev = np.interp(U, qs, np.linspace(0, 1, 512))
Uc = np.maximum(U, -3.6)          # freeze levels below the moat floor
ring = kit.contour_ridge(Uc, 0.32, 1.05 * SS * rs ** 0.5)
ring *= np.clip((U + 3.6) / 1.1, 0, 1)   # fade the last ring into the moat
ringcol = kit.ramp(1 - lev, kit.DUSK)
buf += ring[..., None] * ringcol * (0.62 + 0.55 * (1 - lev[..., None]))

# 2b. escape-equipotentials: contours of how far the pasts have run (interior)
esc_s = gaussian_filter(esc, 1.5 * SS)
ering = kit.contour_ridge(esc_s, 0.16, 0.85 * SS * rs ** 0.5)
ering *= np.clip((U + 3.6) / 1.1, 0, 1)
buf += np.where(inside[..., None], 1.0, 0.12) * ering[..., None] * np.array([0.50, 0.22, 0.08]) * 0.85

# 3. the veil (branch locus) -- cyan blaze with an escape aura
veil = kit.locus_glow(D, 1.6 * SS * rs ** 0.5)
aura = kit.locus_glow(D, 7.0 * SS * rs ** 0.5)
buf += veil[..., None] * kit.CYAN * 0.52
buf += 0.42 * aura[..., None] * np.array([0.10, 0.42, 0.52])

# 4. the wall v=0 (c=0: the third past returns from infinity along x=0)
px_per_v = H / (v1 - v0)
wall_d = np.abs(vv) * px_per_v
wall = np.exp(-(wall_d / (1.3 * SS * rs ** 0.5)) ** 2)
wglow = np.exp(-(wall_d / (9.0 * SS * rs ** 0.5)) ** 2)
buf += 0.9 * wall[..., None] * np.array([0.25, 0.62, 0.66])
buf += 0.22 * wglow[..., None] * np.array([0.10, 0.30, 0.34])

# 5. stars: q* (gold, the collision image) + cusps (ember-white triple roots)
def px(u_, v_): return ((u_ - u0) / (u1 - u0) * W, (v1 - v_) / (v1 - v0) * H)
kit.splat_star(buf, px(0, 0), kit.GOLD, 3.2, 3.5 * SS * rs, 16 * SS * rs, 0.45)
for s in (1, -1):
    kit.splat_star(buf, px(field.U_CUSP, s), np.array([1.0, 0.75, 0.45]), 2.6, 2.6 * SS * rs, 11 * SS * rs, 0.5)

buf = kit.bloom(buf, 5 * SS * rs, 0.55, thresh=0.60)
out = kit.filmic(buf, 1.25, 0.94)
kit.save(out, f"hero_{FINAL}.png", down=SS)
