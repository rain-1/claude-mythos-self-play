import mpmath as mp
mp.mp.dps = 60
def E(z, r):
    s = mp.mpf(0); t = mp.mpf(1); m = 0
    # sum z^m/(m!)^r with enough terms
    tot = mp.mpc(0)
    term = mp.mpc(1)
    for m in range(0, 400):
        if m > 0:
            term = term * z / mp.power(m, r)
        tot += term
        if m > 20 and abs(term) < mp.mpf(10) ** (-50) * (1 + abs(tot)):
            break
    return tot
for r, z0 in [(1.2, mp.mpc(-9.34076, 5.8363)), (1.5, None), (1.7, None), (2.5, None), (2.0, None), (3.0, None)]:
    if z0 is not None:
        z = mp.findroot(lambda z: E(z, r), z0)
        print('r', r, 'root', mp.nstr(z, 15), '|E|', mp.nstr(abs(E(z, r)), 5))
    # argument principle: number of zeros in |z|<R minus number of real negative zeros (sign changes on (-R,0))
    for R in [20, 60]:
        n = 4000
        w = [E(R * mp.expjpi(2 * mp.mpf(k) / n), r) for k in range(n + 1)]
        wind = sum(mp.im(mp.log(w[k + 1] / w[k])) for k in range(n)) / (2 * mp.pi)
        xs = [-R * mp.mpf(k) / 4000 for k in range(1, 4001)]
        vals = [mp.re(E(x, r)) for x in xs]
        sc = sum(1 for k in range(len(vals) - 1) if vals[k] * vals[k + 1] < 0)
        print('  r=%.2f R=%d zeros in disc %s, real negative sign changes %d' % (r, R, mp.nstr(wind, 6), sc), flush=True)
