"""Render Piece B — Brownian rain on the Koch coast.

Layers:
  1. cold fog       — WoS walker waypoints (the rain in flight),
  2. warm coast     — boundary segments lit by log hit-density,
  3. silhouette     — untouched segments as barely-visible dark ember wire,
  4. interior       — pure black (Brownian motion never enters).
"""
import numpy as np
from scipy.ndimage import gaussian_filter
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artlib import splat_points, filmic, bloom, ramp, save
from koch_rain import (koch_snowflake, run_wos, run_fog, run_streaks,
                       makarov_dimension)


def streak_layer(streaks, W, world, tail=100, spseg=6, cx=0.0, cy=0.0):
    """Vectorised splat of landing trajectories, fading in toward landing."""
    scale = W / (2 * world)
    ns = len(streaks)
    arr = np.full((ns, tail, 2), np.nan, np.float32)
    for i, s in enumerate(streaks):
        if len(s) >= 4:
            arr[i, -len(s):] = s[-tail:]
    p0 = arr[:, :-1, :]; p1 = arr[:, 1:, :]
    t = np.linspace(0, 1, spseg, endpoint=False)[None, None, :, None]
    pts_ = p0[:, :, None, :] + (p1 - p0)[:, :, None, :] * t   # (ns, tail-1, spseg, 2)
    wgt = (np.arange(tail - 1) / (tail - 2)) ** 2.0            # fade toward landing
    w = np.broadcast_to(wgt[None, :, None], pts_.shape[:3]).ravel() / spseg
    x = pts_[..., 0].ravel(); y = pts_[..., 1].ravel()
    ok = np.isfinite(x) & np.isfinite(y)
    layer = np.zeros((W, W), np.float32)
    px = (x[ok] - cx + world) * scale
    py = (world - (y[ok] - cy)) * scale
    splat_points(layer, px, py, w[ok])
    return layer


def render(hits, pts, wx, wy, ww, path, S=2560, ss=2, world=1.32,
           fog_gain=1.0, coast_gain=1.0, k_tone=2.6, gamma=0.88,
           streaks=None, streak_gain=1.0, cx=0.0, cy=0.0):
    W = S * ss
    scale = W / (2 * world)

    def to_px(x, y):
        return (x - cx + world) * scale, (world - (y - cy)) * scale

    # ---- fog layer (cold): Brownian occupation density, log-compressed
    fog = np.zeros((W, W), np.float32)
    for a in range(0, len(wx), 4_000_000):
        px, py = to_px(wx[a:a + 4_000_000].astype(np.float64),
                       wy[a:a + 4_000_000].astype(np.float64))
        splat_points(fog, px, py, ww[a:a + 4_000_000].astype(np.float64))
    fog = gaussian_filter(fog, 1.3 * ss)
    fog = np.log1p(fog / max(np.percentile(fog[fog > 0], 60), 1e-12))
    fog /= max(np.percentile(fog, 99.8), 1e-9)

    # ---- coast layer: per-segment brightness from hits
    b = np.roll(pts, -1, axis=0)
    seglen = np.hypot(*(b - pts).T)
    h = hits.astype(np.float64)
    lh = np.log1p(h)
    u = lh / max(lh.max(), 1e-9)          # 0 = never touched, 1 = brightest

    # dense boundary samples, each carrying its segment's u
    npseg = np.maximum(2, np.ceil(seglen * scale * 3).astype(int))
    idx = np.repeat(np.arange(len(pts)), npseg)
    t = (np.arange(idx.size) - np.repeat(np.concatenate(([0], np.cumsum(npseg)[:-1])), npseg)) \
        / np.repeat(npseg, npseg)
    sx = pts[idx, 0] + (b[idx, 0] - pts[idx, 0]) * t
    sy = pts[idx, 1] + (b[idx, 1] - pts[idx, 1]) * t
    su = u[idx]
    mass = 1.0 / np.repeat(npseg, npseg)  # constant mass per segment-length

    cr = np.zeros((W, W), np.float32)
    cg = np.zeros((W, W), np.float32)
    cb = np.zeros((W, W), np.float32)
    col = ramp(su, [(0.00, (0.14, 0.04, 0.14)),   # untouched: dark wine wire
                    (0.18, (0.42, 0.08, 0.10)),
                    (0.40, (0.85, 0.28, 0.06)),
                    (0.62, (1.00, 0.58, 0.16)),
                    (0.84, (1.00, 0.86, 0.46)),
                    (1.00, (1.00, 0.98, 0.90))])
    # brightness IS the measure: linear in hit fraction (percentile-pinned),
    # plus a faint floor so the untouched coast exists as a dark wire
    hp = np.percentile(h[h > 0], 99.9) if (h > 0).any() else 1.0
    bright = 0.15 + 2.0 * np.clip(h / hp, 0, 1.2)[idx]
    px, py = to_px(sx, sy)
    spp = npseg.astype(np.float64)  # samples per seg — keep px-mass uniform
    m0 = np.repeat(seglen * scale / npseg, npseg)  # arclength px per sample
    for acc, c in ((cr, 0), (cg, 1), (cb, 2)):
        splat_points(acc, px, py, col[..., c] * bright * m0)
    for acc in (cr, cg, cb):
        acc[:] = gaussian_filter(acc, 0.7 * ss) * min(2 * np.pi * (0.7 * ss) ** 2, 4.0)

    # ---- vignette: quiet the far field so the coast is the light source
    yy, xx = np.mgrid[0:W, 0:W]
    rr = np.hypot(xx - (W - 1) / 2, yy - (W - 1) / 2) / (W / 2)
    vig = 1.0 / (1.0 + np.exp((rr - 0.98) * 5.0))

    # ---- rain streaks (landing trajectories)
    st = None
    if streaks is not None and len(streaks):
        st = streak_layer(streaks, W, world, cx=cx, cy=cy)
        st = gaussian_filter(st, 0.8 * ss)
        st /= max(np.percentile(st[st > 0], 99.9), 1e-12)

    # ---- compose
    rgb = np.zeros((W, W, 3), np.float32)
    fog_col = np.array([0.15, 0.26, 0.44])
    for c in range(3):
        rgb[..., c] = (fog_gain * fog * fog_col[c]) * vig + coast_gain * [cr, cg, cb][c]
    if st is not None:
        st_col = np.array([0.75, 0.88, 1.0])
        for c in range(3):
            rgb[..., c] += streak_gain * st * st_col[c]
    rgb = filmic(rgb, k=k_tone, gamma=gamma)
    rgb = bloom(rgb, mask_lo=0.55, sigma=6 * ss, gain=0.6, tint=(1.0, 0.85, 0.6))
    save(rgb, path, down=ss)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--depth', type=int, default=6)
    ap.add_argument('--walkers', type=int, default=8_000_000)
    ap.add_argument('--batch', type=int, default=1_000_000)
    ap.add_argument('--grid', type=int, default=8192)
    ap.add_argument('--out', default='variants/koch_proto.png')
    ap.add_argument('--size', type=int, default=1280)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--world', type=float, default=1.32)
    ap.add_argument('--cx', type=float, default=0.0)
    ap.add_argument('--cy', type=float, default=0.0)
    ap.add_argument('--fog', type=float, default=1.0)
    ap.add_argument('--coast', type=float, default=1.0)
    ap.add_argument('--ktone', type=float, default=2.6)
    ap.add_argument('--fogwalkers', type=int, default=200_000)
    ap.add_argument('--streakwalkers', type=int, default=50_000)
    ap.add_argument('--streak', type=float, default=1.0)
    ap.add_argument('--cache', default='')
    args = ap.parse_args()

    if args.cache and os.path.exists(args.cache):
        z = np.load(args.cache, allow_pickle=True)
        hits, pts, wx, wy, ww = z['hits'], z['pts'], z['wx'], z['wy'], z['ww']
        streaks = list(z['streaks']) if 'streaks' in z else []
        depth = int(z['depth'])
        print('loaded cache', args.cache, 'hits total', hits.sum())
    else:
        pts = koch_snowflake(args.depth)
        hits, _ = run_wos(pts, args.walkers, args.batch, args.depth,
                          G=args.grid, record_waypoints=False)
        wx, wy, ww = run_fog(pts, args.fogwalkers, G=args.grid)
        streaks = run_streaks(pts, args.streakwalkers, G=args.grid)
        if args.cache:
            np.savez_compressed(args.cache, hits=hits, depth=args.depth,
                                pts=pts.astype(np.float32), wx=wx, wy=wy, ww=ww,
                                streaks=np.array(streaks, dtype=object))
    rows, dim = makarov_dimension(hits, args.depth)
    print('info dimension:', round(dim, 4),
          ' untouched fraction:', round((hits == 0).mean(), 4))
    render(hits, pts, wx, wy, ww, args.out, S=args.size, ss=args.ss,
           world=args.world, fog_gain=args.fog, coast_gain=args.coast,
           k_tone=args.ktone, streaks=streaks, streak_gain=args.streak,
           cx=args.cx, cy=args.cy)
