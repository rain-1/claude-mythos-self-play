"""Production runs: python3 run_main.py R budget_seconds Nmax_log2 seed0 outname"""
import sys, json, time, numpy as np
sys.path.insert(0, '/home/user/claude-mythos-self-play/art_lrjr/math_cover')
from sim import Sim

R = float(sys.argv[1]); budget = float(sys.argv[2]); L = int(sys.argv[3]); seed0 = int(sys.argv[4]); out = sys.argv[5]
NB = 40
sim = Sim()
runs = []
hist = np.zeros((L + 1, NB), np.int64)   # summed depth histograms of holes at N=2^k
alive = np.zeros(L + 1, np.int64)        # number of runs observed at checkpoint k (uncovered or not)
t0 = time.time(); sd = seed0
def dump():
    json.dump(dict(R=R, Nmax_log2=L, nruns=len(runs), elapsed=time.time() - t0,
                   hist=hist.tolist(), runs=runs), open(out, 'w'))
while time.time() - t0 < budget:
    res = sim.run(sd, R=R, Nmax_log2=L, nbins=NB)
    nc = [0] * (L + 1)
    for (k, c, h, nleaf) in res['holes']:
        nc[k] = c
        hist[k] += np.array(h)
    runs.append(dict(seed=sd, T=res['T'], Trim=res['Trim'], fail_at=res['fail_at'], last=res['last'],
                     amb=res['ambiguous'], ovf=res['overflowcap'], holes=nc))
    sd += 1
    if len(runs) % 50 == 0:
        dump()
dump()
print('done', len(runs), time.time() - t0)
