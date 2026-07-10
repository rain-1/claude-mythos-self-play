"""FPUT braid — the energy river that refused to thermalize.

Streamgraph of normal-mode energies E_k(t) from the 1955 alpha-FPUT chain
(N=32, alpha=0.25, mode-1 start). Mode 1 = gold bedrock; the cascade braids
through ember/coral/violet/indigo and twice reassembles (super-recurrence).
Bands lit at their edges like backlit silk; boundaries drawn as glowing threads.

Usage: python3 fput_render.py <W> <H> <outname>
"""
import sys
import numpy as np
from common import splat_rgb, filmic, bloom, save

MODE_COLORS = np.array([
    (1.00, 0.82, 0.38),   # 1 gold
    (0.93, 0.52, 0.24),   # 2 ember
    (0.86, 0.33, 0.32),   # 3 coral
    (0.64, 0.30, 0.58),   # 4 magenta-violet
    (0.45, 0.30, 0.68),   # 5 violet
    (0.30, 0.34, 0.74),   # 6 indigo
    (0.26, 0.46, 0.72),   # 7 blue
    (0.25, 0.57, 0.62),   # 8 teal
], dtype=np.float32)


def mode_color(k):  # k is 0-based
    if k < len(MODE_COLORS):
        return MODE_COLORS[k]
    f = min(1.0, (k - 7) / 12.0)
    a = np.array((0.30, 0.62, 0.62), dtype=np.float32)
    b = np.array((0.55, 0.85, 0.90), dtype=np.float32)
    return a + f * (b - a)


def render(W=1280, H=640, out=None, K=10):
    d = np.load("fput_modes.npz")
    rows, times = d["rows"], d["times"]
    sh = rows / rows.sum(axis=1, keepdims=True)      # shares, sum=1
    T = len(times)

    # resample to pixel columns by averaging samples per column (keeps grain)
    edges = np.linspace(0, T, W + 1).astype(int)
    S = np.empty((W, K), dtype=np.float64)
    for x in range(W):
        a, b = edges[x], max(edges[x] + 1, edges[x + 1])
        S[x] = sh[a:b, :K].mean(axis=0)
    S[:, K - 1] += 1.0 - S.sum(axis=1)               # fold tail modes into last band

    AMP = 0.54 * H
    c = np.cumsum(S, axis=1)
    bounds = np.concatenate([np.zeros((W, 1)), c], axis=1)   # (W, K+1) in [0,1]
    # energy conservation makes the raw outline a rectangle; give the river a
    # wiggle baseline driven by the mode centroid (cascade deep -> river bows)
    mu = (S * (np.arange(K) + 0.5)).sum(axis=1) / K
    from scipy.ndimage import gaussian_filter1d
    mu_s = gaussian_filter1d(mu, W / 220.0)
    offset = -0.40 * H * (mu_s - mu_s.mean())
    ymid = H / 2.0
    ys = ymid + AMP * (0.5 - bounds) + offset[:, None]  # y decreases as cum rises
    # ys[:,0] = bottom (mode1 bottom edge), ys[:,K] = top

    img = np.zeros((H, W, 3), dtype=np.float32)
    Y = np.arange(H, dtype=np.float32)[:, None]       # (H,1)

    for k in range(K):
        ytop = ys[:, k + 1][None, :]                  # smaller y
        ybot = ys[:, k][None, :]
        cov = np.clip(ybot - Y, 0, 1) * np.clip(Y - ytop, 0, 1)
        cov = np.minimum(cov, 1.0)
        inside = (Y < ybot) & (Y > ytop)
        cov = np.where(inside, 1.0, np.clip(1.0 - np.abs(np.where(np.abs(Y - ytop) < np.abs(Y - ybot), Y - ytop, Y - ybot)), 0, 1))
        width = np.maximum(ybot - ytop, 1e-3)
        mid = 0.5 * (ytop + ybot)
        rel = np.clip(np.abs(Y - mid) / (0.5 * width), 0, 1)
        lum = 0.14 + 0.68 * rel ** 1.7
        col = mode_color(k)
        img += (cov * lum)[..., None].astype(np.float32) * col[None, None, :]

    # glowing boundary threads
    acc = np.zeros((H, W, 3), dtype=np.float32)
    sub = 12
    for k in range(K + 1):
        yb = ys[:, k]
        xs = np.repeat(np.arange(W, dtype=np.float32), sub) + np.tile((np.arange(sub) + 0.5) / sub, W)
        yv = np.interp(xs, np.arange(W, dtype=np.float32) + 0.5, yb).astype(np.float32)
        cA = mode_color(min(k, K - 1))
        cB = mode_color(max(k - 1, 0))
        cc = 0.65 * (cA + cB) / 2 + 0.35
        w = np.tile(cc.astype(np.float32), (xs.size, 1)) * (0.60 / sub)
        splat_rgb(acc, xs, yv, w, W, H)
    img += acc

    img = filmic(img, k=1.35, gamma=0.9)
    img = bloom(img, sigma_tight=1.5, sigma_wide=9.0, amt_tight=0.30, amt_wide=0.18,
                thresh=0.60)
    save(img, out or "variants/fput_braid_%dx%d.png" % (W, H))


if __name__ == "__main__":
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
    H = int(sys.argv[2]) if len(sys.argv) > 2 else 640
    out = sys.argv[3] if len(sys.argv) > 3 else None
    render(W, H, out)
