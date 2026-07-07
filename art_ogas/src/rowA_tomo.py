"""Row A — tomography. A1 the world / A2 its sinogram / A3 the limited-angle return.

The Radon transform is what an instrument can take of the world: line integrals
only. With every angle, inversion is exact (FBP); deny it a wedge of angles and
the world comes back streaked and smeared along the directions we kept.
"""
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
import tone

RNG = np.random.default_rng(20260707)


def make_phantom(N):
    """A layered luminous world: atmosphere + shells + filaments + kernels."""
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    cx = cy = (N - 1) / 2
    r = np.hypot(x - cx, y - cy) / (N / 2)

    # power-law Gaussian random field atmosphere (fixed seed)
    k = np.fft.fftfreq(N)[:, None] ** 2 + np.fft.fftfreq(N)[None, :] ** 2
    amp = (k + (2.0 / N) ** 2) ** (-3.2 / 2)
    phase = np.exp(2j * np.pi * RNG.random((N, N)))
    grf = np.fft.ifft2(amp * phase).real
    grf = (grf - grf.mean()) / grf.std()
    atmo = 1.0 * (1 / (1 + np.exp(-1.6 * grf))) ** 1.4

    # soft nebula body: atmosphere carried by a radial envelope
    body = np.exp(-0.5 * (r / 0.52) ** 2)
    field = (atmo * (0.18 + 0.82 * body)).astype(np.float32)

    # two hollow shells
    for r0, w, b in [(0.62, 0.018, 0.85), (0.33, 0.013, 0.6)]:
        field += b * np.exp(-0.5 * ((r - r0) / w) ** 2)

    # filaments: closed random Fourier loops, splatted as soft threads
    t = np.linspace(0, 2 * np.pi, 6000, dtype=np.float32)
    for i in range(5):
        coeff = RNG.normal(0, 1, (2, 4)) / (np.arange(1, 5) ** 1.3)
        rad = 0.15 + 0.55 * RNG.random()
        px = cx + N / 2 * (rad * np.cos(t) + 0.10 * sum(coeff[0, m] * np.cos((m + 2) * t + RNG.random() * 7) for m in range(4)))
        py = cy + N / 2 * (rad * np.sin(t) + 0.10 * sum(coeff[1, m] * np.cos((m + 2) * t + RNG.random() * 7) for m in range(4)))
        h, _, _ = np.histogram2d(py, px, bins=N, range=[[0, N], [0, N]])
        field += 0.9 * gaussian_filter(h.astype(np.float32), N / 800) * (N / 800) ** 2

    # bright kernels near the outer shell + a core
    ang = RNG.random(42) * 2 * np.pi
    rr = 0.62 + RNG.normal(0, 0.06, 42)
    for a, rho, b in zip(ang, rr, 0.5 + RNG.random(42)):
        g = np.exp(-0.5 * (((x - cx - rho * N / 2 * np.cos(a)) ** 2 +
                            (y - cy - rho * N / 2 * np.sin(a)) ** 2) / (N / 300) ** 2))
        field += 0.9 * b * g
    field += 2.2 * np.exp(-0.5 * (((x - cx - 0.13 * N / 2) ** 2 + (y - cy + 0.09 * N / 2) ** 2) / (N / 120) ** 2))

    # keep the world inside the scanner's disc
    field *= np.clip((0.97 - r) / 0.03, 0, 1)
    return field


def radon(img, n_angles, n_s=None):
    """Sinogram S[theta, s] by gathering along rotated lines (bilinear)."""
    N = img.shape[0]
    n_s = n_s or N
    c = (N - 1) / 2
    s = np.linspace(-c, c, n_s, dtype=np.float32)
    t = np.linspace(-c, c, N, dtype=np.float32)
    S, T = np.meshgrid(s, t, indexing="ij")
    sino = np.empty((n_angles, n_s), dtype=np.float32)
    thetas = np.linspace(0, np.pi, n_angles, endpoint=False)
    for i, th in enumerate(thetas):
        ct, st = np.cos(th), np.sin(th)
        xs = c + S * ct - T * st
        ys = c + S * st + T * ct
        vals = map_coordinates(img, [ys, xs], order=1, mode="constant", cval=0.0)
        sino[i] = vals.sum(axis=1)
    return sino, thetas


def fbp(sino, thetas, N, keep=None):
    """Filtered back-projection; keep = boolean mask of angles to use."""
    n_angles, n_s = sino.shape
    if keep is None:
        keep = np.ones(n_angles, bool)
    # ramp * Hann filter, zero-padded
    pad = 2 * n_s
    f = np.fft.rfftfreq(pad)
    filt = f * (0.5 + 0.5 * np.cos(np.pi * f / f.max()))
    fs = np.fft.irfft(np.fft.rfft(sino, pad, axis=1) * filt[None, :], pad, axis=1)[:, :n_s]
    c = (N - 1) / 2
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    xr, yr = x - c, y - c
    out = np.zeros((N, N), dtype=np.float32)
    s_axis = np.linspace(-c, c, n_s).astype(np.float32)
    for i, th in enumerate(thetas):
        if not keep[i]:
            continue
        svals = xr * np.cos(th) + yr * np.sin(th)
        idx = (svals - s_axis[0]) / (s_axis[1] - s_axis[0])
        i0 = np.clip(np.floor(idx).astype(np.int32), 0, n_s - 2)
        frac = idx - i0
        out += fs[i][i0] * (1 - frac) + fs[i][i0 + 1] * frac
    out *= np.pi / (2 * keep.sum())
    return out


def colorize_world(field, out_size, neg=None):
    """Shared treatment for column I and III: palette on tone-mapped density.
    neg: optional negative-artifact field (FBP undershoot) shown as cool glow."""
    v = tone.norm_percentile(field, 1, 99.8)
    v = tone.filmic(v, k=2.2, gamma=0.9)
    rgb = tone.lerp_palette(v, tone.PAL_EMBER)
    if neg is not None:
        # the wound: undershoot artifacts as faint cold slate light
        u = tone.filmic(tone.norm_percentile(neg, 50, 99.9), k=2.0)
        rgb += u[..., None] * np.array([0.07, 0.11, 0.22], np.float32)
        # ghost the whole return slightly toward slate
        lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        slate = np.stack([0.80 * lum, 0.86 * lum, 1.00 * lum], -1)
        rgb = 0.70 * rgb + 0.30 * slate
    rgb = tone.bloom(rgb, threshold=0.75, gain=0.5)
    return tone.to_image(np.clip(rgb, 0, 1), out_size)


def colorize_sinogram(sino, out_size):
    v = tone.norm_percentile(sino, 0.5, 99.95)
    v = tone.filmic(v, k=1.7, gamma=1.0)
    rgb = tone.lerp_palette(v, tone.PAL_EMBER)
    rgb = tone.bloom(rgb, threshold=0.8, gain=0.35)
    return tone.to_image(rgb, out_size)


def main(N=1024, n_angles=900, out_size=512, wedge_deg=110, outdir="."):
    import os, time
    t0 = time.time()
    ph = make_phantom(N)
    print(f"phantom {N}²  {time.time()-t0:.1f}s", flush=True)
    sino, thetas = radon(ph, n_angles)
    print(f"radon {n_angles} angles  {time.time()-t0:.1f}s", flush=True)
    # limited wedge centred on 90° (vertical-ish lines kept)
    keep = np.abs(np.degrees(thetas) - 90) <= wedge_deg / 2
    rec = fbp(sino, thetas, N, keep)
    print(f"fbp keep={keep.sum()}/{n_angles}  {time.time()-t0:.1f}s", flush=True)
    np.savez_compressed(os.path.join(outdir, "rowA_fields.npz"),
                        ph=ph, sino=sino, rec=rec)

    colorize_world(ph, out_size).save(os.path.join(outdir, "A1_the_world.png"))
    # sinogram panel: resample to square via PIL at colorize time
    colorize_sinogram(sino, out_size).save(os.path.join(outdir, "A2_the_shadow.png"))
    colorize_world(np.maximum(rec, 0), out_size,
                   neg=np.maximum(-rec, 0)).save(os.path.join(outdir, "A3_the_return.png"))
    print(f"done {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    import sys
    kw = dict(arg.split("=") for arg in sys.argv[1:])
    main(**{k: (int(v) if v.isdigit() else v) for k, v in kw.items()})
