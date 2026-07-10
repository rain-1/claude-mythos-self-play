"""KdV ridgeline waterfall — the cosine that shattered into individuals.

~120 time slices of Zabusky-Kruskal u(x,t), stacked back (t=0, smooth cosine)
to front (t ~ 10.8, past the near-recurrence at 9.54). Hidden-line occlusion:
nearer ridges hide what lies behind. Co-moving chart x' = x - v t keeps the
peaks roughly in place so each soliton reads as one mountain drifting slowly.
Stroke color follows height: indigo valleys, verdigris slopes, gold summits.

Usage: python3 kdv_waterfall.py <S> <out> [v_frame] [warp] [rows]
"""
import sys
import numpy as np
from scipy.ndimage import gaussian_filter
from common import splat_rgb, filmic, bloom, save, lerp_palette

STROKE_STOPS = [
    (0.00, (0.09, 0.12, 0.28)),   # deep trough indigo
    (0.25, (0.14, 0.26, 0.42)),
    (0.45, (0.20, 0.46, 0.48)),   # verdigris
    (0.62, (0.62, 0.60, 0.36)),
    (0.76, (1.00, 0.80, 0.38)),   # gold
    (1.00, (1.08, 1.00, 0.78)),   # white-hot summit
]


def render(S=1280, out=None, v_frame=0.504, warp=0.62, R=120):
    sw = (S / 1280.0) ** 0.9          # stroke-weight rescale for canvas size
    d = np.load("kdv_field.npz")
    field, times = d["field"], d["times"]
    Trows, N = field.shape
    T_end = float(times[-1])
    L = 2.0
    H = W = S

    acc = np.zeros((H, W, 3), dtype=np.float32)

    y_back, y_front = 0.16 * H, 0.93 * H
    A = 0.062 * H                       # height per unit u
    umin, umax = -1.0, 3.0

    xg_data = np.arange(N) * (L / N)
    sub = 6                              # subsamples per pixel column
    WF = W * sub
    xs_fine = (np.arange(WF) + 0.5) / sub
    XWIN = 1.00                          # zoomed co-moving window width (units)
    X0 = -0.38
    xg_canvas = X0 + xs_fine * (XWIN / W)

    ymin = np.full(WF, np.inf, dtype=np.float64)

    for i in range(R - 1, -1, -1):      # front (late) -> back (early)
        frac = i / (R - 1.0)
        t = T_end * (frac ** (1.0 / warp))
        fi = np.interp(t, times, np.arange(Trows))
        i0 = min(int(fi), Trows - 2)
        f = fi - i0
        row = (1 - f) * field[i0] + f * field[i0 + 1]
        xq = (xg_canvas + v_frame * t) % L
        u = np.interp(xq, xg_data, row, period=L)
        base = y_back + (y_front - y_back) * (frac ** 1.0)
        y = base - A * u

        vis = y < (ymin - 0.4)
        # color/weight from height, plus atmospheric depth (front brighter)
        hn = np.clip((u - umin) / (umax - umin), 0, 1).astype(np.float32)
        col = lerp_palette(hn ** 1.1, STROKE_STOPS)
        depth = 0.5 + 0.5 * frac
        wgt = ((0.40 + 1.1 * hn ** 1.2 + 3.6 * np.clip(hn - 0.55, 0, 1) ** 1.4) * depth * sw).astype(np.float32)
        w = col * wgt[:, None]
        if vis.any():
            xs = xs_fine[vis].astype(np.float32)
            yv = y[vis].astype(np.float32)
            ww = w[vis]
            splat_rgb(acc, xs, yv, ww * (0.4 / sub), W, H)
            splat_rgb(acc, xs, (yv + 0.6).astype(np.float32), ww * (0.4 / sub), W, H)
            splat_rgb(acc, xs, (yv + 1.2).astype(np.float32), ww * (0.25 / sub), W, H)
        ymin = np.minimum(ymin, y)

    # gentle vertical smear for body, then compose
    body = np.stack([gaussian_filter(acc[..., c], (3.0, 0.5)) for c in range(3)], -1)
    img = acc + 0.95 * body
    img = filmic(img, k=1.5, gamma=0.9)
    img = bloom(img, sigma_tight=1.4, sigma_wide=9.0, amt_tight=0.32, amt_wide=0.18,
                thresh=0.60)
    save(img, out or ("variants/kdv_wf_%d.png" % S))


if __name__ == "__main__":
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
    out = sys.argv[2] if len(sys.argv) > 2 else None
    v = float(sys.argv[3]) if len(sys.argv) > 3 else 0.504
    warp = float(sys.argv[4]) if len(sys.argv) > 4 else 0.62
    R = int(sys.argv[5]) if len(sys.argv) > 5 else 120
    render(S, out, v, warp, R)
