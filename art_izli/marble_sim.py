"""Kelvin-Helmholtz vortex-sheet roll-up (Krasny delta-regularized
Birkhoff-Rott) -> stored velocity frames for marbling advection.

Sheet: y=0, periodic in x with period 2pi, N point vortices of equal
circulation, initial perturbation a*sin(x).  Periodic BR kernel:
  conj(v)(z) = (Gamma_j/(4 pi i)) * sum_j cot((z - z_j)/2)   (delta-smoothed)
Krasny smoothing: replace cot by the delta-blob periodic kernel
  u - i v = (1/(4 pi)) sum G_j * (sin(y..)..)/ (cosh(dy) - cos(dx) + delta^2)
Diagnostics: total circulation conserved trivially; check centroid drift and
delta-refinement convergence of the spiral tip.

Velocity frames on a grid are stored every ksave steps for semi-Lagrangian
backward pigment advection at render time.
"""
import numpy as np, time, json

def velocity(z_eval_x, z_eval_y, xv, yv, gam, delta2):
    """Periodic Krasny-blob induced velocity at eval points.  Chunked over
    BOTH eval points and vortices so peak temp stays ~100MB."""
    u = np.zeros_like(z_eval_x); v = np.zeros_like(z_eval_x)
    EB, CH = 4096, 4096
    for e0 in range(0, len(z_eval_x), EB):
        ex = z_eval_x[e0:e0 + EB]; ey = z_eval_y[e0:e0 + EB]
        uu = np.zeros_like(ex); vv = np.zeros_like(ex)
        for i0 in range(0, len(xv), CH):
            dx = ex[:, None] - xv[None, i0:i0 + CH]
            dy = ey[:, None] - yv[None, i0:i0 + CH]
            den = np.cosh(dy) - np.cos(dx) + delta2
            g = gam[None, i0:i0 + CH] / den
            uu += -(1 / (4 * np.pi)) * np.sum(g * np.sinh(dy), axis=1)
            vv += (1 / (4 * np.pi)) * np.sum(g * np.sin(dx), axis=1)
        u[e0:e0 + EB] = uu; v[e0:e0 + EB] = vv
    return u, v

def run(N=2200, delta=0.10, dt=0.0125, T=3.6, amp=0.02, grid=320,
        yspan=2.4, ksave=5, tag='a'):
    t0 = time.time()
    s = np.linspace(0, 2 * np.pi, N, endpoint=False)
    xv = s + amp * np.sin(s)      # slight clustering with the perturbation
    yv = -amp * np.sin(s)
    gam = np.full(N, 2 * np.pi / N)      # total circulation 2pi per period
    delta2 = delta * delta
    nst = int(round(T / dt))
    gx = np.linspace(0, 2 * np.pi, grid, endpoint=False)
    gy = np.linspace(-yspan, yspan, grid)
    GX, GY = np.meshgrid(gx, gy)
    frames = []
    sheet_snaps = []
    for k in range(nst + 1):
        if k % ksave == 0:
            u, v = velocity(GX.ravel(), GY.ravel(), xv, yv, gam, delta2)
            frames.append(np.stack([u.reshape(grid, grid),
                                    v.reshape(grid, grid)]).astype(np.float32))
            sheet_snaps.append(np.stack([xv, yv]).astype(np.float32))
        # RK4 on the sheet itself
        def rhs(x, y):
            u, v = velocity(x, y, x, y, gam, delta2)   # self-induction (blob)
            return u, v
        k1 = rhs(xv, yv)
        k2 = rhs(xv + 0.5 * dt * k1[0], yv + 0.5 * dt * k1[1])
        k3 = rhs(xv + 0.5 * dt * k2[0], yv + 0.5 * dt * k2[1])
        k4 = rhs(xv + dt * k3[0], yv + dt * k3[1])
        xv = xv + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        yv = yv + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        if k % 60 == 0:
            print(f"  step {k}/{nst} ymax={np.abs(yv).max():.3f} "
                  f"[{time.time()-t0:.0f}s]", flush=True)
    frames = np.stack(frames)          # (F, 2, grid, grid)
    np.save(f'marble_frames_{tag}.npy', frames)
    np.save(f'marble_sheet_{tag}.npy', np.stack(sheet_snaps))
    meta = dict(N=N, delta=delta, dt=dt, T=T, amp=amp, grid=grid,
                yspan=float(yspan), ksave=ksave,
                centroid_y_drift=float(np.mean(yv)),
                ymax=float(np.abs(yv).max()))
    json.dump(meta, open(f'marble_meta_{tag}.json', 'w'))
    print("meta:", meta)
    return meta

if __name__ == '__main__':
    import sys
    tag = sys.argv[1] if len(sys.argv) > 1 else 'a'
    if tag == 'conv':
        # delta-refinement convergence check on the roll-up core position
        for dl in (0.14, 0.10, 0.07):
            s = run(N=1200, delta=dl, dt=0.02, T=2.0, grid=64, ksave=1000,
                    tag=f'c{int(dl*100)}')
    else:
        run(tag=tag)
