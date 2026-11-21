"""camel.py — one dromedary cut from paper: a signed-distance union of capsules and ellipses,
rounded off the way scissors round a corner.  camel(w, phase) -> float mask (h, w), walking RIGHT,
feet on the bottom row."""
import numpy as np
from scipy import ndimage as ndi

def _seg(x, y, ax, ay, bx, by, ra, rb):
    """distance to a tapered capsule (negative inside)"""
    dx, dy = bx - ax, by - ay
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy + 1e-12), 0, 1)
    return np.hypot(x - ax - t * dx, y - ay - t * dy) - (ra + (rb - ra) * t)

def _ell(x, y, cx, cy, rx, ry, rot=0.0):
    c, s = np.cos(rot), np.sin(rot); X = (x - cx) * c + (y - cy) * s; Y = -(x - cx) * s + (y - cy) * c
    k = np.hypot(X / rx, Y / ry)
    return (k - 1) * min(rx, ry)

def _smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)

def camel(w, phase=0.0, rope=False):
    """w: width in pixels of the unit box (1.0 x 0.86).  phase in [0,1): position in the stride."""
    H = 0.86; ss = 3 if w < 200 else 2
    W = int(np.ceil(w)) * ss; Hh = int(np.ceil(w * H)) * ss
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    x = (xx + 0.5) / W; y = (Hh - yy - 0.5) / W            # y up, unit = width
    d = _ell(x, y, 0.44, 0.50, 0.235, 0.105, -0.05)                      # barrel
    d = _smin(d, _ell(x, y, 0.42, 0.605, 0.135, 0.105, 0.0), 0.11)       # hump
    d = _smin(d, _ell(x, y, 0.245, 0.50, 0.075, 0.095, 0.2), 0.04)        # haunch
    d = _smin(d, _ell(x, y, 0.635, 0.475, 0.07, 0.09, -0.3), 0.04)        # shoulder / chest
    # neck: an S from the chest up to the head
    for (a, b, ra, rb) in [((0.655, 0.47), (0.735, 0.475), 0.072, 0.054), ((0.735, 0.475), (0.790, 0.56), 0.050, 0.040),
                           ((0.790, 0.56), (0.810, 0.68), 0.040, 0.033), ((0.810, 0.68), (0.832, 0.765), 0.033, 0.030)]:
        d = _smin(d, _seg(x, y, a[0], a[1], b[0], b[1], ra, rb), 0.025)
    d = _smin(d, _seg(x, y, 0.825, 0.775, 0.925, 0.742, 0.034, 0.024), 0.02)   # head and muzzle
    d = _smin(d, _seg(x, y, 0.925, 0.742, 0.952, 0.722, 0.022, 0.017), 0.012)  # lip
    d = np.minimum(d, _seg(x, y, 0.822, 0.80, 0.806, 0.838, 0.011, 0.006))     # ear
    # tail
    d = _smin(d, _seg(x, y, 0.185, 0.555, 0.150, 0.43, 0.012, 0.008), 0.012)
    d = np.minimum(d, _seg(x, y, 0.150, 0.43, 0.146, 0.385, 0.012, 0.014))
    # legs: hip -> knee -> hoof ; stride swings the hoof
    def leg(hx, hy, swing, front):
        kx = hx + 0.35 * swing + (0.012 if front else -0.018); ky = 0.235
        fx = hx + swing; lift = max(0.0, 0.0)
        r0 = 0.040 if front else 0.046
        a = _seg(x, y, hx, hy, kx, ky, r0, 0.021)
        b = _seg(x, y, kx, ky, fx, 0.030, 0.021, 0.016)
        c = _seg(x, y, fx - 0.004, 0.018, fx + 0.026, 0.016, 0.017, 0.015)      # foot pad
        return np.minimum(_smin(a, b, 0.01), c)
    s = np.sin(2 * np.pi * phase); c2 = np.cos(2 * np.pi * phase)
    amp = 0.062
    legs = np.minimum.reduce([leg(0.275, 0.44, amp * s, False), leg(0.245, 0.44, -amp * s, False),
                              leg(0.625, 0.42, amp * c2, True), leg(0.655, 0.42, -amp * c2, True)])
    d = _smin(d, legs, 0.018)
    m = np.clip(0.5 - d * W / ss * 1.0, 0, 1)                                      # 1 px edge at output scale
    m = m.reshape(Hh // ss, ss, W // ss, ss).mean((1, 3))
    return m.astype(np.float32)

if __name__ == "__main__":
    from PIL import Image
    row = np.concatenate([camel(360, p) for p in (0.0, 0.17, 0.33, 0.6)], 1)
    small = np.concatenate([camel(70, p) for p in np.linspace(0, 1, 12, endpoint=False)], 1)
    Image.fromarray((255 - row * 255).astype(np.uint8)).save('/tmp/claude-0/-home-user-claude-mythos-self-play/c015e99f-f8a8-5d9e-b3ff-e626a8475740/scratchpad/camel.png')
    Image.fromarray((255 - small * 255).astype(np.uint8)).save('/tmp/claude-0/-home-user-claude-mythos-self-play/c015e99f-f8a8-5d9e-b3ff-e626a8475740/scratchpad/camel_s.png')
