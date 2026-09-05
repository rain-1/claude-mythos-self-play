import numpy as np
from cpack_rect import *
class Disc(Leaf):
    def __init__(self): self.terms=()
region = Disc(); h = 0.1
P = build(h, region=region, verbose=False, ncert=0)
mesh, zn, corners, L1, L2 = P['mesh'], P['z'], P['corners'], P['L1'], P['L2']
W, bd = mesh['W'], mesh['boundary']
print('discrete corners', zn[corners], 'L1 L2', L1, L2)
ex = ExactMap(region)
cang = np.angle(W[corners]); p = ex(region.r(cang)*np.exp(1j*cang)); p /= np.abs(p)
S = rect_map_setup(p); K, Kp = S['K'], S['Kp']
sel = np.where(~bd)[0][::7]
zex = F_elliptic(S['m'](S['T'](ex(W[sel]))), S['k']) + K
t = zex.imag + 1j*zex.real          # swap
t = (Kp - t.real) + 1j*t.imag       # flipx
sc = Kp / L1
zd = zn[sel]*sc
e = np.abs(zd - t)
print('err max/mean', e.max(), e.mean())
for i in range(0, len(sel), max(1, len(sel)//12)):
    print(f'W={W[sel[i]]:.3f}  disc={zd[i]:.3f}  exact={t[i]:.3f}  err={e[i]:.3f}')
# error vs radius
r = np.abs(W[sel]); 
for lo, hi in ((0,0.3),(0.3,0.6),(0.6,0.8),(0.8,0.9),(0.9,1.0)):
    m = (r>=lo)&(r<hi); print(lo, hi, m.sum(), e[m].mean() if m.any() else None, e[m].max() if m.any() else None)
