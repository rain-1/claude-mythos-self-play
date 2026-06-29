"""Arnold tongues of the sine circle map
    x_{n+1} = x_n + Omega - (K/2pi) sin(2pi x_n)   (lifted; W = winding number)
Compute the rotation number W over the (Omega,K) plane.  Locked 'tongues'
(rational W) are flat plateaus -> detected by |grad W| ~ 0.  Hue = W (which
rational), brightness = lockedness.  Frozen (locked) wedges vs the free
quasiperiodic sea; at the critical line K=1 the tongues fill the line save a
measure-zero Cantor set.
"""
import numpy as np, sys, time
from PIL import Image
from scipy.ndimage import gaussian_filter

S = int(sys.argv[1]) if len(sys.argv) > 1 else 800
Niter = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
Ntrans = int(sys.argv[3]) if len(sys.argv) > 3 else 600
Kmax = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
outp = sys.argv[5] if len(sys.argv) > 5 else f"arnold_{S}.npy"
om0 = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
om1 = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
Kmin = float(sys.argv[8]) if len(sys.argv) > 8 else 0.0

t0 = time.time()
Om = np.linspace(om0, om1, S, dtype=np.float64)[None, :]      # x axis
K  = np.linspace(Kmin, Kmax, S, dtype=np.float64)[:, None]    # y axis (row 0 = K=Kmin)
twopi = 2*np.pi
x = np.zeros((S, S), dtype=np.float64)                        # start theta=0
k2 = K / twopi
# transient
for _ in range(Ntrans):
    x += Om - k2 * np.sin(twopi * x)
x0 = x.copy()
for _ in range(Niter):
    x += Om - k2 * np.sin(twopi * x)
W = (x - x0) / Niter                                          # winding number
np.save(outp, W.astype(np.float32))
print(f"computed W {S}x{S} in {time.time()-t0:.1f}s  W range [{W.min():.3f},{W.max():.3f}]")
