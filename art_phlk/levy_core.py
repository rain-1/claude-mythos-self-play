"""Levy-flight engine: heavy-tailed random walk, occupation-measure splatting.

A Levy flight = random walk whose step lengths follow a power law
P(L > l) = (l0/l)^alpha (Pareto tail, index alpha), directions uniform.
For alpha >= 2 the variance exists -> CLT -> Brownian fuzz.
For alpha < 2 the second moment DIVERGES -> the walk is dominated by its
largest leaps -> a self-similar archipelago of islands at every scale.
"""
import numpy as np


def levy_walk(n, alpha, seed=0, l0=1.0, chunk=20_000_000):
    """Positions of an n-step Levy flight (float64 cumsum for accuracy,
    returned as float64 [n,2]). Pareto(alpha) step lengths, uniform angles."""
    rng = np.random.default_rng(seed)
    out = np.empty((n, 2), np.float64)
    pos = np.zeros(2)
    done = 0
    while done < n:
        m = min(chunk, n - done)
        u = rng.random(m)
        L = l0 * u ** (-1.0 / alpha)          # Pareto tail index alpha
        th = rng.random(m) * (2 * np.pi)
        dx = L * np.cos(th)
        dy = L * np.sin(th)
        xs = np.cumsum(dx) + pos[0]
        ys = np.cumsum(dy) + pos[1]
        out[done:done + m, 0] = xs
        out[done:done + m, 1] = ys
        pos = np.array([xs[-1], ys[-1]])
        done += m
    return out


def splat_bilinear(acc, X, Y, W, w=None):
    """Additive bilinear splat of points (X,Y in pixel coords) into acc[W,W]."""
    m = (X >= 0) & (X < W - 1) & (Y >= 0) & (Y < W - 1)
    X = X[m]; Y = Y[m]
    if w is not None:
        w = w[m]
    x0 = X.astype(np.int64); y0 = Y.astype(np.int64)
    fx = X - x0; fy = Y - y0
    flat = acc.ravel()
    for ddy, ddx, ww in ((0, 0, (1 - fx) * (1 - fy)), (0, 1, fx * (1 - fy)),
                         (1, 0, (1 - fx) * fy), (1, 1, fx * fy)):
        wgt = ww if w is None else ww * w
        np.add.at(flat, (y0 + ddy) * W + (x0 + ddx), wgt.astype(acc.dtype))
    return int(m.sum())


def occupation(pos, W, box, channels=1, tchan=None, chunk=30_000_000):
    """Accumulate occupation density of positions into a [W,W] (or [W,W,C])
    field. box=(cx,cy,half). tchan: optional [n] channel weights in [0,C)."""
    cx, cy, half = box
    scale = (W - 1) / (2 * half)
    if channels == 1:
        acc = np.zeros((W, W), np.float32)
    else:
        acc = np.zeros((channels, W, W), np.float32)
    n = len(pos)
    kept = 0
    for s in range(0, n, chunk):
        p = pos[s:s + chunk]
        X = (p[:, 0] - (cx - half)) * scale
        Y = (p[:, 1] - (cy - half)) * scale
        if channels == 1:
            kept += splat_bilinear(acc, X, Y, W)
        else:
            t = tchan[s:s + chunk]
            c0 = np.clip(t.astype(np.int64), 0, channels - 1)
            c1 = np.clip(c0 + 1, 0, channels - 1)
            f = np.clip(t - c0, 0, 1)
            for c in range(channels):
                w = np.where(c0 == c, 1 - f, 0) + np.where(c1 == c, f, 0)
                mm = w > 0
                if mm.any():
                    kept += splat_bilinear(acc[c], X[mm], Y[mm], W, w[mm])
    return acc, kept


def hist_eq(field, gamma=1.0):
    """Histogram-equalise log-density of a nonneg field -> [0,1]."""
    v = np.log1p(field.astype(np.float64))
    flat = v.ravel()
    nz = flat > 0
    order = np.argsort(flat[nz], kind='stable')
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, order.size + 1)
    out = np.zeros_like(flat)
    out[nz] = (ranks / order.size) ** gamma
    return out.reshape(field.shape)
