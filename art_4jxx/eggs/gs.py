"""Gray-Scott reaction-diffusion on an icosphere.

    python3 gs.py F k SUB STEPS SEED out.npz

u_t = Du Δu - u v² + F(1-u),  v_t = Dv Δv + u v² - (F+k) v
Δ = (2/3)·graph Laplacian (unit-spacing hex normalisation).  The same two
equations everywhere; only (F, k) differ between eggs.
"""
import sys, numpy as np, scipy.sparse as sp

def icosphere(sub):
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    V = np.array(V, float); V /= np.linalg.norm(V, axis=1)[:, None]
    F = np.array(F)
    for _ in range(sub):
        E = np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1)
        Eu, inv = np.unique(E, axis=0, return_inverse=True)
        mids = V[Eu[:, 0]] + V[Eu[:, 1]]; mids /= np.linalg.norm(mids, axis=1)[:, None]
        nV = len(V); V = np.vstack([V, mids])
        m = inv.reshape(3, -1).T + nV          # mid of (0,1),(1,2),(2,0)
        a, b, c = F[:, 0], F[:, 1], F[:, 2]
        ab, bc, ca = m[:, 0], m[:, 1], m[:, 2]
        F = np.concatenate([np.stack([a, ab, ca], 1), np.stack([b, bc, ab], 1),
                            np.stack([c, ca, bc], 1), np.stack([ab, bc, ca], 1)])
    return V, F

def laplacian(V, F):
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    E = np.unique(np.sort(E, axis=1), axis=0)
    n = len(V)
    A = sp.coo_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
    deg = np.asarray(A.sum(1)).ravel()
    return (2 / 3) * (A - sp.diags(deg)).tocsr()

def run(Fr, k, sub, steps, seed, Du=0.16, Dv=0.08, dt=1.0, scale=1.0):
    # scale>1: finer mesh with the same physical pattern size (D*scale^2, dt/scale^2)
    Du *= scale ** 2; Dv *= scale ** 2; dt /= scale ** 2; steps = int(steps * scale ** 2)
    V, F = icosphere(sub)
    L = laplacian(V, F)
    rng = np.random.default_rng(seed)
    n = len(V)
    u = np.ones(n); v = np.zeros(n)
    # sprinkle ~30 seed patches of radius ~6 cells
    h = np.sqrt(4 * np.pi / n * 2 / np.sqrt(3))
    for _ in range(30):
        c = rng.normal(size=3); c /= np.linalg.norm(c)
        m = np.linalg.norm(V - c, axis=1) < 6 * h * scale * rng.uniform(0.6, 1.4)
        u[m] = 0.5; v[m] = 0.25
    u += rng.normal(size=n) * 0.01; v += rng.normal(size=n) * 0.01
    for s in range(steps):
        uvv = u * v * v
        u = u + dt * (Du * (L @ u) - uvv + Fr * (1 - u))
        v = v + dt * (Dv * (L @ v) + uvv - (Fr + k) * v)
    return V, F, u, v

if __name__ == "__main__":
    Fr, k, sub, steps, seed, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    sc = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
    V, F, u, v = run(Fr, k, sub, steps, seed, scale=sc)
    np.savez_compressed(out, V=V.astype(np.float32), F=F.astype(np.int32), u=u.astype(np.float32), v=v.astype(np.float32), Fk=np.array([Fr, k]))
    print(out, Fr, k, len(V), float(v.min()), float(v.max()), float((v > 0.15).mean()))
