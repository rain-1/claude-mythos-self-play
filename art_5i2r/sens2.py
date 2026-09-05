import numpy as np
from cpack_rect import *
region = Leaf(); h = 0.05; rc = Offset(region, h/2); ex = ExactMap(rc)
def modulus(dirs):
    p = ex(rc.r(np.array(dirs))*np.exp(1j*np.array(dirs))); p /= np.abs(p)
    return rect_map_setup(p)['modulus']
base = [0.35,1.9,3.4,5.0]
print('base', modulus(base))
for i in range(4):
    for d in (-0.05, 0.05):
        dd = list(base); dd[i] += d
        print(f'corner {i} shifted {d:+.2f} rad -> modulus {modulus(dd):.5f}  (boundary speed |w\'| ~ {abs(rc.r(base[i]+1e-4)*np.exp(1j*(base[i]+1e-4))-rc.r(base[i])*np.exp(1j*base[i]))/1e-4:.2f})')
# harmonic-measure density at each corner: |phi'| along boundary
for i, d in enumerate(base):
    w1 = rc.r(d-1e-4)*np.exp(1j*(d-1e-4)); w2 = rc.r(d+1e-4)*np.exp(1j*(d+1e-4))
    print('corner', i, 'harmonic density |dphi/ds| =', abs(ex(w2)-ex(w1))/abs(w2-w1))
