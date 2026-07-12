"""THE PARLIAMENT OF POLYGONS — hero render.

Nested grand-canonical ensembles of uniform convex lattice arcs. Level k is a
square rotated 45deg*k, scaled 2^{-k/2}, holding an ensemble at N_k = N0*2^k.
Each level's polygons touch their square at its side midpoints; the midpoint
square hosts the next, finer parliament. Arcs are destiny-colored by their
signed-area deviation from the exact finite-N limit path.

Usage: python3 render_poly.py proto|final
"""
import os, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter
from polysample import tune_t, sample_arcs, arc_points, limit_path
from raster import splat_points, sample_polyline, filmic, palette3, save_png, downscale

CACHE = os.path.join(os.path.dirname(__file__), "proto", "pools")
os.makedirs(CACHE, exist_ok=True)

def get_pool(N, count, window, seed):
    f = os.path.join(CACHE, f"pool_N{N}_w{window}_s{seed}.npz")
    if os.path.exists(f):
        d = np.load(f, allow_pickle=True)
        arcs = list(d["arcs"])
        if len(arcs) >= count:
            return [tuple(a) for a in arcs[:count]], float(d["t"])
    smax = max(16, int(14 * N ** (1 / 3)))
    t, V = tune_t(N, smax)
    rng = np.random.default_rng(seed)
    t0 = time.time()
    arcs, st = sample_arcs(N, t, V, count, window=window, rng=rng, verbose=False)
    print(f"  sampled N={N}: {count} arcs, rate {st['rate']:.1e}, "
          f"repaired {st['repaired']}, {time.time()-t0:.0f}s")
    np.savez_compressed(f, arcs=np.array([(a[0], a[1]) for a in arcs], dtype=object),
                        t=t)
    return arcs, t

def arc_deviation(pts, lim):
    """Signed area between arc and limit path (shoelace of arc + reversed limit)."""
    loop = np.vstack([pts, lim[::-1]])
    x, y = loop[:, 0], loop[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

def render(mode="proto"):
    if mode == "proto":
        SIZE, SS = 1024, 2
        levels = [dict(N=24, count=1400, gain=1.9), dict(N=48, count=1100, gain=1.5),
                  dict(N=96, count=900, gain=1.2), dict(N=192, count=700),
                  dict(N=384, count=520, window=1)]
    else:
        SIZE, SS = 4096, 2
        levels = [dict(N=24, count=4200), dict(N=48, count=3400),
                  dict(N=96, count=2800), dict(N=192, count=2200),
                  dict(N=384, count=1500, window=1),
                  dict(N=768, count=1000, window=2)]
    S = SIZE * SS
    acc = np.zeros((S, S), np.float32)
    accv = np.zeros((S, S), np.float32)
    hero_acc = np.zeros((S, S), np.float32)
    C = np.array([S / 2, S / 2])
    side0 = 0.94 * S
    rng = np.random.default_rng(99)

    for k, lv in enumerate(levels):
        N, count = lv["N"], lv["count"]
        window = lv.get("window", 0)
        arcs, t = get_pool(N, count, window, seed=1000 + 7 * N)
        smax = max(16, int(14 * N ** (1 / 3)))
        tt, V = tune_t(N, smax)
        lim = limit_path(tt, V)
        side = side0 * 2 ** (-k / 2)
        u = side / (2 * N)
        th = k * np.pi / 4
        R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        ds_lat = 0.7 / u  # sample spacing in lattice units -> ~0.7 px

        # per-arc deviation values, normalized by level std
        pts_all, vals = [], []
        for a in arcs:
            pts = arc_points(a).astype(np.float64)
            pts_all.append(pts)
            vals.append(arc_deviation(pts, lim))
        vals = np.array(vals)
        vals = vals / (np.std(vals) + 1e-12)
        vals = np.clip(vals / 2.5, -1, 1)

        # ink budget: equal per-pixel BAND density across levels (band width
        # shrinks as 2^{-5k/6}: side 2^{-k/2} x fluctuation N^{2/3}/N), with a
        # gentle inward gain so the sharpening law blazes
        w_level = lv.get("gain", 1.0) * 2 ** (-5 * k / 6) * 1.18 ** k
        w_level *= 700.0 / count

        # splat each arc in all 4 roles (rot90 within the level frame)
        t0 = time.time()
        for a_i, pts in enumerate(pts_all):
            smp, m = sample_polyline(pts, ds_lat)
            if len(smp) == 0:
                continue
            v = vals[a_i]
            q = pts  # lattice coords
            for rot in range(4):
                # rotate arc within lattice frame: (x,y) -> (-y, x) about (0, N) chain
                if rot == 0:
                    P = smp.copy()
                elif rot == 1:
                    P = np.stack([N - smp[:, 1] + 0, smp[:, 0] + N], axis=1)
                elif rot == 2:
                    P = np.stack([-smp[:, 0], 2 * N - smp[:, 1]], axis=1)
                else:
                    P = np.stack([smp[:, 1] - N, N - smp[:, 0]], axis=1)
                # center lattice square [-N,N]x[0,2N] at (0,N), map to screen
                Q = (P - np.array([0.0, N])) * u
                scr = (R @ Q.T).T
                xs = C[0] + scr[:, 0]
                ys = C[1] - scr[:, 1]
                splat_points(acc, xs, ys, m.astype(np.float32) * w_level,
                             accv, np.full(len(xs), v, np.float32))
        # a few crisp individual polygons: 4 random arcs each, own buffer
        nhero = 6
        hrng = np.random.default_rng(4000 + k)
        for h in range(nhero):
            picks = hrng.choice(len(pts_all), 4, replace=False)
            for rot, ai in enumerate(picks):
                smp, m = sample_polyline(pts_all[ai], ds_lat)
                v = vals[ai]
                if rot == 0:
                    P = smp
                elif rot == 1:
                    P = np.stack([N - smp[:, 1], smp[:, 0] + N], axis=1)
                elif rot == 2:
                    P = np.stack([-smp[:, 0], 2 * N - smp[:, 1]], axis=1)
                else:
                    P = np.stack([smp[:, 1] - N, N - smp[:, 0]], axis=1)
                Q = (P - np.array([0.0, N])) * u
                scr = (R @ Q.T).T
                xs = C[0] + scr[:, 0]
                ys = C[1] - scr[:, 1]
                splat_points(hero_acc, xs, ys, m.astype(np.float32))
        print(f"level {k} N={N}: splatted {len(arcs)} arcs x4 in {time.time()-t0:.0f}s")

    # tone map + colorize
    den = acc
    vbar = np.where(den > 1e-8, accv / np.maximum(den, 1e-8), 0.0)
    # smooth the value field slightly so color doesn't sparkle
    vs = gaussian_filter(vbar * den, 1.5) / np.maximum(gaussian_filter(den, 1.5), 1e-8)
    k_tone = 2.6 / np.percentile(den[den > 0], 99.2)
    L = filmic(den * k_tone, 1.0) ** 1.0
    col = palette3(np.clip(vs * 1.4, -1, 1),
                   c_neg=(0.34, 0.55, 0.90),   # steel blue: bulged toward center
                   c_mid=(1.00, 0.92, 0.74),   # ivory-gold: agreement
                   c_pos=(0.96, 0.40, 0.13))   # ember: pressed to the walls
    rgb = L[..., None] * col
    # crisp individual polygons: faint pewter threads over the law
    if hero_acc.max() > 0:
        kh = 0.85 / np.percentile(hero_acc[hero_acc > 0], 90)
        Lh = filmic(hero_acc * kh, 1.0)
        rgb += 0.38 * Lh[..., None] * np.array([0.72, 0.78, 0.80], np.float32)
    # the fixed point of the recursion: a small star where all parliaments
    # would converge
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    r2 = (xx - C[0]) ** 2 + (yy - C[1]) ** 2
    star = 0.55 * np.exp(-r2 / (2 * (S / 160.0) ** 2)) + 0.9 * np.exp(-r2 / (2 * (S / 1100.0) ** 2))
    rgb += star[..., None] * np.array([1.0, 0.9, 0.62], np.float32)
    # gentle bloom on the bright core
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    mask = np.clip((lum - 0.55) / 0.45, 0, 1) ** 2
    bl = gaussian_filter(rgb * mask[..., None], S / 340)
    rgb = 1 - (1 - rgb) * (1 - 0.55 * bl)
    rgb = np.clip(rgb, 0, 1) ** 0.92
    out = downscale(rgb, SIZE)
    path = os.path.join(os.path.dirname(__file__),
                        "proto" if mode == "proto" else ".",
                        f"parliament_{mode}.png")
    save_png(out, path)
    print("saved", path)

if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "proto")
