"""Held-Karp 1-tree lower bound with subgradient ascent; records edge dwell.
The dwell web = where the solver spends its time (MO 501687, Concorde)."""
import numpy as np

def cities(n=220, seed=11, rmin=0.052):
    rng = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        p = rng.uniform(-1, 1, 2)
        if p @ p > 1.0: continue
        if pts and (np.hypot(*(np.array(pts) - p).T).min() < rmin): continue
        pts.append(p)
    return np.array(pts)

def prim_mst(W):
    """Prim on full matrix W (n,n) -> list of edges (i,j). O(n^2)."""
    n = len(W)
    intree = np.zeros(n, bool); intree[0] = True
    best = W[0].copy(); parent = np.zeros(n, int)
    edges = []
    for _ in range(n - 1):
        j = np.argmin(np.where(intree, np.inf, best))
        edges.append((parent[j], j))
        intree[j] = True
        upd = W[j] < best
        best = np.where(upd, W[j], best)
        parent = np.where(upd, j, parent)
    return edges

def held_karp(D, iters=3000, seed=0, UB=None):
    """Held-Karp ascent, classic step rule lam*(UB-bound)/||g||^2, lam halves
    on stall.  Returns lb, pi, dwell dict, last_seen dict."""
    n = len(D)
    pi = np.zeros(n)
    lb = -np.inf
    dwell = {}
    last = {}
    lam = 2.0; stall = 0
    if UB is None: UB = 2.0 * D[0].sum()
    prev = set(); toggles = {}
    for it in range(iters):
        W = D + pi[:, None] + pi[None, :]
        np.fill_diagonal(W, np.inf)
        # MST on nodes 1..n-1 (index 1..), attach node 0 by two cheapest
        sub = W[1:, 1:]
        edges = [(i+1, j+1) for i, j in prim_mst(sub)]
        w0 = W[0, 1:]
        two = np.argsort(w0)[:2] + 1
        edges += [(0, two[0]), (0, two[1])]
        deg = np.zeros(n, int)
        cost = 0.0
        for i, j in edges:
            deg[i] += 1; deg[j] += 1
            cost += W[i, j]
            key = (min(i,j), max(i,j))
            dwell[key] = dwell.get(key, 0) + 1
            last[key] = it
        cur = set()
        for i, j in edges:
            cur.add((min(i,j), max(i,j)))
        for k in cur.symmetric_difference(prev):
            toggles[k] = toggles.get(k, 0) + 1
        prev = cur
        bound = cost - 2 * pi.sum()
        if bound > lb + 1e-12: lb = bound; stall = 0
        else:
            stall += 1
            if stall >= 60: lam *= 0.7; stall = 0
        g = deg - 2
        if (g == 0).all(): break                      # 1-tree is a tour: optimal
        step = lam * (UB - bound) / (g @ g)
        if step <= 0: break
        pi = pi + step * g
    return lb, pi, dwell, last, toggles

def tour_len(D, tour):
    return D[tour, np.roll(tour, -1)].sum()

def two_opt(D, tour):
    """Vectorized-ish 2-opt to local optimality."""
    n = len(tour)
    improved = True
    while improved:
        improved = False
        pos = tour
        nxt = np.roll(pos, -1)
        for a in range(n - 1):
            i, inx = pos[a], nxt[a]
            js = np.arange(a+2, n if a > 0 else n-1)
            if len(js) == 0: continue
            j, jnx = pos[js], nxt[js]
            delta = D[i, j] + D[inx, jnx] - D[i, inx] - D[j, jnx]
            k = delta.argmin()
            if delta[k] < -1e-12:
                b = js[k]
                tour[a+1:b+1] = tour[a+1:b+1][::-1]
                improved = True
                pos = tour; nxt = np.roll(pos, -1)
    return tour

def or_opt(D, tour):
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for seglen in (1, 2, 3):
            for a in range(n):
                seg = [(a + k) % n for k in range(seglen)]
                p = tour[(a - 1) % n]; s0 = tour[seg[0]]; s1 = tour[seg[-1]]
                q = tour[(a + seglen) % n]
                rem = D[p, q] - D[p, s0] - D[s1, q]
                bestd = 0; bestb = -1
                for b in range(n):
                    if (b - a) % n < seglen + 1 or (a - 1 - b) % n == 0: continue
                    u = tour[b]; v = tour[(b + 1) % n]
                    add = D[u, s0] + D[s1, v] - D[u, v]
                    if rem + add < bestd - 1e-12:
                        bestd = rem + add; bestb = b
                if bestb >= 0:
                    segv = [tour[i] for i in seg]
                    rest = [tour[i] for i in range(n) if i not in seg]
                    bi = rest.index(tour[bestb])
                    tour = np.array(rest[:bi+1] + segv + rest[bi+1:])
                    improved = True
    return tour

def best_tour(D, starts=8, seed=3, kicks=60):
    rng = np.random.default_rng(seed)
    n = len(D); best = None; bl = np.inf
    for s in range(starts):
        cur = int(rng.integers(n))
        unv = set(range(n)); unv.discard(cur)
        tour = [cur]
        while unv:
            nxt = min(unv, key=lambda j: D[cur, j])
            tour.append(nxt); unv.discard(nxt); cur = nxt
        tour = two_opt(D, np.array(tour))
        tour = or_opt(D, tour); tour = two_opt(D, tour)
        L = tour_len(D, tour)
        if L < bl: bl, best = L, tour.copy()
    # iterated local search with double-bridge kicks
    for k in range(kicks):
        t = best.copy()
        cuts = np.sort(rng.choice(np.arange(1, n), 3, replace=False))
        a, b, c = cuts
        t = np.concatenate([t[:a], t[b:c], t[a:b], t[c:]])
        t = two_opt(D, t)
        if k % 3 == 0: t = or_opt(D, t); t = two_opt(D, t)
        L = tour_len(D, t)
        if L < bl - 1e-12: bl, best = L, t.copy()
    return best, bl
