"""Random domino tilings of the n x n board and long domino-respecting paths.
Digraph: D -> D' iff white(D) is adjacent to black(D').  A domino-respecting path = directed simple path.
Search: anneal a path/cycle cover (succ/pred links) towards one Hamiltonian path."""
import numpy as np, numba as nb, sys

@nb.njit(cache=True)
def random_tiling(n, sweeps, seed):
    np.random.seed(seed)
    own = np.empty((n, n), np.int32)          # partner direction: 0=R,1=L,2=D,3=U
    for r in range(n):
        for c in range(n):
            own[r, c] = 0 if c % 2 == 0 else 1
    for it in range(sweeps * n * n):
        r = np.random.randint(n - 1); c = np.random.randint(n - 1)
        if own[r, c] == 0 and own[r + 1, c] == 0:
            own[r, c] = 2; own[r + 1, c] = 3; own[r, c + 1] = 2; own[r + 1, c + 1] = 3
        elif own[r, c] == 2 and own[r, c + 1] == 2:
            own[r, c] = 0; own[r, c + 1] = 1; own[r + 1, c] = 0; own[r + 1, c + 1] = 1
    return own

def build(own):
    n = own.shape[0]
    dr = [0, 0, 1, -1]; dc = [1, -1, 0, 0]
    idx = -np.ones((n, n), np.int32); cells = []
    for r in range(n):
        for c in range(n):
            if idx[r, c] < 0:
                d = own[r, c]; r2, c2 = r + dr[d], c + dc[d]
                idx[r, c] = idx[r2, c2] = len(cells)
                a, b = (r, c), (r2, c2)
                cells.append((a, b) if (r + c) % 2 == 0 else (b, a))     # (black, white)
    ND = len(cells)
    out = -np.ones((ND, 3), np.int32)
    for d, (b, w) in enumerate(cells):
        k = 0
        for q in range(4):
            r2, c2 = w[0] + dr[q], w[1] + dc[q]
            if 0 <= r2 < n and 0 <= c2 < n and idx[r2, c2] != d:
                out[d, k] = idx[r2, c2]; k += 1
    return idx, np.array(cells, np.int32), out

@nb.njit(cache=True)
def _head_len(x, succ, pred):
    h = x; L = 1
    while pred[h] >= 0: h = pred[h]; L += 1
    y = x
    while succ[y] >= 0: y = succ[y]; L += 1
    return h, L

@nb.njit(cache=True)
def anneal(out, iters, seed, T0, T1, beta=1.0):
    """State: vertex-disjoint directed paths (no cycles).  Energy = #paths - beta*sum(len^2)/ND^2."""
    np.random.seed(seed)
    ND = out.shape[0]
    succ = -np.ones(ND, np.int32); pred = -np.ones(ND, np.int32)
    bestL = 0; bs = succ.copy()
    hs = np.empty(3, np.int32); qs = np.empty(3, np.int32)
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        a = np.random.randint(ND); v = out[a, np.random.randint(3)]
        if v < 0 or succ[a] == v: continue
        olds = succ[a]; oldp = pred[v]
        ha, la = _head_len(a, succ, pred); hv, lv = _head_len(v, succ, pred)
        if ha == hv:
            # same path: legal only if v is downstream of a (else a cycle closes)
            x = succ[a]
            while x >= 0 and x != v: x = succ[x]
            if x != v: continue
        before = la * la + (lv * lv if hv != ha else 0)
        if olds >= 0: pred[olds] = -1
        if oldp >= 0: succ[oldp] = -1
        succ[a] = v; pred[v] = a
        k = 0; after = 0
        qs[0] = a; qs[1] = olds; qs[2] = oldp
        for qi in range(3):
            q = qs[qi]
            if q < 0: continue
            h, L = _head_len(q, succ, pred)
            dup = False
            for j in range(k):
                if hs[j] == h: dup = True
            if not dup:
                hs[k] = h; k += 1; after += L * L
                if L > bestL:
                    bestL = L; bs[:] = succ
        dE = 1 - (1 if olds >= 0 else 0) - (1 if oldp >= 0 else 0)
        dcost = -dE + beta * (before - after) / (ND * ND)
        if dcost > 0 and np.random.random() >= np.exp(-dcost / T):
            succ[a] = olds; pred[v] = oldp
            if olds >= 0: pred[olds] = a
            if oldp >= 0: succ[oldp] = v
        if bestL == ND: break
    return bs, ND - bestL

@nb.njit(cache=True)
def longest(succ, pred):
    ND = succ.shape[0]; bestL = 0
    seen = np.zeros(ND, np.uint8)
    for s in range(ND):
        if pred[s] < 0:
            x = s; L = 0
            while x >= 0: seen[x] = 1; L += 1; x = succ[x]
            if L > bestL: bestL = L
    for s in range(ND):
        if not seen[s]:
            x = s; L = 0
            while not seen[x]: seen[x] = 1; L += 1; x = succ[x]
            if L > bestL: bestL = L          # a cycle of L nodes gives a path of L nodes
    return bestL

def extract(succ):
    ND = len(succ); pred = -np.ones(ND, np.int32)
    for a in range(ND):
        if succ[a] >= 0: pred[succ[a]] = a
    best = []
    seen = np.zeros(ND, bool)
    for s in range(ND):
        if pred[s] < 0:
            p = []; x = s
            while x >= 0: p.append(x); seen[x] = True; x = succ[x]
            if len(p) > len(best): best = p
    for s in range(ND):
        if not seen[s]:
            p = []; x = s
            while not seen[x]: p.append(x); seen[x] = True; x = succ[x]
            if len(p) > len(best): best = p
    return best

def insert_improve(path, out):
    """greedy: insert unvisited u between consecutive a,b when a->u->b; extend ends."""
    ND = out.shape[0]; S = [set(int(v) for v in out[d] if v >= 0) for d in range(ND)]
    path = list(path); ch = True
    while ch:
        ch = False; inp = set(path)
        for u in range(ND):
            if u in inp: continue
            if path[0] in S[u]: path.insert(0, u); inp.add(u); ch = True; continue
            if u in S[path[-1]]: path.append(u); inp.add(u); ch = True; continue
            for i in range(len(path) - 1):
                if u in S[path[i]] and path[i + 1] in S[u]:
                    path.insert(i + 1, u); inp.add(u); ch = True; break
    return path

if __name__ == "__main__":
    n = int(sys.argv[1]); seed = int(sys.argv[2]); iters = int(float(sys.argv[3])); R = int(sys.argv[4]); off = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    own = random_tiling(n, 400, seed)
    idx, cells, out = build(own)
    ND = len(cells); bestp = []
    S = [set(int(v) for v in out[d] if v >= 0) for d in range(ND)]
    for rs in range(R):
        succ, miss = anneal(out, iters, seed * 100 + rs + off, 0.6 if rs % 2 == 0 else 1.0, 0.08 if rs % 2 == 0 else 0.05, 0.0 if rs % 2 == 0 else 8.0)
        p = insert_improve(extract(succ), out)
        assert len(set(p)) == len(p) and all(p[i + 1] in S[p[i]] for i in range(len(p) - 1))
        if len(p) > len(bestp):
            bestp = p
            np.savez(f'path_{n}_{seed}_{off}.npz', own=own, idx=idx, cells=cells, out=out, path=np.array(bestp))
        print(n, seed, rs, 'path', len(p), 'of', ND, 'best', len(bestp), flush=True)
        if len(p) == ND: break
