import sys, json, time, numpy as np
from stealthy import Stealthy, poisson
N = int(sys.argv[1]); aspect = float(sys.argv[2]); chi = float(sys.argv[3]); out = sys.argv[4]
st = Stealthy(N, aspect=aspect, chi=chi, seed=0)
print('N', st.N, 'M', st.M, 'chi', st.chi, 'K', st.K, 'box', st.box, flush=True)
t0 = time.time()
r, phiN, nit = st.optimise(maxiter=4000)
print('done %.0fs iters %d phi/N %.3e' % (time.time() - t0, nit, phiN), flush=True)
np.save(out + '_points.npy', r)
radii = np.array([0.5, 1, 1.5, 2, 3, 4, 5, 6, 8])
nv = st.number_variance(r, radii, nwin=6000); nvp = st.number_variance(poisson(N, st.box), radii, nwin=6000)
cert = dict(N=N, M=st.M, chi=st.chi, K=float(st.K), box=st.box.tolist(), phi_over_N=float(phiN), iterations=int(nit),
            radii=radii.tolist(), stealthy_mean_var=nv.tolist(), poisson_mean_var=nvp.tolist(), seconds=time.time() - t0)
json.dump(cert, open(out + '_cert.json', 'w'), indent=1)
print(json.dumps(cert, indent=1), flush=True)
