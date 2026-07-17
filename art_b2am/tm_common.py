"""Shared helpers for the 'Negation of the Negation' triptych.
Automatic sequences = fixed points of complement-based substitutions.
"""
import numpy as np
from scipy.ndimage import gaussian_filter

# ---- sequences ----
def thue_morse(N):
    """t[n] = parity of popcount(n); fixed point of 0->01, 1->10 (append the negation)."""
    t = np.zeros(N, np.int8)
    for n in range(N):
        t[n] = bin(n).count('1') & 1
    return t

def dragon_turns(k):
    """Regular paperfolding turn sequence, length 2^k-1.
    Recursion s -> s , +1 , complement(reverse(s))  == the negation of the reversed negation."""
    s = np.array([1], dtype=np.int8)
    for _ in range(k - 1):
        s = np.concatenate([s, [1], -s[::-1]])
    return s

def dragon_xy(k):
    """Vertices of the order-k dragon on the integer lattice (90-degree turns)."""
    turns = dragon_turns(k)
    head = (np.concatenate([[0], np.cumsum(turns)]) % 4)
    dx = np.where(head == 0, 1, np.where(head == 2, -1, 0))
    dy = np.where(head == 1, 1, np.where(head == 3, -1, 0))
    x = np.concatenate([[0], np.cumsum(dx)]).astype(np.float64)
    y = np.concatenate([[0], np.cumsum(dy)]).astype(np.float64)
    return x, y

# ---- palette: shared 'dusk' ramp across the whole triptych ----
DUSK = np.array([
    [1.00, 0.72, 0.18],   # gold
    [0.94, 0.34, 0.20],   # ember
    [0.78, 0.16, 0.48],   # magenta
    [0.34, 0.20, 0.62],   # indigo
    [0.10, 0.48, 0.82],   # deep cyan
])
def ramp(t, stops=DUSK):
    t = np.clip(np.asarray(t, float), 0, 1)
    x = t * (len(stops) - 1)
    i = np.clip(np.floor(x).astype(int), 0, len(stops) - 2)
    f = (x - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f

# ---- rendering ----
def filmic(acc, expo=3.0, gamma=0.9, pct=99.9):
    b = acc / (np.percentile(acc, pct) + 1e-12)
    b = 1 - np.exp(-expo * b)
    return np.clip(b, 0, 1) ** gamma

def wide_bloom(chan, sigma, ds=6):
    """Fast wide gaussian via downsample->blur->upsample."""
    from PIL import Image
    W = chan.shape[0]
    small = np.array(Image.fromarray((np.clip(chan, 0, chan.max() + 1e-9) /
             (chan.max() + 1e-9) * 255).astype(np.uint8)).resize((max(4, W // ds), max(4, W // ds)), Image.BILINEAR)).astype(np.float32)
    small = gaussian_filter(small, sigma / ds)
    big = np.array(Image.fromarray(small.astype(np.uint8)).resize((W, W), Image.BILINEAR)).astype(np.float32)
    return big / 255.0 * (chan.max() + 1e-9)

def bilinear_splat(acc, fx, fy, col, w=1.0):
    """Additive bilinear splat of colored points into HxWx3 acc."""
    Ws = acc.shape[0]
    xi0 = np.floor(fx).astype(int); yi0 = np.floor(fy).astype(int)
    wx = fx - xi0; wy = fy - yi0
    for ox, oy, ww in [(0, 0, (1 - wx) * (1 - wy)), (1, 0, wx * (1 - wy)),
                       (0, 1, (1 - wx) * wy), (1, 1, wx * wy)]:
        xi = np.clip(xi0 + ox, 0, Ws - 1); yi = np.clip(yi0 + oy, 0, Ws - 1)
        wgt = ww * w
        for ch in range(3):
            np.add.at(acc[:, :, ch], (yi, xi), col[:, ch] * wgt)
