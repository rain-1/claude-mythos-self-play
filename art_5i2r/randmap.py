"""randmap.py — a uniform random planar map told in coins.
1. Uniform random plane tree with n edges (random Dyck word by the cycle lemma) with labels
   changing by -1,0,+1 along edges (uniform).
2. Cori–Vauquelin–Schaeffer: each corner is joined to the next corner (cyclically) with label one
   less; corners of minimal label are joined to a new vertex v*  =>  a uniform random pointed
   quadrangulation with n faces, n+2 vertices.  Certificate: graph distance from v* equals
   label - min + 1 for every vertex (the bijection's theorem), Euler's formula.
3. Planar embedding (networkx), faces fan-triangulated, v* removed  =>  a triangulated disc;
   maximal circle packing in the unit disc (Koebe–Andreev–Thurston) via the hyperbolic engine.
"""
import numpy as np, json, time, sys
from collections import defaultdict, deque
import networkx as nx


def random_plane_tree(n, rng):
    """uniform plane tree with n edges: Dyck word via the cycle lemma; returns parent array and the
    contour sequence of vertices (2n+1 entries) with corners."""
    w = np.array([1] * n + [-1] * (n + 1))
    rng.shuffle(w)
    # cycle lemma: unique rotation making all proper prefix sums >= 0 (of the (n+1) down steps word)
    s = np.cumsum(w)
    k = int(np.argmin(s)) + 1
    w = np.roll(w, -k)[:-1]     # drop the final -1: a Dyck word of length 2n
    assert w.sum() == 0 and (np.cumsum(w) >= 0).all()
    parent = [-1]
    contour = [0]
    stack = [0]
    nv = 1
    for step in w:
        if step == 1:
            parent.append(stack[-1]); stack.append(nv); contour.append(nv); nv += 1
        else:
            stack.pop(); contour.append(stack[-1])
    return np.array(parent), contour


def cvs(n, seed=0):
    rng = np.random.default_rng(seed)
    parent, contour = random_plane_tree(n, rng)
    V = n + 1
    lab = np.zeros(V, int)
    for v in range(1, V):
        lab[v] = lab[parent[v]] + rng.integers(-1, 2)
    corners = contour[:-1]                     # 2n corners, cyclic
    clab = lab[corners]
    m = clab.min()
    star = V                                   # v*
    edges = []
    N = len(corners)
    # successor: next corner cyclically with label l-1
    # build for each label the sorted list of corner indices
    by_lab = defaultdict(list)
    for i, l in enumerate(clab):
        by_lab[int(l)].append(i)
    import bisect
    for i, l in enumerate(clab):
        if l == m:
            edges.append((corners[i], star))
        else:
            lst = by_lab[int(l) - 1]
            j = bisect.bisect_right(lst, i)
            jj = lst[j] if j < len(lst) else lst[0]
            edges.append((corners[i], corners[jj]))
    G = nx.MultiGraph(); G.add_nodes_from(range(V + 1)); G.add_edges_from(edges)
    # distance certificate
    dist = nx.single_source_shortest_path_length(nx.Graph(G), star)
    ok = all(dist[v] == lab[v] - m + 1 for v in range(V))
    return dict(parent=parent, lab=lab, star=star, edges=edges, G=G, dist_ok=ok,
                n_multi=int(G.number_of_edges() - nx.Graph(G).number_of_edges()), V=V + 1, F=n)


def triangulated_disc(Q):
    """planar embedding of the simple graph, fan-triangulate faces, remove v*."""
    G = nx.Graph(Q['G'])
    star = Q['star']
    is_planar, emb = nx.check_planarity(G)
    assert is_planar
    faces = []
    seen = set()
    face_sizes = defaultdict(int)
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        f = emb.traverse_face(u, v, mark_half_edges=seen)
        face_sizes[len(f)] += 1
        for k in range(1, len(f) - 1):
            faces.append((f[0], f[k], f[k + 1]))
    faces = np.array(faces)
    Vn = G.number_of_nodes()
    euler_sphere = Vn - G.number_of_edges() + sum(face_sizes.values())
    # remove star
    keep = ~(faces == star).any(axis=1)
    faces = faces[keep]
    used = np.unique(faces)
    remap = -np.ones(Vn, int); remap[used] = np.arange(len(used))
    faces = remap[faces]
    V = len(used)
    es = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    eu, cnt = np.unique(es, axis=0, return_counts=True)
    boundary = np.zeros(V, bool); boundary[eu[cnt == 1].ravel()] = True
    euler = V - len(eu) + len(faces)
    # orientation: make all faces consistently oriented: networkx faces are consistent; flip all if needed later
    return dict(faces=faces, boundary=boundary, edges=eu, euler=euler, used=used, remap=remap,
                face_sizes=dict(face_sizes), euler_sphere=euler_sphere, V=V, W=np.zeros(V, complex))


def pack_map(n=1500, seed=1, verbose=True):
    from cpack import pack, layout, euclid_circles
    Q = cvs(n, seed)
    if verbose:
        print(f'CVS: V={Q["V"]} F={Q["F"]} multi-edges merged={Q["n_multi"]} distance certificate={Q["dist_ok"]}', flush=True)
    D = triangulated_disc(Q)
    if verbose:
        print(f'disc: V={D["V"]} faces={len(D["faces"])} boundary={D["boundary"].sum()} euler={D["euler"]} sphere-euler={D["euler_sphere"]} face sizes={D["face_sizes"]}', flush=True)
    mesh = dict(W=D['W'], faces=D['faces'], boundary=D['boundary'], edges=D['edges'], euler=D['euler'], h=0)
    r, th, it = pack(mesh, verbose=verbose, maxit=60000)
    # root: an interior vertex of high degree near the 'centre' — use the tree root
    root_new = int(D['remap'][0]) if D['remap'][0] >= 0 else int(np.where(~D['boundary'])[0][0])
    if D['boundary'][root_new]:
        root_new = int(np.where(~D['boundary'])[0][0])
    edges = D['edges']
    nb = np.concatenate([edges[edges[:, 0] == root_new][:, 1], edges[edges[:, 1] == root_new][:, 0]])
    v1 = int(nb[0])
    z, placed = layout(mesh, r, root_new, v1)
    assert placed.all(), f'unplaced {(~placed).sum()}'
    C, R, hs = euclid_circles(mesh, r, z)
    # orientation check: if the layout came out mirrored the faces would overlap; check signed area sum
    d = np.abs(C[edges[:, 0]] - C[edges[:, 1]]); s = R[edges[:, 0]] + R[edges[:, 1]]
    tang = np.abs(d - s) / s
    cert = dict(n=n, seed=seed, V_map=Q['V'], faces_map=Q['F'], multi_edges_merged=Q['n_multi'], distance_certificate=bool(Q['dist_ok']),
                V_disc=D['V'], faces_disc=int(len(D['faces'])), boundary=int(D['boundary'].sum()), euler_disc=int(D['euler']),
                euler_sphere=int(D['euler_sphere']), face_sizes=D['face_sizes'],
                max_angle_err=float(np.abs(th[~D['boundary']] - 2 * np.pi).max()), pack_iters=int(it),
                max_tangency_rel=float(tang.max()), horocycle_spread=float(hs),
                radius_min=float(R[~D['boundary']].min()), radius_max=float(R.max()))
    if verbose:
        print(json.dumps(cert, indent=1), flush=True)
    return dict(Q=Q, D=D, mesh=mesh, r=r, z=z, C=C, R=R, cert=cert)


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    P = pack_map(n)
