"""ONE PARTITION, ALREADY THE LAW — a single uniform random partition of n,
drawn at cell grain, lit by hook length; its staircase rim already hugs the
Vershik curve  e^{-pi x/sqrt(6n)} + e^{-pi y/sqrt(6n)} = 1.

Ghost ensemble: 42 sibling partitions' boundary staircases in ice blue.
Usage: python3 render_partition.py proto|final
"""
import os, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter
from fristedt import sample_partitions, parts_from_mult, boundary_staircase
from raster import splat_points, sample_polyline, filmic, save_png

def render(mode="proto"):
    if mode == "proto":
        n, FRAME, PX = 250_000, 1024, 1     # frame in cells, px per cell
        NGHOST = 46
    else:
        n, FRAME, PX = 250_000, 1024, 2
        NGHOST = 46
    S = FRAME * PX
    rs = np.sqrt(n)

    print("sampling hero partition (exact)...")
    t0 = time.time()
    hero = sample_partitions(n, 1, window=0, seed=20260712, verbose=True)[0]
    print(f"  {time.time()-t0:.0f}s")
    parts = parts_from_mult(hero)
    lam = parts.astype(np.int64)                     # descending
    print(f"largest part {lam[0]}, #parts {len(lam)}")

    # conjugate
    lamp = np.zeros(lam[0] + 1, np.int64)
    np.add.at(lamp, lam, 0)  # noop, keep shape
    # lambda'_j = #{i: lam_i > j}
    cnt = np.bincount(lam, minlength=lam[0] + 1)
    lamp = n_ge = np.cumsum(cnt[::-1])[::-1]  # n_ge[v] = #{parts >= v}
    # cell grid (FRAME x FRAME), row i, col j occupied iff j < lam_i
    L = np.zeros((FRAME, FRAME), np.int64)
    nrows = min(len(lam), FRAME)
    lam_c = np.minimum(lam[:nrows], FRAME)
    mask = np.arange(FRAME)[None, :] < lam_c[:, None]     # (nrows, FRAME)
    # hooks: h = (lam_i - j) + (lam'_j - i) - 1
    jj = np.arange(FRAME)[None, :]
    ii = np.arange(nrows)[:, None]
    lamp_j = n_ge[np.minimum(jj + 1, lam[0])]             # lambda'_j = #{parts >= j+1}
    H = (lam[:nrows, None] - jj) + (lamp_j - ii) - 1
    Hf = np.zeros((FRAME, FRAME), np.float32)
    Hf[:nrows][mask] = H[mask].astype(np.float32)
    occ = Hf > 0
    assert (Hf[occ] >= 1).all()
    total = int(mask.sum())
    print(f"cells in frame: {total} of n={n}")

    # verify hooks on the fly: h==1 cells == number of outer corners+edges? sanity:
    # every column/row end cell must have small h; check min==1
    assert Hf[occ].min() == 1.0

    # luminance from hooks: glowing rim, smoldering interior; log-periodic
    # shimmer = a ring at every doubling of hook length (honest: pure f(h))
    v = np.zeros_like(Hf)
    hh = Hf[occ]
    base = 0.11 + 0.59 * (1.0 / hh) ** 0.30 + 0.30 * (1.0 / hh)
    amp = 0.20 * np.exp(-np.log2(np.maximum(hh, 2)) / 12.0)
    ring = 1.0 + amp * np.cos(2 * np.pi * np.log2(hh)) * (hh > 2)
    v[occ] = np.clip(base * ring, 0, 1)

    # upscale to pixels (NEAREST => crisp cells)
    img_v = np.kron(v, np.ones((PX, PX), np.float32))
    # y flip: row 0 (longest part) at BOTTOM
    img_v = img_v[::-1]

    # color: ember body -> gold rim
    t = np.clip((img_v - 0.11) / 0.89, 0, 1) ** 0.8
    c_dark = np.array([0.30, 0.075, 0.075], np.float32)
    c_mid = np.array([0.85, 0.32, 0.10], np.float32)
    c_hot = np.array([1.00, 0.88, 0.58], np.float32)
    col = (c_dark[None, None] * (1 - t)[..., None]
           + c_mid[None, None] * (t * (1 - t) * 4 * 0.65)[..., None]
           + c_hot[None, None] * (t ** 2)[..., None])
    body = col * (0.30 + 0.70 * t[..., None])
    rgb = body * (img_v > 0)[..., None]

    # explicit hero boundary: crisp ivory staircase (the one individual)
    xs_h, ys_h = boundary_staircase(parts)
    pts_h = np.stack([xs_h * PX, (FRAME - ys_h) * PX], axis=1)
    acc_h = np.zeros((S, S), np.float32)
    smp, mm = sample_polyline(pts_h, 0.6)
    splat_points(acc_h, smp[:, 0], smp[:, 1], mm)
    kh = 1.1 / np.percentile(acc_h[acc_h > 0], 98)
    Lh = np.clip(acc_h * kh, 0, 1.3)
    rgb += 0.9 * Lh[..., None] * np.array([1.0, 0.96, 0.88], np.float32)

    # ghost ensemble boundaries (ice blue) + hero rim glow
    ghosts = sample_partitions(n, NGHOST, window=200, seed=7, verbose=True)
    acc_g = np.zeros((S, S), np.float32)
    for m in ghosts:
        p = parts_from_mult(m)
        xs, ys = boundary_staircase(p)
        pts = np.stack([xs * PX, (FRAME - ys) * PX], axis=1)
        smp, mm = sample_polyline(pts, 0.8)
        splat_points(acc_g, smp[:, 0], smp[:, 1], mm)
    kg = 2.2 / np.percentile(acc_g[acc_g > 0], 99)
    Lg = filmic(acc_g * kg, 1.0)
    rgb += 0.6 * Lg[..., None] * np.array([0.45, 0.65, 0.88], np.float32)

    # Vershik curve, gold hairline with soft glow
    b = np.sqrt(6 * n) / np.pi
    xg = np.linspace(1e-3, FRAME, 6000)
    e = np.exp(-xg / b)
    yg = np.where(e < 1, -b * np.log(np.maximum(1 - e, 1e-300)), np.inf)
    okc = (yg > 0) & (yg < FRAME * 1.05)
    pts = np.stack([xg[okc] * PX, (FRAME - yg[okc]) * PX], axis=1)
    acc_c = np.zeros((S, S), np.float32)
    smp, mm = sample_polyline(pts, 0.6)
    splat_points(acc_c, smp[:, 0], smp[:, 1], mm)
    kc = 1.3 / np.percentile(acc_c[acc_c > 0], 98)
    Lc = np.clip(acc_c * kc, 0, 1.5)
    glow = gaussian_filter(Lc, S / 900)
    rgb += (0.85 * Lc + 0.55 * glow)[..., None] * np.array([1.0, 0.83, 0.42], np.float32)

    rgb = 1 - np.exp(-rgb * 1.25)
    rgb = np.clip(rgb, 0, 1) ** 0.94
    outdir = os.path.join(os.path.dirname(__file__), "proto" if mode == "proto" else ".")
    path = os.path.join(outdir, f"partition_{mode}.png")
    save_png(rgb, path)
    print("saved", path)

if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "proto")
