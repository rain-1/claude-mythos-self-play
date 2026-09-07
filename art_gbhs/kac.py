"""kac.py — Mark Kac's ring (1956): the reversible model that looks irreversible.

N sites on a ring, a ball (white or black) on each; M of the N edges carry a marker. Each
step every ball moves one site clockwise and flips colour when it crosses a marker. The
dynamics is a bijection of period 2N: after N steps every ball has crossed every marker once
(all colours flipped if M is odd), after 2N steps the ring is exactly as it began.

Exact solution. Let S(j) = number of markers on the edges 0..j-1 (prefix count, extended
periodically with S(j + N) = S(j) + M). Ball at site i at time t started at site i - t and
crossed exactly S(i) - S(i - t) markers, so

    colour(i, t) = colour0(i - t)  XOR  parity( S(i) - S(i - t) ),
    flips(i, t)  = S(i) - S(i - t).

Greyness (Kac's observable): G(t) = (#white - #black)/N. For a random marker set of density
mu = M/N the ensemble mean is (1 - 2 mu)^t — an exponential 'death' — while the exact
single-ring curve returns to 1 at t = 2N.
"""
import numpy as np


def markers(N, M, kind='random', seed=1):
    rng = np.random.default_rng(seed)
    if kind == 'random':
        idx = rng.choice(N, M, replace=False)
    elif kind == 'sturmian':                          # Beatty set of the golden ratio, scaled to M markers
        phi = (1 + 5 ** 0.5) / 2
        idx = (np.floor(np.arange(M) * N / M * 1.0 + rng.uniform(0, 1)) ).astype(int) % N
        idx = np.unique((np.floor((np.arange(M) + 0.5) * phi * N / (M * phi))).astype(int) % N)
    elif kind == 'clustered':                          # markers in a few dense arcs
        centres = rng.uniform(0, N, 5)
        idx = np.unique((np.concatenate([c + rng.normal(0, N * 0.02, M // 5) for c in centres]).astype(int)) % N)
    m = np.zeros(N, np.int64); m[idx] = 1
    return m


def prefix(m):
    """S(j) for j = 0..N (S(0)=0, S(N)=M)"""
    return np.concatenate([[0], np.cumsum(m)])


def flips_field(m, T):
    """flips(i, t) for i in 0..N-1, t in 0..T (T may exceed N; periodic extension)"""
    N = len(m); M = int(m.sum())
    S = prefix(m)                                     # length N+1
    def Sext(j):
        j = np.asarray(j); q, r = np.divmod(j, N)
        return S[r] + q * M
    i = np.arange(N)[None, :]; t = np.arange(T + 1)[:, None]
    return Sext(i) - Sext(i - t)                      # (T+1, N)


def colour_field(m, T, colour0=None):
    F = flips_field(m, T)
    N = len(m)
    if colour0 is None:
        colour0 = np.zeros(N, np.int64)               # all white (Kac's initial condition)
    i = np.arange(N)[None, :]; t = np.arange(T + 1)[:, None]
    return (colour0[(i - t) % N] + F) % 2, F


def greyness(C):
    return 1 - 2 * C.mean(axis=1)


def simulate(m, T, colour0=None):
    """brute-force step-by-step dynamics, for the certificate"""
    N = len(m)
    c = np.zeros(N, np.int64) if colour0 is None else colour0.copy()
    out = [c.copy()]
    for t in range(T):
        # ball at site i moves to i+1 crossing edge i (marker m[i])
        c = np.roll((c + m) % 2, 1)
        out.append(c.copy())
    return np.array(out)


if __name__ == '__main__':
    N, M = 240, 61
    m = markers(N, M, 'random', seed=3)
    C, F = colour_field(m, 2 * N)
    B = simulate(m, 2 * N)
    print('closed form == brute force:', np.array_equal(C, B))
    print('recurrence at 2N:', np.array_equal(C[2 * N], C[0]), ' anti-recurrence at N (M odd):', np.array_equal(C[N], 1 - C[0]))
    G = greyness(C)
    mu = M / N
    print('greyness t=1..6:', np.round(G[1:7], 3), ' Kac mean (1-2mu)^t:', np.round((1 - 2 * mu) ** np.arange(1, 7), 3))
    print('G(N) =', G[N], ' G(2N) =', G[2 * N])
