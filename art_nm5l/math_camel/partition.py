"""Is there a DISJOINT-events reading of Weyl's identity?  (the open half of MO 392723)
Candidate rule: j* = the leg with the largest projection on the resultant, argmax_j Re(z_j conj S).
Compare P(j* = j) with W_j = P(|S - z_j| < a_j)."""
import numpy as np, sys
def test(a, K=8_000_000, seed=2):
    a = np.asarray(a, float); n = len(a); rng = np.random.default_rng(seed)
    z = a * np.exp(2j * np.pi * rng.random((K, n))); S = z.sum(1, keepdims=True)
    Wj = (np.abs(S - z) < a).mean(0)
    proj = (z * np.conj(S)).real
    P1 = np.bincount(proj.argmax(1), minlength=n) / K
    # second candidate: the leg whose removal shortens the journey most = argmin |S - z_j| - ... (same as E_j's margin)
    P2 = np.bincount((np.abs(S - z) - a).argmin(1), minlength=n) / K
    P3 = np.bincount((np.abs(S - z) / a).argmin(1), minlength=n) / K
    print(a, '\n  W        ', np.round(Wj, 4), '\n  argmax proj', np.round(P1, 4), '\n  argmin |R|-a', np.round(P2, 4), '\n  argmin |R|/a', np.round(P3, 4))
test([5, 4, 3]); test([4, 3, 2.4, 1.7, 1.1]); test([3, 2, 2, 1])
