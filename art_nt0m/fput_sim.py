"""Fermi-Pasta-Ulam-Tsingou 1955 (alpha model): N=32 moving masses, fixed ends,
q''_j = (q_{j+1} + q_{j-1} - 2 q_j) + alpha[(q_{j+1}-q_j)^2 - (q_j-q_{j-1})^2],
alpha = 0.25, initial displacement = mode 1, amplitude 1, zero velocity.

Velocity Verlet. Records normal-mode energies E_k(t). Verifies total energy
conservation and detects the famous near-recurrences of mode 1.
"""
import numpy as np

N = 32          # moving masses j=1..N, with q_0 = q_{N+1} = 0
alpha = 0.25
j = np.arange(1, N + 1)
modes = np.arange(1, N + 1)
# normal modes of the linear chain with fixed ends
Smat = np.sqrt(2.0 / (N + 1)) * np.sin(np.pi * np.outer(modes, j) / (N + 1))
omega = 2.0 * np.sin(np.pi * modes / (2.0 * (N + 1)))

A0 = 1.0
q = A0 * np.sin(np.pi * j / (N + 1))
p = np.zeros(N)

def accel(q):
    qp = np.concatenate(([0.0], q, [0.0]))
    d = np.diff(qp)                      # d_i = q_{i+1} - q_i, i=0..N
    lin = d[1:] - d[:-1]
    nl = alpha * (d[1:]**2 - d[:-1]**2)
    return lin + nl

def total_energy(q, p):
    qp = np.concatenate(([0.0], q, [0.0]))
    d = np.diff(qp)
    return 0.5 * (p**2).sum() + (0.5 * d**2 + (alpha / 3.0) * d**3).sum()

dt = 0.02
T_end = 22000.0
record_every = int(round(2.0 / dt))       # every 2 time units -> 11000 rows
nsteps = int(T_end / dt)

rows = []
times = []
E0 = total_energy(q, p)
a = accel(q)
for n in range(nsteps + 1):
    if n % record_every == 0:
        ak = Smat @ q
        vk = Smat @ p
        Ek = 0.5 * (vk**2 + (omega * ak)**2)
        rows.append(Ek.astype(np.float32))
        times.append(n * dt)
    p_half = p + 0.5 * dt * a
    q = q + dt * p_half
    a = accel(q)
    p = p_half + 0.5 * dt * a

rows = np.array(rows)
times = np.array(times)
Ef = total_energy(q, p)
print("total energy drift: %.2e (relative)" % (abs(Ef - E0) / E0))
# recurrences of mode 1
e1 = rows[:, 0] / rows.sum(axis=1)
print("initial mode-1 share: %.4f" % e1[0])
# find local maxima of e1 above 0.8 after t>500
from scipy.signal import find_peaks
pk, _ = find_peaks(e1, height=0.70, distance=50)
pk = pk[times[pk] > 100]
print("near-recurrences (t, mode-1 share):")
for i in pk[:12]:
    print("   t=%8.1f   %.4f" % (times[i], e1[i]))
np.savez_compressed("fput_modes.npz", rows=rows, times=times)
print("saved fput_modes.npz", rows.shape)
