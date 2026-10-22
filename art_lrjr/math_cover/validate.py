"""Validation of sim.py against brute-force fine-grid checks."""
import numpy as np, math, json, time, sys
from numba import njit
from scipy import ndimage, stats
sys.path.insert(0, '/home/user/claude-mythos-self-play/art_lrjr/math_cover')
from sim import Sim

@njit(cache=True)
def first_cover(disks, G, R, x0, y0, h):
    """first covering index for each point of a G x G grid (x0+i h, y0+j h); -1 if never; -2 outside D_R."""
    out = np.full((G, G), -1.0)
    for i in range(G):
        for j in range(G):
            px = x0 + i * h; py = y0 + j * h
            if px * px + py * py > R * R:
                out[i, j] = -2.0
    for t in range(disks.shape[0]):
        n = disks[t, 0]; cx = disks[t, 1]; cy = disks[t, 2]; r = 1.0 / math.sqrt(n)
        ia = max(0, int(math.floor((cx - r - x0) / h))); ib = min(G - 1, int(math.ceil((cx + r - x0) / h)))
        ja = max(0, int(math.floor((cy - r - y0) / h))); jb = min(G - 1, int(math.ceil((cy + r - y0) / h)))
        for i in range(ia, ib + 1):
            px = x0 + i * h
            for j in range(ja, jb + 1):
                if out[i, j] != -1.0:
                    continue
                py = y0 + j * h
                if (px - cx) ** 2 + (py - cy) ** 2 < r * r:
                    out[i, j] = n
    return out

@njit(cache=True)
def rim_first_cover(disks, M, R):
    out = np.full(M, -1.0)
    for t in range(disks.shape[0]):
        n = disks[t, 0]; cx = disks[t, 1]; cy = disks[t, 2]; r = 1.0 / math.sqrt(n)
        for k in range(M):
            if out[k] != -1.0:
                continue
            th = 2 * math.pi * k / M
            if (R * math.cos(th) - cx) ** 2 + (R * math.sin(th) - cy) ** 2 < r * r:
                out[k] = n
    return out

def main():
    sim = Sim()
    rep = {}
    # ---- 1. exact T vs brute force, unthinned disk streams
    rows = []
    for R in (1.0, 0.95):
        for sd in range(40):
            res = sim.run(1000 + sd, R=R, Nmax_log2=17, thin=False, record_disks=True, count=False)
            T = res['T']
            if T < 0:
                continue
            d = res['disks']
            d = d[d[:, 0] <= T]
            G = 2001
            fc = first_cover(d, G, R, -R, -R, 2 * R / (G - 1))
            inside = fc != -2.0
            Tgrid = fc[inside].max()
            # zoom on last hole
            lx, ly = res['last']
            Gz = 801; hz = 4.0 / math.sqrt(T) / (Gz - 1)
            fz = first_cover(d, Gz, R, lx - 2 / math.sqrt(T), ly - 2 / math.sqrt(T), hz)
            Tzoom = fz[fz != -2.0].max() if (fz != -2.0).any() else -1
            # exact check of witness: uncovered by disks < T, covered by disk T
            rr = 1 / np.sqrt(d[:, 0])
            dist2 = (d[:, 1] - lx) ** 2 + (d[:, 2] - ly) ** 2
            cov = dist2 < rr ** 2
            wit_ok = (not cov[:-1].any()) and bool(cov[-1]) and (lx * lx + ly * ly <= R * R + 1e-12)
            rimfc = rim_first_cover(d, 200000, R)
            rows.append(dict(R=R, seed=1000 + sd, T=T, Tgrid=float(Tgrid), Tzoom=float(Tzoom), witness_ok=wit_ok,
                             Trim=res['Trim'], Trim_grid=float(rimfc.max()), amb=res['ambiguous']))
            print(rows[-1], flush=True)
    rep['exact_vs_grid'] = rows
    # ---- 2. hole counts vs brute force labelling (unthinned), small N
    hrows = []
    for sd in range(15):
        res = sim.run(2000 + sd, R=1.0, Nmax_log2=12, thin=False, record_disks=True, count=True)
        d = res['disks']
        for (k, nc, hist, nleaf) in res['holes']:
            N = 1 << k
            if N < 64:
                continue
            dd = d[d[:, 0] < N]
            G = 3001
            fc = first_cover(dd, G, 1.0, -1, -1, 2 / (G - 1))
            unc = fc == -1.0
            lab, ncomp = ndimage.label(unc, structure=np.ones((3, 3)))
            hrows.append(dict(seed=2000 + sd, N=N, sim=nc, grid=int(ncomp)))
        if res['T'] > 0 and res['T'] < 4096:
            pass
    rep['holes_vs_grid'] = hrows
    for h in hrows:
        print(h)
    # ---- 3. thinned vs unthinned distribution of min(T, 2^16)
    t0 = time.time()
    a = []; b = []
    for sd in range(300):
        r1 = sim.run(5000 + sd, Nmax_log2=16, thin=True, count=False)
        r2 = sim.run(9000 + sd, Nmax_log2=16, thin=False, count=False)
        a.append(r1['T'] if r1['T'] > 0 else 2 ** 17); b.append(r2['T'] if r2['T'] > 0 else 2 ** 17)
    ks = stats.ks_2samp(a, b)
    rep['thin_vs_direct'] = dict(n=300, ks_stat=float(ks.statistic), p=float(ks.pvalue),
                                 med_thin=float(np.median(a)), med_direct=float(np.median(b)),
                                 frac_le_2_16_thin=float(np.mean(np.array(a) <= 2 ** 16)),
                                 frac_le_2_16_direct=float(np.mean(np.array(b) <= 2 ** 16)))
    print(rep['thin_vs_direct'], time.time() - t0)
    json.dump(rep, open('/home/user/claude-mythos-self-play/art_lrjr/math_cover/validation.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
