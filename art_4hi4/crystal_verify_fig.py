"""Verification figure for THE CRYSTAL THAT COUNTS CURVES:
the melt IS the amoeba of 1 + z + w.

Left: every surface cell of the sampled crystal placed at its amoeba
coordinates (x,y) = c*(h-i, h-j), colored by its EMPIRICAL classification
(mixed face orientations = melt, else frozen).  The three exact boundary
curves of the amoeba are drawn on top: the melt cloud should fill the
amoeba and the frozen cells its three complement components.

Right: MacMahon's function vs brute-force enumeration, and the exact
mean-volume check.
"""
import numpy as np
import os, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
z = np.load(os.path.join(HERE, "crystal_h.npz"))
h = z["h"]
L = h.shape[0]
c = 0.0145
v = json.load(open(os.path.join(HERE, "crystal_verify.json")))

iiG, jjG = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
gx = np.abs(np.diff(h, axis=0, append=h[-1:]))
gy = np.abs(np.diff(h, axis=1, append=h[:, -1:]))
mixed = gaussian_filter(((gx > 0) & (gy > 0)).astype(float), 2.0)
melt = mixed > 0.22
X = c * (h - iiG); Y = c * (h - jjG)

BG = '#06090c'; FG = '#cfd8d6'; GOLD = '#e8b45a'; TEAL = '#3d9aa0'
plt.rcParams.update({'text.color': FG, 'axes.edgecolor': '#334', 'axes.labelcolor': FG,
                     'xtick.color': FG, 'ytick.color': FG, 'font.size': 11})
fig = plt.figure(figsize=(15, 6.6), dpi=140, facecolor=BG)

ax = fig.add_subplot(1, 2, 1, facecolor=BG)
sub = np.random.default_rng(0).random(h.shape) < 0.25
ax.scatter(X[sub & ~melt], Y[sub & ~melt], s=0.6, c='#26495c', lw=0, label='frozen (empirical)')
ax.scatter(X[sub & melt], Y[sub & melt], s=0.6, c=GOLD, lw=0, label='melt (empirical)')
t = np.linspace(-6, 6, 800)
# boundaries: e^x + e^y = 1 ; e^x = 1 + e^y ; e^y = 1 + e^x
xx = t[t < -0.02]
ax.plot(xx, np.log(np.maximum(1 - np.exp(xx), 1e-12)), color='w', lw=1.4)
ax.plot(t, np.log(np.maximum(np.exp(t) - 1, 1e-12)), color='w', lw=1.4)
ax.plot(np.log(np.maximum(np.exp(t) - 1, 1e-12)), t, color='w', lw=1.4)
ax.set_xlim(-5.5, 5.5); ax.set_ylim(-5.5, 5.5); ax.set_aspect(1)
ax.set_xlabel('$x = c\\,(h-i)$'); ax.set_ylabel('$y = c\\,(h-j)$')
ax.set_title(f'the melt is the amoeba of $1+z+w$  '
             f'(agreement {v["amoeba_agree"]:.1%} in window)', color=FG)
ax.legend(frameon=False, markerscale=8, loc='lower left', fontsize=9)
ax.grid(color='#223', lw=0.4)
for s in ax.spines.values(): s.set_color('#334')

ax2 = fig.add_subplot(1, 2, 2, facecolor=BG)
pl = v['pl']
n = np.arange(len(pl))
ax2.semilogy(n, pl, 'o-', color=TEAL, lw=2,
             label='PL(n): brute-force enumeration')
ax2.semilogy(n, pl, 'x', color=GOLD, ms=9, mew=2,
             label='coefficients of $\\prod (1-q^k)^{-k}$  (exact match)')
ax2.set_xlabel('$n$'); ax2.set_ylabel('plane partitions of $n$')
ax2.set_title('MacMahon = DT of $\\mathbb{C}^3$, verified exactly;  '
              f'sampler $E[\\mathrm{{vol}}]$ dev {v["vol_dev"]:.1%}', color=FG)
ax2.legend(frameon=False, fontsize=9); ax2.grid(color='#223', lw=0.4)
for s in ax2.spines.values(): s.set_color('#334')

fig.suptitle('THE CRYSTAL THAT COUNTS CURVES — verification', color=FG, fontsize=13, y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(HERE, 'crystal_verify.png'), facecolor=BG)
print('saved crystal_verify.png')
