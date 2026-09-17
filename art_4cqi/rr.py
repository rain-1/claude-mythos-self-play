"""rr.py — the Rogers–Ramanujan continued fraction on the disc.
R(q) = q^{1/5} / (1 + q/(1 + q^2/(1 + q^3/ ...))) = q^{1/5} prod (1-q^{5n-1})(1-q^{5n-4}) / ((1-q^{5n-2})(1-q^{5n-3})).
On the disc of w = q^{1/5} it is single-valued: R = w * prod(...)(w^5), with R(zeta w) = zeta R(w) (zeta^5 = 1)
and R(conj w) = conj R(w), so one twentieth... one tenth of the disc (theta in [0, pi/5]) is enough.
Polar grid, log-spaced radii toward the rim, term count by radius.  Saves cache/rr_polar.npz (complex64).
    python3 rr.py NR NTH RMAX
"""
import sys, time, numpy as np
NR = int(sys.argv[1]); NTH = int(sys.argv[2]); RMAX = float(sys.argv[3])
smax = -np.log(1 - RMAX)
s = np.linspace(0, smax, NR)
r = 1 - np.exp(-s)
th = np.linspace(0, np.pi / 5, NTH)
nterms = np.minimum(np.ceil(40.0 / (5 * (1 - r))).astype(int), 6000)
w = (r[:, None] * np.exp(1j * th[None, :])).astype(np.complex64)
q = w ** 5
q2 = q * q; q3 = q2 * q; q4 = q3 * q; q5 = q4 * q
R = w.copy()
qp = np.ones_like(q)
nmax = int(nterms.max())
t0 = time.time()
for n in range(1, nmax + 1):
    j0 = int(np.searchsorted(nterms, n))          # radii needing >= n terms (nterms is nondecreasing)
    if j0 >= NR: break
    sl = slice(j0, NR)
    qp[sl] *= q5[sl] if n > 1 else 1
    if n == 1:
        qp[sl] = 1
    t1 = qp[sl] * q[sl]; t2 = qp[sl] * q2[sl]; t3 = qp[sl] * q3[sl]; t4 = qp[sl] * q4[sl]
    R[sl] *= (1 - t1) * (1 - t4) / ((1 - t2) * (1 - t3))
    if n % 500 == 0:
        print('term', n, 'rows', NR - j0, f'{time.time()-t0:.0f}s', flush=True)
np.savez_compressed('cache/rr_polar.npz', R=R, r=r, th=th, nterms=nterms)
# certificate: R at tau = i, i.e. w = exp(-2 pi / 5) real: closed form sqrt((5+sqrt5)/2) - (1+sqrt5)/2
w0 = np.exp(-2 * np.pi / 5)
j = int(np.argmin(np.abs(r - w0)))
exact = np.sqrt((5 + np.sqrt(5)) / 2) - (1 + np.sqrt(5)) / 2
print('R(e^-2pi) grid', R[j, 0], 'at r', r[j], 'exact', exact)
# direct high-precision check at w0
qq = w0 ** 5; val = w0
for n in range(1, 400):
    val *= (1 - qq ** (5 * n - 4)) * (1 - qq ** (5 * n - 1)) / ((1 - qq ** (5 * n - 3)) * (1 - qq ** (5 * n - 2)))
print('direct', val, 'err', abs(val - exact))
print('done', f'{time.time()-t0:.0f}s')
