"""locate r_c: on the negative axis, f(x) = E_r(−x) oscillates; a non-real zero pair shows up as an extremum of f
that fails to reach zero (two consecutive extrema of the same sign).  For each r report such 'ghost' extrema."""
import mpmath as mp, sys, numpy as np
mp.mp.dps = int(sys.argv[4]) if len(sys.argv) > 4 else 70
def f(x, r):
    tot = mp.mpf(0); term = mp.mpf(1)
    for m in range(2000):
        if m: term = -term * x / mp.power(m, r)
        tot += term
        if m > 30 and abs(term) < mp.mpf(10) ** (-mp.mp.dps + 10) * (1 + abs(tot)): break
    return tot
X = float(sys.argv[2]); n = int(sys.argv[3])
for r in [mp.mpf(s) for s in sys.argv[1].split(',')]:
    xs = np.linspace(0.05, X, n)
    v = [f(mp.mpf(x), r) for x in xs]
    # envelope-normalised: divide by local scale  (use |v| max over a window)
    a = np.array([float(mp.sign(t)) * float(mp.log(1 + abs(t))) for t in v])   # signed log
    ext = [i for i in range(1, n - 1) if (a[i] - a[i - 1]) * (a[i + 1] - a[i]) < 0]
    ghosts = [(xs[ext[j]], xs[ext[j + 1]]) for j in range(len(ext) - 1) if np.sign(a[ext[j]]) == np.sign(a[ext[j + 1]])]
    sc = int(np.sum(np.sign(a[1:]) * np.sign(a[:-1]) < 0))
    print('r=%s sign changes %d, ghost pairs at %s' % (mp.nstr(r, 6), sc, [(round(p, 2), round(q, 2)) for p, q in ghosts]), flush=True)
