"""Numerics for MO 392723: sum_k W(a_k; others) = 1.
Single core: set OMP_NUM_THREADS=1 before numpy import."""
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import numpy as np
from scipy import integrate, special

rng = np.random.default_rng(12345)


# ---------- exact-ish W via Bessel integral -------------------------------
def W_bessel(b, others, T=4000.0):
    """b * int_0^inf J1(bt) prod J0(a t) dt, integrated piecewise to T + tail ignored."""
    f = lambda t: b * special.j1(b * t) * np.prod([special.j0(a * t) for a in others], axis=0)
    # piecewise Gauss-Legendre on [0,T], panels of length 0.5
    x, w = np.polynomial.legendre.leggauss(40)
    edges = np.arange(0.0, T + 1e-12, 0.5)
    lo, hi = edges[:-1, None], edges[1:, None]
    t = 0.5 * (hi - lo) * x[None, :] + 0.5 * (hi + lo)
    return float(np.sum(f(t) * 0.5 * (hi - lo) * w[None, :]))


# ---------- W via angle quadrature (independent method) -------------------
def W_angles(b, others, N=2000):
    """Fix U_1 = 1 (rotation invariance); average over the remaining angles
    except the last on an N-point periodic grid; last angle in closed form."""
    others = list(others)
    aL = others[-1]
    rest = others[:-1]
    if len(rest) == 0:
        r = np.array([0.0])
        Z = np.array([0.0 + 0j])
    else:
        th = 2 * np.pi * np.arange(N) / N
        Z = np.array([rest[0] + 0j])
        for a in rest[1:]:
            Z = (Z[:, None] + a * np.exp(1j * th)[None, :]).ravel()
    r = np.abs(Z)
    with np.errstate(divide="ignore", invalid="ignore"):
        c = (b * b - r * r - aL * aL) / (2 * aL * r)
    c = np.where(r == 0, np.where(aL < b, 2.0, -2.0), c)
    p = np.where(c >= 1, 1.0, np.where(c <= -1, 0.0, 1 - np.arccos(np.clip(c, -1, 1)) / np.pi))
    return float(p.mean())


def all_W(a, method):
    a = list(a)
    return [method(a[k], a[k + 1:] + a[:k]) for k in range(len(a))]


# ---------- Monte Carlo on events E_k ------------------------------------
def unit_vectors(M, m, d):
    if d == 2:
        th = rng.uniform(0, 2 * np.pi, (M, m))
        return np.stack([np.cos(th), np.sin(th)], -1)
    g = rng.standard_normal((M, m, d))
    return g / np.linalg.norm(g, axis=-1, keepdims=True)


def mc(a, d=2, M=2_000_000, chunks=5):
    a = np.asarray(a, float)
    m = len(a)
    acc = dict(PE=np.zeros(m), Pjk=np.zeros((m, m)), cnt=np.zeros(m + 1),
               w=np.zeros(m), argmax=np.zeros(m), deepest=np.zeros(m), flux=np.zeros(m),
               invS=0.0)
    for _ in range(chunks):
        U = unit_vectors(M, m, d)
        V = a[None, :, None] * U
        S = V.sum(1)
        S2 = (S * S).sum(-1)
        T = S[:, None, :] - V
        Tn = np.linalg.norm(T, axis=-1)
        E = Tn < a[None, :]
        acc["PE"] += E.mean(0)
        acc["Pjk"] += (E[:, :, None] & E[:, None, :]).mean(0)
        N = E.sum(1)
        acc["cnt"] += np.bincount(N, minlength=m + 1)[: m + 1] / M
        SU = (S[:, None, :] * U).sum(-1)
        w = a[None, :] * SU / S2[:, None]          # 2D partition of unity
        acc["w"] += w.mean(0)
        acc["argmax"] += np.bincount(w.argmax(1), minlength=m) / M
        acc["deepest"] += np.bincount((Tn / a[None, :]).argmin(1), minlength=m) / M
        acc["flux"] += (a[None, :] ** (d - 1) * SU / S2[:, None] ** (d / 2)).mean(0)
        acc["invS"] += (S2 ** ((2 - d) / 2)).mean()
    return {k: v / chunks for k, v in acc.items()}


def W3_sinc(b, others):
    """d=3: P(|sum|<b) = (2/pi) int (sin bt - bt cos bt)/t prod sinc(a t) dt."""
    def f(t):
        s = np.sin(b * t) - b * t * np.cos(b * t)
        return s / t * np.prod([np.sinc(a * t / np.pi) for a in others], axis=0)
    x, w = np.polynomial.legendre.leggauss(40)
    edges = np.arange(1e-9, 3000.0, 0.5)
    lo, hi = edges[:-1, None], edges[1:, None]
    t = 0.5 * (hi - lo) * x[None, :] + 0.5 * (hi + lo)
    return float(2 / np.pi * np.sum(f(t) * 0.5 * (hi - lo) * w[None, :]))


if __name__ == "__main__":
    np.set_printoptions(precision=5, suppress=True, linewidth=150)
    vecs = [(1, 1, 1), (1.0, 0.8, 0.3), (2.0, 1.0, 0.7, 0.5), (1, 1, 1, 1),
            (1.0, 0.85, 0.7, 0.55, 0.4), (3.0, 1, 1, 1)]
    print("=== d=2: exact W (Bessel / angle quadrature) and Monte Carlo ===")
    for a in vecs:
        Wb = all_W(a, W_bessel)
        Wa = all_W(a, W_angles if len(a) <= 4 else (lambda b, o: W_angles(b, o, N=2000)))
        r = mc(a, d=2, M=1_000_000, chunks=4)
        print("a =", a)
        print("  W_bessel ", np.array(Wb), " sum", sum(Wb))
        print("  W_angles ", np.array(Wa), " sum", sum(Wa))
        print("  MC P(E_k)", r["PE"], " sum", r["PE"].sum())
        print("  MC E[w_k]", r["w"], " sum", r["w"].sum())
        print("  P(N=j), j=0..", r["cnt"], " E[N]", (np.arange(len(a) + 1) * r["cnt"]).sum())
        print("  P(E_j & E_k):\n", r["Pjk"])
        print("  P(argmax w = k)", r["argmax"], "  P(argmin |T_k|/a_k = k)", r["deepest"])
    print("\n=== d=3 ===")
    for a in [(1, 1, 1), (1.0, 0.8, 0.3), (1.0, 0.85, 0.7, 0.55, 0.4), (1, 1, 1, 1)]:
        r = mc(a, d=3, M=1_000_000, chunks=4)
        al = list(a)
        W3 = [W3_sinc(al[k], al[k + 1:] + al[:k]) for k in range(len(al))]
        Einv = W3_sinc_inv = 2 / np.pi * integrate.quad(
            lambda t: np.prod([np.sinc(x * t / np.pi) for x in al]), 0, np.inf, limit=2000)[0]
        print("a =", a)
        print("  MC P(E_k)", r["PE"], " sum", r["PE"].sum(), "  exact", np.array(W3), "sum", sum(W3))
        lhs = sum(W3[k] / al[k] for k in range(len(al)))
        print("  sum a_k^{-1} P(E_k) =", lhs, "  E|S|^{-1}: exact", Einv, " MC", r["invS"])
        print("  MC flux E[a^2 S.U/|S|^3]", r["flux"], " (should equal P(E_k))")
    print("\n=== d=4 ===")
    for a in [(1, 1, 1), (1.0, 0.85, 0.7, 0.55, 0.4)]:
        r = mc(a, d=4, M=1_000_000, chunks=4)
        al = np.array(a, float)
        print("a =", a, " MC P(E_k)", r["PE"], "sum", r["PE"].sum(),
              " sum a^-2 P(E_k)", (r["PE"] / al ** 2).sum(), " E|S|^-2", r["invS"])
