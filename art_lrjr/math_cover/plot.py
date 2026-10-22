import json, math, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D = '/home/user/claude-mythos-self-play/art_lrjr/math_cover/'
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for fn, lab, col in [('runs_R1.00.json', 'R=1: T', '#1f5fa8'), ('runs_R0.95.json', 'R=0.95: T', '#c0552b'),
                     ('runs_R1.05.json', 'R=1.05: T (incl. failures)', '#4c9a4c')]:
    try:
        d = json.load(open(D + fn))
    except Exception:
        continue
    L = d['Nmax_log2']; ks = np.arange(1, L)
    T = np.array([r['T'] if r['T'] > 0 else np.inf for r in d['runs']], float)
    S = np.array([(T > 2.0 ** k).mean() for k in ks])
    x = ks * math.log(2)
    ax[0].loglog(x, S, 'o-', ms=3, color=col, label=f"{lab} (n={len(T)})")
    if d['R'] == 1.0:
        Tr = np.array([r['Trim'] if r['Trim'] > 0 else np.inf for r in d['runs']], float)
        Sr = np.array([(Tr > 2.0 ** k).mean() for k in ks])
        ax[0].loglog(x, Sr, 's--', ms=3, color='#7a7a7a', label='R=1: T_rim')
        H = np.array([r['holes'] for r in d['runs']], float)
        ax[1].plot(ks, H[:, 1:L].mean(0), 'o-', ms=3, color=col, label='R=1  E[#holes at N]')
        hist = np.array(d['hist'], float) / len(T)
        ax[1].plot(ks, hist[1:L, 0], '--', color='#7a7a7a', label='R=1  E[#rim holes (depth<r_N)]')
    if d['R'] == 0.95:
        H = np.array([r['holes'] for r in d['runs']], float)
        ax[1].plot(ks, H[:, 1:L].mean(0), 'o-', ms=3, color=col, label='R=0.95  E[#holes at N]')
xx = np.linspace(5, 36, 50)
ax[0].loglog(xx, 3.5 / np.sqrt(xx), ':', color='k', label='3.5 (log N)^-1/2')
ax[0].loglog(xx, 12 / xx, '-.', color='k', label='12 / log N')
ax[0].set_xlabel('log N'); ax[0].set_ylabel('P(T > N)'); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3, which='both')
ax[1].set_xlabel('log2 N'); ax[1].set_ylabel('mean # uncovered components'); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(D + 'tail_and_holes.png', dpi=120)
print('ok')
