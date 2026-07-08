"""Physical smearing: mixture over drop radii + convolution with the sun's disk.
Writes data/bow_profile_mix.npz  (same format as bow_profile.npz).

Usage: python3 bow_mix.py <Rmean_mm> <sigma_frac> <nR> <nlam> <tag>
"""
import numpy as np, sys, time, os
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bow_physics import gamma_profile

t0 = time.time()
Rmean = float(sys.argv[1])*1e-3 if len(sys.argv) > 1 else 0.18e-3
sig   = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
nR    = int(sys.argv[3]) if len(sys.argv) > 3 else 7
nlam  = int(sys.argv[4]) if len(sys.argv) > 4 else 96
tag   = sys.argv[5] if len(sys.argv) > 5 else "_mix"

lams = np.linspace(385e-9, 715e-9, nlam)
gamma = np.linspace(0.0, np.deg2rad(75), 9000)
zs = np.linspace(-2, 2, nR)
Rs = Rmean*(1 + sig*zs)
wR = np.exp(-0.5*zs**2); wR /= wR.sum()

def job(a):
    lam, R, p = a
    return gamma_profile(lam, R, gamma, p)

tasks = [(lam, R, p) for p in (1, 2) for R in Rs for lam in lams]
with Pool(4) as pool:
    res = pool.map(job, tasks, chunksize=4)
res = np.array(res).reshape(2, nR, nlam, len(gamma))
I = (res*wR[None, :, None, None]).sum(axis=1)         # radius mixture
print(f"profiles {time.time()-t0:.1f}s", flush=True)

# sun disk: 0.533 deg diameter, limb-darkened chord profile
dg = gamma[1]-gamma[0]
half = np.deg2rad(0.2665)
nk = int(half/dg)
xk = np.arange(-nk, nk+1)*dg
kern = np.sqrt(np.clip(1-(xk/half)**2, 0, None))**1.3
kern /= kern.sum()
from scipy.ndimage import convolve1d
I1 = convolve1d(I[0], kern, axis=-1, mode="nearest")
I2 = convolve1d(I[1], kern, axis=-1, mode="nearest")

np.savez_compressed(f"art_x61t/data/bow_profile{tag}.npz",
                    gamma=gamma, lams=lams, I1=I1, I2=I2, R=Rmean)
print(f"saved tag={tag}  {time.time()-t0:.1f}s")
