import mpmath as mp, sys
mp.mp.dps = 140
def E(z, r):
    tot = mp.mpc(0); term = mp.mpc(1)
    for m in range(0, 3000):
        if m > 0: term = term * z / mp.power(m, r)
        tot += term
        if m > 30 and abs(term) < mp.mpf(10) ** (-120) * (1 + abs(tot)): break
    return tot
for r in [float(x) for x in sys.argv[1].split(',')]:
    for R in [float(x) for x in sys.argv[2].split(',')]:
        n = 3000
        w = [E(R * mp.expjpi(2 * mp.mpf(k) / n), r) for k in range(n + 1)]
        wind = sum(mp.im(mp.log(w[k + 1] / w[k])) for k in range(n)) / (2 * mp.pi)
        xs = [-R * mp.mpf(k) / 6000 for k in range(1, 6001)]
        vals = [mp.re(E(x, r)) for x in xs]
        sc = sum(1 for k in range(len(vals) - 1) if vals[k] * vals[k + 1] < 0)
        print('r=%.2f R=%g zeros in disc %s, real sign changes %d' % (r, R, mp.nstr(wind, 6), sc), flush=True)
