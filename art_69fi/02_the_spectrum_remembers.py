"""THE SPECTRUM REMEMBERS -- Riemann's explicit formula as wave-sea.

psi(x) = x - log 2pi - (1/2)log(1-x^-2) - sum_rho x^rho/rho.
In u = ln x, each nontrivial zero rho = 1/2 + i*gamma contributes a pure
cosine of frequency gamma to R(u) = (psi(x) - x)/sqrt(x):
    R_K(u) = -(log 2pi + (1/2)log(1-e^{-2u})) e^{-u/2}
             - sum_{k<=K} 2 cos(gamma_k u - phi_k)/|rho_k|.
We draw every partial sum k = 0..K as one additive thread: the early waves
are a deep slow sea; as k grows the family converges onto the sawtooth that
drops at every prime power (the Gibbs flares ARE the primes announcing
themselves). Brightness = how many partial sums agree; colour = mean k.
Zeros: Odlyzko's table (first 100k, 9 decimals).
"""
import sys, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

ZEROS_PATH = '/tmp/claude-0/-home-user-claude-mythos-self-play/e06df1c8-cf4f-59c4-9d23-ef917a2189a2/scratchpad/zeros1.txt'


def psi_true(xs):
    """Chebyshev psi(x) directly from primes (ground truth for verification)."""
    n = int(xs.max()) + 1
    sieve = np.ones(n + 1, bool); sieve[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    primes = np.nonzero(sieve)[0]
    out = np.zeros_like(xs)
    for p in primes:
        pk = float(p)
        while pk <= xs.max():
            out += (xs >= pk) * np.log(p)
            pk *= p
    return out


def partial_terms(u, gammas):
    """Terms: -2 cos(gamma u - phi)/|rho| for each zero (matrix K x len(u))."""
    rho_abs = np.sqrt(0.25 + gammas ** 2)
    phi = np.arctan2(gammas, 0.5)
    return -2.0 * np.cos(np.outer(gammas, u) - phi[:, None]) / rho_abs[:, None]


STOPS = [(0.00, (0.10, 0.16, 0.45)), (0.30, (0.05, 0.42, 0.55)),
         (0.55, (0.75, 0.30, 0.38)), (0.80, (1.00, 0.62, 0.20)),
         (1.00, (1.05, 0.88, 0.45))]


def ramp_color(t):
    for (p0, c0), (p1, c1) in zip(STOPS[:-1], STOPS[1:]):
        if p0 <= t <= p1:
            f = (t - p0) / (p1 - p0)
            return tuple((1 - f) * a + f * b for a, b in zip(c0, c1))
    return STOPS[-1][1]


def main(W=2560, H=1600, K=64, KFULL=1500, x_lo=1.8, x_hi=62.0, ssx=3,
         amp=190.0, kexp=0.88, name='02_the_spectrum_remembers.png'):
    """WATERFALL: 0..K partial sums as legible wave-threads condensing
    downward, then one blazing LIMIT stroke (KFULL zeros) at the bottom."""
    t0 = time.time()
    gammas = np.loadtxt(ZEROS_PATH)[:KFULL]
    nu = W * ssx
    u = np.linspace(np.log(x_lo), np.log(x_hi), nu)
    x = np.exp(u)
    base = -(np.log(2 * np.pi) + 0.5 * np.log1p(-x ** -2.0)) / np.sqrt(x)

    # VERIFY the explicit formula converges to the truth (von Dyck discipline)
    terms_all = partial_terms(u, gammas)
    R_true = (psi_true(x) - x) / np.sqrt(x)
    R_limit = base + terms_all.sum(0)
    err = np.abs(R_limit - R_true)
    interior = err < np.percentile(err, 90)
    print('verify vs primes: median |R-R_true|=%.4f (interior p90 max %.4f)'
          % (np.median(err), err[interior].max()))
    terms = terms_all[:K]

    RGB = np.zeros((H, W, 3), np.float64)
    pad_t, pad_b = 130, 330
    span = H - pad_t - pad_b
    kk = np.arange(K + 1, dtype=np.float64)
    y0s = pad_t + span * (kk / K) ** kexp
    y_limit = H - 230

    def draw_curve(vals, y0, color, kw):
        yy = y0 - vals * amp * 0.32
        xx = np.arange(nu) / ssx
        y0_, y1_ = yy[:-1], yy[1:]
        x0_, x1_ = xx[:-1], xx[1:]
        nfill = np.minimum(np.ceil(np.maximum(np.abs(y1_ - y0_), 1.0)), 64).astype(np.int64)
        reps = np.repeat(np.arange(nu - 1), nfill)
        tfr = (np.arange(reps.size) - np.repeat(np.cumsum(nfill) - nfill, nfill)) \
              / np.repeat(nfill, nfill)
        px = x0_[reps] + (x1_ - x0_)[reps] * tfr
        py = y0_[reps] + (y1_ - y0_)[reps] * tfr
        w = np.repeat(1.0 / nfill, nfill) * kw
        xi = px.astype(np.int64); fx = px - xi
        yi = py.astype(np.int64); fy = py - yi
        ok = (xi >= 0) & (xi < W - 1) & (yi >= 0) & (yi < H - 1)
        xi, fx, yi, fy, w = xi[ok], fx[ok], yi[ok], fy[ok], w[ok]
        cvec = np.array(color)
        for dx, wxf in ((0, 1 - fx), (1, fx)):
            for dy, wyf in ((0, 1 - fy), (1, fy)):
                ww = (w * wxf * wyf)
                for c in range(3):
                    np.add.at(RGB[..., c], (yi + dy, xi + dx), ww * cvec[c])

    run = base.copy()
    for k in range(K + 1):
        t = (k / K) ** 0.8
        col = ramp_color(0.72 * t)          # waves live in indigo->rose
        bright = 0.7 + 1.0 * t
        draw_curve(run, y0s[k], col, bright)
        if k < K:
            run += terms[k]
        if (k + 1) % 32 == 0:
            print('  k=%d %.0fs' % (k + 1, time.time() - t0))
    # the LIMIT: all KFULL zeros -- the primes, fully remembered
    for rep, w in ((0.0, 4.5), (0.8, 2.0), (-0.8, 2.0)):
        draw_curve(R_limit + rep * 0.004, y_limit, ramp_color(1.0), w)

    np.save('spectrum_RGB.npy', RGB.astype(np.float32))
    img = colorize(RGB)
    Image.fromarray(img).save(name)
    print('saved', name, '%.0fs' % (time.time() - t0))


def colorize(RGB, expo=0.55, k=2.3):
    lum = RGB.sum(2)
    hi = np.percentile(lum[lum > 0], 99.0)
    rgb = np.clip(RGB / hi, 0, None) ** expo
    # saturation lift
    luma = rgb.mean(2, keepdims=True)
    rgb = np.clip(luma + 1.3 * (rgb - luma), 0, None)
    v = np.clip(lum / hi, 0, 3)
    for sig, ampl in ((5, 0.30), (16, 0.20), (46, 0.13)):
        halo = gaussian_filter(np.clip(v - 0.55, 0, None), sig)
        rgb += ampl * halo[..., None] * np.array([1.0, 0.85, 0.55])
    out = 1 - np.exp(-k * rgb)
    return (np.clip(out, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)


if __name__ == '__main__':
    main()
