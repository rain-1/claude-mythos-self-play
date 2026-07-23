import numpy as np
from conics_engine import *

# test on an exact ellipse: osculating conic must BE the ellipse everywhere,
# sextactic det must vanish identically
dx, dy = make_curve({2: (0.25, 0.0)})   # rho = 1+0.25cos2t -> NOT ellipse; first test circle-ish
# exact ellipse via param (a cos t, b sin t) isn't rho-form; do direct:
a, b = 1.4, 0.9
x = a*np.cos(t); y = b*np.sin(t)
def dfft(f, order):
    F = np.fft.rfft(f); k = np.arange(len(F))
    F[np.abs(F) < 1e-9 * np.abs(F).max()] = 0
    F[64:] = 0
    return np.fft.irfft(F * (1j*k)**order, n=len(f))
dxe = [x] + [dfft(x, o) for o in range(1, 6)]
dye = [y] + [dfft(y, o) for o in range(1, 6)]
idx = np.arange(0, K, 64)
Q, sex, cond = osculating_conics(dxe, dye, idx)
# normalize: true ellipse coeffs prop to (1/a^2, 0, 1/b^2, 0, 0, -1)
true = None  # centered-coords check below
# centered conic of ellipse at (x0,y0): (u+x0)^2/a^2+(v+y0)^2/b^2-1=0
x0, y0 = x[idx], y[idx]
errs = []
for i in range(len(idx)):
    tru = np.array([1/a**2, 0, 1/b**2, 2*x0[i]/a**2, 2*y0[i]/b**2, 0.0])
    q = Q[i] / np.linalg.norm(Q[i]); tru = tru / np.linalg.norm(tru)
    errs.append(min(np.abs(q-tru).max(), np.abs(q+tru).max()))
print("ellipse: max conic-coeff err", max(errs), " max|sex det|", np.abs(sex).max())

# generic convex oval
dx, dy = make_curve({2: (0.09, 0.7), 3: (0.055, 0.0), 5: (0.012, 1.9)})
# convexity check: curvature > 0
xp, yp, xpp, ypp = dx[1], dy[1], dx[2], dy[2]
curv = (xp*ypp - yp*xpp) / (xp**2 + yp**2)**1.5
print("min curvature:", curv.min(), "(convex iff > 0)")
idx = np.arange(K)
Q, sex, cond = osculating_conics(dx, dy, idx)
sgn = np.sign(sex)
flips = np.nonzero(sgn != np.roll(sgn, 1))[0]
print("sextactic points (sign changes of 6x6 det):", len(flips))
# classification: discriminant b^2-4ac of osculating conics
disc = Q[:,1]**2 - 4*Q[:,0]*Q[:,2]
print("conic types: ellipses", (disc<0).sum(), "hyperbolae", (disc>0).sum())
