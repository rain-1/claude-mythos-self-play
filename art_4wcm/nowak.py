"""nowak.py — the spatial Prisoner's Dilemma of Nowak & May (Nature 1992), one defector
in a sea of cooperators, deterministic, with self-interaction.

Payoff matrix: C–C = 1, C–D = 0 (the sucker), D–C = b, D–D = 0.  Each site plays the
game with its 8 Moore neighbours AND itself, then adopts the strategy of the highest-
scoring site of that 9-site neighbourhood (itself included).  The only comparisons that
ever occur are 'n' (a cooperator with n cooperators among its 9 sites, itself included)
against 'b*m' (a defector with m cooperating neighbours, 1..8), so the dynamics depend on
b only through which of the fractions n/m lie below b: the family of futures is FINITE.
"""
import numpy as np
from fractions import Fraction
from scipy.ndimage import convolve

K9 = np.ones((3, 3), np.int32)


def step(D, b, tie='keep'):
    """D: bool array (True = defector). Returns next D. Payoff of a C site = number of C
    sites in its 3x3 (itself included); of a D site = b * number of C sites in its 3x3
    (itself excluded since D-D pays 0)."""
    C = ~D
    nC = convolve(C.astype(np.int32), K9, mode='constant', cval=1)   # outside = cooperators
    pay = np.where(D, b * nC.astype(np.float64), nC.astype(np.float64))
    # best payoff in the 3x3 among C sites and among D sites, separately
    NEG = -1.0
    payC = np.where(C, pay, NEG); payD = np.where(D, pay, NEG)
    from scipy.ndimage import maximum_filter
    mC = maximum_filter(payC, size=3, mode='constant', cval=NEG)
    mD = maximum_filter(payD, size=3, mode='constant', cval=NEG)
    # boundary: outside sites are cooperators with payoff 9 (all-C surroundings) — approximate
    # by running with enough margin so the boundary is never reached.
    if tie == 'keep':
        newD = np.where(mD > mC, True, np.where(mC > mD, False, D))
    elif tie == 'D':
        newD = mD >= mC
    else:
        newD = mD > mC
    return newD


def run(N, b, T, record=True, seed_shape='one'):
    """N x N grid, one central defector, T steps. Returns final D and accumulated counts:
    cntD (steps as D), arrive (first step a site was D, -1 if never), flips (number of
    strategy changes)."""
    D = np.zeros((N, N), bool)
    c = N // 2
    if seed_shape == 'one':
        D[c, c] = True
    elif seed_shape == 'plus':
        D[c, c] = D[c - 1, c] = D[c + 1, c] = D[c, c - 1] = D[c, c + 1] = True
    cntD = np.zeros((N, N), np.int32)
    arrive = np.full((N, N), -1, np.int32)
    flips = np.zeros((N, N), np.int32)
    lastflip = np.zeros((N, N), np.int32)
    frames = []
    for t in range(T):
        nd = step(D, b)
        ch = nd != D
        flips += ch
        lastflip[ch] = t
        newly = nd & (arrive < 0)
        arrive[newly] = t
        D = nd
        cntD += D
        if record and (t % max(1, T // 8) == 0):
            frames.append(D.copy())
    return D, dict(cntD=cntD, arrive=arrive, flips=flips, lastflip=lastflip, frames=frames)


def breakpoints():
    """all fractions n/m > 1 with 1<=n<=9, 1<=m<=8 (C payoff vs D payoff/b), sorted, unique"""
    S = set()
    for n in range(1, 10):
        for m in range(1, 9):
            f = Fraction(n, m)
            if f > 1:
                S.add(f)
    return sorted(S)


if __name__ == '__main__':
    import time
    bps = breakpoints()
    print(len(bps), 'breakpoints:', [str(x) for x in bps])
    t0 = time.time()
    D, acc = run(401, 1.85, 200, record=False)
    print('b=1.85 T=200: D fraction', D.mean(), 'time', time.time() - t0)
    # symmetry check
    print('D4 symmetric:', np.array_equal(D, D.T), np.array_equal(D, D[::-1]), np.array_equal(D, D[:, ::-1]))
