"""heat_cert.py — certificates for BARELY TRUE.
(1) every zero of Xi below 260 at lambda=0 vs the known list (odlyzko-style check via mpmath zetazero for the first 30);
(2) the flow law dt_j/dlambda = H''/H' = 2 sum_k 1/(t_j - t_k) checked against the tracked zeros;
(3) collision table: pair spacing at lambda=0, collision lambda_c, the isolated-pair prediction -delta^2/8."""
import numpy as np, json, mpmath as mp
from heat import H, real_zeros
dat = np.load('cache/heat_T260.npz', allow_pickle=True)
lams = dat['lams']; rows = dat['rows']
i0 = int(np.argmin(np.abs(lams))); z0 = np.asarray(rows[i0], float)
cert = {}
mp.mp.dps = 20
ref = [float(mp.im(mp.zetazero(k))) for k in range(1, 31)]
cert['first_30_zeros_max_abs_err'] = float(np.max(np.abs(z0[:30] - np.array(ref))))
cert['zeros_below_260'] = int(np.sum(z0 < 260)); cert['zero_114_mpmath'] = float(mp.im(mp.zetazero(114))); cert['zero_115_mpmath'] = float(mp.im(mp.zetazero(115))); cert['our_114th'] = float(z0[113])
# (2) flow law at lambda = 0 for the first 40 zeros, using the zeros to 2000 for the sum (tail beyond added by an integral)
zbig = real_zeros(0.0, 0, 1500, dt=0.05); zbig = zbig[np.isfinite(zbig)]; zbig = zbig[np.concatenate([[True], np.diff(zbig) > 1e-6])]
print('zbig', len(zbig), 'nan-free', np.isfinite(zbig).all())
def law(j, zs):
    tj = zs[j]; others = np.delete(zs, j)
    s = np.sum(1 / (tj - others)) + np.sum(1 / (tj + others)) + 1 / (tj + tj)  # the zeros at -t_k, and -t_j
    return 2 * s
h = 0.002
fd, lw = [], []
for j in range(40):
    tp = real_zeros(h, z0[j] - 1, z0[j] + 1, dt=0.05)[0]; tm = real_zeros(-h, z0[j] - 1, z0[j] + 1, dt=0.05)[0]
    fd.append((tp - tm) / (2 * h)); lw.append(law(j, zbig))
fd, lw = np.array(fd), np.array(lw)
# the truncated sum misses zeros above 1500: tail ~ 2 * int_{1500}^inf (1/(t-u) + 1/(t+u)) dN(u) ~ -2 * int 2u/(u^2) * (log(u/2pi)/2pi) du -> small; report raw
Tcut = zbig.max()
tail = -(4 * z0[:40] / (2 * np.pi)) * (np.log(Tcut / (2 * np.pi)) + 1) / Tcut    # zeros above Tcut, by the density log(u/2pi)/2pi
lwt = lw + tail
cert['flow_law_check'] = dict(note='dt_j/dlambda = H\'\'/H\' = 2 sum_k 1/(t_j - t_k) over all zeros +-t_k; sum truncated at T=%.0f, tail by the zero density' % Tcut,
                              max_abs_diff=float(np.max(np.abs(fd - lwt))), median_abs_diff=float(np.median(np.abs(fd - lwt))), median_rel_diff=float(np.median(np.abs(fd - lwt) / np.abs(fd))),
                              examples=[dict(t=round(float(z0[j]), 3), finite_difference=round(float(fd[j]), 4), two_sum_truncated=round(float(lw[j]), 4), two_sum_with_tail=round(float(lwt[j]), 4)) for j in [0, 1, 5, 10, 20, 39]])
# (3) collisions
ctr = json.load(open('cache/heat_T260_complex.json'))
tab = []
for tr in ctr:
    lc, rc = tr['lam'][0], tr['re'][0]
    # the pair at lambda = 0: nearest two zeros to rc
    k = np.argsort(np.abs(z0 - rc))[:2]; a, b = sorted(z0[k]); delta = b - a
    tab.append(dict(pair=[round(float(a), 3), round(float(b), 3)], delta0=round(float(delta), 3), lambda_c=round(float(lc), 3), isolated_pair=round(float(-delta ** 2 / 8), 3), ratio=round(float(lc / (-delta ** 2 / 8)), 3)))
tab.sort(key=lambda r_: -r_['lambda_c'])
cert['collisions'] = tab
cert['n_collisions_below_260_by_lambda_-1.3'] = len(tab)
rat = np.array([r_['ratio'] for r_ in tab])
cert['ratio_lambda_c_over_isolated'] = dict(mean=round(float(rat.mean()), 3), min=round(float(rat.min()), 3), max=round(float(rat.max()), 3))
# HYPOTHESIS: the neighbours delay the collision; ratio - 1 grows with the pair's spacing relative to the mean spacing
clean = [r_ for r_ in tab if r_['ratio'] < 2.5 and r_['lambda_c'] > -0.8]
u = np.array([(r_['delta0'] * np.log(np.mean(r_['pair']) / (2 * np.pi)) / (2 * np.pi)) ** 2 for r_ in clean])   # (delta/mean spacing)^2
v = np.array([r_['ratio'] - 1 for r_ in clean])
A = np.vstack([u, np.ones_like(u)]).T; coef, res, _, _ = np.linalg.lstsq(A, v, rcond=None)
cert['hypothesis_ratio_minus_1_vs_norm_spacing_sq'] = dict(slope=round(float(coef[0]), 3), intercept=round(float(coef[1]), 3), n=len(clean),
    corr=round(float(np.corrcoef(u, v)[0, 1]), 3), samples=[dict(norm_sp2=round(float(a), 3), ratio_minus_1=round(float(b), 3)) for a, b in zip(u[:8], v[:8])])
# spacing statistics along the forward flow: coefficient of variation of nearest-neighbour spacing, 20 < t < 260
cv = []
for lam in [0, 0.5, 1, 2, 3]:
    i = int(np.argmin(np.abs(lams - lam))); r = np.asarray(rows[i], float); r = r[(r > 20) & (r < 260)]
    sp = np.diff(r) * np.log(r[:-1] / (2 * np.pi)) / (2 * np.pi)      # normalised spacing
    cv.append(dict(lam=lam, n=int(len(r)), cv=round(float(sp.std() / sp.mean()), 4), min_norm_spacing=round(float(sp.min()), 3)))
cert['forward_spacing_cv'] = cv
json.dump(cert, open('cert_heat.json', 'w'), indent=1)
print(json.dumps(cert, indent=1)[:4000])
