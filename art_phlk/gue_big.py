"""Big GUE sample: 60 tridiagonal beta=2 matrices, N=20000, bulk 60%
-> 720k unfolded levels. Saves to gue_levels.npy."""
import numpy as np
from spectra2 import gue_tridiag_unfolded, pair_r2

g = gue_tridiag_unfolded(n_matrices=60, N=20000, seed=42)
np.save("gue_levels.npy", g)
print("levels:", len(g))
u = np.linspace(0.005, 4, 400)
r2t = 1 - np.sinc(u) ** 2
r2 = pair_r2(g)
m = (u > 0.05) & (u < 3.8)
print("median |R2 - sine| =", np.median(np.abs(r2[m] - r2t[m])).round(4))
print("median |R2 - 1|    =", np.median(np.abs(r2[m] - 1)).round(4))
