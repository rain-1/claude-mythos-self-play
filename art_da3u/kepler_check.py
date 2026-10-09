"""Rolling shutter of a thin radial blade = Kepler's equation.
Centre at the frame origin row y0; row y read at time (y)/H; blade angle a(t)=a0+2*pi*k*t.
Point (r,phi) is on the blade iff phi = a0 + 2*pi*k*(y0 + r sin phi)/H  (mod 2pi/N)
  <=> phi - e sin(phi) = M,  e = 2*pi*k*r/H,  M = a0 + 2*pi*k*y0/H.
Mean (over M) number of blade points on the circle of radius r:
  N/(2pi) * int_0^{2pi} |1 - e cos phi| dphi = N                                  (e<=1)
                                             = N(1 - 2acos(1/e)/pi + 2 sqrt(e^2-1)/pi)  (e>1)"""
import numpy as np
def count(e, M, N, n=200000):
    phi = np.linspace(0, 2*np.pi, n, endpoint=False)
    g = (phi - e*np.sin(phi) - M) * N/(2*np.pi)       # blade crossings = integer crossings of g
    fl = np.floor(g); fl2 = np.roll(fl, -1); fl2[-1] = np.floor(g[0] + N) # wrap adds N (one full period of phi)
    return np.abs(fl2 - fl).sum()
def formula(e, N):
    return N if e <= 1 else N*(1 - 2*np.arccos(1/e)/np.pi + 2*np.sqrt(e*e - 1)/np.pi)
rng = np.random.default_rng(1)
for N in (1, 5, 6):
    for e in (0.5, 1.0, 1.5, 3.0, 7.0):
        c = np.mean([count(e, rng.uniform(0, 2*np.pi), N) for _ in range(300)])
        print(f'N={N} e={e}: mean crossings {c:.3f}  formula {formula(e,N):.3f}')
