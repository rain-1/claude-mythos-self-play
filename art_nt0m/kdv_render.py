"""KdV spacetime — the cosine that shattered into individuals.

Zabusky-Kruskal 1965: u_t + u u_x + (0.022)^2 u_xxx = 0, u(x,0) = cos(pi x).
Time flows DOWN, warped y ~ t^0.65 so the smooth beginning and the breakup
(t_B = 1/pi) get their light. Chart is a co-moving frame x' = x - v t (v chosen
near the mean soliton speed) so world-lines weave around the vertical. The wave
steepens, shatters into eight solitons (crossings = phase-shift kinks), and
near-realigns at t ~ 9.54 (shift-max corr 0.926 with the initial cosine —
verified in kdv_sim.py, invariants conserved to ~1e-10).

Usage: python3 kdv_render.py <S> <outname> [v_frame] [warp]
"""
import sys
import numpy as np
from common import splat_rgb, filmic, bloom, save, lerp_palette

FIELD_STOPS = [
    (0.00, (0.02, 0.03, 0.09)),
    (0.30, (0.06, 0.10, 0.24)),
    (0.55, (0.09, 0.22, 0.28)),
    (0.75, (0.16, 0.36, 0.36)),
    (0.90, (0.42, 0.50, 0.36)),
    (1.00, (0.85, 0.72, 0.42)),
]
GOLD = np.array([1.00, 0.86, 0.50], dtype=np.float32)


def render(S=1280, out=None, v_frame=0.294, warp=0.65):
    d = np.load("kdv_field.npz")
    field, times = d["field"], d["times"]
    Trows, N = field.shape
    T_end = times[-1]
    L = 2.0
    H = W = S

    img_f = np.empty((H, W), dtype=np.float32)      # scalar field, colored later
    acc = np.zeros((H, W, 3), dtype=np.float32)     # crest threads

    xg_data = np.arange(N) * (L / N)
    xg_canvas = (np.arange(W) + 0.5) * (L / W)

    for j in range(H):
        t = T_end * (((j + 0.5) / H) ** (1.0 / warp))
        # bracketing data rows
        fi = np.interp(t, times, np.arange(Trows))
        i0 = min(int(fi), Trows - 2)
        f = fi - i0
        row = (1 - f) * field[i0] + f * field[i0 + 1]
        # co-moving frame: sample u at x + v t (periodic)
        xq = (xg_canvas + v_frame * t) % L
        rowc = np.interp(xq, xg_data, row, period=L)
        img_f[j] = rowc
        # crest maxima on the canvas row
        lft = np.roll(rowc, 1)
        rgt = np.roll(rowc, -1)
        pk = np.nonzero((rowc > lft) & (rowc >= rgt) & (rowc > 1.0))[0]
        if pk.size:
            y0v, y1v, y2v = lft[pk], rowc[pk], rgt[pk]
            den = y0v - 2 * y1v + y2v
            delta = np.where(np.abs(den) > 1e-9, 0.5 * (y0v - y2v) / den, 0.0)
            xs = (pk + delta).astype(np.float32)
            ys = np.full(pk.size, j, dtype=np.float32)
            amp = np.clip((y1v - 1.0) / 1.6, 0, 1).astype(np.float32)
            # hue by amplitude: teal-white -> gold -> white-hot
            cA = np.array([0.50, 0.82, 0.85], dtype=np.float32)
            cB = np.array([1.00, 0.84, 0.42], dtype=np.float32)
            cC = np.array([1.05, 0.97, 0.80], dtype=np.float32)
            f1c = np.clip(amp / 0.6, 0, 1)[:, None]
            f2c = np.clip((amp - 0.6) / 0.4, 0, 1)[:, None]
            col = cA[None, :] * (1 - f1c) + cB[None, :] * f1c
            col = col * (1 - f2c) + cC[None, :] * f2c
            wgt = (0.10 + 0.85 * amp ** 1.3).astype(np.float32)
            w = col * wgt[:, None]
            for dy in (-0.33, 0.0, 0.33):
                splat_rgb(acc, xs, ys + dy, w * 0.3333, W, H)

    lo, hi = np.percentile(img_f, 0.5), np.percentile(img_f, 99.8)
    Fn = np.clip((img_f - lo) / (hi - lo), 0, 1)
    img = lerp_palette((Fn ** 1.6).astype(np.float32), FIELD_STOPS)
    img = img + acc

    img = filmic(img, k=1.6, gamma=0.92)
    img = bloom(img, sigma_tight=1.6, sigma_wide=10.0, amt_tight=0.35, amt_wide=0.20,
                thresh=0.55)
    save(img, out or ("variants/kdv_carpet_%d.png" % S))


if __name__ == "__main__":
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
    out = sys.argv[2] if len(sys.argv) > 2 else None
    v = float(sys.argv[3]) if len(sys.argv) > 3 else 0.504
    warp = float(sys.argv[4]) if len(sys.argv) > 4 else 0.65
    render(S, out, v, warp)
