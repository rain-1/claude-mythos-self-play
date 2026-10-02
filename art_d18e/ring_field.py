import numpy as np, time, sys
from ring import field, config
r = tuple(map(float, sys.argv[1].split(','))); n = int(sys.argv[2]); M = int(sys.argv[3]); ext = float(sys.argv[4]); out = sys.argv[5]
C, R = config(r)
xs = np.linspace(-ext, ext, n); ys = np.linspace(-ext, ext, n)
t = time.time(); F = field(xs, ys, C, R, M); print('time', time.time()-t)
np.savez(out, F=F, C=C, R=R, ext=ext)
print(F.min(), F.max(), F[n//2, n//2])
i = np.unravel_index(F.argmax(), F.shape); print('argmax', xs[i[1]], ys[i[0]])
