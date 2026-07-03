import numpy as np
from spectra2 import gue_tridiag_unfolded
g = gue_tridiag_unfolded(n_matrices=110, N=20000, seed=777)
np.save("gue_levels2.npy", g)
print("levels:", len(g))
