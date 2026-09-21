"""Where does Pinchuk's map send the plane?  Find the source region that lands
in a viewing window around the two missed points, and check the 2-to-1 claim."""
import numpy as np
from pinchuk import F, aux, asymptotic_variety, MISSED

rng = np.random.default_rng(1)
# where is the action?  the asymptotic variety for h in [-2, 1]
hh = np.linspace(-2.2, 1.2, 2000)
u, v = asymptotic_variety(hh)
print('asymptotic variety over h in [-2.2,1.2]:  u in [%.3f, %.3f]  v in [%.2f, %.2f]' %
      (u.min(), u.max(), v.min(), v.max()))
print('missed points:', MISSED)

# sample the source plane on a wide log-spaced grid and see what lands nearby
U0, U1, V0, V1 = -4.0, 4.0, -70.0, 25.0
tot = 0; inw = 0
keepx = []; keepy = []
for rad in [0.3, 1, 3, 10, 30, 100, 300, 1000]:
    xs = rng.uniform(-rad, rad, 400000); ys = rng.uniform(-rad, rad, 400000)
    P, Q = F(xs, ys)
    m = (P > U0) & (P < U1) & (Q > V0) & (Q < V1)
    tot += len(xs); inw += m.sum()
    keepx.append(xs[m]); keepy.append(ys[m])
    print(f'  source box |x|,|y|<{rad:6.1f}: {m.mean()*100:7.4f}% land in the window   '
          f'(x range of hits {xs[m].min() if m.any() else 0:.3f}..{xs[m].max() if m.any() else 0:.3f})')
kx = np.concatenate(keepx); ky = np.concatenate(keepy)
print('hits:', len(kx))
if len(kx):
    print('  |x| of hits: %.4g .. %.4g   |y|: %.4g .. %.4g' % (np.abs(kx).min(), np.abs(kx).max(),
                                                               np.abs(ky).min(), np.abs(ky).max()))
    t, h, f = aux(kx, ky)
    print('  h of hits: %.3f .. %.3f      t: %.3g .. %.3g' % (h.min(), h.max(), t.min(), t.max()))
