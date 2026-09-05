import numpy as np
from cpack_rect import *
class Disc(Leaf):
    def __init__(self): self.terms=()
region = Disc(); h = 0.1
mesh = hex_mesh(region, h); W, bd, cyc = mesh['W'], mesh['boundary'], mesh['cycle']
corners = []
for d in (0.35, 1.9, 3.4, 5.0):
    ang = np.mod(np.angle(W[cyc]) - d + np.pi, 2*np.pi) - np.pi
    corners.append(int(cyc[np.argmin(np.abs(ang))]))
ex = ExactMap(region)
cang = np.angle(W[corners]); p = ex(region.r(cang)*np.exp(1j*cang)); p /= np.abs(p)
print('corner angles', cang, 'phi(corners)', np.angle(p))
S = rect_map_setup(p)
print('order', S['order'], 'k', S['k'], 'K', S['K'], 'Kp', S['Kp'])
Tz = S['T'](p); print('T(p)', Tz); mz = S['m'](Tz); print('m(T(p))', mz)
Fz = F_elliptic(mz + 1e-12j, S['k']); print('F', Fz)
# interior test points along radius at angle 0.35+..: check conformality: compare F(m(T(phi(w)))) for w on a small circle
w = 0.3*np.exp(1j*np.linspace(0,2*np.pi,8,endpoint=False))
q = ex(w); print('|phi(w)|', np.abs(q)[:3], 'vs |w|', np.abs(w)[:3])
Fw = F_elliptic(S['m'](S['T'](q)), S['k']); print('F(w)', Fw)
