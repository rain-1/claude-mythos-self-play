"""sweeps.py — two small measurements for the notes:
 (1) stealthy number-variance coefficient c(χ) in σ²(R) ≈ c R (N = 1500, square box)
 (2) strange-eigenmode decay per block vs κ for the chosen protocol (A=2.5, P=3, seed 2), n scaled with κ
"""
import json, time, numpy as np
from stealthy import Stealthy, poisson
from eigenmode import SineFlow, initial
out = {}
t0 = time.time()
res = []
for chi in (0.1, 0.2, 0.3, 0.4, 0.45):
    st = Stealthy(1500, aspect=1.0, chi=chi, seed=1)
    r, phiN, nit = st.optimise(maxiter=2500, verbose=False)
    radii = np.array([1, 2, 3, 4, 6, 8])
    nv = st.number_variance(r, radii, nwin=6000)
    c = np.polyfit(radii, nv[:, 1], 1)
    res.append(dict(chi=st.chi, K=float(st.K), phi_over_N=float(phiN), iters=int(nit), radii=radii.tolist(),
                    var=nv[:, 1].tolist(), slope=float(c[0]), intercept=float(c[1])))
    print('chi %.3f K %.3f phi/N %.1e  var: %s  slope %.3f' % (st.chi, st.K, phiN, np.round(nv[:, 1], 2), c[0]), flush=True)
out['stealthy_variance_vs_chi'] = res
res = []
rng = np.random.default_rng(2); ph = rng.uniform(0, 2 * np.pi, (3, 2))
for n, kap in ((256, 1e-3), (512, 2.5e-4), (1024, 6.25e-5), (2048, 1.5625e-5)):
    flows = [SineFlow(n, A=2.5, kappa=kap, phases=tuple(p), tau=2.0) for p in ph]
    th = initial('sinx', n); th -= th.mean(); th /= np.sqrt((th ** 2).mean())
    ratios = []
    for b in range(40):
        for f in flows: th = f.period(th)
        th -= th.mean(); v = np.sqrt((th ** 2).mean()); ratios.append(float(v)); th /= v
    res.append(dict(n=n, kappa=kap, ratio_per_block_last5=ratios[-5:], rate_per_period=float(-np.log(np.mean(ratios[-5:])) / 3)))
    print('n %d kappa %.2e ratio/block %.4f rate/period %.4f [%.0fs]' % (n, kap, np.mean(ratios[-5:]), -np.log(np.mean(ratios[-5:])) / 3, time.time() - t0), flush=True)
out['eigenmode_decay_vs_kappa'] = res
json.dump(out, open('sweeps.json', 'w'), indent=1)
