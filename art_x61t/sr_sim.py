"""Stochastic resonance field: overdamped double well + subthreshold sine, noise sweep.

  dx = (x - x^3 + A sin(W t)) dt + sqrt(2 D) dW,   A = 0.25 < A_c = 0.385
Rows: noise D log-swept. Per row an ensemble of M walkers (all start in the
left well). Field = P(right well)(D, t). Also records per-row coherence
(power of <x>(t) at the drive frequency, relative) and a few witness paths.

Kramers matching 2 r_K = W  ->  D* ~ 0.14 for period 80.

Usage: python3 sr_sim.py [rows] [cols] [M] [out_tag]
"""
import numpy as np, sys, time

t0 = time.time()
R    = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
C    = int(sys.argv[2]) if len(sys.argv) > 2 else 2560
M    = int(sys.argv[3]) if len(sys.argv) > 3 else 64
TAG  = sys.argv[4] if len(sys.argv) > 4 else ""

A, PER = 0.14, 80.0
W = 2*np.pi/PER
NPER = 10
dt = 0.02
burn = int(2*PER/dt)
steps = int(NPER*PER/dt)                 # 40k for NPER=10
rec_every = max(steps//C, 1)

D = np.logspace(-2.5, 0, R).astype(np.float32)   # rows: quiet (top) -> storm
sig = np.sqrt(2*D*dt)[:, None]                   # [R,1]

rng = np.random.default_rng(5)
x = np.full((R, M), -1.0, dtype=np.float32)
field = np.zeros((R, C), dtype=np.float32)
meanx = np.zeros((R, C), dtype=np.float32)
sing  = np.zeros((R, C), dtype=np.float32)   # one walker per row: honest SR observable

# witness rows: quiet, resonant, loud
wit_rows = [int(R*0.18), int(np.searchsorted(D, 0.14)), int(R*0.93)]
wit = np.zeros((len(wit_rows), C), dtype=np.float32)

t = -burn*dt
for s in range(-burn, steps):
    drive = A*np.sin(W*t)
    x += (x - x*x*x + drive)*dt + sig*rng.standard_normal((R, M), dtype=np.float32)
    t += dt
    if s >= 0 and s % rec_every == 0:
        c = s//rec_every
        if c < C:
            field[:, c] = (x > 0).mean(axis=1)
            meanx[:, c] = x.mean(axis=1)
            sing[:, c] = x[:, 0]
            for k, wr in enumerate(wit_rows):
                wit[k, c] = x[wr, 0]
    if s % 4000 == 0:
        print(f"step {s}/{steps} {time.time()-t0:.1f}s", flush=True)

# per-row SNR of a SINGLE trajectory at the drive bin vs local background (classic SR)
two = np.sign(sing)                        # two-state (hop) signal: classic SR
F = np.fft.rfft(two - two.mean(axis=1, keepdims=True), axis=1)
P = np.abs(F)**2
tot_time = C*rec_every*dt
kbin = int(round(W/(2*np.pi)*tot_time))
sigpow = P[:, kbin-1:kbin+2].sum(axis=1)
bg = np.median(np.concatenate([P[:, max(kbin-14,1):kbin-2], P[:, kbin+3:kbin+15]], axis=1),
               axis=1)*3 + 1e-12
coh = sigpow/bg

np.savez_compressed(f"art_x61t/data/sr_field{TAG}.npz",
                    field=field, meanx=meanx, coh=coh, D=D,
                    wit=wit, wit_rows=np.array(wit_rows), A=A, PER=PER)
print(f"saved. D*={D[np.argmax(coh)]:.3f}  {time.time()-t0:.1f}s")
