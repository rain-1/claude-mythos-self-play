"""
02 — What Silence Computes
Inspired by Philosophy StackExchange front page: "Is silence a valid
mathematical structure?"

We build the honest mathematical object that answers "yes" most literally:
a MANDELBROT MULTIPLICATIVE CASCADE (canonical 2-D multifractal measure). Start
with total mass 1 uniformly spread over the unit square; at every recursive
quadrant split, redistribute each cell's mass among its 4 children by random
(Dirichlet) weights that always sum back to 1. Iterate ~12 times.

The resulting measure is almost everywhere "silent": on a set of full
Lebesgue measure the local density -> 0 as resolution refines (a.e. point has
local scaling exponent alpha(x) > 1, meaning the measure vanishes there faster
than area does -- literal silence, structurally provable, not an accident of
rendering). Yet the *total* mass is exactly 1, all of it concentrated on a
zero-area multifractal support where alpha(x) can be as low as ~0 (spikes as
loud, in the limit, as a point mass). Every point of the square gets its own
well-defined "loudness" alpha(x) = log(measure)/log(cell size) -- the
multifractal spectrum -- and that field IS the piece: we render alpha as hue
(cool = silent regions, hot = singular bursts) and log-measure as luminance,
so the canvas becomes a literal portrait of a structure built entirely out of
near-total silence with rare, precisely located, mathematically necessary
bursts of sound.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

L = 12                      # 2^12 = 4096
N = 2 ** L
rng = np.random.default_rng(20260704)

measure = np.ones((1, 1), dtype=np.float64)

# Dirichlet concentration: smaller alpha0 -> more extreme (spikier) cascades.
# We vary the concentration slightly with level so the cascade doesn't look
# uniformly noisy at every scale (early levels = broad gentle contrast, later
# levels = sharper multiplicative bite), which better matches how a real
# physical multifractal (turbulence dissipation, financial volatility) looks.
# Canonical multiplicative cascade: a FIXED multiset of 4 weights, randomly
# permuted among the 4 children of every cell independently. This is the
# textbook binomial/multinomial cascade (Mandelbrot 1974) -- using a fixed
# multiset (rather than a broad Dirichlet draw) is what gives a cascade its
# sharply defined, reproducible multifractal spectrum instead of washing out
# into homogeneous noise after many levels.
BASE_WEIGHTS = np.array([0.045, 0.115, 0.29, 0.55])
assert abs(BASE_WEIGHTS.sum() - 1.0) < 1e-9

for k in range(L):
    n = measure.shape[0]
    # independent random permutation of the 4 weights per cell: draw 4
    # uniform "sort keys" and argsort -- fully vectorised.
    keys = rng.random((4, n, n))
    order = np.argsort(keys, axis=0)          # order[j,i1,i2] = which weight-rank
    w = BASE_WEIGHTS[order]                    # shape (4,n,n), each column a permutation of BASE_WEIGHTS

    child = np.empty((2 * n, 2 * n), dtype=np.float64)
    # order: 0=TL,1=TR,2=BL,3=BR
    child[0::2, 0::2] = measure * w[0]
    child[0::2, 1::2] = measure * w[1]
    child[1::2, 0::2] = measure * w[2]
    child[1::2, 1::2] = measure * w[3]
    measure = child
    print(f"level {k+1}/{L}: grid {measure.shape}, mass sum={measure.sum():.6f}")

assert measure.shape == (N, N)

# ---------------------------------------------------------------------------
# Multifractal formalism: local Hölder-ish exponent alpha(x) = log(mu)/log(eps)
# where eps = 1/N is the finest cell size. mu is tiny almost everywhere (a.e.
# "silence"), so log(mu) is very negative and alpha is correspondingly large;
# near singular points mu stays large and alpha drops toward its minimum.
# ---------------------------------------------------------------------------
eps = 1.0 / N
log_mu = np.log(np.maximum(measure, 1e-300))
alpha = log_mu / np.log(eps)   # log(eps) is negative; alpha > 0

print("alpha stats:", np.percentile(alpha, [0.01, 1, 50, 99, 99.99]))
print("log_mu stats:", np.percentile(log_mu, [0.01, 1, 50, 99, 99.99]))

# Normalize alpha to [0,1] using robust percentiles (multifractal spectra are
# heavy-tailed; a hard min/max would be dominated by a handful of cells).
a_lo, a_hi = np.percentile(alpha, [0.5, 99.5])
a_norm = np.clip((alpha - a_lo) / (a_hi - a_lo), 0, 1)

# log_mu -> luminance driver; also robust-normalized.
m_lo, m_hi = np.percentile(log_mu, [8, 99.9])
m_norm = np.clip((log_mu - m_lo) / (m_hi - m_lo), 0, 1)

# ---------------------------------------------------------------------------
# Palette: hue sweeps from a near-silent deep indigo/black (high alpha, low
# measure -- "the quiet") through teal and jade, to an incandescent gold/white
# at the rare singular points (low alpha, concentrated measure -- "the sound").
# Luminance is driven mostly by m_norm (measure) so the "silent" majority stays
# genuinely dark and only the true bursts glow -- matching the theorem: almost
# every point really is quiet.
# ---------------------------------------------------------------------------
hue = 0.60 - 0.62 * (1 - a_norm)   # a_norm near 1 (loud) -> hue ~0.60-0.62*0=0.60?
# want: loud (a_norm=0, i.e. alpha near minimum) -> hot hue near 0.08 (gold/amber)
#       quiet (a_norm=1, alpha near max) -> cool hue near 0.66 (indigo)
hue = 0.63 - 0.55 * (1 - a_norm)
hue = np.clip(hue, 0.08, 0.66)

sat = 0.15 + 0.80 * (1 - a_norm) ** 0.7    # louder points get richer, more saturated colour
val_curve = m_norm ** 3.4                   # push the bulk toward dark; only true peaks pop
val = 0.008 + 1.1 * val_curve
val = np.clip(val, 0, 1)

Hf, Sf, Vf = hue.ravel(), sat.ravel(), val.ravel()
i = np.floor(Hf * 6.0)
f = Hf * 6.0 - i
p = Vf * (1 - Sf)
q = Vf * (1 - f * Sf)
t = Vf * (1 - (1 - f) * Sf)
ii = i.astype(int) % 6
conds = [ii == kk for kk in range(6)]
r = np.select(conds, [Vf, q, p, p, t, Vf])
gch = np.select(conds, [t, Vf, Vf, q, p, p])
b = np.select(conds, [p, p, t, Vf, Vf, q])
rgb = np.stack([r, gch, b], axis=-1).reshape(N, N, 3)

# Bloom on the true singular bursts only (very high threshold, they are rare).
lum = 0.2126*rgb[...,0] + 0.7152*rgb[...,1] + 0.0722*rgb[...,2]
mask = np.clip((lum - 0.72) / 0.28, 0, 1) ** 2
bloom_src = rgb * mask[..., None]
b1 = gaussian_filter(bloom_src, sigma=(3, 3, 0))
b2 = gaussian_filter(bloom_src, sigma=(10, 10, 0))
b3 = gaussian_filter(bloom_src, sigma=(28, 28, 0))
final = rgb + 0.55*b1 + 0.35*b2 + 0.22*b3

final = final / (1.0 + final)
final = np.clip(final, 0, 1) ** (1/2.2)

out = (final * 255).astype(np.uint8)
Image.fromarray(out, 'RGB').save('/home/user/claude-mythos-self-play/art_nifty/02_what_silence_computes.png')
print("saved 02")
