"""kb1d.py — the Kuramoto–Battogtokh (2002) ring chimera, the original one.
θ_t(x) = ω − ∫ G(x−y) sin(θ(x) − θ(y) + α) dy on a ring of length 1, G(x) = (κ/2) e^{−κ|x|}, κ = 4, α = 1.457.
Coexistence of a phase-locked arc and a drifting arc among identical oscillators.
Saves the space–time phase carpet and the mean-frequency profile (the arch)."""
import numpy as np, json, sys, time
def run(N=512, kappa=4.0, alpha=1.457, T=3000.0, dt=0.025, save_last=800.0, seed=1, ic='kb'):
    rng = np.random.default_rng(seed)
    x = (np.arange(N) + 0.5) / N
    d = np.abs(x[:, None] - x[None, :]); d = np.minimum(d, 1 - d)
    G = 0.5 * kappa * np.exp(-kappa * d) / N
    G /= G.sum(1, keepdims=True)
    if ic == 'kb':      # KB's initial condition: phase spread ∝ Gaussian envelope × uniform random
        theta = 6 * np.exp(-30 * (x - 0.5) ** 2) * rng.uniform(-0.5, 0.5, N)
    else:
        theta = rng.uniform(-np.pi, np.pi, N)
    nsteps = int(T / dt); nsave = int(save_last / dt)
    carpet = np.zeros((nsave, N), np.float32); freq = np.zeros(N); nf = 0
    Zs = []
    t0 = time.time()
    for it in range(nsteps):
        def rhs(th):
            Z = G @ np.exp(1j * th)
            return -np.imag(np.exp(1j * (th + alpha)) * np.conj(Z)), Z
        k1, Z = rhs(theta); k2, _ = rhs(theta + 0.5 * dt * k1)
        if it >= nsteps - nsave:
            j = it - (nsteps - nsave); carpet[j] = theta; freq += k2; nf += 1
            if j % 40 == 0: Zs.append(np.abs(Z))
        theta = np.mod(theta + dt * k2 + np.pi, 2 * np.pi) - np.pi
    freq /= nf
    return x, carpet, freq, np.array(Zs)
if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 512
    x, carpet, freq, Zs = run(N=N)
    np.savez_compressed(f'kb1d_{N}.npz', x=x, carpet=carpet, freq=freq, Zs=Zs)
    med = np.median(freq); locked = np.abs(freq - med) < 0.005
    print(f'N={N}: Omega_locked={med:.4f}, locked fraction {locked.mean():.3f}, freq range {freq.min():.3f}..{freq.max():.3f}, mean|Z| locked {Zs[:, locked].mean():.3f} drifting {Zs[:, ~locked].mean():.3f}')
