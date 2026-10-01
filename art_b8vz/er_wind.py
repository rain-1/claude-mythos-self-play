"""argument principle for E_r in |z| < R vs real sign changes on (−R, 0); prints #non-real zeros."""
import mpmath as mp, sys
r = mp.mpf(sys.argv[1]); R = mp.mpf(sys.argv[2]); n = int(sys.argv[3]); mp.mp.dps = int(sys.argv[4])
def E(z):
    tot = mp.mpc(0); term = mp.mpc(1)
    for m in range(100000):
        if m: term = term * z / mp.power(m, r)
        tot += term
        if m > 30 and abs(term) < mp.mpf(10) ** (-mp.mp.dps + 15) * (1 + abs(tot)): break
    return tot
w = [E(R * mp.expjpi(2 * mp.mpf(k) / n)) for k in range(n + 1)]
steps = [mp.im(mp.log(w[k + 1] / w[k])) for k in range(n)]
wind = sum(steps) / (2 * mp.pi)
xs = [-R * mp.mpf(k) / (2 * n) for k in range(1, 2 * n + 1)]
vals = [mp.re(E(x)) for x in xs]
sc = sum(1 for k in range(len(vals) - 1) if vals[k] * vals[k + 1] < 0)
print('r=%s R=%s zeros in disc %s (max arg step %.3f), real sign changes %d -> non-real %s' % (
    mp.nstr(r, 5), mp.nstr(R, 6), mp.nstr(wind, 6), float(max(abs(s) for s in steps)), sc, mp.nstr(wind - sc, 4)), flush=True)
