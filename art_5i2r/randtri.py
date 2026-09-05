"""randtri.py — a uniformly random SIMPLE planar triangulation by edge flips, told in coins.

The CVS route (randmap.py) produces quadrangulations with multi-edges, which no coin packing can
realise (two coins cannot touch twice). Instead: start from any simple triangulation of the sphere with
n vertices, run the edge-flip Markov chain, rejecting flips that would create a multi-edge or a
degree-2 vertex. The chain is symmetric and the flip graph of simple triangulations is connected
(Wagner 1936), so its stationary law is UNIFORM over simple triangulations of the sphere with n
labelled vertices. Then remove the highest-degree vertex (its link becomes the rim) and compute the
maximal circle packing of the resulting triangulated disc (Koebe–Andreev–Thurston) with the hyperbolic
engine in cpack.py.

Certificates: simplicity (no multi-edges) and Euler V − E + F = 2 after every 10^5 flips, acceptance
rate, degree histogram vs the known limit law for uniform triangulations (mean degree → 6), tangencies.
"""
import numpy as np, json, time, sys
from collections import defaultdict, deque
BD_RADIUS = 0.5   # hyperbolic radius of the rim coins (finite: every layout pivot stays finite)


def initial_sphere(n, rng):
    """Delaunay triangulation of n-1 random points + a pole joined to the convex hull."""
    from scipy.spatial import Delaunay
    pts = rng.random((n - 1, 2))
    tri = Delaunay(pts)
    faces = [tuple(int(x) for x in f) for f in tri.simplices]
    hull = tri.convex_hull                     # edges (i,j) of the hull
    pole = n - 1
    # orient hull edges consistently: walk the hull
    nb = defaultdict(list)
    for a, b in hull:
        nb[int(a)].append(int(b)); nb[int(b)].append(int(a))
    start = int(hull[0, 0]); cyc = [start]; prev = -1; cur = start
    while True:
        nxt = [x for x in nb[cur] if x != prev][0]
        if nxt == start:
            break
        cyc.append(nxt); prev, cur = cur, nxt
    for i in range(len(cyc)):
        faces.append((cyc[i], cyc[(i + 1) % len(cyc)], pole))
    return faces


class Tri:
    """simple triangulation of the sphere as edge -> its two apexes."""
    def __init__(self, faces):
        self.apex = {}
        self.adj = defaultdict(set)
        for f in faces:
            for i in range(3):
                u, v, w = f[i], f[(i + 1) % 3], f[(i + 2) % 3]
                key = (u, v) if u < v else (v, u)
                self.apex.setdefault(key, []).append(w)
                self.adj[u].add(v); self.adj[v].add(u)
        for k, a in self.apex.items():
            assert len(a) == 2, (k, a)
        self.edges = list(self.apex.keys())
        self.nflips = 0; self.nacc = 0

    def flip(self, rng):
        i = rng.integers(len(self.edges))
        u, v = self.edges[i]
        a, b = self.apex[(u, v)]
        self.nflips += 1
        if b in self.adj[a] or len(self.adj[u]) <= 3 or len(self.adj[v]) <= 3:
            return False
        # remove edge (u,v), add (a,b); update the four surrounding edges' apexes
        del self.apex[(u, v)]
        self.adj[u].discard(v); self.adj[v].discard(u)
        key = (a, b) if a < b else (b, a)
        self.apex[key] = [u, v]
        self.adj[a].add(b); self.adj[b].add(a)
        self.edges[i] = key
        for (x, y, old, new) in ((u, a, v, b), (a, v, u, b), (v, b, u, a), (b, u, v, a)):
            k2 = (x, y) if x < y else (y, x)
            ap = self.apex[k2]
            ap[ap.index(old)] = new
        self.nacc += 1
        return True

    def faces(self):
        fs = set()
        for (u, v), (a, b) in self.apex.items():
            fs.add(tuple(sorted((u, v, a)))); fs.add(tuple(sorted((u, v, b))))
        return [list(f) for f in fs]

    def check(self, n):
        E = len(self.apex); F = len(self.faces())
        simple = all(len(self.adj[v]) == len(set(self.adj[v])) for v in self.adj)
        ok_apex = all(len(a) == 2 and a[0] != a[1] for a in self.apex.values())
        return dict(V=n, E=E, F=F, euler=n - E + F, simple=simple, apex_ok=ok_apex)


def orient(faces):
    """consistent orientation by BFS over shared edges."""
    faces = [list(f) for f in faces]
    ef = defaultdict(list)
    for i, f in enumerate(faces):
        for k in range(3):
            a, b = f[k], f[(k + 1) % 3]
            ef[(a, b) if a < b else (b, a)].append(i)
    done = [False] * len(faces); done[0] = True
    q = deque([0])
    while q:
        i = q.popleft(); f = faces[i]
        for k in range(3):
            a, b = f[k], f[(k + 1) % 3]           # directed edge a->b in face i
            for j in ef[(a, b) if a < b else (b, a)]:
                if j == i or done[j]:
                    continue
                g = faces[j]
                # face j must traverse b->a
                ia = g.index(a); ib = g.index(b)
                if (ia + 1) % 3 == ib:            # it traverses a->b: flip
                    g[1], g[2] = g[2], g[1]
                done[j] = True; q.append(j)
    assert all(done)
    return np.array(faces)


def build(n=1500, flips=None, seed=3, verbose=True):
    from cpack import pack_fast, layout, euclid_circles
    rng = np.random.default_rng(seed)
    T = Tri(initial_sphere(n, rng))
    flips = flips or 400 * n
    t0 = time.time()
    checks = []
    for step in range(flips):
        T.flip(rng)
        if (step + 1) % 100000 == 0:
            c = T.check(n); checks.append(c)
            assert c['euler'] == 2 and c['simple'] and c['apex_ok'], c
            if verbose:
                print(f'   flips {step+1} acc {T.nacc/T.nflips:.3f} euler {c["euler"]} simple {c["simple"]} {time.time()-t0:.0f}s', flush=True)
    faces = orient(T.faces())
    deg = np.array([len(T.adj[v]) for v in range(n)])
    # remove a high-degree vertex whose removal (after ear pruning) leaves a clean disc: no interior
    # vertex with only boundary neighbours (unplaceable by angles), no pinched boundary
    faces_all = faces
    order = np.argsort(-deg)
    for star in order[:40]:
        star = int(star)
        faces = faces_all[~(faces_all == star).any(axis=1)]
        n_ears = 0
        while True:
            cnt = np.bincount(faces.ravel(), minlength=n)
            ears = np.where(cnt == 1)[0]
            if len(ears) == 0:
                break
            faces = faces[~np.isin(faces, ears).any(axis=1)]
            n_ears += len(ears)
        es_ = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
        eu_, cnt_ = np.unique(es_, axis=0, return_counts=True)
        bd_ = np.zeros(n, bool); bd_[eu_[cnt_ == 1].ravel()] = True
        deg_f = np.bincount(faces.ravel(), minlength=n); deg_e = np.bincount(eu_.ravel(), minlength=n)
        present = deg_f > 0
        pinch = (present & bd_ & (deg_f != deg_e - 1)).any()
        # interior vertices with all-boundary neighbours
        int_v = present & ~bd_
        nb_int = np.zeros(n, bool)
        nb_int[eu_[int_v[eu_[:, 1]], 0]] = True; nb_int[eu_[int_v[eu_[:, 0]], 1]] = True
        bad_int = (int_v & ~nb_int).any()
        if not pinch and not bad_int:
            break
    else:
        raise RuntimeError('no clean star vertex found')
    used = np.unique(faces)
    remap = -np.ones(n, int); remap[used] = np.arange(len(used))
    faces = remap[faces]
    V = len(used)
    es = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    eu, cnt = np.unique(es, axis=0, return_counts=True)
    boundary = np.zeros(V, bool); boundary[eu[cnt == 1].ravel()] = True
    mesh = dict(W=np.zeros(V, complex), faces=faces, boundary=boundary, edges=eu, euler=V - len(eu) + len(faces), h=0)
    if verbose:
        print(f'disc: V={V} faces={len(faces)} boundary={boundary.sum()} euler={mesh["euler"]} degree mean {deg.mean():.3f}', flush=True)
    r, th, it = pack_fast(mesh, verbose=verbose, bd_radius=BD_RADIUS)
    mesh_l = dict(mesh, boundary=np.zeros(V, bool))   # every vertex finite for the layout
    # centre: an interior vertex of maximal graph distance from the rim
    import scipy.sparse as sp
    from scipy.sparse.csgraph import shortest_path
    A = sp.coo_matrix((np.ones(len(eu)), (eu[:, 0], eu[:, 1])), shape=(V, V)); A = A + A.T
    drim = shortest_path(A, unweighted=True, indices=np.where(boundary)[0]).min(axis=0)
    v0 = int(np.argmax(drim))
    nbv = np.concatenate([eu[eu[:, 0] == v0][:, 1], eu[eu[:, 1] == v0][:, 0]])
    v1 = int(nbv[np.argmax(r[nbv])])
    z, placed = layout(mesh_l, r, v0, v1)
    if not placed.all():
        from collections import defaultdict as dd
        nb = dd(set)
        for a, b in eu:
            nb[a].add(b); nb[b].add(a)
        un = np.where(~placed)[0]
        print('UNPLACED', len(un), 'boundary among them', int(boundary[un].sum()), flush=True)
        for w in un[:12]:
            fs = [f for f in faces if w in f]
            print('  w', w, 'bd' if boundary[w] else 'int', 'r', round(float(r[w]), 5), 'nbrs', len(nb[w]),
                  'placed nbrs', sum(placed[u] for u in nb[w]), 'bd nbrs', sum(boundary[u] for u in nb[w]),
                  'faces2placed', sum(placed[[x for x in f if x != w]].all() for f in fs),
                  'nan/out among placed nbrs', sum((np.isnan(z[u]) or abs(z[u]) > 1 + 1e-9) for u in nb[w] if placed[u]), flush=True)
        raise RuntimeError('unplaced')
    C, R, hs = euclid_circles(mesh_l, r, z)
    # if mirrored (faces CW in the picture), reflect
    P = C[faces]; area = ((P[:, 1] - P[:, 0]).conj() * (P[:, 2] - P[:, 0])).imag
    mirrored = (area < 0).mean() > 0.5
    if mirrored:
        C = np.conj(C); z = np.conj(z)
    d = np.abs(C[eu[:, 0]] - C[eu[:, 1]]); s = R[eu[:, 0]] + R[eu[:, 1]]
    tang = np.abs(d - s) / s
    dcen = shortest_path(A, unweighted=True, indices=v0)
    cert = dict(n=n, seed=seed, flips=int(T.nflips), accepted=int(T.nacc), acceptance=float(T.nacc / T.nflips),
                euler_sphere=checks[-1]['euler'] if checks else None, simple=bool(checks[-1]['simple']) if checks else None,
                degree_mean=float(deg.mean()), degree_hist={int(k): int(v) for k, v in zip(*np.unique(deg, return_counts=True))},
                removed_vertex_degree=int(deg[star]), ears_pruned=int(n_ears), V_disc=int(V), faces_disc=int(len(faces)), boundary=int(boundary.sum()),
                euler_disc=int(mesh['euler']), pack_iters=int(it), max_angle_err=float(np.abs(th[~boundary] - 2 * np.pi).max()),
                max_tangency_rel=float(tang.max()), horocycle_spread=float(hs), mirrored=bool(mirrored),
                radius_min=float(R[~boundary].min()), radius_max=float(R.max()), rim_hyperbolic_radius=BD_RADIUS, max_dist_from_centre=int(dcen.max()))
    if verbose:
        print(json.dumps(cert, indent=1), flush=True)
    return dict(mesh=mesh, r=r, z=z, C=C, R=R, cert=cert, deg=deg[used], dcen=dcen, drim=drim, v0=v0, adjA=A)


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    P = build(n)
    np.savez(f'randtri_{n}.npz', faces=P['mesh']['faces'], boundary=P['mesh']['boundary'], edges=P['mesh']['edges'],
             r=P['r'], C=P['C'], R=P['R'], deg=P['deg'], dcen=P['dcen'], drim=P['drim'], v0=P['v0'])
    json.dump(P['cert'], open(f'randtri_{n}_cert.json', 'w'), indent=1)
