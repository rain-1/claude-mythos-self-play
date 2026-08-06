"""MO 513954: inertia of M = D - ww^T/Delta, w = Dx, Delta = x^T D x != 0.
Claim: inertia(M) = (n+ - 1, n-, n0 + 1) if Delta > 0, (n+, n- - 1, n0 + 1) if Delta < 0.

Proof (Sylvester congruence, no D^{-1}):
  H = ker(w^T) has dim n-1 and R^n = H + span{x} since w^T x = Delta != 0.
  With P = [Z x] (Z basis of H):  P^T D P = diag(Z^T D Z, Delta),
                                  P^T M P = diag(Z^T D Z, 0)
  (off-diagonals: Z^T D x = Z^T w = 0; Z^T M x = Z^T w - Z^T w = 0; x^T M x = 0).
  So inertia(D) = inertia(Z^T D Z) + (sign Delta) and
     inertia(M) = inertia(Z^T D Z) + (0,0,1).  QED.

This script: (a) float verification incl. very singular D, n up to 400;
(b) EXACT rational verification via fraction-LDL-style pivoted congruence, n<=9;
(c) iterated cascade: general symmetric M, repeat until M = 0; assert one
    sign-unit dies per step; save eigenvalue-flow data for the render."""
import numpy as np
from fractions import Fraction

rng = np.random.default_rng(20260806)


def inertia_eig(S, tol):
    ev = np.linalg.eigvalsh(S)
    return (int((ev > tol).sum()), int((ev < -tol).sum()), int((np.abs(ev) <= tol).sum()))


# ---------- (a) float check on diagonal D ----------
fails = 0
trials = 0
for it in range(3000):
    n = rng.integers(2, 40)
    nz = rng.integers(0, n)                      # force many exact zeros
    d = np.round(rng.normal(0, 3, n), 2)
    d[rng.choice(n, nz, replace=False)] = 0.0
    if it % 3 == 0:
        d = np.round(d)                          # integer diagonals, more degeneracy
    x = np.round(rng.normal(0, 2, n), 2)
    D = np.diag(d)
    Delta = float(x @ (d * x))
    if abs(Delta) < 1e-9:
        continue
    trials += 1
    w = d * x
    M = D - np.outer(w, w) / Delta
    scale = max(1.0, np.abs(d).max())
    tol = 1e-8 * scale * n
    iD = (int((d > 0).sum()), int((d < 0).sum()), int((d == 0).sum()))
    iM = inertia_eig(M, tol)
    want = (iD[0] - 1, iD[1], iD[2] + 1) if Delta > 0 else (iD[0], iD[1] - 1, iD[2] + 1)
    if iM != want:
        fails += 1
        if fails < 5:
            print("FAIL", d, x, Delta, iD, iM, want)
print(f"(a) diagonal float check: {trials} trials, {fails} failures")
assert fails == 0

# big n
for n in [200, 400]:
    d = np.round(rng.normal(0, 3, n), 1)
    d[rng.choice(n, n // 3, replace=False)] = 0.0
    x = rng.normal(0, 1, n)
    Delta = float(x @ (d * x))
    w = d * x
    M = np.diag(d) - np.outer(w, w) / Delta
    iD = (int((d > 0).sum()), int((d < 0).sum()), int((d == 0).sum()))
    iM = inertia_eig(M, 1e-7 * n)
    want = (iD[0] - 1, iD[1], iD[2] + 1) if Delta > 0 else (iD[0], iD[1] - 1, iD[2] + 1)
    assert iM == want, (n, iD, iM, want)
print("(a) n=200,400 with n/3 zero diagonal: OK")


# ---------- (b) exact rational inertia via recursive congruence ----------
def exact_inertia_schur(S):
    """clean implementation: Schur-complement recursion with Fractions."""
    n = len(S)
    if n == 0:
        return (0, 0, 0)
    # nonzero diagonal pivot
    for p in range(n):
        if S[p][p] != 0:
            a = S[p][p]
            rest = [i for i in range(n) if i != p]
            T = [[S[i][j] - S[i][p] * S[p][j] / a for j in rest] for i in rest]
            sp, sn, sz = exact_inertia_schur(T)
            return (sp + (1 if a > 0 else 0), sn + (1 if a < 0 else 0), sz)
    # all-zero diagonal: off-diagonal pivot
    for i in range(n):
        for j in range(i + 1, n):
            if S[i][j] != 0:
                b = S[i][j]
                rest = [k for k in range(n) if k not in (i, j)]
                # Schur complement of [[0,b],[b,0]]: T[k][l] = S[k][l]
                #  - (S[k][i]*S[j][l] + S[k][j]*S[i][l])/b
                T = [[S[k][l] - (S[k][i] * S[j][l] + S[k][j] * S[i][l]) / b
                      for l in rest] for k in rest]
                sp, sn, sz = exact_inertia_schur(T)
                return (sp + 1, sn + 1, sz)
    return (0, 0, n)


ex_trials = 0
for it in range(400):
    n = int(rng.integers(2, 9))
    d = [Fraction(int(rng.integers(-4, 5)), int(rng.integers(1, 4))) for _ in range(n)]
    for k in range(int(rng.integers(0, n))):
        d[int(rng.integers(0, n))] = Fraction(0)
    x = [Fraction(int(rng.integers(-4, 5)), int(rng.integers(1, 4))) for _ in range(n)]
    Delta = sum(xi * di * xi for xi, di in zip(x, d))
    if Delta == 0:
        continue
    ex_trials += 1
    w = [di * xi for di, xi in zip(d, x)]
    M = [[(Fraction(1) if i == j else Fraction(0)) * d[i] - w[i] * w[j] / Delta
          for j in range(n)] for i in range(n)]
    iD = (sum(1 for v in d if v > 0), sum(1 for v in d if v < 0), sum(1 for v in d if v == 0))
    iM = exact_inertia_schur(M)
    want = (iD[0] - 1, iD[1], iD[2] + 1) if Delta > 0 else (iD[0], iD[1] - 1, iD[2] + 1)
    assert iM == want, (d, x, Delta, iD, iM, want)
print(f"(b) EXACT rational check: {ex_trials} trials, all pass")

# ---------- (c) iterated cascade on general symmetric M (for the render) ----------
def cascade(M0, rng, steps=None, record_flow=None, s_samples=33):
    """iterate M <- M - (Mx)(Mx)^T/(x^T M x) with random unit x (resample if
    |Delta| tiny); returns list of per-step dicts; record_flow: if not None,
    append (stage, s_grid, eigenvalue matrix (s_samples x n))."""
    M = M0.copy()
    n = M.shape[0]
    out = []
    r = np.linalg.matrix_rank(M, tol=1e-9)
    step = 0
    while r > 0:
        step += 1
        for _ in range(200):
            x = rng.normal(0, 1, n)
            x /= np.linalg.norm(x)
            Delta = float(x @ M @ x)
            if abs(Delta) > 1e-6 * np.abs(np.linalg.eigvalsh(M)).max():
                break
        w = M @ x
        P = np.outer(w, w) / Delta
        if record_flow is not None:
            sg = np.linspace(0, 1, s_samples)
            evs = np.array([np.linalg.eigvalsh(M - s * P) for s in sg])
            record_flow.append((step, sg, evs))
        i0 = inertia_eig(M, 1e-8 * n)
        M = M - P
        M = (M + M.T) / 2
        i1 = inertia_eig(M, 1e-8 * n)
        want = (i0[0] - 1, i0[1], i0[2] + 1) if Delta > 0 else (i0[0], i0[1] - 1, i0[2] + 1)
        ok = (i1 == want)
        out.append(dict(step=step, Delta=Delta, i0=i0, i1=i1, ok=ok))
        assert ok, (step, Delta, i0, i1, want)
        r -= 1
        if steps and step >= steps:
            break
    return out, M

if __name__ == "__main__":
    # verify the cascade drains exactly rank steps, mixed signature start
    n = 60
    Q, _ = np.linalg.qr(rng.normal(0, 1, (n, n)))
    lam = np.concatenate([rng.uniform(0.5, 3, 35), -rng.uniform(0.5, 3, 20), np.zeros(5)])
    M0 = (Q * lam) @ Q.T
    hist, Mend = cascade(M0, rng)
    assert len(hist) == 55 and np.abs(Mend).max() < 1e-6
    print(f"(c) cascade: rank-55 mixed matrix drained to 0 in exactly 55 replacements, "
          f"inertia law verified at every step; final |M|max = {np.abs(Mend).max():.2e}")
    print("ALL INERTIA CHECKS PASSED")
