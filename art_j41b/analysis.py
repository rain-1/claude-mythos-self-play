"""analysis.py — certificates for 'Zero Is Not Nothing' from the big configuration and the scaling runs.
- bond correlation vs the exact 2/3 at T_c (triangular lattice)
- nesting-depth slope vs ln L against 1/(4 sqrt3 pi) (Ising) and 1/(2 sqrt3 pi) (percolation)
- wall dimension: perimeter (wall bonds) vs diameter of clusters, expected 11/8 for Ising spin
  clusters (SLE_3 hulls), 7/4 for percolation hulls (SLE_6)
"""
import numpy as np, json
from scipy.ndimage import label
import ising as isg


def perimeter_vs_diameter(s):
    """OUTER perimeter of every cluster = the wall bonds between it and its parent in the nesting tree
    (that loop is the cluster's outer boundary, a CLE loop), versus the cluster's diameter."""
    d, lab, parent, depth, N = isg.depth_field(s, return_tree=True)

    def outer(a, b):
        m = (a != b)
        a, b = a[m], b[m]
        # bond (a, b) is on the outer loop of a if parent[a] == b, and of b if parent[b] == a
        return (np.bincount(a[parent[a] == b], minlength=N + 1) + np.bincount(b[parent[b] == a], minlength=N + 1))
    per = outer(lab[:, :-1], lab[:, 1:]) + outer(lab[:-1, :], lab[1:, :]) + outer(lab[1:, :-1], lab[:-1, 1:])
    # diameter: extent in true coordinates x = j + i/2, y = i sqrt3/2 — use bounding box of (x, y)
    ii, jj = np.indices(s.shape)
    x = (jj + ii / 2).ravel(); y = (ii * np.sqrt(3) / 2).ravel(); l = lab.ravel()
    xmin = np.full(N + 1, np.inf); xmax = np.full(N + 1, -np.inf); ymin = xmin.copy(); ymax = xmax.copy()
    np.minimum.at(xmin, l, x); np.maximum.at(xmax, l, x); np.minimum.at(ymin, l, y); np.maximum.at(ymax, l, y)
    diam = np.maximum(xmax - xmin, ymax - ymin) + 1
    sizes = np.bincount(l, minlength=N + 1)
    # exclude clusters touching the border
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    keep = np.ones(N + 1, bool); keep[border] = False; keep[0] = False
    return per[keep], diam[keep], sizes[keep]


def fit_dim(per, diam, dmin=8, dmax=None):
    if dmax is None:
        dmax = diam.max() / 4
    m = (diam >= dmin) & (diam <= dmax)
    # bin by diameter (log bins), average log perimeter per bin, then fit
    bins = np.geomspace(dmin, dmax, 14)
    idx = np.digitize(diam[m], bins)
    xs, ys = [], []
    for k in range(1, len(bins)):
        mm = idx == k
        if mm.sum() >= 20:
            xs.append(np.log(diam[m][mm]).mean()); ys.append(np.log(per[m][mm]).mean())
    p = np.polyfit(xs, ys, 1)
    return float(p[0]), len(xs), int(m.sum())


if __name__ == '__main__':
    out = {}
    s = np.load('big_spins.npy')
    tr = np.array(json.load(open('big_trace.json')))
    out['big'] = dict(shape=list(s.shape), sweeps=int(tr[-1, 0]), ss_last20_mean=float(tr[-20:, 1].mean()),
                      ss_last20_std=float(tr[-20:, 1].std()), ss_exact_Tc=2 / 3, m_last20_mean=float(tr[-20:, 2].mean()),
                      absm_last20_mean=float(np.abs(tr[-20:, 2]).mean()))
    per, diam, sz = perimeter_vs_diameter(s)
    dI, nb, nc = fit_dim(per, diam)
    out['wall_dim_ising'] = dict(fit=dI, expected=11 / 8, n_bins=nb, n_clusters=nc)
    rng = np.random.default_rng(5)
    sp = rng.choice(np.array([-1, 1], np.int8), size=s.shape)
    per, diam, sz = perimeter_vs_diameter(sp)
    dP, nb, nc = fit_dim(per, diam)
    out['wall_dim_perc'] = dict(fit=dP, expected=7 / 4, n_bins=nb, n_clusters=nc)
    # nesting slopes
    for fn in ['scaling.json', 'scaling2.json']:
        try:
            d = json.load(open(fn))
        except Exception:
            continue
        Ls = sorted(int(k) for k in d)
        x = np.log(Ls)
        yi = np.array([d[str(L)]['depth_ising'] for L in Ls]); ei = np.array([d[str(L)]['depth_ising_se'] for L in Ls])
        yp = np.array([d[str(L)]['depth_perc'] for L in Ls]); ep = np.array([d[str(L)]['depth_perc_se'] for L in Ls])
        pi_, ci_ = np.polyfit(x, yi, 1, w=1 / ei, cov=True)
        pp_, cp_ = np.polyfit(x, yp, 1, w=1 / ep, cov=True)
        out[fn] = dict(L=Ls, depth_ising=yi.tolist(), depth_ising_se=ei.tolist(), depth_perc=yp.tolist(), depth_perc_se=ep.tolist(),
                       slope_ising=float(pi_[0]), slope_ising_se=float(np.sqrt(ci_[0, 0])), theory_ising=1 / (4 * np.sqrt(3) * np.pi),
                       slope_perc=float(pp_[0]), slope_perc_se=float(np.sqrt(cp_[0, 0])), theory_perc=1 / (2 * np.sqrt(3) * np.pi),
                       ratio_perc_over_ising=float(pp_[0] / pi_[0]), theory_ratio=2.0,
                       ss=[d[str(L)]['ss'] for L in Ls])
    print(json.dumps(out, indent=1))
    json.dump(out, open('analysis.json', 'w'), indent=1)
