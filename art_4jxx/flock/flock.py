"""A murmuration as a volume-preserving fold.

Birds start uniformly in a thin flattened ellipsoid and are advected by a smooth,
time-varying, DIVERGENCE-FREE velocity field (curl of random Fourier vector
potentials).  Because the flow preserves volume, the 3-D density of birds stays
exactly uniform for all time: every dark band in a picture of the flock is made
by the projection alone (where the folded sheet is seen edge-on).

    python3 flock.py N SEED T out.npy
"""
import sys, numpy as np

def modes(rng, n, kscale, amp):
    k = rng.normal(size=(n, 3)) * kscale
    a = rng.normal(size=(n, 3)) * amp / np.linalg.norm(k, axis=1)[:, None]
    ph = rng.uniform(0, 2 * np.pi, n)
    w = rng.normal(size=n) * 0.6          # temporal frequency of each mode
    return k, a, ph, w

def velocity(P, t, M):
    k, a, ph, w = M
    v = np.zeros_like(P)
    kxa = np.cross(k, a)                   # curl of a*sin(k.x+ph) = (k x a) cos(.)
    for i in range(len(k)):
        c = np.cos(P @ k[i] + ph[i] + w[i] * t)
        v += c[:, None] * kxa[i]
    return v

def make(N=300000, seed=1, T=60, dt=0.05, thick=0.06, shape=(1.6, 0.25, 0.9)):
    mr = np.random.default_rng(seed)       # modes first, independent of N
    M1 = modes(mr, 10, 1.1, 0.55)        # large folds
    M2 = modes(mr, 14, 2.6, 0.22)        # ripples
    M = tuple(np.concatenate([x, y]) for x, y in zip(M1, M2))
    rng = np.random.default_rng(seed + 1000)
    # uniform in an ellipsoid (radii shape), then flattened to a sheet of 'thick'
    u = rng.normal(size=(N, 3)); u /= np.linalg.norm(u, axis=1)[:, None]
    r = rng.uniform(0, 1, N) ** (1 / 3)
    P = u * r[:, None] * np.array(shape)
    P[:, 1] *= thick / shape[1]
    for s in range(T):
        t = s * dt
        k1 = velocity(P, t, M)
        k2 = velocity(P + 0.5 * dt * k1, t + 0.5 * dt, M)
        P = P + dt * k2
    return P.astype(np.float32)

if __name__ == "__main__":
    N, seed, T, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    th = float(sys.argv[5]) if len(sys.argv) > 5 else 0.06
    P = make(N, seed, T, thick=th)
    np.save(out, P)
    print(out, P.min(0), P.max(0))
