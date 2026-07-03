"""R3 field from the first 2,001,052 zeta zeros (Odlyzko zeros6)."""
import numpy as np
from r3_field import r3_hist, r3_theory

SCRATCH = "/tmp/claude-0/-home-user-claude-mythos-self-play/3b1c892d-85d8-5ccd-86d3-8c63e823ea19/scratchpad"

g = np.loadtxt(f"{SCRATCH}/zeros6")
print("zeros:", len(g))
x = g / (2 * np.pi) * np.log(g / (2 * np.pi * np.e)) + 7.0 / 8.0
print("mean gap:", np.mean(np.diff(x)).round(6))
H = r3_hist(x)
np.save("r3_zeta2M.npy", H)
T = r3_theory()
print("median |R3 - theory|:", np.median(np.abs(H - T)).round(4))
print("median |R3 - 1|     :", np.median(np.abs(H - 1.0)).round(4))
