"""heat.py — the de Bruijn–Newman heat flow of the Riemann Xi zeros.
Xi_lam(t) = 4 Re int_0^inf Phi(v+i a) e^{lam (v+ia)^2} e^{i (v+ia) t} dv   (a = pi/4 - eps),
i.e. H_lam(t) = int_R e^{lam u^2} Phi(u) e^{iut} du, with the vertical contour piece purely imaginary.
lam = 0 : the Riemann Xi.  lam > 0: forward heat (zeros real, repel, -> arithmetic progression).
lam < 0 : backward heat (ill-posed; pairs collide and leave the real line). Lambda (de Bruijn–Newman) in [0, 0.2].
Tracks every zero in [0, T] as lam runs from LMIN to LMAX, including complex zeros after collisions."""
import numpy as np, sys, json, time
from xi2 import PB, uB, Phi_c

def H(lam, t, deriv=0):
    """H_lam at real or complex t (array). returns complex; real for real t."""
    t = np.atleast_1d(np.asarray(t))
    k = PB * np.exp(lam * uB ** 2) * (1j * uB) ** deriv
    out = np.empty(t.shape, np.complex128)
    B = 1500
    if np.iscomplexobj(t):
        for i in range(0, len(t), B):
            tb = t[i:i + B]
            a = np.exp(1j * np.outer(tb, uB)) @ k
            b = np.exp(1j * np.outer(np.conj(tb), uB)) @ k
            out[i:i + B] = 2 * (a + np.conj(b))   # H = int_R = I(t) + conj(I(conj t)) 
        return out
    for i in range(0, len(t), B):
        tb = t[i:i + B]
        out[i:i + B] = 4 * np.real(np.exp(1j * np.outer(tb, uB)) @ k)
    return out

def real_zeros(lam, tmin, tmax, dt=0.05):
    tg = np.arange(tmin, tmax + dt, dt)
    f = np.real(H(lam, tg))
    sc = np.where(np.sign(f[:-1]) * np.sign(f[1:]) < 0)[0]
    a, b = tg[sc], tg[sc + 1]; fa, fb = f[sc], f[sc + 1]
    for _ in range(10):
        m = 0.5 * (a + b); fm = np.real(H(lam, m))
        left = np.sign(fm) == np.sign(fa)
        a = np.where(left, m, a); fa = np.where(left, fm, fa)
        b = np.where(left, b, m); fb = np.where(left, fb, fm)
    z = 0.5 * (a + b)
    for _ in range(3):
        z = z - np.real(H(lam, z)) / np.real(H(lam, z, 1))
    return z

def newton_c(lam, z, iters=12):
    z = np.asarray(z, np.complex128)
    for _ in range(iters):
        z = z - H(lam, z) / H(lam, z, 1)
    return z

if __name__ == '__main__':
    T = float(sys.argv[1]) if len(sys.argv) > 1 else 120
    LMIN, LMAX, DL = float(sys.argv[2]) if len(sys.argv) > 2 else -1.0, float(sys.argv[3]) if len(sys.argv) > 3 else 1.0, 0.004
    t0 = time.time()
    z0 = real_zeros(0, 0, T)
    print('lam=0 zeros', len(z0), z0[:5], z0[-3:])
    # forward branch: lam 0 -> LMAX, track real zeros by re-finding each step (they stay real)
    rows = {}
    lams = np.round(np.arange(0, LMAX + DL / 2, DL), 6)
    for lam in lams:
        rows[lam] = real_zeros(lam, 0, T + 6)
    print('forward done', time.time() - t0)
    # backward branch: lam 0 -> LMIN; track real zeros; on a pair disappearing, continue as complex zeros
    lamsb = np.round(np.arange(0, LMIN - DL / 2, -DL), 6)
    complex_tracks = []   # list of dict(lam=[], z=[])
    active = []           # complex zeros being tracked (upper half plane), np array
    prev = rows[0.0]
    for lam in lamsb[1:]:
        zr = real_zeros(lam, 0, T + 6)
        # detect lost pairs: count drop
        if len(zr) < len(prev) - 0:
            # find which previous zeros have no near successor
            lost = [p for p in prev if np.min(np.abs(zr - p)) > 0.6] if len(zr) else list(prev)
            lost = sorted(lost)
            if len(lost) % 2 == 1 and lost[0] < 1.0:      # a pair met at t = 0 (its mirror image is the partner)
                zc = complex(newton_c(lam, 0.0 + 0.3j)[0])
                if abs(zc.imag) > 1e-6:
                    complex_tracks.append(dict(lam=[float(lam)], z=[zc])); print('collision at the origin', lam, zc)
                lost = lost[1:]
            # pair them up
            for i in range(0, len(lost) - 1, 2):
                zc = 0.5 * (lost[i] + lost[i + 1]) + 0.15j
                zc = complex(newton_c(lam, zc)[0])
                if abs(zc.imag) > 1e-6:
                    active.append(complex(zc)); complex_tracks.append(dict(lam=[float(lam)], z=[complex(zc)]))
                    print(f'collision near t={0.5*(lost[i]+lost[i+1]):.3f} at lam={lam}: z={zc}')
        # continue complex tracks
        newact = []
        for k, tr in enumerate(complex_tracks):
            if tr.get('dead'): continue
            zc = complex(newton_c(lam, tr['z'][-1])[0])
            if not np.isfinite(zc) or abs(zc.imag) < 1e-7 or abs(zc.real) > T + 10:
                tr['dead'] = True; continue
            tr['lam'].append(float(lam)); tr['z'].append(complex(zc))
        rows[lam] = zr
        prev = zr
    print('backward done', time.time() - t0, 'complex tracks', len(complex_tracks))
    np.savez(f'cache/heat_T{int(T)}.npz', lams=np.array(sorted(rows.keys())),
             rows=np.array([rows[l] for l in sorted(rows.keys())], dtype=object), allow_pickle=True)
    json.dump([dict(lam=tr['lam'], re=[z.real for z in tr['z']], im=[z.imag for z in tr['z']]) for tr in complex_tracks],
              open(f'cache/heat_T{int(T)}_complex.json', 'w'))
    for l in [-1.0, -0.5, -0.2, 0.0, 0.2, 0.5, 1.0]:
        r = rows[l]; print(l, len(r), np.round(np.diff(r)[:8], 3))
