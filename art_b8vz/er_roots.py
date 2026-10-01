"""zeros of E_r(z) = Σ z^m/(m!)^r in |z| < R via a long truncation + polish; prints non-real ones."""
import mpmath as mp, sys
mp.mp.dps = 200
def coeffs(r, N): return [1 / mp.factorial(m) ** r for m in range(N + 1)]
def E(z, r, N=400):
    tot = mp.mpc(0); term = mp.mpc(1)
    for m in range(N):
        if m: term = term * z / mp.power(m, r)
        tot += term
        if m > 30 and abs(term) < mp.mpf(10) ** (-150) * (1 + abs(tot)): break
    return tot
def zeros(r, N=130, R=300):
    c = coeffs(r, N)
    rts = mp.polyroots(c[::-1], maxsteps=800, extraprec=1500)
    out = []
    for z in rts:
        if abs(z) < R:
            try: z = mp.findroot(lambda w: E(w, r), z)
            except Exception: pass
            out.append(z)
    return sorted(out, key=lambda z: abs(z))
if __name__ == '__main__':
    for r in [float(x) for x in sys.argv[1].split(',')]:
        zs = zeros(mp.mpf(r))
        nr = [z for z in zs if abs(mp.im(z)) > 1e-20 * (1 + abs(z))]
        print('r=%.4f zeros<300: %d, non-real: %s' % (r, len(zs), ' '.join(mp.nstr(z, 8) for z in nr if mp.im(z) > 0)), flush=True)
