"""THE RIVER AND ITS GHOST -- the discrete Brownian web and its time-reversal
dual. Gold: coalescing random walks falling from every point of the first
moment; rain condenses into brooks, brooks into rivers. Blue: the dual web,
running BACKWARD through the same coin-field, threading the corridors the
gold rivers leave -- provably never crossing them (verified in web_core).
Row axis is warped by the empirical merge-event CDF so the cascade of
identity-mergings is visible at every height.
"""
import sys, time
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from PIL import Image
import web_core, web_fast

NB = 6


def sample_times(warp, T, H):
    """Fractional time per row + the union of bracketing integer times."""
    s = np.linspace(0, 1, 16384)
    w = np.asarray(warp(s))
    targets = (np.arange(H) + 0.5) / H
    tf = np.clip(np.interp(targets, w, s) * T, 0, T)
    lo = np.floor(tf).astype(np.int64)
    hi = np.minimum(lo + 1, T)
    return tf, np.unique(np.concatenate([lo, hi]))


def rows_from_samples(X, M, utimes, tf):
    """Per-row positions by linear time-interpolation between the two
    bracketing samples (kills plateau/stair artifacts in stretched zones)."""
    H = tf.size
    n0 = X.shape[1]
    Xr = np.empty((H, n0), np.float32)
    Mr = np.empty((H, n0), np.int32)
    idx = np.searchsorted(utimes, tf, side='right') - 1
    idx = np.clip(idx, 0, len(utimes) - 2)
    for r in range(H):
        i = idx[r]
        t0_, t1_ = utimes[i], utimes[i + 1]
        a = 0.0 if t1_ == t0_ else (tf[r] - t0_) / (t1_ - t0_)
        Xr[r] = (1 - a) * X[i] + a * X[i + 1]
        Mr[r] = M[i] if a < 0.5 else M[i + 1]
    return Xr, Mr


def splat(X, M, W, ss, sig_t, mexp=1.0):
    """Deposit with FRACTIONAL mass-bands (continuous width growth)."""
    Xs = gaussian_filter1d(X, sig_t, axis=0, mode='nearest') / ss
    H = X.shape[0]
    bands = np.zeros((NB, H, W), np.float32)
    bf_all = np.clip(np.log2(np.maximum(M, 1)).astype(np.float32) / 2, 0, NB - 1 - 1e-4)
    for j in range(H):
        w_arr = M[j].astype(np.float32) ** (mexp - 1.0)
        x = np.mod(Xs[j], W)
        x0 = x.astype(np.int64); f = (x - x0).astype(np.float32)
        x1 = (x0 + 1) % W
        k0 = bf_all[j].astype(np.int64)
        kf = bf_all[j] - k0
        for k in range(NB):
            wk = np.where(k0 == k, 1 - kf, np.where(k0 + 1 == k, kf, 0)).astype(np.float32)
            m = wk > 0
            if m.any():
                np.add.at(bands[k, j], x0[m], (1 - f[m]) * w_arr[m] * wk[m])
                np.add.at(bands[k, j], x1[m], f[m] * w_arr[m] * wk[m])
    return bands


def flatten(bands, base_sig, grow, gains=None):
    out = np.zeros(bands.shape[1:], np.float32)
    for k in range(bands.shape[0]):
        sig = base_sig * grow ** k
        g = 1.0 if gains is None else gains[k]
        out += g * gaussian_filter(bands[k], (sig * 0.5, sig))
    return out


def tone(acc, p_hi=99.7, gamma=0.5):
    a = np.log1p(acc)
    nz = a[a > 0]
    hi = np.percentile(nz, p_hi) if nz.size else 1.0
    return np.clip(a / hi, 0, 1) ** gamma

WARM = [(0.00, (0.015, 0.006, 0.003)), (0.28, (0.20, 0.062, 0.012)),
        (0.58, (0.72, 0.34, 0.05)), (0.85, (1.00, 0.66, 0.16)),
        (1.00, (1.05, 0.85, 0.42))]
GHOST = [(0.00, (0.002, 0.005, 0.012)), (0.40, (0.014, 0.065, 0.15)),
         (0.75, (0.06, 0.22, 0.42)), (1.00, (0.14, 0.40, 0.66))]


def ramp(v, stops):
    out = np.zeros(v.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (v >= p0) & (v <= p1)
        f = ((v - p0) / max(p1 - p0, 1e-9))[m][:, None]
        out[m] = (1 - f) * np.array(c0) + f * np.array(c1)
    return out


def compose(fF, fD, k=1.35, ghost_gain=0.75):
    H, W = fF.shape
    r = (np.arange(H) / H)[:, None].astype(np.float32)
    fade = np.ones(H, np.float32)
    n = max(int(0.03 * H), 2)
    fade[:n] = np.linspace(0.15, 1, n)
    fade[-n:] = np.linspace(1, 0.15, n)
    vF = tone(fF) * fade[:, None]
    # ghost dims toward the bottom (its own dense rain zone) so the great
    # gold rivers own the lower register
    vD = tone(fD) * fade[:, None] * ghost_gain * (1.0 - 0.55 * r ** 2)
    rgb = ramp(vF, WARM) + ramp(vD, GHOST)
    # faint atmospheric wash: indigo dawn at top -> ember dusk at bottom
    wash = (1 - r) * np.array([0.012, 0.016, 0.034]) + r * np.array([0.030, 0.016, 0.008])
    rgb += wash[:, None, :]
    for sig, amp in ((5, 0.20), (18, 0.13), (55, 0.08)):
        rgb += amp * gaussian_filter(np.clip(vF - 0.65, 0, None), sig)[..., None] \
               * np.array([1.0, 0.72, 0.30])
        rgb += 0.5 * amp * gaussian_filter(np.clip(vD - 0.74, 0, None), sig)[..., None] \
               * np.array([0.30, 0.62, 1.0])
    out = 1 - np.exp(-k * rgb)
    return (np.clip(out, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)


def build(S, Tmul, seed, stride, ss, blend, sig_t, name, mexp=1.0):
    t0 = time.time()
    W = H = S; T = S * Tmul; Ws = W * ss
    tsF, nF, _, _ = web_fast.run(Ws, T, seed, stride, forward=True)
    tsD, nD, _, _ = web_fast.run(Ws, T, seed, stride, forward=False)
    nD_asc = np.interp(tsF, tsD[::-1], nD[::-1])
    print('profile %.1fs  nF %d->%d  nD %d->%d' %
          (time.time() - t0, nF[0], nF[-1], nD_asc[0], nD_asc[-1]))
    warp = web_core.warp_from_profile(tsF, nF, nD_asc, T, blend)
    tf, utimes = sample_times(warp, T, H)
    _, _, XF, MF = web_fast.run(Ws, T, seed, stride, True, sample_set=utimes)
    print('fwd %.1fs' % (time.time() - t0))
    XF = web_fast.unwrap(XF, Ws)
    XF, MF = rows_from_samples(XF, MF, utimes, tf)
    bF = splat(XF, MF, W, ss, sig_t, mexp); del XF, MF
    _, _, XD, MD = web_fast.run(Ws, T, seed, stride, False, sample_set=utimes)
    print('dual %.1fs' % (time.time() - t0))
    XD = web_fast.unwrap(XD, Ws)
    XD, MD = rows_from_samples(XD, MD, utimes, tf)
    bD = splat(XD, MD, W, ss, sig_t, mexp); del XD, MD
    sc = (S / 768) ** 0.5
    fF = flatten(bF, 0.68 * sc, 1.6, gains=[0.7, 1, 1, 1, 1, 1])
    fD = flatten(bD, 0.55 * sc, 1.5, gains=[0.8, 1, 1, 1, 1, 1])
    Image.fromarray(compose(fF, fD, ghost_gain=0.8)).save(name)
    print('saved', name, '%.1fs total' % (time.time() - t0))


if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1536
    Tmul = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    sig_t = float(sys.argv[4]) if len(sys.argv) > 4 else 14 * S / 768
    name = sys.argv[5] if len(sys.argv) > 5 else f'river_{S}_{Tmul}_{seed}.png'
    build(S, Tmul, seed, stride=8, ss=4, blend=0.55, sig_t=sig_t, name=name)
