"""xi.py — the Riemann Xi function and its Weyl fractional derivatives.
Xi(t) = xi(1/2 + i t) = 2 * int_0^inf Phi(u) cos(u t) du,
Phi(u) = sum_n (2 pi^2 n^4 e^{9u/2} - 3 pi n^2 e^{5u/2}) exp(-pi n^2 e^{2u}).
Weyl derivative of order s (Fourier multiplier (iu)^s):
D^s Xi(t) = 2 * int_0^inf Phi(u) u^s cos(u t + s pi/2) du.
Riesz variant (multiplier |u|^s): 2 * int Phi u^s cos(ut) du (even in t)."""
import numpy as np

U = 4.0
DU = 2.5e-5
u = np.arange(0, U + DU / 2, DU)

def Phi(u):
    out = np.zeros_like(u)
    for n in range(1, 8):
        e2 = np.exp(2 * u)
        out += (2 * np.pi ** 2 * n ** 4 * np.exp(4.5 * u) - 3 * np.pi * n ** 2 * np.exp(2.5 * u)) * np.exp(-np.pi * n ** 2 * e2)
    return out

PH = Phi(u)
W = np.full_like(u, DU); W[0] = W[-1] = DU / 2   # trapezoid

def D(s, t, kind='weyl'):
    """D^s Xi at points t (array), vectorised over t in blocks."""
    t = np.atleast_1d(np.asarray(t, np.float64))
    k = 2 * PH * W * (u ** s if s != 0 else 1.0)
    ph = s * np.pi / 2 if kind == 'weyl' else 0.0
    out = np.empty_like(t)
    B = 2000
    for i in range(0, len(t), B):
        tb = t[i:i + B]
        out[i:i + B] = np.cos(np.outer(tb, u) + ph) @ k
    return out

def Dt(s, t, kind='weyl'):
    """d/dt of D^s Xi"""
    t = np.atleast_1d(np.asarray(t, np.float64))
    k = 2 * PH * W * u ** (s + 1)
    ph = s * np.pi / 2 if kind == 'weyl' else 0.0
    out = np.empty_like(t)
    B = 2000
    for i in range(0, len(t), B):
        tb = t[i:i + B]
        out[i:i + B] = -np.sin(np.outer(tb, u) + ph) @ k
    return out

def zeros(s, tmin, tmax, dt=0.05, kind='weyl', iters=6):
    tg = np.arange(tmin, tmax + dt, dt)
    f = D(s, tg, kind)
    sc = np.where(np.sign(f[:-1]) * np.sign(f[1:]) < 0)[0]
    a, b = tg[sc], tg[sc + 1]
    fa, fb = f[sc], f[sc + 1]
    for _ in range(iters):            # regula falsi / bisection hybrid
        m = 0.5 * (a + b)
        fm = D(s, m, kind)
        left = np.sign(fm) == np.sign(fa)
        a = np.where(left, m, a); fa = np.where(left, fm, fa)
        b = np.where(left, b, m); fb = np.where(left, fb, fm)
    z = 0.5 * (a + b)
    # Newton polish
    for _ in range(3):
        z = z - D(s, z, kind) / Dt(s, z, kind)
    return z

if __name__ == '__main__':
    import time
    t0 = time.time()
    print('Xi(0)=', D(0, 0.0), 'expect 0.4971207781')
    z = zeros(0, 0, 60)
    print('zeros of Xi below 60:', np.round(z, 6))
    print('expect 14.134725 21.022040 25.010858 30.424876 32.935062 37.586178 40.918719 43.327073 48.005151 49.773832 52.970321 56.446248 59.347044')
    print('Xi\'(t) zeros (s=1):', np.round(zeros(1, -5, 60), 4))
    print('time', time.time() - t0)
