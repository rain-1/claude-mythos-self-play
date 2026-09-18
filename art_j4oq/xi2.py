"""xi2.py — Weyl fractional derivatives of the Riemann Xi function by a shifted contour.
I(s,t) = int_0^inf Phi(u) u^s e^{iut} du, path 0 -> i*alpha -> i*alpha + inf (first quadrant, analytic).
D^s Xi(t) (Weyl, multiplier (iu)^s)  = C * 2 Re[ e^{i s pi/2} I(s,t) ]
R^s Xi(t) (Riesz, multiplier |u|^s)  = C * 2 Re[ I(s,t) ]
C = 2 so that Xi(0) = xi(1/2) = 0.4971207781...
The direct real-axis integral loses everything past t ~ 50 (Xi ~ e^{-pi t/4}); the contour
extracts e^{-alpha t} analytically, alpha = pi/4 - eps."""
import numpy as np

ALPHA = np.pi / 4 - 0.035
NMAX = 60

def Phi_c(u):
    """Phi at complex u (array), Re e^{2u} > 0 required"""
    e2 = np.exp(2 * u)
    out = np.zeros_like(u, dtype=np.complex128)
    for n in range(1, NMAX + 1):
        out += (2 * np.pi ** 2 * n ** 4 * np.exp(4.5 * u) - 3 * np.pi * n ** 2 * np.exp(2.5 * u)) * np.exp(-np.pi * n ** 2 * e2)
    return out

def gl_panels(edges, n):
    x, w = np.polynomial.legendre.leggauss(n)
    nodes, wts = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        nodes.append(0.5 * (b - a) * x + 0.5 * (a + b)); wts.append(0.5 * (b - a) * w)
    return np.concatenate(nodes), np.concatenate(wts)

# piece A: u = i y, y in [0, alpha], geometric grading toward 0 (cusp y^s)
edgesA = np.concatenate([[0.0], ALPHA * 2.0 ** (-np.arange(40, -1, -1, dtype=float))])
yA, wA = gl_panels(edgesA, 14)
uA = 1j * yA
PA = Phi_c(uA) * 1j * wA          # du = i dy
# piece B: u = v + i alpha, v in [0, V]
V = 3.4
edgesB = np.arange(0, V + 1e-9, 0.04)
vB, wB = gl_panels(edgesB, 16)
uB = vB + 1j * ALPHA
PB = Phi_c(uB) * wB

def I(s, t):
    """I(s,t) for array t (real or complex). returns complex array"""
    t = np.atleast_1d(np.asarray(t))
    kA = PA * uA ** s
    kB = PB * uB ** s
    out = np.empty(t.shape, np.complex128)
    B = 1500
    for i in range(0, len(t), B):
        tb = t[i:i + B]
        out[i:i + B] = np.exp(1j * np.outer(tb, uA)) @ kA + np.exp(1j * np.outer(tb, uB)) @ kB
    return out

def D(s, t, kind='weyl', deriv=0):
    """D^s Xi(t) (and its t-derivatives)"""
    ph = np.exp(1j * s * np.pi / 2) if kind == 'weyl' else 1.0
    return 2 * 2 * np.real(ph * (1j) ** deriv * I(s + deriv, t))

def D_complex(s, t, kind='weyl', deriv=0):
    """analytic continuation to complex t: the Weyl derivative is the real-analytic function
    2*(ph*I + conj(ph)*conj(I(s, conj t)))... for complex t use I(s,t) and I(s,-conj?) — simplest: 
    D^s Xi(t) = C*[ph*I(s,t) + conj(ph)*J(s,t)], J(s,t)=int Phi u^s e^{-iut} du = conj(I(s, conj(t)))"""
    ph = np.exp(1j * s * np.pi / 2) if kind == 'weyl' else 1.0
    t = np.atleast_1d(np.asarray(t, np.complex128))
    a = I(s + deriv, t) * (1j) ** deriv
    b = np.conj(I(s + deriv, np.conj(t))) * (-1j) ** deriv
    return 2 * (ph * a + np.conj(ph) * b)

def zeros(s, tmin, tmax, dt=0.1, kind='weyl'):
    tg = np.arange(tmin, tmax + dt, dt)
    f = D(s, tg, kind)
    sc = np.where(np.sign(f[:-1]) * np.sign(f[1:]) < 0)[0]
    a, b = tg[sc], tg[sc + 1]; fa, fb = f[sc], f[sc + 1]
    for _ in range(8):
        m = 0.5 * (a + b); fm = D(s, m, kind)
        left = np.sign(fm) == np.sign(fa)
        a = np.where(left, m, a); fa = np.where(left, fm, fa)
        b = np.where(left, b, m); fb = np.where(left, fb, fm)
    z = 0.5 * (a + b)
    for _ in range(3):
        z = z - D(s, z, kind) / D(s, z, kind, deriv=1)
    return z

if __name__ == '__main__':
    import time, mpmath as mp
    mp.mp.dps = 30
    def xi_mp(t):
        s = mp.mpf(1) / 2 + 1j * mp.mpf(t)
        return mp.re(mp.mpf(1) / 2 * s * (s - 1) * mp.pi ** (-s / 2) * mp.gamma(s / 2) * mp.zeta(s))
    t0 = time.time()
    for t in [0, 10, 50, 100, 150, 200, 250, 300]:
        a = D(0, float(t))[0]; b = float(xi_mp(t))
        print(f't={t:4d}  contour {a: .6e}  mpmath {b: .6e}  rel {abs(a-b)/abs(b):.1e}')
    # derivative check: s=1 vs finite difference of s=0
    h = 1e-3
    for t in [20.0, 100.0, 220.0]:
        fd = (D(0, t + h) - D(0, t - h))[0] / (2 * h)
        print('s=1 check', t, D(1, t)[0], fd, D(0, t, deriv=1)[0])
    print('zeros s=0 :', np.round(zeros(0, 0, 80), 6))
    print('zeros s=1 :', np.round(zeros(1, -5, 80), 4))
    print('zeros s=20:', np.round(zeros(20, -40, 80), 3))
    print('zeros s=0.5:', np.round(zeros(0.5, -40, 80), 3))
    print('time', time.time() - t0)
