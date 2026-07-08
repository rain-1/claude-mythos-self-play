"""Piece B — 'To Be Touched' (harmonic measure on the Koch snowflake).

Brownian rain from infinity falls on a Koch snowflake coast. Where it lands
is the harmonic measure of the fractal boundary. Makarov's theorem (1985):
the harmonic measure of ANY simply-connected planar domain lives on a set of
Hausdorff dimension exactly 1 — the rain sees only a dimension-1 sliver of
the dimension-log4/log3 (~1.2619) coast. The fjords stay dark forever.

Method: vectorised walk-on-spheres.
  * distance field to the boundary polygon on a fine grid (EDT),
  * walkers start on / re-enter through a circle via the exact exterior
    Poisson kernel (wrapped-Cauchy sampling) — honest 'from infinity' law,
  * a walker within eps of the coast lands: nearest boundary segment gets
    the hit. Hit counts per depth-D segment aggregate 4-to-1 up the Koch
    hierarchy, giving the multifractal information dimension directly.
"""
import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter
from scipy.spatial import cKDTree
import argparse, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artlib import splat_points, filmic, bloom, ramp, save


def koch_snowflake(depth):
    """Vertices of the Koch snowflake (counterclockwise), circumradius 1."""
    # start from equilateral triangle, apex up
    ang = np.array([90, 210, 330]) * np.pi / 180
    pts = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    for _ in range(depth):
        a = pts
        b = np.roll(pts, -1, axis=0)
        d = b - a
        p1 = a + d / 3
        p2 = a + d / 2 + np.stack([d[:, 1], -d[:, 0]], 1) * (np.sqrt(3) / 6)
        p3 = a + 2 * d / 3
        pts = np.stack([a, p1, p2, p3], axis=1).reshape(-1, 2)
    return pts


def outward_bump(pts):
    """Check orientation: for apex-up triangle listed clockwise?"""
    # signed area
    x, y = pts[:, 0], pts[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def build_distance_field(pts, G, world):
    """Grid distance (in world units) to the polygon boundary."""
    # rasterize boundary: dense samples marked in a boolean grid
    seg = np.hypot(*(np.roll(pts, -1, axis=0) - pts).T)
    n_per = np.maximum(1, np.ceil(seg / (world * 0.5 / G)).astype(int))
    allx, ally = [], []
    b = np.roll(pts, -1, axis=0)
    for i in range(len(pts)):
        t = np.linspace(0, 1, n_per[i], endpoint=False)
        allx.append(pts[i, 0] + (b[i, 0] - pts[i, 0]) * t)
        ally.append(pts[i, 1] + (b[i, 1] - pts[i, 1]) * t)
    bx = np.concatenate(allx); by = np.concatenate(ally)
    gi = np.clip(((bx + world) / (2 * world) * G).astype(int), 0, G - 1)
    gj = np.clip(((by + world) / (2 * world) * G).astype(int), 0, G - 1)
    occ = np.ones((G, G), bool)
    occ[gj, gi] = False
    dist_px = distance_transform_edt(occ)
    cell = 2 * world / G
    return (dist_px * cell).astype(np.float32), cell


def run_wos(pts, n_walkers, batch, depth, G=8192, world=1.9,
            eps_factor=1.0, seed=1, record_waypoints=True, way_stride=1):
    """Returns per-segment hit counts + optional waypoint splat lists."""
    rng = np.random.default_rng(seed)
    DF, cell = build_distance_field(pts, G, world)
    eps = eps_factor * 2 * cell
    safety = 1.5 * cell

    # boundary segments for landing assignment
    mid = 0.5 * (pts + np.roll(pts, -1, axis=0))
    tree = cKDTree(mid)
    nseg = len(pts)
    hits = np.zeros(nseg, np.int64)

    R_in = 2.0           # start / re-entry circle (outside the render frame)
    R_out = 4.0          # beyond this, re-enter via Poisson kernel
    total_landed = 0
    way_x, way_y, way_w = [], [], []

    t0 = time.time()
    while total_landed < n_walkers:
        m = batch
        th = rng.uniform(0, 2 * np.pi, m)
        x = R_in * np.cos(th); y = R_in * np.sin(th)
        alive = np.ones(m, bool)
        for step in range(400):
            if not alive.any():
                break
            xi = x[alive]; yi = y[alive]
            # distance lookup (nearest-cell; conservative with safety margin)
            gi = np.clip(((xi + world) / (2 * world) * G).astype(np.int32), 0, G - 1)
            gj = np.clip(((yi + world) / (2 * world) * G).astype(np.int32), 0, G - 1)
            d = DF[gj, gi] - safety

            landed = d < eps
            if landed.any():
                lx = xi[landed]; ly = yi[landed]
                _, si = tree.query(np.stack([lx, ly], 1), workers=-1)
                np.add.at(hits, si, 1)
                total_landed += landed.sum()
            # move survivors
            move = ~landed
            xi = xi[move]; yi = yi[move]; d = d[move]
            if xi.size:
                # outside the far circle: exact exterior-disk re-entry
                r = np.hypot(xi, yi)
                far = r > R_out
                if far.any():
                    rho = R_in / r[far]
                    thx = np.arctan2(yi[far], xi[far])
                    u = rng.uniform(0, 1, far.sum())
                    dth = 2 * np.arctan((1 - rho) / (1 + rho)
                                        * np.tan(np.pi * (u - 0.5)))
                    xi[far] = R_in * np.cos(thx + dth)
                    yi[far] = R_in * np.sin(thx + dth)
                    d[far] = np.maximum(DF[
                        np.clip(((yi[far] + world) / (2 * world) * G).astype(np.int32), 0, G - 1),
                        np.clip(((xi[far] + world) / (2 * world) * G).astype(np.int32), 0, G - 1)]
                        - safety, eps * 0.5)
                ang = rng.uniform(0, 2 * np.pi, xi.size)
                xi = xi + d * np.cos(ang)
                yi = yi + d * np.sin(ang)
                if record_waypoints and (step % way_stride == 0):
                    way_x.append(xi[::4].astype(np.float32))
                    way_y.append(yi[::4].astype(np.float32))
            # compact
            idx = np.where(alive)[0]
            alive[idx[landed]] = False
            alive[idx[move]] = True
            nx = np.full(m, np.nan)
            ny = np.full(m, np.nan)
            keep = idx[move]
            x[keep] = xi; y[keep] = yi
            alive_new = np.zeros(m, bool); alive_new[keep] = True
            alive = alive_new
        print(f'  landed {total_landed}/{n_walkers}  ({time.time()-t0:.0f}s)', flush=True)
    return hits, (way_x, way_y)


def interior_mask(pts, G, world):
    """Boolean grid: True inside the snowflake polygon."""
    from PIL import Image, ImageDraw
    im = Image.new('1', (G, G), 0)
    dr = ImageDraw.Draw(im)
    poly = [((x + world) / (2 * world) * G, (y + world) / (2 * world) * G)
            for x, y in pts]
    dr.polygon(poly, fill=1)
    return np.array(im, bool)


def run_fog(pts, n_walkers, G=8192, world=1.9, seed=7, max_steps=4000,
            record_stride=2, sigma_frac=0.33, sigma_cap=0.06):
    """True small-step Brownian occupation pass (for the rain fog layer).

    Gaussian increments with adaptive sigma = sigma_frac * dist (capped);
    each recorded position carries weight sigma^2 (occupation time), so the
    splat estimates the Green's function of the exterior — no WoS caustics.
    """
    rng = np.random.default_rng(seed)
    DF, cell = build_distance_field(pts, G, world)
    inside = interior_mask(pts, G, world)
    eps = 2.5 * cell
    R_in, R_out = 2.0, 4.0

    th = rng.uniform(0, 2 * np.pi, n_walkers)
    x = R_in * np.cos(th); y = R_in * np.sin(th)
    fx, fy, fw = [], [], []
    t0 = time.time()
    for step in range(max_steps):
        if x.size == 0:
            break
        gi = np.clip(((x + world) / (2 * world) * G).astype(np.int32), 0, G - 1)
        gj = np.clip(((y + world) / (2 * world) * G).astype(np.int32), 0, G - 1)
        d = DF[gj, gi]
        dead = (d < eps) | inside[gj, gi]
        # exterior re-entry for far walkers
        r = np.hypot(x, y)
        far = r > R_out
        if far.any():
            rho = R_in / r[far]
            thx = np.arctan2(y[far], x[far])
            u = rng.uniform(0, 1, far.sum())
            dth = 2 * np.arctan((1 - rho) / (1 + rho) * np.tan(np.pi * (u - 0.5)))
            x[far] = R_in * np.cos(thx + dth)
            y[far] = R_in * np.sin(thx + dth)
            d[far] = eps * 4
        keep = ~dead
        x = x[keep]; y = y[keep]; d = d[keep]
        sig = np.clip(d * sigma_frac, cell, sigma_cap)
        x = x + rng.normal(0, sig)
        y = y + rng.normal(0, sig)
        if step % record_stride == 0:
            fx.append(x.astype(np.float32))
            fy.append(y.astype(np.float32))
            fw.append((sig * sig).astype(np.float32))
        if step % 500 == 0:
            print(f'  fog step {step}: {x.size} alive ({time.time()-t0:.0f}s)',
                  flush=True)
    return (np.concatenate(fx) if fx else np.array([])), \
           (np.concatenate(fy) if fy else np.array([])), \
           (np.concatenate(fw) if fw else np.array([]))


def run_streaks(pts, n_walkers, G=8192, world=1.9, seed=13, max_steps=6000,
                tail=28, sigma_frac=0.33, sigma_cap=0.06):
    """Small-step Brownian walkers; returns the last `tail` positions of each
    walker that lands — true landing trajectories ('rain streaks')."""
    rng = np.random.default_rng(seed)
    DF, cell = build_distance_field(pts, G, world)
    inside = interior_mask(pts, G, world)
    eps = 2.5 * cell
    R_in, R_out = 2.0, 4.0

    th = rng.uniform(0, 2 * np.pi, n_walkers)
    x = R_in * np.cos(th); y = R_in * np.sin(th)
    hist = np.full((n_walkers, tail, 2), np.nan, np.float32)
    head = 0
    streaks = []
    alive_idx = np.arange(n_walkers)
    t0 = time.time()
    for step in range(max_steps):
        if x.size == 0:
            break
        gi = np.clip(((x + world) / (2 * world) * G).astype(np.int32), 0, G - 1)
        gj = np.clip(((y + world) / (2 * world) * G).astype(np.int32), 0, G - 1)
        d = DF[gj, gi]
        dead = (d < eps) | inside[gj, gi]
        if dead.any():
            for i in np.where(dead)[0]:
                buf = hist[alive_idx[i]]
                # unroll ring buffer into time order
                sl = np.concatenate([buf[head:], buf[:head]], 0)
                sl = sl[~np.isnan(sl[:, 0])]
                streaks.append(sl)
        keep = ~dead
        x = x[keep]; y = y[keep]; alive_idx = alive_idx[keep]; d = d[keep]
        r = np.hypot(x, y)
        far = r > R_out
        if far.any():
            rho = R_in / r[far]
            thx = np.arctan2(y[far], x[far])
            u = rng.uniform(0, 1, far.sum())
            dth = 2 * np.arctan((1 - rho) / (1 + rho) * np.tan(np.pi * (u - 0.5)))
            x[far] = R_in * np.cos(thx + dth)
            y[far] = R_in * np.sin(thx + dth)
            hist[alive_idx[far]] = np.nan     # streak restarts after re-entry
            d[far] = eps * 4
        sig = np.clip(d * sigma_frac, cell, sigma_cap)
        x = x + rng.normal(0, sig)
        y = y + rng.normal(0, sig)
        hist[alive_idx, head, 0] = x
        hist[alive_idx, head, 1] = y
        head = (head + 1) % tail
        if step % 1000 == 0:
            print(f'  streak step {step}: {x.size} alive, {len(streaks)} landed '
                  f'({time.time()-t0:.0f}s)', flush=True)
    return streaks


def makarov_dimension(hits, depth):
    """Information dimension estimate by 4-to-1 coarse-graining up the Koch
    hierarchy: at level j (scale 3^-j), segments group in 4s."""
    p = hits / hits.sum()
    rows = []
    h = hits.astype(np.float64)
    for j in range(depth, -1, -1):
        pj = h / h.sum()
        nz = pj[pj > 0]
        I = -(nz * np.log(nz)).sum()
        rows.append((j, (1 / 3) ** j, I))
        if j > 0:
            h = h.reshape(-1, 4).sum(1)
    # slope of I vs log(1/scale) over the middle scales
    js = np.array([r[0] for r in rows], float)
    Is = np.array([r[2] for r in rows])
    sel = (js >= 2) & (js <= depth - 1)   # avoid the two extreme scales
    A = np.polyfit(js[sel] * np.log(3), Is[sel], 1)
    return rows, A[0]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--depth', type=int, default=6)
    ap.add_argument('--walkers', type=int, default=2_000_000)
    ap.add_argument('--batch', type=int, default=500_000)
    ap.add_argument('--grid', type=int, default=8192)
    ap.add_argument('--save-hits', default='variants/koch_hits.npz')
    args = ap.parse_args()

    pts = koch_snowflake(args.depth)
    print(f'depth {args.depth}: {len(pts)} segments, signed area {outward_bump(pts):.4f}')
    hits, (wx, wy) = run_wos(pts, args.walkers, args.batch, args.depth,
                             G=args.grid)
    rows, dim = makarov_dimension(hits, args.depth)
    print('information dimension of hit measure (Makarov predicts 1):', round(dim, 4))
    print('box dim of coast: log4/log3 =', round(np.log(4) / np.log(3), 4))
    for j, s, I in rows:
        print(f'   level {j}: scale 3^-{j}, I = {I:.3f}, I/ln(3^j) = '
              f'{I / max(j * np.log(3), 1e-9):.3f}' if j else '')
    frac_dark = (hits == 0).mean()
    print(f'fraction of coast never touched: {frac_dark:.3f}')
    np.savez_compressed(args.save_hits, hits=hits, depth=args.depth,
                        pts=pts.astype(np.float32),
                        wx=np.concatenate(wx) if wx else np.array([]),
                        wy=np.concatenate(wy) if wy else np.array([]))
    print('saved', args.save_hits)
