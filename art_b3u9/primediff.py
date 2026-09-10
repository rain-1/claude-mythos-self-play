"""primediff.py — iterated differences of the primes (MO 515079 + Gilbreath).

D_n(j) = sum_k (-1)^k C(n,k) p_{j+k}   (signed n-th forward difference, p_1 = 2, MO 515079's sum)
G_n(j) = |G_{n-1}(j+1) - G_{n-1}(j)|,  G_0 = p   (Gilbreath's absolute-difference triangle)

Outputs primediff.json: for each n, the least j with D_n(j) = 0, the number of zeros up to J,
and for Gilbreath the last column where an entry > 2 appears in each row (the wild band).
"""
import numpy as np, json, sys, time

LIM = int(float(sys.argv[1])) if len(sys.argv) > 1 else 200_000_000
NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 64
t0 = time.time()
sieve = np.ones(LIM // 2, dtype=bool)   # odd numbers 1,3,5,...
sieve[0] = False
for i in range(1, int(LIM ** 0.5) // 2 + 1):
    if sieve[i]:
        p = 2 * i + 1
        sieve[p * p // 2::p] = False
primes = np.concatenate([[2], 2 * np.nonzero(sieve)[0] + 1]).astype(np.int64)
J = len(primes)
print('primes', J, 'last', primes[-1], f'{time.time()-t0:.1f}s', flush=True)

out = dict(limit=LIM, n_primes=int(J), rows={})
D = primes.copy()
for n in range(1, NMAX + 1):
    D = D[1:] - D[:-1]                      # D_n(j) for j = 1..J-n  (index 0 <-> j = 1)
    z = np.nonzero(D == 0)[0] + 1
    sd = float(D[: min(len(D), 2_000_000)].astype(np.float64).std())
    out['rows'][n] = dict(j_min=int(z[0]) if len(z) else None, n_zeros=int(len(z)),
                          first_zeros=[int(x) for x in z[:12]], std_first2M=sd,
                          zeros_le_1e5=int((z <= 100_000).sum()), zeros_le_1e6=int((z <= 1_000_000).sum()))
    print(n, out['rows'][n]['j_min'], len(z), f'std {sd:.3g}', flush=True)

# Gilbreath: absolute differences, wild band (entries > 2) for the first COLS columns, rows up to ROWS
COLS, ROWS = 6000, 3000
G = primes[:COLS + ROWS + 1].copy()
wild_last = []      # per row: largest column index with entry > 2 (within the first COLS columns)
first_entry = []
big = []
for n in range(1, ROWS + 1):
    G = np.abs(G[1:] - G[:-1])
    first_entry.append(int(G[0]))
    w = np.nonzero(G[:COLS] > 2)[0]
    wild_last.append(int(w[-1]) + 1 if len(w) else 0)
    big.append(int(G[:COLS].max()))
out['gilbreath'] = dict(cols=COLS, rows=ROWS, first_entry_all_one=bool(all(x == 1 for x in first_entry)),
                        wild_last_col=wild_last, row_max=big)
json.dump(out, open('primediff.json', 'w'), indent=1)
print('done', f'{time.time()-t0:.1f}s')
