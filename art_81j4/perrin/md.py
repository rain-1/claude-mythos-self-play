# md.py — 2-D WCA molecular dynamics: N small atoms (diam 1, mass 1) + M pollen grains (radius RB, mass ∝ area),
# periodic box, velocity Verlet, Berendsen-free (NVE after a short thermostat). Saves grain positions every 'every'
# steps (unwrapped) and one final snapshot of all atoms.
import numpy as np, numba as nb, sys, time
@nb.njit(cache=True)
def forces(x, rad, L, nsmall, ncell, cs, head, nxt, F):
    N = x.shape[0]; F[:] = 0.0; U = 0.0
    # cell list for small atoms
    head[:] = -1
    for i in range(nsmall):
        cx = int(x[i, 0] / cs) % ncell; cy = int(x[i, 1] / cs) % ncell
        nxt[i] = head[cx * ncell + cy]; head[cx * ncell + cy] = i
    # small-small
    for i in range(nsmall):
        cx = int(x[i, 0] / cs) % ncell; cy = int(x[i, 1] / cs) % ncell
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                j = head[((cx + dx) % ncell) * ncell + (cy + dy) % ncell]
                while j >= 0:
                    if j > i:
                        rx = x[i, 0] - x[j, 0]; ry = x[i, 1] - x[j, 1]
                        rx -= L * np.round(rx / L); ry -= L * np.round(ry / L)
                        r2 = rx * rx + ry * ry
                        if r2 < 1.2599210498948732:
                            s2 = 1.0 / r2; s6 = s2 * s2 * s2; f = 24 * s2 * s6 * (2 * s6 - 1)
                            F[i, 0] += f * rx; F[i, 1] += f * ry; F[j, 0] -= f * rx; F[j, 1] -= f * ry
                    j = nxt[j]
    # big-small and big-big (shifted WCA: contact at r = ri + rj, unit-width core)
    for b in range(nsmall, N):
        R = rad[b]; reach = R + 0.5 + 1.2
        nc = int(reach / cs) + 1
        cx = int(x[b, 0] / cs) % ncell; cy = int(x[b, 1] / cs) % ncell
        for dx in range(-nc, nc + 1):
            for dy in range(-nc, nc + 1):
                j = head[((cx + dx) % ncell) * ncell + (cy + dy) % ncell]
                while j >= 0:
                    rx = x[b, 0] - x[j, 0]; ry = x[b, 1] - x[j, 1]
                    rx -= L * np.round(rx / L); ry -= L * np.round(ry / L)
                    r = np.sqrt(rx * rx + ry * ry); h = r - (R + 0.5) + 1.0   # shifted distance
                    if h < 1.122462048309373:
                        if h < 0.6: h = 0.6
                        s2 = 1.0 / (h * h); s6 = s2 * s2 * s2; f = 24 * s6 * (2 * s6 - 1) / h / r
                        F[b, 0] += f * rx; F[b, 1] += f * ry; F[j, 0] -= f * rx; F[j, 1] -= f * ry
                    j = nxt[j]
        for c in range(b + 1, N):
            rx = x[b, 0] - x[c, 0]; ry = x[b, 1] - x[c, 1]
            rx -= L * np.round(rx / L); ry -= L * np.round(ry / L)
            r = np.sqrt(rx * rx + ry * ry); h = r - (rad[b] + rad[c]) + 1.0
            if h < 1.122462048309373:
                if h < 0.6: h = 0.6
                s2 = 1.0 / (h * h); s6 = s2 * s2 * s2; f = 24 * s6 * (2 * s6 - 1) / h / r
                F[b, 0] += f * rx; F[b, 1] += f * ry; F[c, 0] -= f * rx; F[c, 1] -= f * ry
    return U
@nb.njit(cache=True)
def run(x, v, m, rad, L, nsmall, dt, nsteps, every, thermo, seed, traj):
    np.random.seed(seed)
    N = x.shape[0]; cs = 1.13; ncell = int(L / cs); cs = L / ncell
    head = np.empty(ncell * ncell, np.int64); nxt = np.empty(N, np.int64)
    F = np.zeros((N, 2)); forces(x, rad, L, nsmall, ncell, cs, head, nxt, F)
    unw = x[nsmall:].copy(); k = 0
    for step in range(nsteps):
        for i in range(N):
            v[i, 0] += 0.5 * dt * F[i, 0] / m[i]; v[i, 1] += 0.5 * dt * F[i, 1] / m[i]
            dx0 = dt * v[i, 0]; dx1 = dt * v[i, 1]
            x[i, 0] = (x[i, 0] + dx0) % L; x[i, 1] = (x[i, 1] + dx1) % L
            if i >= nsmall: unw[i - nsmall, 0] += dx0; unw[i - nsmall, 1] += dx1
        forces(x, rad, L, nsmall, ncell, cs, head, nxt, F)
        for i in range(N):
            v[i, 0] += 0.5 * dt * F[i, 0] / m[i]; v[i, 1] += 0.5 * dt * F[i, 1] / m[i]
        if step < thermo and step % 50 == 0:   # velocity rescale to kT = 1 (small atoms only)
            ke = 0.0
            for i in range(nsmall): ke += 0.5 * (v[i, 0] ** 2 + v[i, 1] ** 2)
            sc = np.sqrt(nsmall / ke)
            for i in range(nsmall): v[i, 0] *= sc; v[i, 1] *= sc
        if step % every == 0 and k < traj.shape[0]:
            traj[k] = unw; k += 1
    return k
MB = 3.0
if __name__ == "__main__":
    N = int(sys.argv[1]); phi = float(sys.argv[2]); nsteps = int(sys.argv[3]); every = int(sys.argv[4]); out = sys.argv[5]
    radii = [7.0, 5.5, 6.5, 4.5, 8.0, 5.0, 6.0, 7.5, 4.0, 5.5, 6.5, 5.0]
    rng = np.random.default_rng(3)
    L = np.sqrt(N * np.pi * 0.25 / phi + sum(np.pi * r * r for r in radii) * 1.3)
    # place grains on a jittered grid, atoms by rejection
    M = len(radii); g = int(np.ceil(np.sqrt(M))); xb = []
    for i, r in enumerate(radii):
        xb.append(((i % g + 0.5 + 0.3 * rng.uniform(-1, 1)) * L / g, (i // g + 0.5 + 0.3 * rng.uniform(-1, 1)) * L / (int(np.ceil(M / g)))))
    xb = np.array(xb)
    xs = []
    while len(xs) < N:
        p = rng.uniform(0, L, (N, 2))
        d = np.min([np.hypot(*(((p - c + L / 2) % L) - L / 2).T) - r for c, r in zip(xb, radii)], axis=0)
        xs.extend(p[d > 1.0][:N - len(xs)])
    xs = np.array(xs[:N])
    # small atoms start on a lattice-free random set: overlaps resolved by a soft start (capped forces via h>=0.6 for big; small-small: jitter-free)
    # resolve small-small overlaps by a quick grid placement instead
    n1 = int(np.ceil(np.sqrt(N * 1.0))); cand = []
    sp = L / int(L / 1.05); gx = np.arange(0.5 * sp, L, sp)
    G = np.array(np.meshgrid(gx, gx)).reshape(2, -1).T
    d = np.min([np.hypot(*(((G - c + L / 2) % L) - L / 2).T) - r for c, r in zip(xb, radii)], axis=0)
    G = G[d > 1.2]; G = G[rng.permutation(len(G))[:N]]; assert len(G) == N, (len(G), N)
    x = np.vstack([G, xb]).astype(np.float64)
    rad = np.concatenate([np.full(N, 0.5), radii]); m = np.concatenate([np.ones(N), MB * np.array(radii)])
    v = rng.standard_normal((N + M, 2)) / np.sqrt(m)[:, None]
    traj = np.zeros((nsteps // every + 1, M, 2))
    t0 = time.time(); k = run(x, v, m, rad, L, N, 0.005, nsteps, every, 4000, 1, traj)
    print('L', L, 'time', time.time() - t0, 'frames', k)
    np.savez(out, traj=traj[:k], x=x, rad=rad, L=L, dt=0.005 * every)
