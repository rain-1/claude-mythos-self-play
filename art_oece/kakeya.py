"""Kakeya / Besicovitch: a Perron tree — 2^K elementary triangles (each carrying
a unit needle in its own direction) translated by the bisection scheme so they
overlap into vanishing area.  Brightness = overlap multiplicity; hue = direction.

Construction (Falconer, 'The geometry of fractal sets', ch. 7):
  cut triangle T (base on the x-axis, apex height H) into 2^K elementary
  triangles by joining the apex to 2^K+1 evenly spaced base points.  Then
  recursively: given two adjacent groups each spanning base width W, translate
  the RIGHT group left by (1-alpha)*W (bases stay on the x-axis).  Applied
  bottom-up (pairs, pairs-of-pairs, ...) with alpha ~ 2/3 the union area -> 0
  as K grows, while every direction of the original fan survives (translation
  never changes a direction).

We verify the invariant: the multiset of edge DIRECTIONS is unchanged, and we
measure the union area of the final tree vs the original triangle.
"""
import numpy as np
import time, os, sys
from PIL import Image, ImageDraw

SCRATCH = "/tmp/claude-0/-home-user-claude-mythos-self-play/14486fce-1a7e-527f-9de4-a144326c3b0e/scratchpad"

def perron_triangles(K, alpha=2/3, H=1.0, halfwidth=1.0):
    """Return list of 2^K triangles, each as (3,2) vertex array, after the
    bisection-translation scheme.  Elementary triangle i has base
    [x_i, x_{i+1}] on y=0 and apex at (0, H) initially."""
    n = 1 << K
    xs = np.linspace(-halfwidth, halfwidth, n + 1)
    tris = []
    for i in range(n):
        tris.append(np.array([[xs[i], 0.0], [xs[i + 1], 0.0], [0.0, H]]))
    tris = np.array(tris)  # (n, 3, 2)
    # bottom-up pairing: at level l, groups of size 2^l merge in pairs.
    # Perron's lemma: two triangles spanning total base 2b merge by shifting the
    # right one left by 2(1-alpha)b; at level l the merged "hearts" have shrunk
    # by alpha^l, so the effective 2b is alpha^l * (pair base width).
    group = 1
    level = 0
    while group < n:
        pair_w = 2 * group * (2 * halfwidth / n)
        shift = (1 - alpha) * (alpha ** level) * pair_w
        for start in range(0, n, 2 * group):
            tris[start + group:start + 2 * group, :, 0] -= shift
        group *= 2
        level += 1
    return tris

def perron_optimized(K, H=1.0, halfwidth=1.0, res=1400):
    """Same pairing structure, but each level's (single, shared) shift is chosen
    by direct search to minimize the rasterized union area — the Besicovitch
    mechanism made empirical."""
    n = 1 << K
    xs = np.linspace(-halfwidth, halfwidth, n + 1)
    tris = np.array([[[xs[i], 0.0], [xs[i + 1], 0.0], [0.0, H]] for i in range(n)])
    group = 1
    while group < n:
        pair_w = 2 * group * (2 * halfwidth / n)
        def area_for(s):
            t2 = tris.copy()
            for start in range(0, n, 2 * group):
                t2[start + group:start + 2 * group, :, 0] -= s
            return union_area(t2, res=res), t2
        best = (None, None, None)
        for s in np.linspace(0, pair_w, 13):
            a, t2 = area_for(s)
            if best[0] is None or a < best[0]:
                best = (a, s, t2)
        # refine around the winner
        s0 = best[1]
        for s in np.linspace(max(0, s0 - pair_w / 12), s0 + pair_w / 12, 9):
            a, t2 = area_for(s)
            if a < best[0]:
                best = (a, s, t2)
        tris = best[2]
        group *= 2
    return tris

def union_area(tris, res=2000):
    """Monte-Carlo-free union area: rasterize on a grid."""
    lo = tris.reshape(-1, 2).min(axis=0); hi = tris.reshape(-1, 2).max(axis=0)
    span = (hi - lo).max()
    img = Image.new("1", (res, res), 0)
    dr = ImageDraw.Draw(img)
    for t in tris:
        pts = [(float((x - lo[0]) / span * (res - 1)),
                float((y - lo[1]) / span * (res - 1))) for x, y in t]
        dr.polygon(pts, fill=1)
    a = np.asarray(img).sum() / ((res - 1) / span) ** 2
    return a

def perron_stages(K, res=1400, upto_levels=None):
    """Run the optimized scheme, returning snapshots after each level (list of
    (n,3,2) arrays), starting with the untouched fan."""
    n = 1 << K
    xs = np.linspace(-1.0, 1.0, n + 1)
    tris = np.array([[[xs[i], 0.0], [xs[i + 1], 0.0], [0.0, 1.0]] for i in range(n)])
    snaps = [tris.copy()]
    group = 1
    while group < n:
        pair_w = 2 * group * (2.0 / n)
        def area_for(s):
            t2 = tris.copy()
            for start in range(0, n, 2 * group):
                t2[start + group:start + 2 * group, :, 0] -= s
            return union_area(t2, res=res), t2
        best = (None, None, None)
        for s in np.linspace(0, pair_w, 13):
            a, t2 = area_for(s)
            if best[0] is None or a < best[0]:
                best = (a, s, t2)
        s0 = best[1]
        for s in np.linspace(max(0, s0 - pair_w / 12), s0 + pair_w / 12, 9):
            a, t2 = area_for(s)
            if a < best[0]:
                best = (a, s, t2)
        tris = best[2]
        snaps.append(tris.copy())
        group *= 2
    return snaps

def rasterize_tris(tris, W, H_px, world_box, hue_by_dir=True):
    """Additive scanline rasterization: rgb accumulation of triangle multiplicity.
    world_box = (x0, y0, x1, y1) mapped to the WxH_px raster (y up -> row down).
    Returns (H_px, W, 3) float array.  Uses the interval-cumsum trick."""
    x0w, y0w, x1w, y1w = world_box
    sx = W / (x1w - x0w); sy = H_px / (y1w - y0w)
    acc = np.zeros((3, H_px, W + 1), np.float32)
    dirs = []
    for t in tris:
        apex = t[2]; bmid = 0.5 * (t[0] + t[1])
        d = apex - bmid
        dirs.append(np.arctan2(d[1], d[0]))
    dirs = np.array(dirs)
    # map direction range onto ramp
    lo, hi = dirs.min(), dirs.max()
    tfrac = (dirs - lo) / max(hi - lo, 1e-9)
    cols = ramp_warmcool_k(tfrac)  # (n,3)
    for t, rgb in zip(tris, cols):
        # rows spanned by the triangle
        ys_w = t[:, 1]
        r0 = int(np.floor((y0w - ys_w.max()) * 0 + (ys_w.min() - y0w) * sy))
        r1 = int(np.ceil((ys_w.max() - y0w) * sy))
        r0 = max(r0, 0); r1 = min(r1, H_px)
        if r1 <= r0: continue
        rows = np.arange(r0, r1)
        yw = y0w + (rows + 0.5) / sy
        # triangle edges: interpolate x at each row (triangle = base edge on some
        # y plus apex; generic: for each row find intersections with 3 edges)
        xs_at = []
        for (a, b) in ((0, 1), (1, 2), (2, 0)):
            pa, pb = t[a], t[b]
            if pa[1] == pb[1]:
                continue
            tt = (yw - pa[1]) / (pb[1] - pa[1])
            valid = (tt >= 0) & (tt <= 1)
            x = pa[0] + tt * (pb[0] - pa[0])
            xs_at.append(np.where(valid, x, np.nan))
        X = np.stack(xs_at)          # (2-3, rows)
        xl = np.nanmin(X, axis=0); xr = np.nanmax(X, axis=0)
        okm = ~np.isnan(xl)
        cl = np.clip(((xl - x0w) * sx), 0, W).astype(np.int32)
        cr = np.clip(((xr - x0w) * sx), 0, W).astype(np.int32)
        cr = np.maximum(cr, cl + 1)
        rr = rows[okm]; cl = cl[okm]; cr = cr[okm]
        for c in range(3):
            np.add.at(acc[c], (rr, cl), rgb[c])
            np.add.at(acc[c], (rr, cr), -rgb[c])
    acc = np.cumsum(acc, axis=2)[:, :, :W]
    return np.moveaxis(acc, 0, -1)

def ramp_warmcool_k(t):
    stops = np.array([
        [1.00, 0.84, 0.42],
        [1.00, 0.60, 0.30],
        [0.95, 0.40, 0.46],
        [0.70, 0.34, 0.74],
        [0.30, 0.46, 0.86],
        [0.12, 0.66, 0.70],
    ])
    x = np.clip(t, 0, 1) * (len(stops) - 1)
    i = np.minimum(x.astype(int), len(stops) - 2)
    f = (x - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f

def verify():
    K = 6
    t0 = perron_triangles(K, alpha=1.0)   # alpha=1 => no shift: the original fan
    t1 = perron_triangles(K)
    # directions of the two slanted edges of each elementary triangle are
    # translation-invariant: compare direction multisets
    def dirs(tris):
        d1 = tris[:, 2] - tris[:, 0]
        d2 = tris[:, 2] - tris[:, 1]
        ang = np.concatenate([np.arctan2(d1[:, 1], d1[:, 0]), np.arctan2(d2[:, 1], d2[:, 0])])
        return np.sort(ang)
    assert np.allclose(dirs(t0), dirs(t1)), "directions changed under translation!"
    a0, a1 = union_area(t0), union_area(t1)
    print(f"K={K}: fan area {a0:.4f} -> perron tree area {a1:.4f} (ratio {a1/a0:.3f})")
    for K in (2, 4, 6, 8, 10):
        t = perron_triangles(K)
        print(f"  K={K:2d}  ntri={1<<K:5d}  union area = {union_area(t):.4f}")

def render_cascade(K=11, stage_ids=(0, 3, None), S_out=2048, SS=2,
                   fname="kakeya_proto.png", outdir=None, nneedles=36,
                   expo=2.6, gamma=0.86, labels=True):
    """Vertical cascade: the fan, a mid stage, the compressed Perron tree.
    One global additive canvas -> one tone map, so growing overlap = growing blaze."""
    from scipy.ndimage import gaussian_filter
    from PIL import Image, ImageDraw, ImageFont
    t0 = time.time()
    snaps = perron_stages(K)
    ids = [i if i is not None else len(snaps) - 1 for i in stage_ids]
    stages = [snaps[i] for i in ids]
    areas = [union_area(t) for t in stages]
    S = S_out * SS
    acc = np.zeros((S, S, 3), np.float32)
    # layout: 3 bands, each world height 1 -> band_h px
    margin = 0.025 * S
    band_h = (S - 2 * margin) / 3.22
    gap = ((S - 2 * margin) - 3 * band_h) / 2
    xspan = S / band_h   # preserve world aspect (square pixels)
    placed = []
    for bi, tris in enumerate(stages):
        cx = 0.5 * (tris.reshape(-1, 2)[:, 0].min() + tris.reshape(-1, 2)[:, 0].max())
        top = margin + bi * (band_h + gap)
        # world box: x centered on cx, width xspan; y: 0..1 mapped to band (y up)
        wb = (cx - xspan / 2, 0.0, cx + xspan / 2, 1.0)
        Wpx = S
        Hpx = int(band_h)
        img = rasterize_tris(tris, Wpx, Hpx, wb)
        img = img[::-1]  # world y-up -> row-down
        acc[int(top):int(top) + Hpx, :, :] += img
        placed.append((top, Hpx, wb, tris))
    # needles on the last stage
    tris = stages[-1]
    top, Hpx, wb, _ = placed[-1]
    x0w, y0w, x1w, y1w = wb
    n = len(tris)
    needle_layer = np.zeros((S, S), np.float32)
    hero_layer = np.zeros((S, S), np.float32)
    from hopf import bilin_add
    picks = list(np.linspace(0, n - 1, nneedles).astype(int))
    hero_i = picks[max(1, len(picks) // 5)]   # a clearly slanted direction
    for i in picks:
        t = tris[i]
        apex = t[2]; bmid = 0.5 * (t[0] + t[1])
        d = bmid - apex; d = d / np.hypot(*d)
        p0, p1 = apex, apex + d  # unit needle
        ts = np.linspace(0, 1, 1200)
        xw = p0[0] + ts * (p1[0] - p0[0]); yw = p0[1] + ts * (p1[1] - p0[1])
        xs = (xw - x0w) / (x1w - x0w) * S
        ys = top + (1 - (yw - y0w) / (y1w - y0w)) * Hpx
        bilin_add(hero_layer if i == hero_i else needle_layer, xs, ys, np.full_like(xs, 1.0))
    # tone map: log multiplicity, floor so single-cover (the fan) stays visible
    mult = acc.sum(axis=-1)
    mult[mult < 1e-2] = 0.0   # float32 cumsum residue is ~1e-7; real cover >= ~0.1
    lum = np.log1p(mult) / np.log1p(max(mult.max(), 1e-9))
    lum = np.where(mult > 0, 0.30 + 0.70 * lum ** 0.8, 0.0)
    csum = acc.sum(axis=-1, keepdims=True); csum[csum < 1e-2] = 1
    chroma = acc / csum
    img = chroma * (2.4 * lum[..., None])
    img = 1 - np.exp(-expo * img)
    # needles: additive white-gold, gently fattened; one gold hero needle + glow
    nl = gaussian_filter(needle_layer, 0.55 * SS) * (2 * np.pi * (0.55 * SS) ** 2)
    nl = np.clip(nl * 0.22, 0, 0.85)
    img += nl[..., None] * np.array([1.0, 0.95, 0.8])
    hl = gaussian_filter(hero_layer, 0.6 * SS) * (2 * np.pi * (0.6 * SS) ** 2)
    hglow = gaussian_filter(hero_layer, 5.0 * SS) * (2 * np.pi * (5.0 * SS) ** 2)
    img += np.clip(hl * 0.5, 0, 1.0)[..., None] * np.array([1.0, 0.87, 0.5])
    img += np.clip(hglow * 0.13, 0, 0.30)[..., None] * np.array([1.0, 0.72, 0.32])
    # soft bloom on the hot overlap cores
    lumf = img.mean(axis=-1)
    m = np.clip((lumf - 0.62) / 0.38, 0, 1)[..., None] * img
    for sgm, amp in ((2.5 * SS, 0.30), (8 * SS, 0.15)):
        for c in range(3):
            img[..., c] += amp * gaussian_filter(m[..., c], sgm)
    img = np.clip(img, 0, 1) ** gamma
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((S_out, S_out), Image.LANCZOS)
    if labels:
        dr = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(S_out * 0.014))
        except Exception:
            font = ImageFont.load_default()
        for (top, Hpx, wb, tris), a in zip(placed, areas):
            y = (top + Hpx) / SS - S_out * 0.012
            dr.text((S_out * 0.045, y), f"area {a:.3f}", fill=(150, 150, 158), font=font)
    path = os.path.join(outdir or SCRATCH, fname)
    im.save(path)
    print(path, f"areas={['%.3f' % a for a in areas]}", f"{time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    verify()
