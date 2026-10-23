"""Mirror-symmetric backtracking search (integer coordinates, mirror x -> -x).
sigma: an involutive automorphism of the graph; sigma-fixed vertices lie on the axis x=0, other vertices
come in pairs (x,y), (-x,y). `order` lists one representative per orbit, each (after the first) adjacent
to an earlier-placed vertex (or its mirror).  All edges must get integer length; faces must stay CCW
(both global orientations are tried); no crossings.  Best min-angle solution kept per max edge."""
import math, json, sys
import numpy as np
from numba import njit
sys.path.insert(0, '.')
from gsearch import isq, orient, onseg, seg_conflict, minang

@njit(cache=True)
def check_new(X, Y, st, E, FF, L, n, k):
    # st: 0 unplaced, 1 placed, 2 new
    for u in range(n):
        if st[u] == 2:
            for w in range(n):
                if w != u and st[w] > 0 and X[w] == X[u] and Y[w] == Y[u]: return False
    for e in range(E.shape[0]):
        a = E[e,0]; b = E[e,1]
        if st[a] > 0 and st[b] > 0 and (st[a] == 2 or st[b] == 2):
            d2 = (X[a]-X[b])**2 + k*(Y[a]-Y[b])**2
            if d2 > L*L or isq(d2) < 0: return False
    for f in range(FF.shape[0]):
        a = FF[f,0]; b = FF[f,1]; c = FF[f,2]
        if st[a] > 0 and st[b] > 0 and st[c] > 0 and (st[a] == 2 or st[b] == 2 or st[c] == 2):
            if orient(X[a],Y[a],X[b],Y[b],X[c],Y[c],1) <= 0: return False
    for e in range(E.shape[0]):
        a = E[e,0]; b = E[e,1]
        if st[a] == 0 or st[b] == 0: continue
        enew = st[a] == 2 or st[b] == 2
        for v in range(n):
            if v == a or v == b or st[v] == 0: continue
            if not (enew or st[v] == 2): continue
            if orient(X[a],Y[a],X[b],Y[b],X[v],Y[v],1) == 0 and onseg(X[a],Y[a],X[b],Y[b],X[v],Y[v]): return False
        if not enew: continue
        for e2 in range(E.shape[0]):
            c = E[e2,0]; d = E[e2,1]
            if st[c] == 0 or st[d] == 0 or e2 == e: continue
            if c == a or c == b or d == a or d == b: continue
            if seg_conflict(X[a],Y[a],X[b],Y[b],X[c],Y[c],X[d],Y[d]): return False
    return True

@njit(cache=True)
def search(n, order, ref, sigma, E, FF, PVx, PVy, legs, nlegs, L, B, best_ang, best_sol, maxnodes, F0, k):
    m = order.shape[0]
    X = np.zeros(n, np.int64); Y = np.zeros(n, np.int64)
    st = np.zeros(n, np.int64)
    idx = np.zeros(m, np.int64)
    nodes = 0; nsol = 0
    # first vertex: if fixed -> (0,0); else (x,0) with x in 1..B (enumerated as level 0)
    t = 0
    while t >= 0:
        if nodes > maxnodes: break
        v = order[t]; fixed = sigma[v] == v
        # clear this and later levels
        for s in range(t, m):
            st[order[s]] = 0; st[sigma[order[s]]] = 0
        placed = False
        while True:
            w = idx[t]; idx[t] += 1
            if t == 0:
                if fixed:
                    if w > 0: break
                    x = 0; y = 0
                else:
                    if w >= B: break
                    x = w + 1; y = 0
            else:
                r = ref[t]
                if fixed:
                    if X[r] == 0:
                        if w >= 2*L: break
                        x = 0; y = Y[r] + (w//2 + 1) * (1 if w % 2 == 0 else -1)
                    else:
                        ax = abs(X[r])
                        if w >= 2*nlegs[ax]: break
                        x = 0; y = Y[r] + legs[ax, w//2] * (1 if w % 2 == 0 else -1)
                        if w % 2 == 1 and legs[ax, w//2] == 0: continue
                else:
                    if w >= PVx.shape[0]: break
                    x = X[r] + PVx[w]; y = Y[r] + PVy[w]
                    if x == 0: continue
            if abs(x) > B or abs(y) > B: continue
            nodes += 1
            X[v] = x; Y[v] = y; st[v] = 2
            if not fixed:
                X[sigma[v]] = -x; Y[sigma[v]] = y; st[sigma[v]] = 2
            if check_new(X, Y, st, E, FF, L, n, k):
                placed = True; break
            st[v] = 0; st[sigma[v]] = 0
        if not placed:
            idx[t] = 0
            t -= 1
            continue
        st[v] = 1; st[sigma[v]] = 1
        if t == m - 1:
            nsol += 1
            mx = 0
            for e in range(E.shape[0]):
                a = E[e,0]; b = E[e,1]
                d = isq((X[a]-X[b])**2 + k*(Y[a]-Y[b])**2)
                if d > mx: mx = d
            ang = minang(X, Y, F0, k)
            if ang > best_ang[mx]:
                best_ang[mx] = ang
                for u in range(n):
                    best_sol[mx, 2*u] = X[u]; best_sol[mx, 2*u+1] = Y[u]
            st[v] = 0; st[sigma[v]] = 0
            continue
        t += 1
        idx[t] = 0
    return nsol, nodes

def run(n, edges, faces, sigma, order, L, B, maxnodes=10**12, k=1):
    E = np.array(edges, np.int64)
    adj = {v: set() for v in range(n)}
    for a, b in edges: adj[a].add(b); adj[b].add(a)
    placed = set(); ref = [0]
    for t, v in enumerate(order):
        if t > 0:
            nb = [u for u in adj[v] if u in placed]
            assert nb, "order not connected"
            # prefer an off-axis neighbour for fixed v (finite candidate list)
            nb.sort(key=lambda u: (sigma[u] == u))
            ref.append(nb[0])
        placed |= {v, sigma[v]}
    legs = np.zeros((B+1, L+2), np.int64); nlegs = np.zeros(B+1, np.int64)
    for x in range(1, B+1):
        ds = [d for d in range(0, L+1) if x*x+k*d*d <= L*L and math.isqrt(x*x+k*d*d)**2 == x*x+k*d*d]
        legs[x, :len(ds)] = ds; nlegs[x] = len(ds)
    pv = sorted((math.isqrt(dx*dx+k*dy*dy), dx, dy) for dx in range(-L, L+1) for dy in range(-L, L+1)
                if 0 < dx*dx+k*dy*dy <= L*L and math.isqrt(dx*dx+k*dy*dy)**2 == dx*dx+k*dy*dy)
    PVx = np.array([p[1] for p in pv], np.int64); PVy = np.array([p[2] for p in pv], np.int64)
    F0 = np.array(faces, np.int64)
    results = {}; tot = 0
    for sign in (1, -1):
        FF = np.array([f if sign == 1 else (f[0], f[2], f[1]) for f in faces], np.int64)
        best_ang = np.zeros(L+1); best_sol = np.zeros((L+1, 2*n), np.int64)
        nsol, nodes = search(n, np.array(order, np.int64), np.array(ref, np.int64), np.array(sigma, np.int64),
                             E, FF, PVx, PVy, legs, nlegs, L, B, best_ang, best_sol, maxnodes, F0, k)
        tot += nsol
        for mx in range(L+1):
            if best_ang[mx] > results.get(mx, (0,))[0]:
                results[mx] = (best_ang[mx], best_sol[mx].reshape(n, 2).tolist())
    return tot, results

if __name__ == "__main__":
    import graphs, time
    from common import faces_from_drawing
    name = sys.argv[1]; sigma = json.loads(sys.argv[2]); order = json.loads(sys.argv[3]); L = int(sys.argv[4])
    B = int(sys.argv[5]) if len(sys.argv) > 5 else L
    k = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    n, edges, refd = getattr(graphs, name)()
    es = set(map(tuple, map(sorted, edges)))
    assert all(tuple(sorted((sigma[a], sigma[b]))) in es for a, b in edges), "sigma not an automorphism"
    faces = faces_from_drawing(refd, edges)
    t0 = time.time()
    tot, res = run(n, edges, faces, sigma, order, L, B, k=k)
    print('k', k)
    print(name, 'mirror L', L, 'sols', tot, round(time.time()-t0, 1))
    best = -1
    for mx in sorted(res):
        a = math.degrees(res[mx][0])
        if a > best + 0.01: best = a; print('   max', mx, 'ang', round(a, 2), res[mx][1])
    json.dump({str(k): v for k, v in res.items()}, open(f'mirror_{name}_L{L}_k{k}.json', 'w'))
