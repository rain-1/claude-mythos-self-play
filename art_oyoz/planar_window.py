"""planar_window.py — the exact moment the tide turns (MO 409058).

D(N) = #{n<=N planar} - #{n<=N non-planar}  (n=1 counted planar: empty graph).
D steps by +-1 per integer, so:
  (a) a window sieve of exponent signatures around the crossing gives D(N) exactly for
      every N in the window -> first N with D<0, and every later lead change in the window;
  (b) beyond the window, checkpoints N_k with |D(N_k)| > N_{k+1}-N_k CERTIFY no sign change
      in between (the +-1 step bound) — a rigorous 'non-planar leads forever after' up to the
      last checkpoint.
Outputs planar_window.json.
"""
import numpy as np, json, sys, time
from math import isqrt
from planar_race import count_planar, lucy

def window_sigs(A, W):
    """For n in [A, A+W): (omega, emax, e2) of the prime signature — vectorized segmented sieve."""
    B = A + W
    r = isqrt(B) + 1
    sv = np.ones(r + 1, bool); sv[:2] = False
    for i in range(2, isqrt(r) + 1):
        if sv[i]:
            sv[i * i::i] = False
    primes = np.nonzero(sv)[0]
    rem = np.arange(A, B, dtype=np.int64)
    omega = np.zeros(W, np.int8); emax = np.zeros(W, np.int8); e2 = np.zeros(W, np.int8)
    for p in primes:
        start = (-A) % p
        idx = np.arange(start, W, p)
        if len(idx) == 0:
            continue
        e = np.ones(len(idx), np.int8)
        pk = p * p
        while pk <= B:
            s2 = (-A) % pk
            sub = np.arange(s2, W, pk)
            # positions of sub inside idx: (sub - start)//p
            e[(sub - start) // p] += 1
            pk *= p
        # divide out
        rem[idx] //= p ** e.astype(np.int64)
        omega[idx] += 1
        old = emax[idx]
        bigger = e > old
        e2[idx] = np.where(bigger, old, np.maximum(e2[idx], e))
        emax[idx] = np.where(bigger, e, old)
    left = rem > 1  # leftover prime factor with exponent 1
    omega[left] += 1
    e2[left] = np.maximum(e2[left], np.minimum(emax[left], 1))
    emax[left] = np.maximum(emax[left], 1)
    return omega, emax, e2

def planar_flags(omega, emax, e2):
    return ((omega == 1) & (emax <= 4)) | ((omega == 2) & (emax <= 3) & (e2 == 1)) | ((omega == 3) & (emax == 1))

if __name__ == '__main__':
    t0 = time.time()
    # --- self-test of the window sieve vs count_planar
    for A, W in [(2, 5000), (1000000, 200000)]:
        om, em, e2 = window_sigs(A, W)
        fl = planar_flags(om, em, e2)
        base = count_planar(A - 1)[0] if A > 1 else 0
        assert base + int(fl.sum()) == count_planar(A + W - 1)[0], 'window sieve mismatch'
    print('window sieve self-test OK', flush=True)
    # --- bracket the first crossing with Lucy (D(N) = 2P(N) - N)
    lo, hi = 10 ** 7, 10 ** 8
    while hi - lo > 2000000:
        mid = (lo + hi) // 2
        D = 2 * count_planar(mid)[0] - mid
        if D > 0: lo = mid
        else: hi = mid
    A = max(2, lo - 3000000); W = (hi - lo) + 30000000
    print(f'bracket [{lo},{hi}] ; sieving window [{A},{A + W})', flush=True)
    om, em, e2 = window_sigs(A, W)
    fl = planar_flags(om, em, e2)
    base = count_planar(A - 1)[0]
    P = base + np.cumsum(fl.astype(np.int64))
    Ns = np.arange(A, A + W, dtype=np.int64)
    D = 2 * P - Ns
    sgn = np.sign(D)
    assert D[0] > 0, 'window starts with non-planar ahead — widen'
    first_neg = int(Ns[np.argmax(D < 0)])
    first_tie = int(Ns[np.argmax(D <= 0)])
    # lead changes: N where sign(D) becomes strictly the opposite of the previous nonzero sign
    nz = sgn != 0
    s_nz = sgn[nz]; N_nz = Ns[nz]
    ch = np.nonzero(s_nz[1:] != s_nz[:-1])[0]
    changes = [(int(N_nz[i + 1]), int(s_nz[i + 1])) for i in ch]
    last_planar_lead = int(Ns[np.nonzero(D > 0)[0][-1]])
    print(f'first tie N={first_tie}; first non-planar lead N={first_neg}; lead changes in window: {len(changes)}; '
          f'last N with planar strictly ahead (in window): {last_planar_lead}; D at window end {int(D[-1])}', flush=True)
    assert D[-1] < -(10 ** 6), 'window end not deep enough for a clean certificate start'
    # store a decimated trace for the chart + full-resolution around the crossing
    trace_step = 1000
    around = (Ns >= first_neg - 400000) & (Ns <= first_neg + 400000)
    out = dict(A=A, W=W, first_tie=first_tie, first_neg=first_neg, changes=changes,
               last_planar_lead_in_window=last_planar_lead, D_end=int(D[-1]),
               trace_N=Ns[::trace_step].tolist(), trace_D=D[::trace_step].tolist(),
               zoom_N=Ns[around][::50].tolist(), zoom_D=D[around][::50].tolist(),
               changes_all_N=[c[0] for c in changes])
    # excursions: maximal intervals where planar leads after first_neg
    pos = D > 0
    idx = np.nonzero(pos & (Ns > first_neg))[0]
    if len(idx):
        breaks = np.nonzero(np.diff(idx) > 1)[0]
        starts = np.concatenate([[idx[0]], idx[breaks + 1]]); ends = np.concatenate([idx[breaks], [idx[-1]]])
        exc = [(int(Ns[s]), int(Ns[e]), int(D[s:e + 1].max())) for s, e in zip(starts, ends)]
        out['excursions'] = exc
        print('planar-lead excursions after first crossing:', len(exc), 'longest', max(exc, key=lambda x: x[1] - x[0]), flush=True)
    # --- checkpoint certificate: no sign change from window end to LIMIT
    LIMIT = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10 ** 12
    N = A + W - 1; Dn = int(D[-1]); cps = [(N, Dn)]
    while N < LIMIT:
        step = int(0.9 * abs(Dn))
        N2 = min(N + step, LIMIT)
        P2 = count_planar(N2)[0]; D2 = 2 * P2 - N2
        assert D2 < 0 and abs(D2) >= 0, 'certificate broken?!'
        # rigorous: |D(N2)| and |D(N)| both exceed the gap? we only need D(N)<0 and step<|D(N)|
        assert N2 - N < abs(Dn) + 1
        N, Dn = N2, D2; cps.append((N, Dn))
        print(f'  checkpoint N={N:,} D={Dn:,} ({time.time() - t0:.0f}s)', flush=True)
    out['checkpoints'] = cps; out['certified_to'] = LIMIT
    json.dump(out, open('planar_window.json', 'w'))
    print('certified: non-planar leads at every N from', first_neg if not out.get('excursions') else out['excursions'][-1][1] + 1, 'to', LIMIT)
