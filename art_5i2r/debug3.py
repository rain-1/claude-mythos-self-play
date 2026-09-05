import numpy as np
from cpack_rect import *
h=0.05; region=Leaf(); rc = Offset(region, h/2)
mesh = hex_mesh(region, h); W, bd = mesh['W'], mesh['boundary']
print('offset inside check: fraction of mesh vertices inside offset region', rc.inside(W).mean(), 'boundary verts inside', rc.inside(W[bd]).mean())
ex = ExactMap(rc); print('mfs resid', ex.bdry_resid)
sel = np.where(~bd)[0][::50]
q = ex(W[sel]); print('|phi| range', np.abs(q).min(), np.abs(q).max())
ex0 = ExactMap(region); q0 = ex0(W[sel]); print('|phi0| range', np.abs(q0).min(), np.abs(q0).max())
# conformality check of ex: compare phi on 4 nearby points -> Cauchy-Riemann
w0 = 0.3+0.2j; d=1e-5
dz = (ex(w0+d)-ex(w0-d))/(2*d); dzi = (ex(w0+1j*d)-ex(w0-1j*d))/(2*d)
print('CR check (should be ~0):', abs(dzi - 1j*dz))
