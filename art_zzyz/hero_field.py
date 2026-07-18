"""Stage compute for 'The Wall at Zero' -- LOG-DEPTH CHART.

Chart:  x = Im s in [IM0, IM1],  y = ln(Re s) in [ln RE0, ln RE1],
        wall (Re s -> 0) at the BOTTOM.  In this chart the shrunken critical
        lines Re s = 1/(2n) become horizontal strata descending forever, and
        the pole ladder s = 1/n a vertical chain of Mobius lights at Im = 0.

Field: F(s) = Re P(s) = sum_{n squarefree <= NMAX} mu(n)/n log|zeta(ns)|.
Split: lines n <= NF computed on the fine coarse grid (CW), lines n > NF on a
half-res grid (mist; amplitudes <= 1/31).  Caches keyed by size.
"""
import numpy as np, os, time
from sympy import mobius
import zetalib as zl

RE0, RE1 = 0.0011, 1.36
Y0, Y1 = np.log(RE0), np.log(RE1)
IM0, IM1 = -7.0, 50.0
NMAX = 420
NF = 30
TMAX_ZEROS = NMAX * IM1 * 1.001

SQF = [n for n in range(1, NMAX + 1) if mobius(n) != 0]
MU = {n: int(mobius(n)) for n in SQF}


def zeros_catalog():
    if os.path.exists("zeros_cat.npy"):
        return np.load("zeros_cat.npy")
    t0 = time.time()
    zs = zl.find_zeros(TMAX_ZEROS, dt=0.02)
    np.save("zeros_cat.npy", zs)
    print(f"zeros: {len(zs)} found to {TMAX_ZEROS:.0f} "
          f"(RvM predicts {zl.NT(TMAX_ZEROS)-1:.1f})  [{time.time()-t0:.0f}s]")
    return zs


def grid(W, H):
    x = IM0 + (IM1 - IM0) * (np.arange(W) + 0.5) / W          # Im s
    y = Y0 + (Y1 - Y0) * (np.arange(H) + 0.5) / H             # ln Re s
    re = np.exp(y)
    return re[::-1], x    # row 0 = TOP = largest Re


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def stratum_window(u):
    """Per-row weight in u = n*Re(s): each line paints its own stratum's
    neighbourhood.  Fade-in over u=[0.12,0.30] kills the divergent reflected
    growth of the truncated series below the stratum (an artifact of cutting
    the Mobius series at NMAX, not a feature of P); fade-out over [4,6]."""
    return smoothstep((u - 0.12) / 0.18) * (1 - smoothstep((u - 4.0) / 2.0))


def line_contrib(F, re_rows, im_cols, n, remax=6.0):
    """Add stratum-windowed mu(n)/n log|zeta(n s)|."""
    u = n * re_rows
    wrow = stratum_window(u)
    rows = np.where((u <= remax) & (wrow > 1e-4))[0]
    if len(rows) == 0:
        return
    sub_re = re_rows[rows]
    S = sub_re[:, None] + 1j * np.abs(im_cols)[None, :]
    w = (n * S).ravel()
    z = np.empty(w.shape, dtype=np.complex128)
    CH = 1 << 19
    for i in range(0, w.size, CH):
        z[i:i + CH] = zl.zeta(w[i:i + CH])
    F[rows, :] += (MU[n] / n) * wrow[rows, None] * np.log(
        np.maximum(np.abs(z), 1e-300)).reshape(len(rows), len(im_cols))


def field_fine(CW, tag=""):
    fn = f"ffine_{CW}{tag}.npy"
    if os.path.exists(fn):
        return np.load(fn)
    re_rows, im_cols = grid(CW, CW)
    F = np.zeros((CW, CW), dtype=np.float64)
    t0 = time.time()
    for n in [m for m in SQF if m <= NF]:
        line_contrib(F, re_rows, im_cols, n)
        print(f"  fine line n={n} ({time.time()-t0:.0f}s)", flush=True)
    np.save(fn, F)
    return F


def field_deep(CD, tag=""):
    fn = f"fdeep_{CD}{tag}.npy"
    if os.path.exists(fn):
        return np.load(fn)
    re_rows, im_cols = grid(CD, CD)
    F = np.zeros((CD, CD), dtype=np.float64)
    t0 = time.time()
    for n in [m for m in SQF if m > NF]:
        line_contrib(F, re_rows, im_cols, n, remax=2.5)
        if n % 30 == 0:
            print(f"  deep line n={n} ({time.time()-t0:.0f}s)", flush=True)
    np.save(fn, F)
    return F


if __name__ == "__main__":
    import sys
    CW = int(sys.argv[1]) if len(sys.argv) > 1 else 2048
    CD = int(sys.argv[2]) if len(sys.argv) > 2 else CW // 2
    zeros_catalog()
    Ff = field_fine(CW)
    print("fine field range:", Ff.min(), Ff.max())
    Fd = field_deep(CD)
    print("deep field range:", Fd.min(), Fd.max())
