import numpy as np, time, sys
from ring import field, config
r = tuple(map(float, sys.argv[1].split(','))); n = int(sys.argv[2]); M = int(sys.argv[3]); out = sys.argv[4]
C, R = config(r)
lo = (C - R[:, None]).min(0); hi = (C + R[:, None]).max(0)
c = (lo + hi) / 2; half = (hi - lo).max() / 2 * 1.04
xs = np.linspace(c[0] - half, c[0] + half, n); ys = np.linspace(c[1] - half, c[1] + half, n)
t = time.time(); F = field(xs, ys, C, R, M); print('time', time.time() - t)
np.savez(out, F=F, C=C, R=R, cx=c[0], cy=c[1], half=half)
print(F.min(), F.max())
