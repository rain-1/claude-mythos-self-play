"""
02 · CIRCLES THAT ONLY KISS
===========================
The complete modular picture on the upper half-plane.

  * Ford circles (horocycles, WARM).  Every rational p/q in lowest terms gets
    a circle tangent to the real line at (p/q, 0) with radius 1/(2 q^2).  Two
    of them are tangent exactly when |p s - q r| = 1 -- i.e. p/q and r/s are
    Farey neighbours / adjacent in the Stern-Brocot tree -- and they NEVER
    overlap.  Circles that kiss but never merge.

  * Farey tessellation (geodesic arches, COOL).  Recursively inserting the
    mediant (p+r)/(q+s) of each interval and drawing the hyperbolic geodesic
    (a semicircle perpendicular to R) between neighbours tessellates H into
    ideal triangles -- the fundamental domains of PSL(2,Z).

Every positive rational below 1 is named exactly once: a drawing of a very
nice bijection N <-> Q.  Colour = Stern-Brocot depth (sum of continued-
fraction partial quotients): shallow/large -> warm gold, deep/tiny -> cool.

Front-page seed: MathOverflow, "How nice can a bijection between N and Q be?"
Technique new to this thread: Ford-circle horocycle packing + recursive Farey
tessellation as the depth-coloured modular picture.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

def sb_depth(p, q):
    a, b, d = p, q, 0
    while b:
        d += a // b; a, b = b, a % b
    return d

WARM = np.array([[1.00, 0.84, 0.46], [1.00, 0.62, 0.28], [0.96, 0.42, 0.30], [0.85, 0.30, 0.40]])
COOL = np.array([[0.42, 0.82, 0.96], [0.28, 0.60, 0.96], [0.40, 0.44, 0.93], [0.56, 0.38, 0.86]])
def ramp(C, t):
    x = np.clip(t, 0, 1) * (len(C) - 1); i = min(int(x), len(C) - 2); f = x - i
    return C[i] * (1 - f) + C[i + 1] * f

def gauss_ring(acc, cx, cy, rpx, w, col, W, Hh, xx, yy, cap_axis=None, amp=1.0, fill=0.0):
    pad = int(rpx + 4)
    xlo = max(0, int(cx - pad)); xhi = min(W, int(cx + pad))
    ylo = max(0, int(cy - pad)); yhi = min(Hh, int(cy + pad))
    if cap_axis is not None:
        yhi = min(yhi, cap_axis + 1)
    if xhi <= xlo or yhi <= ylo:
        return
    sx = xx[ylo:yhi, xlo:xhi]; sy = yy[ylo:yhi, xlo:xhi]
    d = np.sqrt((sx - cx) ** 2 + (sy - cy) ** 2)
    r = np.exp(-((d - rpx) / w) ** 2) * amp
    if fill:
        r = r + np.clip(1 - d / rpx, 0, 1) ** 2 * fill
    acc[ylo:yhi, xlo:xhi] += r[..., None] * col

def render(maxden=170, maxdepth=12, S=2600, supers=2, y1=0.56,
           k=2.0, gamma=0.88, glow=0.26, ringcap=2.3, geo_amp=0.62):
    W = S * supers; Hh = int(W * y1)
    acc = np.zeros((Hh, W, 3), np.float32)
    px = W - 1; axis_y = Hh - 1
    def Y(cy): return axis_y - cy / y1 * (Hh - 1)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    arches, fords = [], set([(0, 1), (1, 1)])
    def rec(a, b, c, d, depth):
        if depth > maxdepth or (b + d) > maxden:
            return
        arches.append((a / b, c / d, depth)); fords.add((a + c, b + d))
        rec(a, b, a + c, b + d, depth + 1); rec(a + c, b + d, c, d, depth + 1)
    rec(0, 1, 1, 1, 0)
    for (x1, x2, dep) in arches:
        cx = (x1 + x2) / 2 * px; rr = abs(x2 - x1) / 2 * px
        gauss_ring(acc, cx, axis_y, rr, max(0.9, min(rr * 0.02, ringcap)),
                   ramp(COOL, dep / maxdepth), W, Hh, xx, yy, cap_axis=axis_y, amp=geo_amp)
    md = max(sb_depth(p, q) for (p, q) in fords)
    for (p, q) in sorted(fords):
        r = 1.0 / (2 * q * q); rpx = r * px
        if rpx < 0.7:
            continue
        gauss_ring(acc, p / q * px, Y(r), rpx, min(max(0.8, rpx * 0.03), ringcap),
                   ramp(WARM, sb_depth(p, q) / md), W, Hh, xx, yy, amp=1.0, fill=0.05)
    g = gaussian_filter(acc, (2.0, 2.0, 0)) * glow
    img = acc + g
    img = img / (img.max() + 1e-9)
    img = 1.0 - np.exp(-k * img * 4)
    img = np.power(np.clip(img, 0, 1), gamma)
    out = (img * 255).astype(np.uint8)
    return Image.fromarray(out, "RGB").resize((S, int(Hh / supers)), Image.LANCZOS)

if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 2600
    print(f"rendering Farey/Ford, width {S} ...")
    im = render(maxden=190, maxdepth=12, S=S, y1=0.56)
    im.save("02_circles_that_only_kiss.png")
    print("saved 02_circles_that_only_kiss.png", im.size)
