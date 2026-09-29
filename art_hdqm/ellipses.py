"""Unit-perimeter ellipses (MO 515557) — envelope via Euler homogeneity.
Family x^2/a^2 + y^2/b^2 = 1 with P(a,b) = 1.  Envelope condition + Euler (aP_a + bP_b = P = 1)
gives the touching point  x^2/a^2 = a P_a,  y^2/b^2 = b P_b   (u+v = 1 automatically).
P_a = int_0^{2pi} a sin^2 t / sqrt(a^2 sin^2 t + b^2 cos^2 t) dt  (complete elliptic integrals)."""
import numpy as np
from scipy.special import ellipe, ellipk
from scipy.optimize import brentq
t = np.linspace(0, 2 * np.pi, 20001)[:-1]
def P(a, b): return np.mean(np.sqrt((a * np.sin(t)) ** 2 + (b * np.cos(t)) ** 2)) * 2 * np.pi
def Pa(a, b): return np.mean(a * np.sin(t) ** 2 / np.sqrt((a * np.sin(t)) ** 2 + (b * np.cos(t)) ** 2 + 1e-300)) * 2 * np.pi
def Pb(a, b): return np.mean(b * np.cos(t) ** 2 / np.sqrt((a * np.sin(t)) ** 2 + (b * np.cos(t)) ** 2 + 1e-300)) * 2 * np.pi
def family(n):
    """a from 1/(2pi) (circle) to 1/4 (segment); b solves P=1"""
    out = []
    for s in np.linspace(0, 1, n):
        # parametrise by k = b/a in [1 -> 0]; scale so P = 1 (P homogeneous of degree 1)
        k = 1 - s
        p = P(1.0, k)
        out.append((1 / p, k / p))
    return np.array(out)
def envelope(n):
    F = family(n); pts = []
    for a, b in F:
        u, v = a * Pa(a, b), b * Pb(a, b)
        pts.append((a * np.sqrt(max(u, 0)), b * np.sqrt(max(v, 0))))
    return F, np.array(pts)
if __name__ == '__main__':
    F, E = envelope(41)
    print('u+v check', max(abs(a * Pa(a, b) + b * Pb(a, b) - 1) for a, b in F[:-1]))
    # brute-force: union radial function in direction theta vs envelope point direction
    FF = family(4001)
    for (x, y) in E[1:-1:6]:
        th = np.arctan2(y, x)
        c, s_ = np.cos(th), np.sin(th)
        r = 1 / np.sqrt((c / FF[:, 0]) ** 2 + (s_ / np.maximum(FF[:, 1], 1e-9)) ** 2)
        print(f'theta {np.degrees(th):6.2f}  envelope r {np.hypot(x, y):.6f}  union max r {r.max():.6f}')
    # compare with astroid-like (a+b = const) guess: x^(2/3)+y^(2/3)
    print('x^(2/3)+y^(2/3) along envelope:', np.round((E[:, 0] ** (2 / 3) + E[:, 1] ** (2 / 3)), 5)[::5])
