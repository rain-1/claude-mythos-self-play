"""Piece 2 — "Almost All of the Cube" (concentration of measure).

For x uniform in the cube [-1,1]^d, the norm ||x|| concentrates: its mean grows
like sqrt(d/3) but the *relative* fluctuation shrinks like 1/sqrt(d). We draw
one ring per dimension d, nested outward. Each ring is placed at base radius
B(d) (increasing with d) and its points scatter by the actual normalized norm
rho = ||x|| / sqrt(d/3). Inner rings (low d) are broad, fuzzy clouds; outer
rings (high d) collapse to razor-thin bright circles. The dark center is the
empty middle of high-dimensional space.
"""
import sys, numpy as np
sys.path.insert(0, "src")
import render as R


def splat_points(canvas, px, py, w):
    S = canvas.shape[0]
    m = (px >= 0) & (px < S - 1) & (py >= 0) & (py < S - 1)
    px, py = px[m], py[m]
    ww = (w[m] if hasattr(w, "__len__") else np.full(px.shape, w))
    x0 = np.floor(px).astype(np.int64); y0 = np.floor(py).astype(np.int64)
    fx = px - x0; fy = py - y0
    flat = canvas.ravel()
    for dx, dy, wf in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(flat, (y0 + dy) * S + (x0 + dx), ww * wf)


def main(S=1024, out="out/p2_concentration.png", down=512, seed=11,
         n_rings=42, pts_per_ring=20000, dmax=3000, gain=0.5):
    rng = np.random.default_rng(seed)
    canvas = np.zeros((S, S), dtype=np.float64)
    huef = np.zeros((S, S), dtype=np.float64)
    cx = cy = S / 2
    R_in, R_out = S * 0.060, S * 0.475

    # geometric spacing in dimension: huge dynamic range so inner rings are
    # dramatically fuzzy and outer rings collapse to razor circles.
    d_vals = np.unique(np.round(
        np.exp(np.linspace(np.log(1), np.log(dmax), n_rings))).astype(int))
    nr = len(d_vals)
    for i, d in enumerate(d_vals):
        frac = i / max(nr - 1, 1)
        ringR = R_in + (R_out - R_in) * frac
        x = rng.uniform(-1.0, 1.0, size=(pts_per_ring, d))
        r = np.sqrt((x * x).sum(axis=1))
        rho = r / np.sqrt(d / 3.0)                 # mean ~ 1, std ~ c/sqrt(d)
        pr = ringR * (1.0 + (rho - 1.0) * gain)    # width shrinks with d
        ang = rng.uniform(0, 2 * np.pi, pts_per_ring)
        px = cx + pr * np.cos(ang)
        py = cy + pr * np.sin(ang)
        # per-ring accumulation, normalized so every ring is visible and the
        # *width* (not raw density) carries the concentration story.
        tmp = np.zeros_like(canvas)
        splat_points(tmp, px, py, 1.0)
        peak = np.percentile(tmp[tmp > 0], 99.0) if (tmp > 0).any() else 1.0
        tmp = np.clip(tmp / (peak + 1e-9), 0, 1)
        ring_bright = 0.55 + 0.45 * frac          # outer rings pop a little
        canvas += tmp * ring_bright
        huef += tmp * float(i)

    with np.errstate(invalid="ignore", divide="ignore"):
        mean_dim = np.where(canvas > 1e-6, huef / np.maximum(canvas, 1e-9), 0)
    t = mean_dim / max(nr - 1, 1)

    bright = R.filmic(canvas, k=2.6, gamma=0.85)
    lut = R.palette_lut(R.PAL_VIRID, 2048)
    rgb = R.apply_lut(np.clip(t, 0, 1), lut) * bright[..., None]
    rgb = np.clip(rgb, 0, 1)
    R.save(rgb, out, downscale_to=down)
    print("wrote", out, "max", round(canvas.max(), 1), "rings", nr)


if __name__ == "__main__":
    main()
