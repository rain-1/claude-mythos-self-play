"""Row B — the phase problem. B1 the thing / B2 its diffraction shadow / B3 the HIO return.

A detector records only |F|² — the phase, which carries the shape, never
reaches us. Fienup's hybrid input-output can claw an image back from magnitude
alone, but the answer is only defined up to the "twin": the 180°-rotated
conjugate. Given a symmetric support, the iteration famously stagnates with
object and twin superimposed — the shadow cannot decide which world cast it.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
import tone

RNG = np.random.default_rng(19270101)  # Heisenberg year


def make_object(P, obj_frac=0.42):
    """A chiral spiral world inside a disc support on a P×P padded grid."""
    N = P
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    c = (N - 1) / 2
    R = obj_frac * N / 2                       # support radius (oversampling > 2)
    r = np.hypot(x - c, y - c)
    obj = np.zeros((N, N), np.float32)

    # two logarithmic spiral arms of splatted particles (chiral!)
    n_pts = int(26000 * (P / 1024) ** 1.5)
    for arm in range(2):
        t = np.linspace(0, 3.4 * np.pi, n_pts).astype(np.float32)
        a0 = arm * np.pi
        rad = R * 0.10 * np.exp(0.185 * t)
        rad = np.minimum(rad, R * 0.96)
        jitter = RNG.normal(0, 0.02 * R, (2, t.size)).astype(np.float32)
        w = 0.028 * R * (0.4 + t / t.max())     # arms broaden outward
        px = c + (rad + jitter[0] * (rad / R + 0.2)) * np.cos(t + a0)
        py = c + (rad + jitter[1] * (rad / R + 0.2)) * np.sin(t + a0)
        px += RNG.normal(0, w)
        py += RNG.normal(0, w)
        h, _, _ = np.histogram2d(py, px, bins=N, range=[[0, N], [0, N]])
        obj += gaussian_filter(h.astype(np.float32), N / 900)

    obj /= max(obj.max(), 1e-9)

    # soft core + a few satellite kernels breaking symmetry further
    obj += 0.75 * np.exp(-0.5 * (r / (0.10 * R)) ** 2)
    for (dx, dy, s, b) in [(0.55, 0.30, 0.05, 0.5), (-0.40, 0.62, 0.035, 0.4),
                           (0.10, -0.70, 0.045, 0.45)]:
        obj += b * np.exp(-0.5 * (((x - c - dx * R) ** 2 + (y - c - dy * R) ** 2)
                                  / (s * R) ** 2))

    # fine interior grain -> rich speckle
    k2 = np.fft.fftfreq(N)[:, None] ** 2 + np.fft.fftfreq(N)[None, :] ** 2
    grain = np.fft.ifft2((k2 + 1e-6) ** (-1.0) *
                         np.exp(2j * np.pi * RNG.random((N, N)))).real
    grain = (grain - grain.mean()) / grain.std()
    obj *= (1 + 0.35 * np.clip(grain, -2, 2) / 2)

    support = (r <= R).astype(np.float32)
    obj = np.clip(obj, 0, None) * support
    return obj, support


def hio(magnitude, support, n_iter=1500, beta=0.9, seed=7):
    """Fienup HIO with ER refinement epochs, from |F| alone (scipy.fft, 4 workers)."""
    from scipy import fft as sfft
    rng = np.random.default_rng(seed)
    g = (rng.random(magnitude.shape) * support).astype(np.float32)
    mag = magnitude.astype(np.float32)
    errs = []
    for it in range(n_iter):
        G = sfft.fft2(g, workers=4)
        Gp = (mag * np.exp(1j * np.angle(G))).astype(np.complex64)
        gp = sfft.ifft2(Gp, workers=4).real.astype(np.float32)
        mask = (support > 0) & (gp > 0)
        if it >= n_iter - 30:                  # brief ER polish at the very end
            g = np.where(mask, gp, 0.0).astype(np.float32)
        else:                                  # pure HIO: stagnates on the twin pair
            g = np.where(mask, gp, g - beta * gp).astype(np.float32)
        if it % 25 == 0:
            errs.append(float(np.linalg.norm(np.abs(G) - mag) / np.linalg.norm(mag)))
    return np.clip(g, 0, None) * support, errs


def colorize(v, out_size, pal, k=2.4, gamma=0.95, ghost=False, bloom_thr=0.78):
    v = tone.filmic(v, k=k, gamma=gamma)
    rgb = tone.lerp_palette(v, pal)
    if ghost:
        lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        slate = np.stack([0.80 * lum, 0.86 * lum, 1.00 * lum], -1)
        rgb = 0.70 * rgb + 0.30 * slate
    rgb = tone.bloom(rgb, threshold=bloom_thr, gain=0.5)
    return tone.to_image(np.clip(rgb, 0, 1), out_size)


def crop_to_object(field, P, obj_frac, pad=1.25):
    c = P // 2
    h = int(obj_frac * P / 2 * pad)
    return field[c - h:c + h, c - h:c + h]


def main(P=1024, n_iter=1200, out_size=512, outdir="."):
    import os, time
    t0 = time.time()
    obj, support = make_object(P)
    F = np.fft.fft2(obj)
    mag = np.abs(F).astype(np.float32)
    print(f"object+fft  {time.time()-t0:.1f}s", flush=True)

    # pick the seed whose return favours the TWIN (shift-invariant xcorr test)
    from scipy import fft as sfft
    O = sfft.fft2(obj)
    on = np.linalg.norm(obj)

    def xmax(rec):
        cc = sfft.ifft2(np.conj(O) * sfft.fft2(rec)).real
        return float(cc.max() / (on * np.linalg.norm(rec)))

    best, best_gap = None, -9
    for seed in range(1, 7):
        r_try, e_try = hio(mag, support, n_iter=max(300, n_iter // 3), seed=seed)
        gap = xmax(np.rot90(r_try, 2)) - xmax(r_try)
        print(f"  seed {seed}: err {e_try[-1]:.3f}, twin-true gap {gap:+.3f}", flush=True)
        if gap > best_gap:
            best, best_gap = seed, gap
    rec, errs = hio(mag, support, n_iter=n_iter, seed=best)
    print(f"hio seed {best}, {n_iter} iters, err {errs[0]:.3f}->{errs[-1]:.3f}  "
          f"twin-gap {best_gap:+.3f}  {time.time()-t0:.1f}s", flush=True)

    # B1: the thing itself (cropped to the support neighbourhood)
    v1 = tone.norm_percentile(crop_to_object(obj, P, 0.42), 0.5, 99.7)
    colorize(v1, out_size, tone.PAL_IRIS).save(os.path.join(outdir, "B1_the_world.png"))

    # B2: what the detector keeps — log |F|², centred, zoomed to the inner speckle
    I = np.fft.fftshift(mag) ** 2
    cq = P // 2
    h = int(P * 0.26)
    I = I[cq - h:cq + h, cq - h:cq + h]
    v2 = np.log10(I + I.max() * 1e-9)
    v2 = tone.norm_percentile(v2, 60, 99.93)
    colorize(v2, out_size, tone.PAL_IRIS, k=2.2, gamma=1.0, bloom_thr=0.85).save(
        os.path.join(outdir, "B2_the_shadow.png"))

    # B3: the return — object + twin superimposed, ghosted
    v3 = tone.norm_percentile(crop_to_object(rec, P, 0.42), 0.5, 99.7)
    colorize(v3, out_size, tone.PAL_IRIS, ghost=True).save(
        os.path.join(outdir, "B3_the_return.png"))
    print(f"done {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    import sys
    kw = dict(arg.split("=") for arg in sys.argv[1:])
    main(**{k: (int(v) if v.isdigit() else v) for k, v in kw.items()})
