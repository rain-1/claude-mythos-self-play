import numpy as np
from cpack_rect import *
P = build(0.05, verbose=False, ncert=0)
mesh, zn, corners, L1, L2, rc = P['mesh'], P['z'], P['corners'], P['L1'], P['L2'], P['region_c']
W, bd = mesh['W'], mesh['boundary']
ex = ExactMap(rc); cang = np.angle(W[corners]); p = ex(rc.r(cang)*np.exp(1j*cang)); p/=np.abs(p)
S = rect_map_setup(p); K, Kp = S['K'], S['Kp']
sel = np.where(~bd & rc.inside(W))[0][::5]
zex = F_elliptic(S['m'](S['T'](ex(W[sel]))), S['k']) + K
t = (2*K - zex.real) + 1j*(Kp - zex.imag)     # flipx, flipy
zd = zn[sel] * (2*K/L1)
e = np.abs(zd - t)
# error by quadrant of the page
for name, m in (('left half', zd.real < K), ('right half', zd.real >= K), ('bottom', zd.imag < Kp/2), ('top', zd.imag >= Kp/2)):
    print(name, 'mean err', e[m].mean(), 'max', e[m].max())
# error vs distance to nearest corner of the page
dc = np.min(np.abs(zd[:, None] - np.array([0, 2*K, 2*K+1j*Kp, 1j*Kp])[None, :]), axis=1)
for lo, hi in ((0,0.3),(0.3,0.8),(0.8,1.5),(1.5,5)):
    m = (dc>=lo)&(dc<hi); print(f'dist to corner [{lo},{hi}) n={m.sum()} mean err {e[m].mean():.4f}')
print('discrete corner coin radii', P['r'][corners], 'mean radius', P['r'].mean(), 'faces at corners', [int((mesh['faces']==c).any(axis=1).sum()) for c in corners])
