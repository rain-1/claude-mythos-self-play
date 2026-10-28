import numpy as np, sys, math, time
from gef import *
W = int(sys.argv[1]); R = float(sys.argv[2]); seed = int(sys.argv[3]); out = sys.argv[4]
K = int(R * R + 8 * R + 40)
c = coeffs(K, seed)
t = time.time(); U, V = field(c, W, R); print('field', time.time() - t)
Z = zeros(c, U, R, W); print('zeros', len(Z))
ZL = np.full((W, W), -1, np.int32)
px = W / (2 * R)
yy, xx = np.mgrid[0:W, 0:W]
for k, z in enumerate(Z):
    cx = (z.real + R) * px - 0.5; cy = (R - z.imag) * px - 0.5
    r = max(2.0, 0.05 * px)
    x0, x1 = int(max(cx - r - 2, 0)), int(min(cx + r + 3, W)); y0, y1 = int(max(cy - r - 2, 0)), int(min(cy + r + 3, W))
    sub = (xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2 <= r * r
    ZL[y0:y1, x0:x1][sub] = k
t = time.time(); L = basins(V, ZL, W, 0.5, 8 * W); print('basins', time.time() - t)
np.savez_compressed(out, U=U, V=V, L=L, Z=Z, R=R, c=c)
areas = np.bincount(L[L >= 0].ravel(), minlength=len(Z)) / px ** 2
inner = [k for k, z in enumerate(Z) if abs(z) < R - 4]
print('mean area (inner zeros)', areas[inner].mean() / math.pi, 'sd', areas[inner].std() / math.pi, 'unlabelled', (L < 0).mean())
