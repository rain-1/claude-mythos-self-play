"""Piece 1 — "The Measure of a Curve" (Crofton / integral geometry).

A curve is recovered as the CAUSTIC ENVELOPE of its own tangent-line measure.
For a convex curve with support function h(theta), the tangent line at angle
theta touches at the point
    P(theta) = (h cos - h' sin, h sin + h' cos)
and runs along the tangent direction (-sin, cos). Drawn additively, the family
of tangent lines piles up density exactly on the curve (a caustic) — the curve
emerges from the *count of lines that touch it*, which is Crofton's idea.

We overlay several support-function curves, each its own caustic, plus a thin
isotropic line haze for the ambient "line measure".
"""
import sys, numpy as np
sys.path.insert(0, "src")
import render as R


def splat_lines(canvas, P0, dirs, L, M, weight, rng, jitter=0.0):
    """Additively splat line segments centered at P0 along dirs, length 2L,
    M samples each, bilinear. canvas in pixel coords [0,S)."""
    S = canvas.shape[0]
    t = np.linspace(-L, L, M)
    # (N, M) coordinates
    xs = P0[:, 0:1] + dirs[:, 0:1] * t[None, :]
    ys = P0[:, 1:2] + dirs[:, 1:2] * t[None, :]
    if jitter:
        xs = xs + rng.normal(0, jitter, xs.shape)
        ys = ys + rng.normal(0, jitter, ys.shape)
    xs = xs.ravel(); ys = ys.ravel()
    w = np.full(xs.shape, weight)
    # taper brightness toward segment ends so caustics dominate, not the rays
    taper = (1.0 - (np.abs(t) / L) ** 2)
    w = (np.broadcast_to(taper[None, :], (P0.shape[0], M)).ravel()) * weight
    m = (xs >= 0) & (xs < S - 1) & (ys >= 0) & (ys < S - 1)
    xs, ys, w = xs[m], ys[m], w[m]
    x0 = np.floor(xs).astype(np.int64); y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0; fy = ys - y0
    for dx, dy, wf in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(canvas.ravel(),
                  ((y0 + dy) * S + (x0 + dx)), w * wf)


def curve_tangents(h_fn, hp_fn, n, S, cx, cy, scale, phase=0.0):
    """Return tangency points (pixel coords) and tangent directions."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False) + phase
    c, s = np.cos(th), np.sin(th)
    h = h_fn(th); hp = hp_fn(th)
    # tangency point in math coords
    px = h * c - hp * s
    py = h * s + hp * c
    P = np.stack([cx + scale * px, cy + scale * py], axis=1)
    dirs = np.stack([-s, c], axis=1)
    return P, dirs


def main(S=1024, out="out/p1_crofton.png", down=512, seed=7):
    rng = np.random.default_rng(seed)
    canvas = np.zeros((S, S), dtype=np.float64)
    cx = cy = S / 2
    f = S / 1024.0                      # density scale for higher resolutions
    Ms = int(900 * f)                   # samples per ambient line
    Mc = int(1100 * f)                  # samples per caustic line

    # ---- ambient isotropic line measure (faint fabric) ----
    N = int(1400 * f)
    th = rng.uniform(0, np.pi, N)
    p = rng.uniform(-0.95, 0.95, N) * (S * 0.46)
    nrm = np.stack([np.cos(th), np.sin(th)], axis=1)
    dirs = np.stack([-np.sin(th), np.cos(th)], axis=1)
    P0 = np.stack([cx, cy], 0)[None, :] + nrm * p[:, None]
    splat_lines(canvas, P0, dirs, L=S * 0.75, M=Ms, weight=0.020, rng=rng,
                jitter=0.0)
    ambient = canvas.copy()

    # ---- several support-function curves: each a caustic ----
    caustic = np.zeros_like(canvas)
    # support functions h(theta)=1+e*cos(k theta+phi); h'=-e*k*sin(...).
    # a nested bouquet of curves across scales fills the frame, each its own
    # caustic; the high-k ones add fine filigree, the low-k ones the big arcs.
    curves = [
        # (e, k, phi, n_lines, scale, phase)
        (0.42, 2, 0.00, 2400, 0.42, 0.35),
        (0.30, 3, 0.20, 2600, 0.31, 0.00),
        (0.18, 5, 0.60, 2600, 0.21, 0.70),
        (0.12, 7, 1.10, 2800, 0.135, 0.30),
        (0.36, 2, 1.57, 2200, 0.50, 1.20),
        (0.08, 9, 0.40, 3000, 0.085, 0.90),
    ]
    for e, k, phi, n, scl, ph in curves:
        h = (lambda e, k, phi: (lambda th: 1 + e * np.cos(k * th + phi)))(e, k, phi)
        hp = (lambda e, k, phi: (lambda th: -e * k * np.sin(k * th + phi)))(e, k, phi)
        sc = S * scl
        c2 = np.zeros_like(canvas)
        P, d = curve_tangents(h, hp, int(n * f), S, cx, cy, sc, ph)
        splat_lines(c2, P, d, L=S * 0.62, M=Mc, weight=0.030, rng=rng)
        caustic += c2

    # tone-map separately, composite as additive light
    amb = R.filmic(ambient, k=2.6, gamma=1.0) * 0.32
    cau = R.filmic(caustic, k=3.0, gamma=0.80)

    field = np.clip(amb + cau, 0, 1)
    lut = R.palette_lut(R.PAL_EMBER, 2048)
    rgb = R.apply_lut(field, lut)
    # add a cool ambient tint where only ambient lives
    cool = R.palette_lut(R.PAL_ICE, 2048)
    rgb = rgb * (0.35 + 0.65 * cau[..., None]) + \
        R.apply_lut(amb, cool) * (0.55 * (1 - cau[..., None]))
    rgb = np.clip(rgb, 0, 1)
    R.save(rgb, out, downscale_to=down)
    print("wrote", out, "max", canvas.max())


if __name__ == "__main__":
    main()
