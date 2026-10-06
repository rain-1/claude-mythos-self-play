"""scene.py packing.npy out.bin [key=val] — place the packing in the world and colour the pearls.
hue walks the sorbet wheel with log(radius) (sizes that touch are neighbours in hue); glow ~ small pearls."""
import sys, numpy as np
ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
A = np.load(sys.argv[1])
S = P('scale', 3.0)
c = A[:, :3] * S; r = A[:, 3] * S
c[:, 2] += S                                     # outer sphere resting on the table at its lowest point
c[:, 0] += P('cx', 0.0); c[:, 1] += P('cy', 0.0)
WHEEL = np.array([(1.00, 0.52, 0.62), (1.00, 0.70, 0.52), (1.00, 0.86, 0.46), (0.76, 0.93, 0.50), (0.52, 0.90, 0.76),
                  (0.52, 0.80, 1.00), (0.64, 0.66, 1.00), (0.80, 0.60, 1.00), (1.00, 0.60, 0.90)])
lr = np.log(A[:, 3] / A[:, 3].max())
h = (P('h0', 0.55) + P('hk', 0.16) * (-lr)) % 1.0
x = h * len(WHEEL); i = x.astype(int) % len(WHEEL); f = (x - np.floor(x))[:, None]
tint = WHEEL[i] ** (1 - f) * WHEEL[(i + 1) % len(WHEEL)] ** f
tint = 1 - P('sat', 1.0) * (1 - tint)
glow = np.clip(-lr / 4, 0, 1)
keep = r > P('rcut', 0.0)
# geode cut: drop pearls whose centre lies in front of the plane n·(x - c0) > 0
if P('cut', 0):
    nvec = np.array([P('nx', -0.35), P('ny', -1.0), P('nz', 0.25)]); nvec /= np.linalg.norm(nvec)
    keep &= (A[:, :3] @ nvec) < P('off', 0.0)
out = np.column_stack([c, r, tint, glow])[keep].astype(np.float64)
out.tofile(sys.argv[2]); print('pearls', keep.sum())
