"""Core solvers for plaquette (2x2) energies on {0,1}^{Z^2}.

Tile convention: window [[a,b],[c,d]] = [[top-left, top-right],[bottom-left, bottom-right]],
tile index t = a + 2b + 4c + 8d.  Grid arrays are indexed grid[row, col], row increasing downward.
Energy per site e(x) = lim average over windows of J[tile].

Upper bounds: e_p = min energy per site over configurations with vertical period p
(arbitrary horizontally) = (min mean cycle of the 2^p-state column transfer graph)/p.
Every doubly periodic configuration has some vertical period p, so inf_p e_p = periodic ground energy.
Lower bounds: LP over shift-consistent probability vectors on m x n windows.
"""
import numpy as np
from numba import njit
import scipy.optimize as so
import scipy.sparse as sp


@njit(cache=True)
def build_W(J, p):
    n = 1 << p
    W = np.empty((n, n))
    for u in range(n):
        for v in range(n):
            s = 0.0
            for i in range(p):
                j = (i + 1) % p
                a = (u >> i) & 1
                b = (v >> i) & 1
                c = (u >> j) & 1
                d = (v >> j) & 1
                s += J[a + 2 * b + 4 * c + 8 * d]
            W[u, v] = s
    return W


@njit(cache=True)
def howard(W, eps, maxit=3000):
    """Howard policy iteration for minimum mean cycle. Returns (eta, pi)."""
    n = W.shape[0]
    pi = np.empty(n, np.int64)
    for u in range(n):
        pi[u] = np.argmin(W[u])
    eta = np.zeros(n)
    x = np.zeros(n)
    state = np.zeros(n, np.int64)
    stack = np.empty(n, np.int64)
    nit = 0
    for it in range(maxit):
        nit += 1
        state[:] = 0
        for s in range(n):
            if state[s] != 0:
                continue
            top = 0
            v = s
            wid = s + 1
            while state[v] == 0:
                state[v] = wid
                stack[top] = v
                top += 1
                v = pi[v]
            if state[v] == wid:
                # cycle starting at v
                tot = 0.0
                L = 0
                w = v
                while True:
                    tot += W[w, pi[w]]
                    L += 1
                    w = pi[w]
                    if w == v:
                        break
                m = tot / L
                # root = minimal-index node of the cycle (stable across iterations)
                r = v
                w = pi[v]
                while w != v:
                    if w < r:
                        r = w
                    w = pi[w]
                # collect cycle in order starting at r, assign backwards
                cyc = np.empty(L, np.int64)
                w = r
                for q in range(L):
                    cyc[q] = w
                    w = pi[w]
                x[r] = 0.0
                eta[r] = m
                state[r] = -1
                for q in range(L - 1, 0, -1):
                    w = cyc[q]
                    eta[w] = m
                    x[w] = W[w, pi[w]] - m + x[pi[w]]
                    state[w] = -1
                k = top - 1
                while stack[k] != v:
                    k -= 1
                top = k
            for q in range(top - 1, -1, -1):
                w = stack[q]
                eta[w] = eta[pi[w]]
                x[w] = W[w, pi[w]] - eta[w] + x[pi[w]]
                state[w] = -1
        changed = False
        for u in range(n):
            best = eta[pi[u]]
            bv = -1
            for v in range(n):
                if eta[v] < best - eps:
                    best = eta[v]
                    bv = v
            if bv >= 0:
                pi[u] = bv
                changed = True
        if changed:
            continue
        for u in range(n):
            best = x[u]
            bv = -1
            for v in range(n):
                if abs(eta[v] - eta[u]) <= eps:
                    val = W[u, v] - eta[u] + x[v]
                    if val < best - eps:
                        best = val
                        bv = v
            if bv >= 0:
                pi[u] = bv
                changed = True
        if not changed:
            break
    return eta, pi, nit


@njit(cache=True)
def karp(W):
    """Karp's exact minimum mean cycle value (O(n^3)), for verification."""
    n = W.shape[0]
    INF = 1e300
    D = np.full((n + 1, n), INF)
    D[0, :] = 0.0  # virtual source to all
    for k in range(1, n + 1):
        for v in range(n):
            best = INF
            for u in range(n):
                val = D[k - 1, u] + W[u, v]
                if val < best:
                    best = val
            D[k, v] = best
    res = INF
    for v in range(n):
        worst = -INF
        for k in range(n):
            if D[k, v] < INF:
                val = (D[n, v] - D[k, v]) / (n - k)
                if val > worst:
                    worst = val
        if worst < res:
            res = worst
    return res


HOWARD_FAIL = [0]


def strip_opt(J, p, eps=1e-9):
    """Return (e_p, config) where config is a p x q 0/1 array of an optimal p-vertically periodic config.
    eps is relative to max|J|*p."""
    J = np.asarray(J, float)
    W = build_W(J, p)
    eta, pi, nit = howard(W, eps * max(1.0, np.abs(J).max()) * p, 3000)
    if nit >= 3000:
        HOWARD_FAIL[0] += 1
    u0 = int(np.argmin(eta))
    # walk to cycle
    seen = set()
    v = u0
    while v not in seen:
        seen.add(v)
        v = int(pi[v])
    cyc = [v]
    w = int(pi[v])
    while w != v:
        cyc.append(w)
        w = int(pi[w])
    q = len(cyc)
    grid = np.zeros((p, q), np.int8)
    for k, c in enumerate(cyc):
        for i in range(p):
            grid[i, k] = (c >> i) & 1
    return eta[u0] / p, grid


def energy_of(J, grid):
    J = np.asarray(J, float)
    a = grid
    b = np.roll(grid, -1, axis=1)
    c = np.roll(grid, -1, axis=0)
    d = np.roll(b, -1, axis=0)
    t = a + 2 * b + 4 * c + 8 * d
    return J[t].mean()


def tile_freq(grid):
    a = grid
    b = np.roll(grid, -1, axis=1)
    c = np.roll(grid, -1, axis=0)
    d = np.roll(b, -1, axis=0)
    t = (a + 2 * b + 4 * c + 8 * d).ravel()
    return np.bincount(t, minlength=16) / t.size


def period_lattice(grid):
    """Minimal period lattice of the torus config grid (p x q). Returns (area, HNF basis
    ((dr1, dc1),(dr2,dc2))) and reduced fundamental domain grid. Periods (dr,dc): grid[r+dr, c+dc]=grid[r,c]."""
    p, q = grid.shape
    per = []
    for dr in range(p):
        for dc in range(q):
            if np.array_equal(np.roll(np.roll(grid, -dr, 0), -dc, 1), grid):
                per.append((dr, dc))
    area = p * q // len(per)
    # minimal vertical period: smallest dr>0 (or p) with (dr,0) a period
    pv = min([dr for (dr, dc) in per if dc == 0 and dr > 0] + [p])
    # smallest horizontal step h>0 such that (s,h) is a period for some s
    cands = [(dc, dr) for (dr, dc) in per if dc > 0]
    if cands:
        h, s = min(cands)
    else:
        h, s = q, 0
    s = s % pv
    assert pv * h == area, (pv, h, area)
    # fundamental domain: rows 0..pv-1, cols 0..h-1; period vectors (pv,0) and (s,h)
    return area, pv, h, s, grid[:pv, :h].copy()


def tile_patch(grid, pv, h, s, size=64):
    """Tile the plane from fundamental domain with periods (pv,0) and (s,h) (row,col)."""
    out = np.zeros((size, size), np.int8)
    for r in range(size):
        for c in range(size):
            k = c // h
            rr = (r - k * s) % pv
            out[r, c] = grid[rr, c % h]
    return out


# ---------------- LP lower bounds -----------------
_lp_cache = {}


def _lp_setup(m, n):
    """Variables: probability on {0,1}^{m x n} windows. Constraints: sum=1, marginal on left m x (n-1)
    equals right m x (n-1); top (m-1) x n equals bottom (m-1) x n. Returns (A_eq, b_eq, tilemap)
    where tilemap[w] = 2x2 tile index of the top-left 2x2 sub-window."""
    key = (m, n)
    if key in _lp_cache:
        return _lp_cache[key]
    N = 1 << (m * n)
    idx = np.arange(N)
    bits = ((idx[:, None] >> np.arange(m * n)[None, :]) & 1).reshape(N, m, n)
    rows = []
    cols = []
    data = []
    r0 = 0

    def enc(sub):
        k = sub.shape[1] * sub.shape[2]
        return (sub.reshape(N, k) << np.arange(k)[None, :]).sum(1)

    # horizontal
    L = enc(bits[:, :, :-1])
    R = enc(bits[:, :, 1:])
    K = 1 << (m * (n - 1))
    rows += [r0 + L, r0 + R]
    cols += [idx, idx]
    data += [np.ones(N), -np.ones(N)]
    r0 += K
    T = enc(bits[:, :-1, :])
    B = enc(bits[:, 1:, :])
    K = 1 << ((m - 1) * n)
    rows += [r0 + T, r0 + B]
    cols += [idx, idx]
    data += [np.ones(N), -np.ones(N)]
    r0 += K
    rows.append(np.full(N, r0))
    cols.append(idx)
    data.append(np.ones(N))
    r0 += 1
    A = sp.csr_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(r0, N))
    b = np.zeros(r0)
    b[-1] = 1
    tm = bits[:, 0, 0] + 2 * bits[:, 0, 1] + 4 * bits[:, 1, 0] + 8 * bits[:, 1, 1]
    _lp_cache[key] = (A, b, tm)
    return _lp_cache[key]


def lp_bound(J, m=3, n=3):
    A, b, tm = _lp_setup(m, n)
    # use the average over all 2x2 sub-windows for a symmetric objective (equal by consistency)
    c = np.asarray(J, float)[tm]
    res = so.linprog(c, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    if res.status != 0:
        raise RuntimeError(res.message)
    return res.fun


# ---------------- sparse strip solver for SFT faces (forbidden tiles = J >= forbid) -----------------
@njit(cache=True)
def _sparse_edges(allowed, p, maxedges):
    """All column pairs (u,v) of height p (cyclic) whose p tiles are all allowed.
    DFS over rows: state = (bit u_0, bit v_0, current u_i, v_i)."""
    src = np.empty(maxedges, np.int64)
    dst = np.empty(maxedges, np.int64)
    m = 0
    su = np.zeros(p + 1, np.int64)
    sv = np.zeros(p + 1, np.int64)
    # iterative DFS: choose (u_i,v_i) pairs for i = 0..p-1
    choice = np.zeros(p + 1, np.int64)
    for start in range(4):
        u0 = start & 1
        v0 = start >> 1
        i = 1
        choice[1] = 0
        su[0] = u0
        sv[0] = v0
        U = np.zeros(p + 1, np.int64)
        V = np.zeros(p + 1, np.int64)
        U[0] = u0
        V[0] = v0
        if p == 1:
            if allowed[u0 + 2 * v0 + 4 * u0 + 8 * v0]:
                src[m] = u0
                dst[m] = v0
                m += 1
            continue
        while i >= 1:
            if choice[i] >= 4:
                i -= 1
                if i >= 1:
                    choice[i] += 1
                continue
            uu = choice[i] & 1
            vv = choice[i] >> 1
            a = U[i - 1]
            b = V[i - 1]
            if allowed[a + 2 * b + 4 * uu + 8 * vv]:
                U[i] = uu
                V[i] = vv
                su[i] = su[i - 1] | (uu << i)
                sv[i] = sv[i - 1] | (vv << i)
                if i == p - 1:
                    if allowed[uu + 2 * vv + 4 * u0 + 8 * v0]:
                        if m >= maxedges:
                            return src, dst, -1
                        src[m] = su[i]
                        dst[m] = sv[i]
                        m += 1
                    choice[i] += 1
                else:
                    i += 1
                    choice[i] = 0
            else:
                choice[i] += 1
    return src, dst, m


@njit(cache=True)
def _edge_w(J, p, src, dst, m):
    w = np.empty(m)
    for e in range(m):
        u = src[e]
        v = dst[e]
        s = 0.0
        for i in range(p):
            j = (i + 1) % p
            s += J[((u >> i) & 1) + 2 * ((v >> i) & 1) + 4 * ((u >> j) & 1) + 8 * ((v >> j) & 1)]
        w[e] = s
    return w


@njit(cache=True)
def howard_sparse(n, indptr, nbr, wt, eps, maxit):
    """Howard on a CSR graph. Nodes without out-edges get eta=+inf. Returns eta, pi, nit."""
    INF = 1e300
    pi = np.full(n, -1, np.int64)
    for u in range(n):
        best = INF
        for e in range(indptr[u], indptr[u + 1]):
            if wt[e] < best:
                best = wt[e]
                pi[u] = e
    eta = np.full(n, INF)
    x = np.zeros(n)
    state = np.zeros(n, np.int64)
    stack = np.empty(n, np.int64)
    nit = 0
    for it in range(maxit):
        nit += 1
        state[:] = 0
        for u in range(n):
            if pi[u] < 0:
                state[u] = -1
                eta[u] = INF
        for s in range(n):
            if state[s] != 0:
                continue
            top = 0
            v = s
            wid = s + 1
            while state[v] == 0:
                state[v] = wid
                stack[top] = v
                top += 1
                v = nbr[pi[v]]
            if state[v] == wid:
                tot = 0.0
                L = 0
                w = v
                r = v
                while True:
                    tot += wt[pi[w]]
                    L += 1
                    w = nbr[pi[w]]
                    if w < r:
                        r = w
                    if w == v:
                        break
                mm = tot / L
                cyc = np.empty(L, np.int64)
                w = r
                for q in range(L):
                    cyc[q] = w
                    w = nbr[pi[w]]
                x[r] = 0.0
                eta[r] = mm
                state[r] = -1
                for q in range(L - 1, 0, -1):
                    w = cyc[q]
                    eta[w] = mm
                    x[w] = wt[pi[w]] - mm + x[nbr[pi[w]]]
                    state[w] = -1
                k = top - 1
                while stack[k] != v:
                    k -= 1
                top = k
            for q in range(top - 1, -1, -1):
                w = stack[q]
                eta[w] = eta[nbr[pi[w]]]
                x[w] = wt[pi[w]] - eta[w] + x[nbr[pi[w]]]
                state[w] = -1
        changed = False
        for u in range(n):
            if pi[u] < 0:
                continue
            best = eta[nbr[pi[u]]]
            be = -1
            for e in range(indptr[u], indptr[u + 1]):
                if eta[nbr[e]] < best - eps:
                    best = eta[nbr[e]]
                    be = e
            if be >= 0:
                pi[u] = be
                changed = True
        if changed:
            continue
        for u in range(n):
            if pi[u] < 0:
                continue
            best = x[u]
            be = -1
            for e in range(indptr[u], indptr[u + 1]):
                v = nbr[e]
                if abs(eta[v] - eta[u]) <= eps:
                    val = wt[e] - eta[u] + x[v]
                    if val < best - eps:
                        best = val
                        be = e
            if be >= 0:
                pi[u] = be
                changed = True
        if not changed:
            break
    return eta, pi, nit


def strip_opt_sft(J, p, forbid=9.0, eps=1e-9, maxedges=60_000_000):
    """Min energy per site over p-vertically-periodic configs using only allowed tiles (J<forbid).
    Returns (e_p or inf, grid or None, nedges)."""
    J = np.asarray(J, float)
    allowed = (J < forbid)
    src, dst, m = _sparse_edges(allowed, p, maxedges)
    if m < 0:
        raise MemoryError("too many edges")
    if m == 0:
        return np.inf, None, 0
    src, dst = src[:m], dst[:m]
    w = _edge_w(J, p, src, dst, m)
    # compress node ids
    nodes, inv = np.unique(np.concatenate([src, dst]), return_inverse=True)
    s2, d2 = inv[:m], inv[m:]
    order = np.argsort(s2, kind="stable")
    s2, d2, w = s2[order], d2[order], w[order]
    n = len(nodes)
    indptr = np.zeros(n + 1, np.int64)
    np.add.at(indptr, s2 + 1, 1)
    indptr = np.cumsum(indptr)
    eta, pi, nit = howard_sparse(n, indptr, d2.astype(np.int64), w, eps * max(1.0, np.abs(J[allowed]).max()) * p, 5000)
    u0 = int(np.argmin(eta))
    if eta[u0] > 1e299:
        return np.inf, None, m
    seen = set(); v = u0
    while v not in seen:
        seen.add(v); v = int(d2[pi[v]])
    cyc = [v]; wv = int(d2[pi[v]])
    while wv != v:
        cyc.append(wv); wv = int(d2[pi[wv]])
    grid = np.zeros((p, len(cyc)), np.int8)
    for k, c in enumerate(cyc):
        col = nodes[c]
        for i in range(p):
            grid[i, k] = (col >> i) & 1
    return eta[u0] / p, grid, m


def lp_bound_sft(J, m=3, n=3, forbid=9.0):
    """LP lower bound with forbidden tiles imposed as hard constraints (any 2x2 sub-window forbidden => variable removed)."""
    A, b, tm = _lp_setup(m, n)
    J = np.asarray(J, float)
    N = A.shape[1]
    idx = np.arange(N)
    bits = ((idx[:, None] >> np.arange(m * n)[None, :]) & 1).reshape(N, m, n)
    ok = np.ones(N, bool)
    for i in range(m - 1):
        for j in range(n - 1):
            t = bits[:, i, j] + 2 * bits[:, i, j + 1] + 4 * bits[:, i + 1, j] + 8 * bits[:, i + 1, j + 1]
            ok &= J[t] < forbid
    c = J[tm][ok]
    res = so.linprog(c, A_eq=A[:, ok], b_eq=b, bounds=(0, None), method="highs")
    if res.status == 2:
        return np.inf
    if res.status != 0:
        raise RuntimeError(res.message)
    return res.fun


def valid_windows(J, m, n, forbid=9.0):
    """All m x n 0/1 patterns using only allowed tiles; returns int64 codes (bit r*n+c)."""
    J = np.asarray(J, float)
    allowed = J < forbid
    R = 1 << n
    rb = (np.arange(R)[:, None] >> np.arange(n)[None, :]) & 1
    comp = np.ones((R, R), bool)
    for c in range(n - 1):
        t = rb[:, None, c] + 2 * rb[:, None, c + 1] + 4 * rb[None, :, c] + 8 * rb[None, :, c + 1]
        comp &= allowed[t]
    pats = np.arange(R, dtype=np.int64)
    last = np.arange(R, dtype=np.int64)
    for r in range(1, m):
        ii, jj = np.nonzero(comp[last])
        pats = pats[ii] | (jj.astype(np.int64) << (r * n))
        last = jj
    return pats


def lp_bound_sft_big(J, m, n, forbid=9.0, return_sol=False):
    J = np.asarray(J, float)
    P = valid_windows(J, m, n, forbid)
    N = len(P)
    if N == 0:
        return np.inf
    def sub(r0, r1, c0, c1):
        code = np.zeros(N, np.int64); k = 0
        for r in range(r0, r1):
            for c in range(c0, c1):
                code |= ((P >> (r * n + c)) & 1) << k; k += 1
        return code
    rows, cols, data = [], [], []
    r0 = 0
    idx = np.arange(N)
    for (A1, A2) in [((0, m, 0, n - 1), (0, m, 1, n)), ((0, m - 1, 0, n), (1, m, 0, n))]:
        L = sub(*A1); Rr = sub(*A2)
        u, inv = np.unique(np.concatenate([L, Rr]), return_inverse=True)
        rows += [r0 + inv[:N], r0 + inv[N:]]; cols += [idx, idx]; data += [np.ones(N), -np.ones(N)]
        r0 += len(u)
    rows.append(np.full(N, r0)); cols.append(idx); data.append(np.ones(N)); r0 += 1
    A = sp.csr_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(r0, N))
    b = np.zeros(r0); b[-1] = 1
    # objective: average of J over all 2x2 sub-windows (equal to single-window value under consistency)
    c = np.zeros(N); cnt = 0
    for i in range(m - 1):
        for j in range(n - 1):
            t = ((P >> (i * n + j)) & 1) + 2 * ((P >> (i * n + j + 1)) & 1) + 4 * ((P >> ((i + 1) * n + j)) & 1) + 8 * ((P >> ((i + 1) * n + j + 1)) & 1)
            c += J[t]; cnt += 1
    c /= cnt
    res = so.linprog(c, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    if res.status == 2:
        return np.inf
    if res.status != 0:
        raise RuntimeError(res.message)
    return (res.fun, P, res.x) if return_sol else res.fun


@njit(cache=True)
def shear_search(J, p):
    """Exact min over configurations x[r,c] = col[(r - s*c) mod p] (period lattice containing (p,0),(s,1)),
    over all columns col in {0,1}^p and shears s. Independent of the transfer-matrix code. Returns (e, col, s)."""
    best = 1e300
    bc = -1
    bs = -1
    for s in range(p):
        for col in range(1 << p):
            tot = 0.0
            for r in range(p):
                a = (col >> r) & 1
                b = (col >> ((r - s) % p)) & 1
                c = (col >> ((r + 1) % p)) & 1
                d = (col >> ((r + 1 - s) % p)) & 1
                tot += J[a + 2 * b + 4 * c + 8 * d]
                if tot >= best * p + 1e-12 and tot > 1e200:
                    break
            if tot / p < best - 1e-13:
                best = tot / p
                bc = col
                bs = s
    return best, bc, bs
