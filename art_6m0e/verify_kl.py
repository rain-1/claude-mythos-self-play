"""Verification for THE LOOM OF BROWN.

1. Build Brownian bridges the OTHER way (random-walk cumsum, tie down ends),
   project onto sqrt(2) sin(k pi t): coefficient variances must be 1/(k pi)^2
   and coefficients uncorrelated -> verifies the KL basis independently.
2. Reconstruct covariance from the KL synthesis: max |cov - (min(s,t)-st)|.
3. Conditional fog width: empirical std given first m dice vs closed form
   sigma_m(t)^2 = sum_{k>m} 2 sin^2(k pi t)/(k pi)^2.
"""
import numpy as np

T, M = 2048, 4000
tg = (np.arange(T) + 0.5) / T
rng = np.random.default_rng(3)

# 1) random-walk bridges -> KL coefficients
dW = rng.standard_normal((M, T)) / np.sqrt(T)
W = np.cumsum(dW, axis=1)
B = W - tg[None, :] * W[:, -1][:, None]
ks = np.arange(1, 25)
basis = np.sqrt(2) * np.sin(np.outer(ks * np.pi, tg))     # (K,T)
coef = (B @ basis.T) / T                                   # ~ Z_k/(k pi)
emp = coef.var(axis=0) * (ks * np.pi) ** 2
print("coefficient variance x (k pi)^2 (should be ~1):")
print("  k=1..8:", np.round(emp[:8], 3))
C = np.corrcoef(coef[:, :8].T)
off = np.abs(C - np.eye(8)).max()
print(f"max off-diagonal coefficient correlation: {off:.3f} (~1/sqrt(M)={1/np.sqrt(M):.3f})")

# 2) covariance from KL synthesis with K modes
K = 2048
Z = rng.standard_normal((M, K))
kk = np.arange(1, K + 1)
sub = tg[::32]
basK = np.sqrt(2) * np.sin(np.outer(kk * np.pi, sub)) / (kk * np.pi)[:, None]
Bs = Z @ basK
cov = (Bs.T @ Bs) / M
theo = np.minimum.outer(sub, sub) - np.outer(sub, sub)
print(f"KL covariance vs min(s,t)-st: max err {np.abs(cov-theo).max():.4f} "
      f"(MC scale ~{1/np.sqrt(M):.4f})")

# 3) conditional tube width for m known dice
for m in (4, 64):
    tail = Z[:, m:] @ basK[m:]
    emp_sd = tail.std(axis=0)
    theo_sd = np.sqrt((2 * np.sin(np.outer(sub, kk[m:] * np.pi)) ** 2
                       / (kk[m:] * np.pi) ** 2).sum(axis=1))
    r = emp_sd[5:-5] / theo_sd[5:-5]
    print(f"conditional sigma_{m}(t): empirical/theory in [{r.min():.3f},{r.max():.3f}]")
