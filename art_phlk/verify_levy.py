"""Verify the Levy engine: displacement must scale like n^(1/alpha) for
alpha<2 and like sqrt(n) (up to log) at the Gaussian edge. Von-Dyck
discipline: check the invariant before trusting the picture."""
import numpy as np
from levy_core import levy_walk

for alpha in (0.9, 1.2, 1.5, 2.5):
    # median displacement over many independent walks at two n values
    med = []
    for n in (10_000, 160_000):
        d = []
        for s in range(40):
            p = levy_walk(n, alpha, seed=1000 + s)
            d.append(np.hypot(*p[-1]))
        med.append(np.median(d))
    # scaling exponent from n->16n : disp ratio = 16^(1/alpha)
    exp_meas = np.log(med[1] / med[0]) / np.log(16.0)
    exp_theo = 1.0 / alpha if alpha < 2 else 0.5
    print(f"alpha={alpha:4.1f}  measured exponent {exp_meas:.3f}  theory {exp_theo:.3f}")
