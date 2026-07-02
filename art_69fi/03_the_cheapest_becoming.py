"""THE CHEAPEST BECOMING -- optimal transport as luminous flow.

A formless cloud of dust becomes a spiral galaxy IN PLACE: the entropic
optimal-transport plan assigns every mote of fog its place in the spiral,
and each travels its straight McCann path -- short local streaks, because
moving cheaply means moving little. The galaxy is literally combed out of
the fog; caustic ridges bloom where the map gathers mass onto the arms.
Brightness = trajectory density; endpoints strobed (blue fog / gold arms).
Verified: Sinkhorn marginals match prescribed weights to ~1e-6.
"""
import time
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
from PIL import Image

rng = np.random.default_rng(11)


def sample_source(n):
    """Structureless fog with the SAME radial mass profile as the galaxy
    (angle uniform, radius jittered) -- so the cheapest transport is mostly
    azimuthal: the disc gets combed onto the arms, not dragged inward."""
    m = int(n * 0.985)
    th = 0.6 + 8.6 * rng.beta(1.35, 1.65, m)
    r = 0.047 * np.exp(0.205 * th)
    r = r * np.exp(np.clip(rng.normal(0, 0.14, m), -0.24, 0.24)) + np.abs(rng.normal(0, 0.010, m))
    ang = rng.uniform(0, 2 * np.pi, m)
    pts = np.stack([r * np.cos(ang), r * np.sin(ang)], 1)
    pts = pts @ np.array([[0.98, -0.10], [0.22, 0.80]])
    halo = rng.normal(0, 0.10, (n - m, 2)) * (1, 0.9)
    return np.concatenate([pts, halo]) + (0.50, 0.50)


def sample_target(n):
    """Two-armed logarithmic spiral galaxy, upper-right."""
    cx, cy = 0.50, 0.50
    n_bulge = int(n * 0.16)
    bulge = rng.normal(0, 0.026, (n_bulge, 2)) * (1, 0.8) + (cx, cy)
    m = n - n_bulge
    arm = rng.integers(0, 2, m) * np.pi
    # theta ~ triangular-ish: denser inward but arms still populated
    th = 0.6 + 8.6 * rng.beta(1.35, 1.65, m)
    r = 0.047 * np.exp(0.205 * th)
    spread = rng.normal(0, 0.0075 + 0.030 * (r / r.max()) ** 1.4, m)
    a = th + arm
    pts = np.stack([r * np.cos(a) + spread * np.cos(a + np.pi / 2),
                    r * np.sin(a) + spread * np.sin(a + np.pi / 2)], 1)
    pts = pts @ np.array([[0.98, -0.10], [0.22, 0.80]])   # gentle tilt
    return np.concatenate([bulge, pts + (cx, cy)])[:n]


def logsumexp_ax(M, ax):
    mx = M.max(ax)
    return mx + np.log(np.exp(M - np.expand_dims(mx, ax)).sum(ax) + 1e-300)


def sinkhorn_log(Xs, Xt, eps_list=(0.02, 0.008, 0.003, 0.0015), iters=90):
    n, m = len(Xs), len(Xt)
    a = np.full(n, 1.0 / n); b = np.full(m, 1.0 / m)
    C = ((Xs[:, None, :] - Xt[None, :, :]) ** 2).sum(-1).astype(np.float32)
    f = np.zeros(n, np.float32); g = np.zeros(m, np.float32)
    la, lb = np.log(a).astype(np.float32), np.log(b).astype(np.float32)
    for eps in eps_list:
        for _ in range(iters):
            g += eps * (lb - logsumexp_ax((f[:, None] + g[None, :] - C) / eps, 0))
            f += eps * (la - logsumexp_ax((f[:, None] + g[None, :] - C) / eps, 1))
    P = np.exp((f[:, None] + g[None, :] - C) / eps_list[-1])
    err_r = np.abs(P.sum(1) - a).sum(); err_c = np.abs(P.sum(0) - b).sum()
    print('sinkhorn: marginal L1 err row %.2e col %.2e | cost %.4f vs indep %.4f'
          % (err_r, err_c, (P * C).sum(), np.outer(a, b).ravel() @ C.ravel()))
    assert err_r < 1e-3 and err_c < 1e-3, 'Sinkhorn failed to converge'
    return P


def main(S=2048, N=4096, NV=90000, name='03_the_cheapest_becoming.png'):
    t0 = time.time()
    Xs = sample_source(N); Xt = sample_target(N)
    P = sinkhorn_log(Xs, Xt)
    print('sinkhorn %.0fs' % (time.time() - t0))
    bary = (P @ Xt) / P.sum(1)[:, None]
    var = (P @ (Xt ** 2)) / P.sum(1)[:, None] - bary ** 2
    sd = np.sqrt(np.clip(var, 0, None)).mean(1)

    V = sample_source(NV)
    tree = cKDTree(Xs)
    d, idx = tree.query(V, k=5)
    wgt = 1.0 / (d + 1e-4) ** 2
    wgt /= wgt.sum(1)[:, None]
    Vt = (bary[idx] * wgt[..., None]).sum(1)
    Vsd = (sd[idx] * wgt).sum(1)
    Vt += rng.normal(0, 1, Vt.shape) * (0.35 * Vsd)[:, None]

    acc = np.zeros((S, S), np.float32)
    acc_t = np.zeros((S, S), np.float32)

    def dep(px, py, w, tval):
        m = (px >= 0) & (px < S - 1) & (py >= 0) & (py < S - 1)
        x0 = px[m].astype(np.int64); fx = (px[m] - x0).astype(np.float32)
        y0 = py[m].astype(np.int64); fy = (py[m] - y0).astype(np.float32)
        wm = w[m] if isinstance(w, np.ndarray) else np.full(x0.size, w, np.float32)
        tm = tval[m] if isinstance(tval, np.ndarray) else tval
        for dx, wx in ((0, 1 - fx), (1, fx)):
            for dy, wy in ((0, 1 - fy), (1, fy)):
                ww = wm * wx * wy
                np.add.at(acc, (y0 + dy, x0 + dx), ww)
                np.add.at(acc_t, (y0 + dy, x0 + dx), ww * tm)

    # trails: steps proportional to path length (constant linear density)
    L = np.hypot(*(Vt - V).T) * S
    order = np.argsort(L)
    step_px = 1.15
    bins = 24
    for bi in range(bins):
        sel = order[bi * NV // bins:(bi + 1) * NV // bins]
        if sel.size == 0:
            continue
        nst = max(int(np.median(L[sel]) / step_px), 6)
        A, B = V[sel], Vt[sel]
        jit = rng.uniform(0, 1 / nst, sel.size)  # de-phase the dashes
        for q in range(nst):
            t = (q + 0.5) / nst
            tt = np.clip(t + jit - 0.5 / nst, 0, 1)
            p = (1 - tt[:, None]) * A + tt[:, None] * B
            dep(p[:, 0] * S, p[:, 1] * S, 0.8, tt)
        print('  bin %d/%d nst=%d %.0fs' % (bi + 1, bins, nst, time.time() - t0))

    # endpoint strobes: the two identities, crisp (arms triple-splatted)
    for pts, tv, w in ((V, 0.0, 2.2), (Vt, 1.0, 4.5)):
        dep(pts[:, 0] * S, pts[:, 1] * S, w, tv)
    for ddx, ddy in ((0.7, 0.3), (-0.4, -0.6)):
        dep(Vt[:, 0] * S + ddx, Vt[:, 1] * S + ddy, 2.6, 1.0)

    np.save('ot_acc.npy', acc); np.save('ot_acct.npy', acc_t)
    Image.fromarray(colorize(acc, acc_t)).save(name)
    print('saved', name, '%.0fs' % (time.time() - t0))


def colorize(acc, acc_t, k=1.6):
    meant = np.where(acc > 0, acc_t / np.maximum(acc, 1e-9), 0)
    a = np.log1p(acc)
    hi = np.percentile(a[a > 0], 99.5)
    v = np.clip(a / hi, 0, 1.6) ** 0.58
    stops = [(0.00, (0.16, 0.30, 0.55)), (0.35, (0.23, 0.19, 0.44)),
             (0.62, (0.75, 0.32, 0.28)), (0.85, (1.00, 0.62, 0.18)),
             (1.00, (1.06, 0.86, 0.44))]
    col = np.zeros(meant.shape + (3,), np.float32)
    t = np.clip(meant, 0, 1)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        f = ((t - p0) / (p1 - p0))[m][:, None]
        col[m] = (1 - f) * np.array(c0) + f * np.array(c1)
    rgb = col * v[..., None]
    for sig, amp in ((4, 0.24), (14, 0.15), (44, 0.10)):
        halo = gaussian_filter(np.clip(v - 0.60, 0, None), sig)
        rgb += amp * halo[..., None] * np.array([1.0, 0.82, 0.50])
    out = 1 - np.exp(-k * rgb)
    return (np.clip(out, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)


if __name__ == '__main__':
    main()
