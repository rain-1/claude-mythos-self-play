"""01 - The Orbit That Never Lands: phyllotaxis & the three-gap theorem.

Seeds at the golden angle (the 'most irrational' rotation of the circle).
The visible spiral arms (parastichies) occur in Fibonacci numbers because
those are the continued-fraction convergents of the golden ratio -- the
'good rational approximations' of an irrational torus rotation. We detect
each seed's nearest neighbours; the index gaps cluster on Fibonacci numbers,
and we colour each spiral thread by which convergent it belongs to.
"""
import sys, numpy as np
from scipy.spatial import cKDTree
from PIL import Image, ImageDraw
import artkit as ak

PHI = (1 + 5 ** 0.5) / 2
GOLDEN_ANGLE = 2 * np.pi * (1 - 1 / PHI)   # ~137.507 deg
FIBS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

# palette: hue per Fibonacci convergent (two adjacent Fibs -> two contrasting hues)
def hex2rgb(h):
    return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32) / 255

FIB_COLORS = {
    1:  hex2rgb("3a2d6b"), 2: hex2rgb("4b3fa0"), 3: hex2rgb("3f6fd0"),
    5:  hex2rgb("23a6c8"), 8: hex2rgb("2fd0a6"), 13: hex2rgb("8fe05a"),
    21: hex2rgb("f0d24a"), 34: hex2rgb("f59a3c"), 55: hex2rgb("ef5d4c"),
    89: hex2rgb("e0408f"), 144: hex2rgb("b148d8"), 233: hex2rgb("7a5cf0"),
    377: hex2rgb("4aa0ff"), 610: hex2rgb("46e0c0"),
}

def render(N=9000, S=1400, angle=GOLDEN_ANGLE, supersample=2, fname="proto_phyllo.png",
           seed_warm=True, thr_factor=2.6, bloom_amp=1.0, expo_k=1.15, sat=1.35,
           line_boost=1.3, seed_inten=0.9):
    W = S * supersample
    n = np.arange(1, N + 1)
    r = np.sqrt(n)
    th = n * angle
    x = r * np.cos(th)
    y = r * np.sin(th)
    Rmax = r.max()
    # map to pixels with margin
    margin = 0.06
    scale = (W / 2) * (1 - margin) / Rmax
    px = W / 2 + x * scale
    py = W / 2 + y * scale

    pts = np.column_stack([x, y])
    # min seed spacing (Vogel ~ constant): estimate from a sample
    tree = cKDTree(pts)
    d1, _ = tree.query(pts[::50], k=2)
    minspace = np.median(d1[:, 1])

    # build line layer with PIL (fast for many polylines).
    # Each parastichy family is n -> n+F; keep only short chords (its band).
    line_img = Image.new("RGB", (W, W), (0, 0, 0))
    dr = ImageDraw.Draw(line_img, "RGBA")
    lw = max(1, int(round(1.5 * supersample)))
    families = [f for f in FIBS if f in FIB_COLORS and f >= 8]
    thr = thr_factor * minspace
    for f in families:
        col = FIB_COLORS[f]
        i = np.arange(0, N - f)
        x0, y0, x1, y1 = x[i], y[i], x[i + f], y[i + f]
        dd = np.hypot(x1 - x0, y1 - y0)
        keep = dd < thr
        a = int(np.clip(120 + 8 * FIBS.index(f), 90, 245))
        rgba = (int(col[0]*255), int(col[1]*255), int(col[2]*255), a)
        ii = i[keep]
        for k in ii:
            dr.line([px[k], py[k], px[k + f], py[k + f]], fill=rgba, width=lw)
    line_arr = np.asarray(line_img, np.float32) / 255.0

    # seed dots as additive glow
    canvas = np.zeros((W, W, 3), np.float32)
    # colour seeds by radius: warm core -> cool rim, OR white
    t = (r / Rmax)
    if seed_warm:
        seed_col = np.stack([
            0.9 - 0.5 * t, 0.7 - 0.1 * t, 0.4 + 0.5 * t
        ], axis=1).clip(0, 1)
    else:
        seed_col = np.ones((N, 3), np.float32)
    rad = max(1.0, 1.1 * supersample)
    ak.splat_add(canvas, px, py, seed_col, radius=rad, intensity=seed_inten)

    # composite: lines under, seed glow over
    field = line_arr * line_boost + canvas
    field = ak.bloom(field, sigmas=(2*supersample, 7*supersample, 20*supersample),
                     amps=(0.18*bloom_amp, 0.11*bloom_amp, 0.06*bloom_amp))
    rgb = ak.filmic(field, k=expo_k)
    # saturation boost (luma-preserving)
    luma = (0.2126*rgb[..., 0] + 0.7152*rgb[..., 1] + 0.0722*rgb[..., 2])[..., None]
    rgb = np.clip(luma + (rgb - luma) * sat, 0, 1)
    rgb = ak.gamma(rgb, 1/1.9)
    if supersample > 1:
        rgb = ak.downscale(rgb, supersample)
    ak.save(rgb, fname)
    print("wrote", fname, "N", N, "angle_deg", np.degrees(angle))

if __name__ == "__main__":
    render()
