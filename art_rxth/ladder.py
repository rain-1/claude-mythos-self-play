"""One Curve Beneath Every Ladder — the reciprocal-Pascal family collapses.

Family F(a, e): triangle with A(n,0)=A(n,n)=e and interior
    A(n,k) = a/A(n-1,k-1) + a/A(n-1,k).
Fixed point of the equal-parent map x -> 2a/x is s = sqrt(2a), multiplier -1.

REDUCTION (one-line scaling proof): B = A/lambda satisfies the family rule
with a_B = a/lambda^2 and edge e_B = e/lambda.  Taking lambda = sqrt(2a)
sends every member to the a = 1/2 family (fixed point 1):
    Mbar(a, e) = sqrt(2a) * m(e / sqrt(2a)),
where m(eps) := Mbar(1/2, eps) is THE universal curve, and the mass is
    Mbar = lim_n  [S_n + S_{n+1}]/2 ,   S_n = sum_k (-1)^n (A(n,k) - s).
(The plain average kills the alternating boundary-layer mass; the bulk
deviation obeys d(n,k) ~ Mbar 2^{-n} C(n,k) — the 2026-08-23 law.)

This script: m(e) on a grid (float64, vectorized rows), convergence audit,
anchor check against the 08-23 constant Mbar(1,1)=0.0654503304268973,
exact linear-response slope m'(1) via the derivative triangle, and the
boundary-layer tower ratio -1/3 check.
"""
import numpy as np, json, sys

def mass_curve(e, nrows=4000, a=0.5, track=False):
    """Return (m, layer, err): averaged mass limit, alternating layer mass,
    and a convergence error estimate, for family (a, edge e)."""
    s = np.sqrt(2*a)
    A = np.array([e], dtype=np.float64)
    S = []
    for n in range(1, nrows+1):
        interior = a/A[:-1] + a/A[1:]
        A = np.concatenate(([e], interior, [e])) if n >= 2 else np.array([e, e])
        if n >= nrows-200 or track:
            S.append(((-1)**n) * (A - s).sum())
    S = np.array(S)
    avg = 0.5*(S[:-1] + S[1:])
    m = avg[-1]
    err = abs(avg[-1] - avg[-100]) if len(avg) > 100 else np.inf
    layer = 0.5*(S[-1] - S[-2]) * ((-1)**nrows)   # coefficient of (-1)^n
    return m, layer, err

def slope_at_1():
    """Exact linearization at (a=1/2, e=1): derivative triangle
    D(n,0)=D(n,n)=1, D' = -(D1+D2)/2.  Gauge E=(-1)^n D is plain averaging
    with edges (-1)^n.  Returns lim (T_n+T_{n+1})/2 for T_n = sum_k E(n,k)."""
    E = np.array([1.0])
    T = []
    N = 20000
    for n in range(1, N+1):
        interior = 0.5*(E[:-1] + E[1:])
        sgn = (-1.0)**n
        E = np.concatenate(([sgn], interior, [sgn])) if n >= 2 else np.array([-1.0, -1.0])
        if n >= N-6:
            T.append(E.sum())
    T = np.array(T)
    avg = 0.5*(T[:-1]+T[1:])
    return avg[-1], abs(avg[-1]-avg[0])

if __name__ == "__main__":
    out = {}

    # --- anchor: the 08-23 constant, family (a=1, e=1) directly ---
    m11, lay11, err11 = mass_curve(1.0, nrows=6000, a=1.0)
    print(f"Mbar(a=1,e=1)  direct   = {m11:.16f}  (err~{err11:.1e})")
    print(f"  08-23 reference        = 0.0654503304268973")
    # --- reduction check: sqrt(2)*m(1/sqrt2) must equal it ---
    mr, layr, errr = mass_curve(1/np.sqrt(2), nrows=6000, a=0.5)
    print(f"sqrt2*m(1/sqrt2) reduced = {np.sqrt(2)*mr:.16f}  (err~{errr:.1e})")
    out['anchor_direct'] = m11; out['anchor_reduced'] = np.sqrt(2)*mr

    # --- slope of the universal curve at e=1 ---
    sl, slerr = slope_at_1()
    print(f"m'(1) exact-linear       = {sl:.12f}  (stab {slerr:.1e})")
    out['slope_at_1'] = sl

    # --- boundary tower ratio at e=1 (linear): w_k+1/w_k -> -1/3 ---
    # steady profile of E near edge: E(n,k) ~ (-1)^n w_k
    # (measure from the derivative triangle at large n)
    E = np.array([1.0])
    for n in range(1, 3001):
        interior = 0.5*(E[:-1]+E[1:]); sgn=(-1.0)**n
        E = np.concatenate(([sgn], interior, [sgn])) if n>=2 else np.array([-1.0,-1.0])
    w = E[:8]*((-1)**3000)
    print("layer profile w_k:", " ".join(f"{x:+.6f}" for x in w))
    print("ratios:", " ".join(f"{w[i+1]/w[i]:+.5f}" for i in range(6)))
    out['layer_profile'] = list(w)

    # --- the universal curve on a log grid ---
    es = np.exp(np.linspace(np.log(0.05), np.log(20.0), 241))
    curve = []
    for e in es:
        m, lay, err = mass_curve(float(e), nrows=3000)
        curve.append((float(e), float(m), float(lay), float(err)))
        if len(curve) % 40 == 0:
            print(f"  grid {len(curve)}/241 e={e:.3f} m={m:+.8f}")
    out['curve'] = curve
    json.dump(out, open('ladder_curve.json','w'))
    print("wrote ladder_curve.json")
