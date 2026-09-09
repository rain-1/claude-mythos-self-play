"""ising.py — critical Ising on the TRIANGULAR lattice by Swendsen–Wang, plus the nesting
depth of spin clusters (the CLE_3 loop tree).

Why triangular: it is a triangulation, so spin clusters and their complements use the SAME
6-neighbour connectivity and every domain wall is an honest closed loop on the dual
honeycomb (no checkerboard ambiguity of the square lattice).

Lattice: site (i, j) has neighbours (i, j±1), (i±1, j), (i-1, j+1), (i+1, j-1)
(square array + anti-diagonal).  True positions x = j + i/2, y = i*sqrt(3)/2.

Swendsen–Wang in numpy: open a bond between equal spins with p = 1 - exp(-2 beta); the
bond clusters are found with ONE scipy.ndimage.label on a doubled lattice (site pixels at
even/even, bond pixels between them, 6-structure), then every cluster flips with prob 1/2.

Depth: parent(C) = cluster of the site directly above C's topmost-leftmost site (that site
is exterior to C, adjacent to C, hence of opposite spin; on a triangulation the exterior
vertex boundary of a finite connected cluster is connected, so that cluster's ring
surrounds C).  Clusters touching the lattice border are roots (depth 0).
"""
import numpy as np, time, sys, json
from scipy.ndimage import label, binary_fill_holes

ST6 = np.array([[0, 1, 1], [1, 1, 1], [1, 1, 0]], bool)   # (dy,dx) in {(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0)}
BETA_C = 0.5 * np.arcsinh(1 / np.sqrt(3))                # triangular lattice: sinh(2 beta_c) = 1/sqrt 3


def bond_energy(s):
    """mean nearest-neighbour correlation <s_i s_j> over the three bond directions (free bc)"""
    e = (s[:, :-1] * s[:, 1:]).sum() + (s[:-1, :] * s[1:, :]).sum() + (s[:-1, 1:] * s[1:, :-1]).sum()
    n = s[:, :-1].size + s[:-1, :].size + s[:-1, 1:].size
    return e / n


def sw_sweep(s, beta, rng, D=None):
    """one Swendsen–Wang sweep on spins s (int8 ±1, shape R×C). Returns new s."""
    R, C = s.shape
    p = 1 - np.exp(-2 * beta)
    if D is None:
        D = np.zeros((2 * R - 1, 2 * C - 1), bool)
    D[:] = False
    D[::2, ::2] = True
    # horizontal bonds (i,j)-(i,j+1) at (2i, 2j+1)
    eq = s[:, :-1] == s[:, 1:]
    D[::2, 1::2] = eq & (rng.random(eq.shape) < p)
    # vertical bonds (i,j)-(i+1,j) at (2i+1, 2j)
    eq = s[:-1, :] == s[1:, :]
    D[1::2, ::2] = eq & (rng.random(eq.shape) < p)
    # anti-diagonal bonds (i+1,j)-(i,j+1) at (2i+1, 2j+1)
    eq = s[1:, :-1] == s[:-1, 1:]
    D[1::2, 1::2] = eq & (rng.random(eq.shape) < p)
    lab, n = label(D, ST6)
    flip = rng.random(n + 1) < 0.5
    f = flip[lab[::2, ::2]]
    s = np.where(f, -s, s).astype(np.int8)
    return s


def depth_field(s, return_tree=False):
    """nesting depth of every site's spin cluster (0 = cluster touches the border)."""
    R, C = s.shape
    labp, npl = label(s > 0, ST6)
    labm, nm = label(s < 0, ST6)
    lab = np.where(s > 0, labp, labm + npl).astype(np.int32)
    N = npl + nm
    flat = lab.ravel()
    u, idx = np.unique(flat, return_index=True)      # first occurrence in row-major order = topmost, then leftmost
    first = np.zeros(N + 1, np.int64); first[u] = idx
    r0, c0 = first // C, first % C
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    root = np.zeros(N + 1, bool); root[border] = True
    parent = np.zeros(N + 1, np.int32)
    ok = (~root) & (r0 > 0)
    parent[ok] = lab[r0[ok] - 1, c0[ok]]
    parent[0] = 0
    # the parent must have the opposite spin (certificate of the construction)
    sp = np.zeros(N + 1, np.int8); sp[lab.ravel()] = s.ravel()
    assert (sp[parent[ok]] == -sp[ok]).all(), 'parent has the same spin'
    depth = np.zeros(N + 1, np.int32)
    for it in range(10000):
        nd = np.where(parent > 0, depth[parent] + 1, 0)
        if (nd == depth).all():
            break
        depth = nd
    depth[0] = 0
    if return_tree:
        return depth[lab], lab, parent, depth, N
    return depth[lab]


def depth_brute(s):
    """independent O(N_clusters) check: depth(site) = #clusters C (not its own) with site in the filled C."""
    R, C = s.shape
    labp, npl = label(s > 0, ST6)
    labm, nm = label(s < 0, ST6)
    lab = np.where(s > 0, labp, labm + npl)
    d = np.zeros(s.shape, np.int32)
    for k in range(1, npl + nm + 1):
        m = lab == k
        f = binary_fill_holes(m, ST6)
        d += (f & ~m)
    return d


def cluster_sizes(s):
    labp, npl = label(s > 0, ST6)
    labm, nm = label(s < 0, ST6)
    lab = np.where(s > 0, labp, labm + npl)
    return lab, np.bincount(lab.ravel())


def run(R, C, beta, nsweeps, seed, tag=None, every=10, log=print):
    rng = np.random.default_rng(seed)
    s = rng.choice(np.array([-1, 1], np.int8), size=(R, C))
    D = np.zeros((2 * R - 1, 2 * C - 1), bool)
    trace = []
    t0 = time.time()
    for t in range(1, nsweeps + 1):
        s = sw_sweep(s, beta, rng, D)
        if t % every == 0 or t == nsweeps:
            e = bond_energy(s); m = s.mean()
            trace.append((t, float(e), float(m)))
            log(f'{tag} sweep {t} <ss>={e:.5f} m={m:+.4f} {time.time()-t0:.0f}s')
            if tag:
                np.save(f'{tag}_spins.npy', s)
                json.dump(trace, open(f'{tag}_trace.json', 'w'))
    return s, trace


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'test':
        rng = np.random.default_rng(1)
        s = rng.choice(np.array([-1, 1], np.int8), size=(48, 48))
        for _ in range(30):
            s = sw_sweep(s, BETA_C, rng)
        d1 = depth_field(s); d2 = depth_brute(s)
        print('depth check equal:', (d1 == d2).all(), 'max depth', d1.max(), 'mismatch', (d1 != d2).sum())
        # percolation control (beta = 0): random spins
        s = rng.choice(np.array([-1, 1], np.int8), size=(64, 64))
        d1 = depth_field(s); d2 = depth_brute(s)
        print('perc depth check equal:', (d1 == d2).all(), 'max depth', d1.max())
    elif mode == 'big':
        R, C = int(sys.argv[2]), int(sys.argv[3]); n = int(sys.argv[4])
        run(R, C, BETA_C, n, seed=2026, tag='big', every=10,
            log=lambda m: (print(m, flush=True)))
    elif mode == 'scaling':
        # mean nesting depth vs L at T_c and at T = inf (site percolation p = 1/2)
        out = {}
        for L in [96, 192, 384, 768, 1536]:
            rng = np.random.default_rng(L)
            s = rng.choice(np.array([-1, 1], np.int8), size=(L, L))
            D = np.zeros((2 * L - 1, 2 * L - 1), bool)
            nth = max(60, 24000 // L)
            for _ in range(nth):
                s = sw_sweep(s, BETA_C, rng, D)
            nm = max(40, 30000 // L)
            ds, es, ms = [], [], []
            # measure on the central half to reduce border effects
            a, b = L // 4, 3 * L // 4
            for k in range(nm):
                for _ in range(3):
                    s = sw_sweep(s, BETA_C, rng, D)
                d = depth_field(s)
                ds.append(float(d[a:b, a:b].mean())); es.append(float(bond_energy(s))); ms.append(float(abs(s.mean())))
            # percolation: random spins, same measurement
            dp = []
            for k in range(max(20, nm // 2)):
                sp = rng.choice(np.array([-1, 1], np.int8), size=(L, L))
                dp.append(float(depth_field(sp)[a:b, a:b].mean()))
            out[L] = dict(depth_ising=float(np.mean(ds)), depth_ising_se=float(np.std(ds) / np.sqrt(len(ds))),
                          ss=float(np.mean(es)), absm=float(np.mean(ms)),
                          depth_perc=float(np.mean(dp)), depth_perc_se=float(np.std(dp) / np.sqrt(len(dp))),
                          n_meas=nm)
            print(L, out[L], flush=True)
            json.dump(out, open('scaling.json', 'w'), indent=1)
