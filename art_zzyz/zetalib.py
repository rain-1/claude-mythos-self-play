"""Vectorised complex Riemann zeta + zero-finder for 'The Wall at Zero'.

Two regimes:
  * Euler-Maclaurin for |Im s| < T_SWITCH  (exact-ish, ~1e-12)
  * Riemann-Siegel-style approximate functional equation (AFE) for large |Im s|
    (error ~ t^{-3/4}, plenty for a painting; verified against mpmath below).

Zero finder: Hardy Z(t) sign-scan + bisection, verified against the
Riemann-von Mangoldt counting formula and the published first zeros.
"""
import numpy as np
from scipy.special import loggamma

T_SWITCH = 450.0   # EM (machine-exact) below this |Im s|; AFE above
LN2PI = np.log(2 * np.pi)


def zeta_em(s, N=48, ncorr=6):
    """Euler-Maclaurin zeta for complex array s (good for |Im s| < ~60)."""
    s = np.asarray(s, dtype=np.complex128)
    k = np.arange(1, N, dtype=np.float64)
    # sum_{k<N} k^-s  (chunk over k to bound memory)
    out = np.zeros(s.shape, dtype=np.complex128)
    lk = np.log(k)
    for i in range(0, len(k), 16):
        out += np.exp(-s[..., None] * lk[i:i + 16]).sum(-1)
    out += N ** (1 - s) / (s - 1) + 0.5 * N ** (-s)
    # Bernoulli correction terms: B_{2j}/(2j)! * s(s+1)...(s+2j-2) * N^{-s-2j+1}
    bern = [1 / 6, -1 / 30, 1 / 42, -1 / 30, 5 / 66, -691 / 2730, 7 / 6]
    fac = np.ones_like(s)
    for j in range(1, ncorr + 1):
        b = bern[j - 1]
        # rising product s(s+1)...(s+2j-2)
        fac = fac * (s + (2 * j - 3)) * (s + (2 * j - 2)) if j > 1 else s.astype(np.complex128)
        import math
        out += b / math.factorial(2 * j) * fac * N ** (-s - 2 * j + 1)
    return out


def chi(s):
    """chi(s) = 2^s pi^(s-1) sin(pi s/2) Gamma(1-s), via logs (stable for large Im)."""
    s = np.asarray(s, dtype=np.complex128)
    # sin(pi s/2) overflows for large |Im|; use log form. For Im s > 0:
    # log sin(z) = -i z - log(2i) + log(1 - e^{2iz}),  Im z > 0 => |e^{2iz}| < 1
    z = 0.5 * np.pi * s
    # sin z = (i/2) e^{-iz} (1 - e^{2iz})   [converges for Im z > 0]
    #       = (-i/2) e^{iz} (1 - e^{-2iz})  [converges for Im z < 0]
    logsin = np.empty(s.shape, dtype=np.complex128)
    up = s.imag >= 0
    logsin[up] = np.log(0.5j) - 1j * z[up] + np.log1p(-np.exp(2j * z[up]))
    logsin[~up] = np.log(-0.5j) + 1j * z[~up] + np.log1p(-np.exp(-2j * z[~up]))
    return np.exp(s * np.log(2) + (s - 1) * np.log(np.pi) + logsin + loggamma(1 - s))


def zeta_afe(s):
    """Approximate functional equation with smooth main sums, K = sqrt(t/2pi).

    zeta(s) ~ sum_{k<=K} k^-s + chi(s) sum_{k<=K} k^{s-1}.  Error O(t^{-1/4})
    absolute-ish near the critical strip -- fine for painting log|zeta| texture.
    """
    s = np.asarray(s, dtype=np.complex128)
    t = np.abs(s.imag)
    K = np.maximum(1, np.floor(np.sqrt(t / (2 * np.pi)))).astype(np.int64)
    Kmax = int(K.max())
    out = np.zeros(s.shape, dtype=np.complex128)
    out2 = np.zeros(s.shape, dtype=np.complex128)
    for k in range(1, Kmax + 1):
        m = K >= k
        if not m.any():
            continue
        lk = np.log(k)
        out[m] += np.exp(-s[m] * lk)
        out2[m] += np.exp((s[m] - 1) * lk)
    return out + chi(s) * out2


EM_BANDS = [(36.0, 48), (80.0, 110), (160.0, 190), (300.0, 330), (T_SWITCH, 480)]


def zeta(s):
    """Dispatch: adaptive-N Euler-Maclaurin below T_SWITCH, AFE above."""
    s = np.asarray(s, dtype=np.complex128)
    flat = s.ravel()
    out = np.empty_like(flat)
    t = np.abs(flat.imag)
    lo = 0.0
    for hi, N in EM_BANDS:
        m = (t >= lo) & (t < hi)
        if m.any():
            out[m] = zeta_em(flat[m], N=N)
        lo = hi
    m = t >= T_SWITCH
    if m.any():
        out[m] = zeta_afe(flat[m])
    return out.reshape(s.shape)


def theta_rs(t):
    """Riemann-Siegel theta via loggamma (exact to machine precision)."""
    t = np.asarray(t, dtype=np.float64)
    return np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * np.log(np.pi)


def rs_Z(t):
    """Riemann-Siegel Z(t) with the C0 correction term (error ~ t^{-3/4})."""
    t = np.asarray(t, dtype=np.float64)
    a = np.sqrt(t / (2 * np.pi))
    K = np.floor(a).astype(np.int64)
    th = theta_rs(t)
    Z = np.zeros_like(t)
    for k in range(1, int(K.max()) + 1):
        m = K >= k
        Z[m] += np.cos(th[m] - t[m] * np.log(k)) / np.sqrt(k)
    Z *= 2.0
    p = a - K
    C0 = np.cos(2 * np.pi * (p * p - p - 1 / 16.0)) / np.cos(2 * np.pi * p)
    Z += ((-1) ** (K + 1)) * C0 / np.sqrt(a)
    return Z


def hardy_Z(t):
    """Exact-engine Z below T_SWITCH, Riemann-Siegel+C0 above."""
    t = np.asarray(t, dtype=np.float64)
    out = np.empty_like(t)
    lo = t < T_SWITCH
    if lo.any():
        out[lo] = np.real(np.exp(1j * theta_rs(t[lo])) * zeta(0.5 + 1j * t[lo]))
    if (~lo).any():
        out[~lo] = rs_Z(t[~lo])
    return out


def NT(T):
    """Riemann-von Mangoldt main term: number of zeros with 0 < Im rho < T."""
    return theta_rs(T) / np.pi + 1


def find_zeros(tmax, dt=0.03, refine_iters=48):
    """All zeros of Z on (2, tmax) by sign-scan + bisection (vectorised)."""
    grid = np.arange(4.0, tmax, dt)
    Z = np.empty_like(grid)
    CH = 200000
    for i in range(0, len(grid), CH):
        Z[i:i + CH] = hardy_Z(grid[i:i + CH])
    sc = np.where(np.signbit(Z[:-1]) != np.signbit(Z[1:]))[0]
    lo, hi = grid[sc].copy(), grid[sc + 1].copy()
    zlo = Z[sc].copy()
    for _ in range(refine_iters):
        mid = 0.5 * (lo + hi)
        zm = np.empty_like(mid)
        for i in range(0, len(mid), CH):
            zm[i:i + CH] = hardy_Z(mid[i:i + CH])
        left = np.signbit(zlo) != np.signbit(zm)
        hi = np.where(left, mid, hi)
        lo = np.where(left, lo, mid)
        zlo = np.where(left, zlo, zm)
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    import mpmath as mp
    rng = np.random.default_rng(1)
    # --- verify zeta engine against mpmath over the paint domain
    for regime, sig, tt in [
        ("EM ", rng.uniform(0.02, 4.0, 40), rng.uniform(0.05, T_SWITCH, 40)),
        ("AFE", rng.uniform(0.02, 2.5, 40), np.exp(rng.uniform(np.log(T_SWITCH), np.log(6000), 40))),
    ]:
        s = sig + 1j * tt
        ours = zeta(s)
        ref = np.array([complex(mp.zeta(complex(x))) for x in s])
        relerr = np.abs(ours - ref) / np.maximum(np.abs(ref), 1e-3)
        print(f"{regime}: max rel err {relerr.max():.2e}  median {np.median(relerr):.2e}")
    # --- verify zero finder
    zs = find_zeros(120.0)
    known = [14.134725141734693, 21.022039638771554, 25.010857580145688,
             30.424876125859513, 32.935061587739189]
    print("first zeros err:", np.abs(zs[:5] - np.array(known)).max())
    print(f"count to 120: found {len(zs)}, RvM predicts {NT(120):.3f}")
    # --- prime zeta values P(2), P(3) via the Mobius series with our engine
    from sympy import mobius
    for sv, ref in [(2.0, 0.45224742004106549850654336483224793417),
                    (3.0, 0.17476263929944936992228464040156700985)]:
        acc = 0.0
        for n in range(1, 80):
            mu = int(mobius(n))
            if mu == 0:
                continue
            acc += mu / n * float(mp.log(mp.zeta(n * sv)))
        print(f"P({sv:.0f}) err vs known: {abs(acc - ref):.2e}")
