"""census_names.py — many Wright–Fisher runs, count-only: mean number of surviving names at generation t
against Kingman's coalescent (Tavaré's formula with n = N lineages, time t/N), and the fixation time
against 2N(1-1/N); the share of the run during which only two names remain.
    python3 census_names.py N RUNS
"""
import sys, json, numpy as np
N = int(sys.argv[1]); RUNS = int(sys.argv[2])
rng = np.random.default_rng(2026)
T = np.zeros(RUNS, int); T2 = np.zeros(RUNS, int)
ts = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]
alive = np.zeros((RUNS, len(ts)))
for r in range(RUNS):
    names = np.arange(N); t = 0; k = N; t2 = None
    while k > 1:
        names = names[rng.integers(0, N, N)]; t += 1
        k = len(np.unique(names))
        if k <= 2 and t2 is None: t2 = t
        if t in ts: alive[r, ts.index(t)] = k
    T[r] = t; T2[r] = t2
    for j, tt in enumerate(ts):
        if tt > t: alive[r, j] = 1
def kingman(n, tau):
    # E[A(tau)] for Kingman's coalescent started from n lineages, tau in units of N generations
    tot = 0.0
    for k in range(1, n + 1):
        lp = np.log(2 * k - 1) - k * (k - 1) * tau / 2
        for j in range(k):
            lp += np.log(n - j) - np.log(n + j)
        tot += np.exp(lp)
        if k * (k - 1) * tau / 2 > 60: break
    return tot
res = dict(N=N, runs=RUNS, fixation_mean=float(T.mean()), fixation_sd=float(T.std()), theory_2N=2 * N * (1 - 1 / N),
           two_names_share_mean=float(((T - T2) / T).mean()), two_names_share_median=float(np.median((T - T2) / T)),
           last_two_duration_mean=float((T - T2).mean()), theory_last_two=N,
           alive=[dict(t=tt, mean=float(alive[:, j].mean()), kingman=float(kingman(N, tt / N)), asymptotic_2N_over_t=2 * N / tt) for j, tt in enumerate(ts)])
print(json.dumps(res, indent=1))
json.dump(res, open('cert_names.json', 'w'), indent=1)
