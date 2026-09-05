import numpy as np, time, sys
from cpack_rect import *
h = float(sys.argv[1])
region = Leaf(); mesh = hex_mesh(region, h); W, bd, cyc = mesh['W'], mesh['boundary'], mesh['cycle']
corners = [int(cyc[np.argmin(np.abs(np.mod(np.angle(W[cyc]) - d + np.pi, 2*np.pi) - np.pi))]) for d in (0.35,1.9,3.4,5.0)]
print('V', len(W))
t=time.time(); r1, th1, it1, tg = pack_euclid_fast(mesh, corners); print('fast', time.time()-t, it1, np.abs(th1-tg).max())
if len(W) < 3000:
    t=time.time(); r2, th2, it2, tg = pack_euclid(mesh, corners, verbose=False); print('jacobi', time.time()-t, it2)
    print('radii agree:', np.abs(r1/r1[0] - r2/r2[0]).max())
