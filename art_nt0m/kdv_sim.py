"""Zabusky-Kruskal 1965: u_t + u u_x + delta^2 u_xxx = 0, u(x,0)=cos(pi x), x in [0,2).
delta = 0.022. Pseudospectral + ETDRK4 (Kassam-Trefethen). Saves spacetime field.

Verifies: conservation of M1=int u, M2=int u^2, M3=int (u^3/3 - d^2 u_x^2);
detects breakup time and the near-recurrence.
"""
import numpy as np

N = 2048
L = 2.0
delta = 0.022
x = np.arange(N) * (L / N)
u0 = np.cos(np.pi * x)
k = 2 * np.pi * np.fft.fftfreq(N, d=L / N)   # wavenumbers

# ETDRK4 setup: u_t = L u + N(u),  L = i delta^2 k^3 (from -d^2 u_xxx),
# N(u) = -u u_x = -0.5 d/dx (u^2)  -> in Fourier: -0.5 i k fft(u^2)
Lin = 1j * delta**2 * k**3
dt = 4e-6 * 5   # 2e-5
M = 64
# FULL circle contour, complex means: Lin is purely imaginary (dispersive),
# the diffusive half-circle + real() variant silently breaks conservation.
r = np.exp(2j * np.pi * (np.arange(1, M + 1) - 0.5) / M)
LR = dt * Lin[:, None] + r[None, :]
Q = dt * np.mean((np.exp(LR / 2) - 1) / LR, axis=1)
f1 = dt * np.mean((-4 - LR + np.exp(LR) * (4 - 3 * LR + LR**2)) / LR**3, axis=1)
f2 = dt * np.mean((2 + LR + np.exp(LR) * (-2 + LR)) / LR**3, axis=1)
f3 = dt * np.mean((-4 - 3 * LR - LR**2 + np.exp(LR) * (4 - LR)) / LR**3, axis=1)
E1 = np.exp(dt * Lin)
E2 = np.exp(dt * Lin / 2)

dealias = (np.abs(k) < (2.0 / 3.0) * np.abs(k).max()).astype(float)

def NL(vh):
    u = np.real(np.fft.ifft(vh))
    return dealias * (-0.5j * k * np.fft.fft(u * u))

T_end = 10.8
nsteps = int(T_end / dt)
save_rows = 4400
save_every = max(1, nsteps // save_rows)

vh = np.fft.fft(u0)
rows = [u0.astype(np.float32)]
times = [0.0]
inv = []
def invariants(u):
    ux = np.real(np.fft.ifft(1j * k * np.fft.fft(u)))
    dx = L / N
    return (u.sum() * dx, (u**2).sum() * dx, ((u**3) / 3 - delta**2 * ux**2).sum() * dx)
inv.append(invariants(u0))

for n in range(1, nsteps + 1):
    Nv = NL(vh)
    a = E2 * vh + Q * Nv
    Na = NL(a)
    b = E2 * vh + Q * Na
    Nb = NL(b)
    c = E2 * a + Q * (2 * Nb - Nv)
    Nc = NL(c)
    vh = E1 * vh + Nv * f1 + 2 * (Na + Nb) * f2 + Nc * f3
    if n % save_every == 0:
        u = np.real(np.fft.ifft(vh))
        rows.append(u.astype(np.float32))
        times.append(n * dt)
        if len(rows) % 400 == 0:
            inv.append(invariants(u))
            print("t=%.3f  max u=%.3f  rows=%d" % (n * dt, u.max(), len(rows)), flush=True)

field = np.array(rows)
times = np.array(times)
inv = np.array(inv)
i0 = inv[0]
print("invariant drift: M1 %.2e  M2 %.2e  M3 %.2e" %
      (np.abs(inv[:, 0] - i0[0]).max(),
       np.abs((inv[:, 1] - i0[1]) / i0[1]).max(),
       np.abs((inv[:, 2] - i0[2]) / i0[2]).max()))
# recurrence: correlation with u0, maximized over spatial shifts (FFT xcorr)
F0 = np.conj(np.fft.rfft(u0))
xc = np.fft.irfft(np.fft.rfft(field, axis=1) * F0[None, :], n=N, axis=1)
corr = xc.max(axis=1) / (np.linalg.norm(field, axis=1) * np.linalg.norm(u0))
late = times > 5.0
ir = np.argmax(corr[late])
print("best late-time shift-max correlation with u0: %.4f at t=%.3f (Zabusky: ~30.4/pi=%.3f)" %
      (corr[late][ir], times[late][ir], 30.4 / np.pi))
np.savez_compressed("kdv_field.npz", field=field, times=times, corr=corr)
print("saved kdv_field.npz", field.shape)
