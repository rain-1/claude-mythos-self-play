"""THE COMET THAT OUTRUNS PROOF -- Goldbach strata, 2560^2.

x = ln n (11 octaves, 2^11..2^22), y = ln( r(2n) / (2 C2 I(2n)) ) where
I(2n) = int_2^{2n-2} dt/(ln t ln(2n-t)) is the Hardy-Littlewood integral.
Then y -> ln S(n) + fluctuation: every even number falls onto the stratum of
its own singular series S(n) = prod_{p|n, p>2} (p-1)/(p-2).  The comet's head
(left) is scatter; rightward the strata tighten toward razors: the primes
keep the promise with ever more precision, and the theorem stays unproven.
Sub-strata condense onto every main stratum (factor 1+1/(p-2) per prime).
"""
import numpy as np, time
from scipy.ndimage import gaussian_filter, zoom as ndzoom
from PIL import Image
import comet_build

FINAL = 2560
SS = 2
S = FINAL * SS
C2 = comet_build.C2
NLO, NHI = 1 << 11, 1 << 22


def hl_integral_interp():
    """ln I(2n) on a log-spaced grid of n, splined; I by adaptive Simpson."""
    from scipy.integrate import quad
    ns = np.unique(np.round(np.exp(np.linspace(np.log(NLO * 0.9), np.log(NHI * 1.1), 400))).astype(np.int64))
    vals = []
    for n in ns:
        m = 2.0 * n
        f = lambda t: 1.0 / (np.log(t) * np.log(m - t))
        v, _ = quad(f, 2.0, m / 2, limit=200)
        vals.append(2.0 * v)          # symmetric halves
    return np.log(ns.astype(float)), np.log(np.array(vals))


def ramp(t):
    """curated ramp: steel-cyan -> pale gold -> amber -> rose-ember."""
    stops = np.array([
        [0.22, 0.55, 0.86],
        [0.48, 0.75, 0.84],
        [0.97, 0.84, 0.52],
        [1.00, 0.60, 0.24],
        [1.00, 0.34, 0.30],
    ])
    pos = np.array([0.0, 0.28, 0.52, 0.76, 1.0])
    t = np.clip(t, 0, 1)
    idx = np.searchsorted(pos, t, side="right").clip(1, len(pos) - 1)
    t0, t1 = pos[idx - 1], pos[idx]
    w = ((t - t0) / (t1 - t0))[:, None]
    return stops[idx - 1] * (1 - w) + stops[idx] * w


def render():
    d = comet_build.build()
    r, Ssing = d["r"], d["S"]
    n = np.arange(len(Ssing), dtype=np.int64)
    sel = (n >= NLO) & (n <= NHI) & (r[: len(Ssing)] > 0)
    n = n[sel]
    rv = r[: len(Ssing)][sel].astype(np.float64)
    Sv = Ssing[sel]
    lx, li = hl_integral_interp()
    I = np.exp(np.interp(np.log(n.astype(float)), lx, li))
    y = np.log(rv / (2 * C2 * I))
    print("y range:", np.percentile(y, [0.1, 50, 99.9]), "max lnS:", np.log(Sv).max())
    # chart
    X0, X1 = np.log(NLO), np.log(NHI)
    Y0, Y1 = -0.30, 1.55
    px = (np.log(n.astype(float)) - X0) / (X1 - X0) * S
    py = (Y1 - y) / (Y1 - Y0) * S
    t = np.clip(np.log(Sv) / 1.5, 0, 1)
    cols = ramp(t)
    w = Sv ** 0.7 / n.astype(np.float64)
    w *= 8.5e5 / w.sum() * S * S / (2560 * 2560)
    buf = np.zeros((S, S, 3), dtype=np.float64)
    ix = np.floor(px).astype(np.int64)
    iy = np.floor(py).astype(np.int64)
    fx, fy = px - ix, py - iy
    ok = (ix >= 0) & (ix < S - 1) & (iy >= 0) & (iy < S - 1)
    for dx, dy, wt in [(0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)]:
        for c in range(3):
            np.add.at(buf[..., c], (iy[ok] + dy, ix[ok] + dx),
                      (w * wt * cols[:, c])[ok])
    # gentle vertical thickening so razor strata survive downscale
    for c in range(3):
        buf[..., c] += 0.7 * gaussian_filter(buf[..., c], (1.6 * SS, 0.6 * SS))
    # soft-knee: lift the fog without clipping strata
    buf = buf ** 0.72
    # bloom on bright strata
    lum = buf.mean(-1)
    p = np.percentile(lum[lum > 0.01], 98)
    mask = np.clip(lum / (p + 1e-9) - 1, 0, 1)[..., None]
    bl = gaussian_filter(buf * mask, (7 * SS, 7 * SS, 0))
    buf = buf + 0.6 * bl
    bg = np.array([0.010, 0.013, 0.028])
    out = 1 - np.exp(-1.12 * buf)
    out = np.clip(out + bg[None, None, :], 0, 1) ** 0.90
    img = Image.fromarray((out * 255).astype(np.uint8)).resize((FINAL, FINAL), Image.LANCZOS)
    img.save("comet.png")
    print("saved comet.png")


if __name__ == "__main__":
    t0 = time.time()
    render()
    print(f"{time.time()-t0:.0f}s")
