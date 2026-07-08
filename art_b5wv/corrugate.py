"""Piece A — 'To Be Short' (Nash–Kuiper 1-D convex integration).

An honest one-dimensional Nash–Kuiper construction: starting from the unit
circle, each stage k corrugates the direction field,

    theta_K(t) = 2*pi*t + pi/2 + sum_k alpha_k * cos(2*pi*N_k*t),

with alpha_k = J0^{-1}(s_{k-1}/s_k) so that stage k has EXACTLY constant
speed s_k (the curve is gamma' = s_K * exp(i*theta) — a C^1 isometric
immersion of a circle of circumference s_K). Choosing every N_k even makes
the loop close EXACTLY: by Jacobi–Anger the closure integral only picks up
resonances 1 + sum m_k N_k = 0, impossible when all N_k are even.

The curve stays C0-close to the unit circle (each corrugation averages out
at frequency N_k) while its length multiplies by rho each stage: infinite
length learning to live in a thin annulus.
"""
import numpy as np
from scipy.special import j0
from scipy.optimize import brentq
from scipy.ndimage import gaussian_filter
import argparse, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artlib import splat_points, filmic, bloom, ramp, save


def alpha_for_ratio(r):
    """alpha with J0(alpha) = r, alpha in (0, first zero of J0)."""
    return brentq(lambda a: j0(a) - r, 0.0, 2.404825)


def build_theta_params(K, rho, N_list):
    assert len(N_list) == K
    alphas = [alpha_for_ratio(1.0 / rho) for _ in range(K)]
    speeds = [2 * np.pi * rho ** k for k in range(K + 1)]  # s_0 .. s_K
    return alphas, speeds


def theta_of_t(t, K, alphas, N_list):
    th = 2 * np.pi * t + np.pi / 2
    for k in range(K):
        th = th + alphas[k] * np.cos(2 * np.pi * N_list[k] * t)
    return th


def integrate_curve(K, alphas, N_list, speed, M):
    """Integrate gamma' = speed * e^{i theta} with M samples; returns x,y arrays
    (M+1 points) via chunked trapezoid cumsum, float64."""
    xs = np.empty(M + 1); ys = np.empty(M + 1)
    xs[0] = 1.0; ys[0] = 0.0   # gamma(0) = (1, 0) (base circle start)
    cx, cy = 1.0, 0.0
    chunk = 1 << 22
    dt = 1.0 / M
    prev_dx = None
    t_prev_end = None
    for a in range(0, M, chunk):
        b = min(a + chunk, M)
        t = np.arange(a, b + 1) * dt
        th = theta_of_t(t, K, alphas, N_list)
        dx = np.cos(th); dy = np.sin(th)
        # trapezoid increments over each dt interval
        ix = 0.5 * (dx[:-1] + dx[1:]) * dt * speed
        iy = 0.5 * (dy[:-1] + dy[1:]) * dt * speed
        xs[a + 1:b + 1] = cx + np.cumsum(ix)
        ys[a + 1:b + 1] = cy + np.cumsum(iy)
        cx = xs[b]; cy = ys[b]
    return xs, ys


def verify(K, alphas, N_list, rho):
    """Closure + C0 distance report at high resolution."""
    Mv = 1 << 23
    xs, ys = integrate_curve(K, alphas, N_list, 2 * np.pi * rho ** K, Mv)
    closure = np.hypot(xs[-1] - xs[0], ys[-1] - ys[0])
    r = np.hypot(xs, ys)
    print(f'  stages={K} rho={rho} length={rho**K:.1f}x base circle')
    print(f'  closure |gamma(1)-gamma(0)| = {closure:.3e}  (analytic: exactly 0)')
    print(f'  radial band: [{r.min():.4f}, {r.max():.4f}] around unit circle')
    print(f'  speed: exactly {2*np.pi*rho**K:.4f} by construction (gamma\'=s e^{{i theta}})')
    return closure, r.min(), r.max()


def render(path, S=1024, ss=2, K=5, rho=2.0, N_list=(10, 60, 360, 2160, 12960),
           samples_per_px=3.0, verify_first=True, style='radius',
           frame_r=1.55, k_tone=5.0, gamma=0.85, mass=3.0, center=(0.0, 0.0)):
    N_list = list(N_list)
    alphas, speeds = build_theta_params(K, rho, N_list)
    if verify_first:
        _, rad_lo, rad_hi = verify(K, alphas, N_list, rho)
    else:
        rad_lo, rad_hi = 0.6, 1.4

    W = S * ss
    # sample count: finest frequency needs resolution; also mass per pixel
    length_px = speeds[K] / (2 * frame_r) * W   # curve length in pixels
    M = int(max(length_px * samples_per_px, N_list[-1] * 64))
    M = min(M, 220_000_000)
    print(f'  render {W}x{W}, curve length {length_px/1e6:.2f} Mpx, M={M/1e6:.1f}M samples')

    acc_r = np.zeros((W, W), np.float64)
    acc_g = np.zeros((W, W), np.float64)
    acc_b = np.zeros((W, W), np.float64)

    # palette by local curvature octave: which corrugation stage dominates theta'
    chunk = 1 << 22
    dt = 1.0 / M
    cx, cy = 1.0, 0.0
    scale = W / (2 * frame_r)
    for a in range(0, M, chunk):
        b = min(a + chunk, M)
        t = np.arange(a, b + 1) * dt
        th = theta_of_t(t, K, alphas, N_list)
        dxu = np.cos(th); dyu = np.sin(th)
        ix = 0.5 * (dxu[:-1] + dxu[1:]) * dt * speeds[K]
        iy = 0.5 * (dyu[:-1] + dyu[1:]) * dt * speeds[K]
        x = cx + np.cumsum(ix); y = cy + np.cumsum(iy)
        cx2, cy2 = x[-1], y[-1]

        tm = 0.5 * (t[:-1] + t[1:])
        if style == 'curvature':
            # signed curvature ~ theta'(t) / s
            thp = 2 * np.pi - sum(alphas[k] * 2 * np.pi * N_list[k]
                                  * np.sin(2 * np.pi * N_list[k] * tm)
                                  for k in range(K))
            kappa = np.abs(thp) / speeds[K]
            u = np.log1p(kappa / np.median(kappa) if np.median(kappa) > 0 else kappa)
            u = u / (u.max() + 1e-12)
        else:
            u = np.hypot(x, y)  # radius colouring, normalised to actual band
            u = (u - rad_lo) / max(rad_hi - rad_lo, 1e-9)

        col = ramp(u, [(0.00, (0.16, 0.05, 0.30)),
                       (0.28, (0.55, 0.12, 0.25)),
                       (0.52, (0.92, 0.38, 0.10)),
                       (0.74, (1.00, 0.72, 0.28)),
                       (0.90, (1.00, 0.92, 0.62)),
                       (1.00, (0.98, 1.00, 0.90))])
        px = (x - center[0] + frame_r) * scale
        py = (frame_r - (y - center[1])) * scale
        splat_points(acc_r, px, py, col[..., 0])
        splat_points(acc_g, px, py, col[..., 1])
        splat_points(acc_b, px, py, col[..., 2])
        cx, cy = cx2, cy2

    # ghost of the base circle: the short smooth map being C0-approximated
    tg = np.linspace(0, 1, 40000, endpoint=False)
    gx = (np.cos(2 * np.pi * tg) - center[0] + frame_r) * scale
    gy = (frame_r - (np.sin(2 * np.pi * tg) - center[1])) * scale
    ghost = np.zeros_like(acc_r)
    splat_points(ghost, gx, gy, 1.0)
    ghost = gaussian_filter(ghost, 1.1 * ss)
    ghost *= 0.55 / max(ghost.max(), 1e-12)

    # normalise mass so tone doesn't depend on M, then soften the thread
    m = M / (length_px)  # samples per pixel of arclength
    rgb = np.stack([acc_r, acc_g, acc_b], -1) * (mass / m)
    rgb += np.stack([ghost * 0.30, ghost * 0.45, ghost * 0.60], -1)
    sig = 0.55 * ss
    peak_fix = 2 * np.pi * sig * sig  # restore amplitude: blur conserves mass
    for c in range(3):
        rgb[..., c] = gaussian_filter(rgb[..., c], sig) * min(peak_fix, 4.0)
    rgb = filmic(rgb, k=k_tone, gamma=gamma)
    rgb = bloom(rgb, mask_lo=0.72, sigma=5 * ss, gain=0.5, tint=(1.0, 0.9, 0.7))
    save(rgb, path, down=ss)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='variants/corr_proto.png')
    ap.add_argument('--size', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--K', type=int, default=5)
    ap.add_argument('--rho', type=float, default=2.0)
    ap.add_argument('--N', type=str, default='10,60,360,2160,12960')
    ap.add_argument('--style', default='radius')
    ap.add_argument('--ktone', type=float, default=5.0)
    ap.add_argument('--frame', type=float, default=1.55)
    ap.add_argument('--mass', type=float, default=3.0)
    ap.add_argument('--cx', type=float, default=0.0)
    ap.add_argument('--cy', type=float, default=0.0)
    args = ap.parse_args()
    N_list = [int(v) for v in args.N.split(',')][:args.K]
    render(args.out, S=args.size, ss=args.ss, K=args.K, rho=args.rho,
           N_list=N_list, style=args.style, k_tone=args.ktone,
           frame_r=args.frame, mass=args.mass, center=(args.cx, args.cy))
