"""scaling2.py — nesting depth vs L with more statistics, plus the box-counting dimension of the walls.

Hypothesis under test (from the Schramm–Sheffield–Wilson law for the log conformal radius of nested
CLE_kappa loops, E[B] = (4 pi/(kappa s0)) tan(pi s0), s0 = |1 - 4/kappa|):
  mean # loops surrounding a typical point  =  ln L / E[B] + const
  Ising spin clusters (kappa = 3): 1/E[B] = 1/(4 sqrt3 pi) = 0.04594 per e-fold
  site percolation p = 1/2 (kappa = 6): 1/(2 sqrt3 pi) = 0.09189 per e-fold — exactly twice.
"""
import numpy as np, json, time, sys
import ising as isg


def box_dim(walls, bs=(1, 2, 4, 8, 16, 32, 64, 128)):
    """walls: bool array (doubled-lattice wall pixels). Returns (b, count) pairs."""
    R, C = walls.shape
    out = []
    for b in bs:
        r, c = R // b * b, C // b * b
        w = walls[:r, :c].reshape(r // b, b, c // b, b).any(axis=(1, 3))
        out.append((b, int(w.sum())))
    return out


def walls_of(s):
    """domain-wall bonds as pixels on the doubled lattice (bond pixel True where spins differ)"""
    R, C = s.shape
    D = np.zeros((2 * R - 1, 2 * C - 1), bool)
    D[::2, 1::2] = s[:, :-1] != s[:, 1:]
    D[1::2, ::2] = s[:-1, :] != s[1:, :]
    D[1::2, 1::2] = s[1:, :-1] != s[:-1, 1:]
    return D


if __name__ == '__main__':
    out = {}
    t0 = time.time()
    for L in [128, 256, 512, 1024, 2048]:
        rng = np.random.default_rng(1000 + L)
        s = rng.choice(np.array([-1, 1], np.int8), size=(L, L))
        D = np.zeros((2 * L - 1, 2 * L - 1), bool)
        nth = max(80, 30000 // L)
        for _ in range(nth):
            s = isg.sw_sweep(s, isg.BETA_C, rng, D)
        nm = max(60, 60000 // L)
        a, b = L // 4, 3 * L // 4
        ds, es = [], []
        for k in range(nm):
            for _ in range(2):
                s = isg.sw_sweep(s, isg.BETA_C, rng, D)
            d = isg.depth_field(s)
            ds.append(float(d[a:b, a:b].mean())); es.append(float(isg.bond_energy(s)))
        bd = box_dim(walls_of(s))
        dp, bdp = [], None
        for k in range(max(60, 60000 // L)):
            sp = rng.choice(np.array([-1, 1], np.int8), size=(L, L))
            dp.append(float(isg.depth_field(sp)[a:b, a:b].mean()))
        bdp = box_dim(walls_of(sp))
        out[L] = dict(depth_ising=float(np.mean(ds)), depth_ising_se=float(np.std(ds) / np.sqrt(len(ds))),
                      ss=float(np.mean(es)), depth_perc=float(np.mean(dp)), depth_perc_se=float(np.std(dp) / np.sqrt(len(dp))),
                      n_meas=nm, box_ising=bd, box_perc=bdp)
        print(L, out[L], f'{time.time()-t0:.0f}s', flush=True)
        json.dump(out, open('scaling2.json', 'w'), indent=1)
