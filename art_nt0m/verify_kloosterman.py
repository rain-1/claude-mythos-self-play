"""Verify Kloosterman sum facts before rendering anything.

S(a,b;p) = sum_{x=1}^{p-1} e^{2 pi i (a x + b x^{-1})/p}

Checks:
  1. S is real (pairing x <-> -x ... actually x <-> inverse conjugate) for all a.
  2. Weil bound |S| <= 2 sqrt(p).
  3. S(a,b;p) depends only on ab mod p  (substitution x -> b^{-1} x... verify numerically).
  4. Salie closed form check for a quadratic-twisted cousin is skipped; instead verify
     Sato-Tate-ish histogram of theta = arccos(S/2sqrt p) roughly follows sin^2.
  5. Kowalski-Sawin normalization: partial sums / sqrt(p) stay O(log p).
"""
import numpy as np

def kloosterman_paths(p, b=1):
    """Return (p-1, p-1) complex array: paths[a-1, t] = partial sum up to x=t+1, /sqrt(p)."""
    inv = np.array([pow(x, p - 2, p) for x in range(1, p)], dtype=np.int64)
    x = np.arange(1, p, dtype=np.int64)
    paths = np.empty((p - 1, p - 1), dtype=np.complex64)
    a_all = np.arange(1, p, dtype=np.int64)
    chunk = 256
    for i in range(0, p - 1, chunk):
        a = a_all[i:i + chunk][:, None]
        phase = (a * x[None, :] + b * inv[None, :]) % p
        steps = np.exp((2j * np.pi / p) * phase)
        paths[i:i + chunk] = np.cumsum(steps, axis=1) / np.sqrt(p)
    return paths

if __name__ == "__main__":
    p = 1009
    paths = kloosterman_paths(p)
    S = paths[:, -1] * np.sqrt(p)          # full sums
    # 1. real
    print("max |Im S| =", np.abs(S.imag).max(), " (float32 cumsum tolerance)")
    # 2. Weil
    print("max |S| / 2sqrt(p) =", np.abs(S).max() / (2 * np.sqrt(p)))
    # 3. depends only on ab: S(a,b) vs S(ab,1)
    p2 = 613
    invx = np.array([pow(x, p2 - 2, p2) for x in range(1, p2)], dtype=np.int64)
    xs = np.arange(1, p2, dtype=np.int64)
    def Sab(a, b):
        return np.exp(2j * np.pi * ((a * xs + b * invx) % p2) / p2).sum()
    rng = np.random.default_rng(0)
    worst = 0.0
    for _ in range(50):
        a, b = rng.integers(1, p2, 2)
        worst = max(worst, abs(Sab(a, b) - Sab(a * b % p2, 1)))
    print("max |S(a,b)-S(ab,1)| over 50 random pairs =", worst)
    # 4. Sato-Tate: histogram of theta vs (2/pi) sin^2
    theta = np.arccos(np.clip(S.real / (2 * np.sqrt(p)), -1, 1))
    hist, edges = np.histogram(theta, bins=12, range=(0, np.pi), density=True)
    mid = 0.5 * (edges[1:] + edges[:-1])
    st = (2 / np.pi) * np.sin(mid) ** 2
    print("theta histogram vs sin^2 density (p=%d):" % p)
    for h, s in zip(hist, st):
        print("   %.3f  vs  %.3f" % (h, s))
    # 5. wander scale
    print("max over a of max_t |partial|/sqrt(p) =", np.abs(paths).max())
    print("mean over a of max_t |partial| =", np.abs(paths).max(axis=1).mean())
