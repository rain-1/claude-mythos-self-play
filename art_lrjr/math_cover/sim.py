"""
Exact-ish simulator of the cover time T for MO 458793.

Bottom set D_R = closed disk radius R (R=1 is the problem). Top disks B_n: open,
radius r_n = n^{-1/2}, centres i.i.d. uniform in the UNIT disk.
T = min{N : D_R subset of B_1 u ... u B_N}.

Method (see RESULTS.md):
 * Uncovered set kept as leaves of quadtrees. Every live leaf carries
   - a witness point w in leaf ∩ D_R that is certified uncovered by all disks so far
   - the COMPLETE list (<= KCAP) of disks seen so far that partially overlap it
     (disks that contain the leaf kill it; disjoint disks are irrelevant).
   A leaf is refined when a new disk partially overlaps it and
   (size > r_n/F) or (list full) or (new disk covers the witness).
   Refinement is recursive (children inherit filtered lists), so a cell covered only by
   a union is split until each piece lies in a single disk (Lebesgue number argument),
   and every surviving leaf again has a certified-uncovered witness.
   => "no live leaves" <=> covered (up to a depth cap, counted as 'ambiguous').
 * Thinning by epochs [N,2N): only disks whose centre lies in
   E = union of grid squares (side s=N^{-1/2}) within distance s of a live leaf can
   matter. #relevant disks ~ Binomial(N, |E|/pi), their indices a uniform random subset,
   centres uniform in E then rejected if outside the unit disk (exact thinning).
 * Rim of D_R tracked exactly as 1D arc intervals (T_rim).
"""
import numpy as np
import numba as nb
from numba import njit
import math, time, json, sys

KCAP = 8          # max partial disks stored per leaf
F = 4.0           # refine leaves larger than r_n/F that a disk boundary crosses
CAPREL = 1e-6     # depth cap: size < CAPREL * r_n  -> ambiguous
B = 2.0           # grid offset

# ---------------------------------------------------------------- geometry
@njit(cache=True, inline='always')
def classify(x0, y0, sz, cx, cy, r):
    """0 disjoint, 1 partial, 2 contained (square closed, disk open)."""
    # closest point
    qx = min(max(cx, x0), x0 + sz)
    qy = min(max(cy, y0), y0 + sz)
    dx = qx - cx; dy = qy - cy
    r2 = r * r
    if dx * dx + dy * dy >= r2:
        return 0
    fx = max(abs(cx - x0), abs(cx - x0 - sz))
    fy = max(abs(cy - y0), abs(cy - y0 - sz))
    if fx * fx + fy * fy < r2:
        return 2
    return 1

@njit(cache=True, inline='always')
def outside_D(x0, y0, sz, R):
    qx = min(max(0.0, x0), x0 + sz)
    qy = min(max(0.0, y0), y0 + sz)
    return qx * qx + qy * qy > R * R

# ---------------------------------------------------------------- pool
def new_pool(cap):
    return dict(
        x0=np.zeros(cap), y0=np.zeros(cap), sz=np.zeros(cap),
        wx=np.zeros(cap), wy=np.zeros(cap),
        child=np.full(cap, -1, np.int64), stat=np.zeros(cap, np.int8),
        cnt=np.zeros(cap, np.int8), lst=np.zeros((cap, KCAP, 3)))

# state array st (float64): [0]=nnodes used, [1]=live, [2]=ambiguous events,
# [3]=last wx, [4]=last wy, [5]=overflow-at-cap events


@njit(cache=True)
def find_witness(cx0, cy0, h, tl, tc, R):
    """Try candidate points (centre, rim projection, corners, edge midpoints) in cell∩D_R
    not covered by any of the tc disks in tl. Returns (ok, x, y)."""
    for q in range(10):
        if q == 0:
            mx = cx0 + 0.5 * h; my = cy0 + 0.5 * h
        elif q == 1:
            mx = cx0 + 0.5 * h; my = cy0 + 0.5 * h
            d = math.sqrt(mx * mx + my * my)
            if d <= R:
                continue
            mx = mx * (R / d); my = my * (R / d)
            if mx < cx0 or mx > cx0 + h or my < cy0 or my > cy0 + h:
                continue
        elif q < 6:
            mx = cx0 + h * ((q - 2) & 1); my = cy0 + h * ((q - 2) >> 1)
        else:
            t = q - 6
            if t == 0:
                mx = cx0 + 0.5 * h; my = cy0
            elif t == 1:
                mx = cx0 + 0.5 * h; my = cy0 + h
            elif t == 2:
                mx = cx0; my = cy0 + 0.5 * h
            else:
                mx = cx0 + h; my = cy0 + 0.5 * h
        if mx * mx + my * my > R * R:
            continue
        cov = False
        for j in range(tc):
            ddx = mx - tl[j, 0]; ddy = my - tl[j, 1]
            if ddx * ddx + ddy * ddy < tl[j, 2] * tl[j, 2]:
                cov = True
                break
        if not cov:
            return True, mx, my
    return False, 0.0, 0.0

@njit(cache=True)
def refine(node, ex, ey, er, rcur, R, x0, y0, sz, wx, wy, child, stat, cnt, lst, st, cap):
    """Refine live leaf `node` given extra disk (ex,ey,er) partially overlapping it."""
    K1 = KCAP + 1
    MAXS = 400
    s_node = np.empty(MAXS, np.int64)
    s_cnt = np.empty(MAXS, np.int64)
    s_lst = np.empty((MAXS, K1, 3))
    s_ext = np.empty(MAXS, np.int8)   # does the extra disk partially overlap this node
    # initial entry: parent's list + extra disk
    sp = 0
    s_node[0] = node
    c = cnt[node]
    for j in range(c):
        s_lst[0, j, 0] = lst[node, j, 0]; s_lst[0, j, 1] = lst[node, j, 1]; s_lst[0, j, 2] = lst[node, j, 2]
    s_lst[0, c, 0] = ex; s_lst[0, c, 1] = ey; s_lst[0, c, 2] = er
    s_cnt[0] = c + 1
    s_ext[0] = 1
    sp = 1
    # node leaves the live set
    if stat[node] == 1 or stat[node] == 2:
        st[1] -= 1
    stat[node] = 3
    st[3] = wx[node]; st[4] = wy[node]
    while sp > 0:
        sp -= 1
        p = s_node[sp]
        pc = s_cnt[sp]
        pext = s_ext[sp]
        n0 = int(st[0])
        if n0 + 4 > cap:
            st[6] = 1.0  # pool overflow flag
            return
        st[0] = n0 + 4
        child[p] = n0
        stat[p] = 3
        h = sz[p] * 0.5
        # copy parent list locally (stack slot sp will be overwritten by pushes)
        plst = s_lst[sp, :pc, :].copy()
        for q in range(4):
            ci = n0 + q
            cx0 = x0[p] + h * (q & 1)
            cy0 = y0[p] + h * (q >> 1)
            x0[ci] = cx0; y0[ci] = cy0; sz[ci] = h; child[ci] = -1
            stat[ci] = 0; cnt[ci] = 0
            if outside_D(cx0, cy0, h, R):
                continue
            # filter list
            tl = np.empty((K1, 3))
            tc = 0
            dead = False
            ext_partial = False
            for j in range(pc):
                k = classify(cx0, cy0, h, plst[j, 0], plst[j, 1], plst[j, 2])
                if k == 2:
                    dead = True
                    break
                if k == 1:
                    tl[tc, 0] = plst[j, 0]; tl[tc, 1] = plst[j, 1]; tl[tc, 2] = plst[j, 2]
                    tc += 1
                    if pext == 1 and j == pc - 1 and plst[j, 0] == ex and plst[j, 1] == ey and plst[j, 2] == er:
                        ext_partial = True
            if dead:
                continue
            # witness
            valid, mx, my = find_witness(cx0, cy0, h, tl, tc, R)
            covered = False
            need = (not valid) or covered or (tc > KCAP) or (ext_partial and h > rcur / F)
            if need and h > CAPREL * rcur and sp < MAXS - 1:
                # push for further refinement
                s_node[sp] = ci
                s_cnt[sp] = tc
                for j in range(tc):
                    s_lst[sp, j, 0] = tl[j, 0]; s_lst[sp, j, 1] = tl[j, 1]; s_lst[sp, j, 2] = tl[j, 2]
                s_ext[sp] = 1 if ext_partial else 0
                # keep the 'extra disk last' convention: if ext partial it is last in tl
                sp += 1
                stat[ci] = 3  # pending
                continue
            # finalize leaf
            if need:
                st[2] += 1  # ambiguous (depth cap)
                stat[ci] = 2
            else:
                stat[ci] = 1
            if tc > KCAP:
                st[5] += 1
                tc = KCAP
            cnt[ci] = tc
            for j in range(tc):
                lst[ci, j, 0] = tl[j, 0]; lst[ci, j, 1] = tl[j, 1]; lst[ci, j, 2] = tl[j, 2]
            wx[ci] = mx; wy[ci] = my
            st[1] += 1


@njit(cache=True)
def apply_disk(cx, cy, r, roots, nroots, R, x0, y0, sz, wx, wy, child, stat, cnt, lst, st, cap, stk):
    for t in range(nroots):
        sp = 0
        stk[0] = roots[t]
        sp = 1
        while sp > 0:
            sp -= 1
            nd = stk[sp]
            s = stat[nd]
            if s == 0:
                continue
            k = classify(x0[nd], y0[nd], sz[nd], cx, cy, r)
            if k == 0:
                continue
            if s == 3:
                if child[nd] < 0:
                    continue
                if k == 2:
                    # kill whole subtree
                    kill_subtree(nd, child, stat, st, wx, wy, stk, sp)
                    continue
                c0 = child[nd]
                for q in range(4):
                    stk[sp] = c0 + q; sp += 1
                continue
            # live leaf
            if k == 2:
                if s == 1:
                    st[3] = wx[nd]; st[4] = wy[nd]
                stat[nd] = 0
                st[1] -= 1
                continue
            if s == 2:
                continue  # ambiguous leaf: only removed by containment
            # partial
            ddx = wx[nd] - cx; ddy = wy[nd] - cy
            wcov = ddx * ddx + ddy * ddy < r * r
            c = cnt[nd]
            done = False
            if c < KCAP and sz[nd] <= r / F:
                lst[nd, c, 0] = cx; lst[nd, c, 1] = cy; lst[nd, c, 2] = r
                cnt[nd] = c + 1
                if not wcov:
                    done = True
                else:
                    ok, mx, my = find_witness(x0[nd], y0[nd], sz[nd], lst[nd], c + 1, R)
                    if ok:
                        wx[nd] = mx; wy[nd] = my
                        done = True
                    else:
                        cnt[nd] = c
            if not done:
                refine(nd, cx, cy, r, r, R, x0, y0, sz, wx, wy, child, stat, cnt, lst, st, cap)
                if st[6] > 0:
                    return


@njit(cache=True)
def kill_subtree(nd, child, stat, st, wx, wy, stk, base):
    sp = base
    stk[sp] = nd; sp += 1
    while sp > base:
        sp -= 1
        a = stk[sp]
        s = stat[a]
        if s == 0:
            continue
        if s == 3:
            c0 = child[a]
            stat[a] = 0
            if c0 >= 0:
                for q in range(4):
                    stk[sp] = c0 + q; sp += 1
            continue
        if s == 1:
            st[3] = wx[a]; st[4] = wy[a]
        stat[a] = 0
        st[1] -= 1


# ---------------------------------------------------------------- rim (1D exact)
@njit(cache=True)
def rim_apply(ia, ib, nint, cx, cy, r, R):
    """uncovered closed intervals [ia,ib] subset [0,2pi]; subtract open arc of disk."""
    if nint == 0:
        return 0
    m = math.sqrt(cx * cx + cy * cy)
    if m < 1e-300:
        if r > R:
            return 0
        return nint
    q = (R * R + m * m - r * r) / (2 * R * m)
    if q >= 1.0:
        return nint
    if q < -1.0:
        return 0
    a = math.acos(q)
    phi = math.atan2(cy, cx)
    lo = phi - a; hi = phi + a
    TWO = 2 * math.pi
    # bring lo into [0,2pi)
    while lo < 0:
        lo += TWO; hi += TWO
    while lo >= TWO:
        lo -= TWO; hi -= TWO
    nint = sub_open(ia, ib, nint, lo, min(hi, TWO + 1e-300))
    if hi > TWO:
        nint = sub_open(ia, ib, nint, -1.0, hi - TWO)
    return nint

@njit(cache=True)
def sub_open(ia, ib, nint, lo, hi):
    # remove (lo,hi) from each interval; intervals stored compactly
    out_a = np.empty(nint * 2 + 2); out_b = np.empty(nint * 2 + 2)
    k = 0
    for i in range(nint):
        a = ia[i]; b = ib[i]
        if hi <= a or lo >= b:
            out_a[k] = a; out_b[k] = b; k += 1
            continue
        if a < lo:  # [a,lo] remains (closed)
            out_a[k] = a; out_b[k] = lo; k += 1
        elif a == lo:
            pass
        if hi < b:
            out_a[k] = hi; out_b[k] = b; k += 1
    if k > ia.shape[0]:
        k = ia.shape[0]  # should not happen
    for i in range(k):
        ia[i] = out_a[i]; ib[i] = out_b[i]
    return k


# ---------------------------------------------------------------- epoch kernel
@njit(cache=True)
def run_disks(ns, cxs, cys, i0, sq_keys, sq_off, sq_roots, s, R,
              x0, y0, sz, wx, wy, child, stat, cnt, lst, st, cap,
              ia, ib, rimst):
    """Process disks i0.. in order. Returns (code, i): code 0 done, 1 covered at disk i,
    2 pool nearly full (resume at i)."""
    stk = np.empty(4096, np.int64)
    nsq = sq_keys.shape[0]
    for i in range(i0, ns.shape[0]):
        if st[0] > cap - 20000:
            return 2, i
        n = ns[i]
        r = 1.0 / math.sqrt(n)
        cx = cxs[i]; cy = cys[i]
        # rim
        if rimst[0] > 0:
            nint = rim_apply(ia, ib, int(rimst[0]), cx, cy, r, R)
            rimst[0] = nint
            if nint == 0:
                rimst[1] = n
        ix = int(math.floor((cx + B) / s)); iy = int(math.floor((cy + B) / s))
        key = (ix << 32) + iy
        j = np.searchsorted(sq_keys, key)
        if j < nsq and sq_keys[j] == key:
            a = sq_off[j]; b = sq_off[j + 1]
            apply_disk(cx, cy, r, sq_roots[a:b], b - a, R, x0, y0, sz, wx, wy, child, stat, cnt, lst, st, cap, stk)
            if st[6] > 0:
                return 3, i
            if st[1] <= 0:
                return 1, i
    return 0, ns.shape[0]


# ---------------------------------------------------------------- compaction / registration
@njit(cache=True)
def compact(x0, y0, sz, wx, wy, child, stat, cnt, lst, st,
            X0, Y0, SZ, WX, WY, CH, STT, CNT, LST):
    n = int(st[0])
    k = 0
    for i in range(n):
        s = stat[i]
        if s == 1 or s == 2:
            X0[k] = x0[i]; Y0[k] = y0[i]; SZ[k] = sz[i]; WX[k] = wx[i]; WY[k] = wy[i]
            CH[k] = -1; STT[k] = s; CNT[k] = cnt[i]
            for j in range(cnt[i]):
                LST[k, j, 0] = lst[i, j, 0]; LST[k, j, 1] = lst[i, j, 1]; LST[k, j, 2] = lst[i, j, 2]
            k += 1
    return k

@njit(cache=True)
def register(x0, y0, sz, nleaf, s):
    # count
    tot = 0
    for i in range(nleaf):
        ixa = int(math.floor((x0[i] - s + B) / s)); ixb = int(math.floor((x0[i] + sz[i] + s + B) / s))
        iya = int(math.floor((y0[i] - s + B) / s)); iyb = int(math.floor((y0[i] + sz[i] + s + B) / s))
        tot += (ixb - ixa + 1) * (iyb - iya + 1)
    keys = np.empty(tot, np.int64); ids = np.empty(tot, np.int64)
    t = 0
    for i in range(nleaf):
        ixa = int(math.floor((x0[i] - s + B) / s)); ixb = int(math.floor((x0[i] + sz[i] + s + B) / s))
        iya = int(math.floor((y0[i] - s + B) / s)); iyb = int(math.floor((y0[i] + sz[i] + s + B) / s))
        for ix in range(ixa, ixb + 1):
            for iy in range(iya, iyb + 1):
                keys[t] = (ix << 32) + iy; ids[t] = i; t += 1
    order = np.argsort(keys, kind='mergesort')
    keys = keys[order]; ids = ids[order]
    # unique
    nu = 0
    for t in range(tot):
        if t == 0 or keys[t] != keys[t - 1]:
            nu += 1
    uk = np.empty(nu, np.int64); off = np.empty(nu + 1, np.int64)
    u = 0
    for t in range(tot):
        if t == 0 or keys[t] != keys[t - 1]:
            uk[u] = keys[t]; off[u] = t; u += 1
    off[nu] = tot
    return uk, off, ids


# ---------------------------------------------------------------- hole counting
@njit(cache=True)
def count_holes(x0, y0, sz, wx, wy, stat, cnt, lst, nleaf, R, rN, nbins):
    """Components (8-connected) of grid cells (side h<=rN/16, dyadic) that contain a certified
    uncovered sample point.  Returns (ncomp, hist by depth bin, ncells).
    depth bin: 0 if component reaches within rN of the rim of D_R, else 1+floor(log2(delta/rN))."""
    hist = np.zeros(nbins, np.int64)
    k = 0
    h = 2 * R
    while h > rN / 16:
        h *= 0.5
    # collect cells
    maxc = 0
    for i in range(nleaf):
        m = int(round(sz[i] / h))
        if m < 1:
            m = 1
        if m > 64:
            m = 64
        maxc += m * m
    keys = np.empty(maxc, np.int64)
    nk = 0
    for i in range(nleaf):
        if sz[i] <= h * 1.0000001:
            ix = int(math.floor((wx[i] + R) / h)); iy = int(math.floor((wy[i] + R) / h))
            keys[nk] = (ix << 31) + iy; nk += 1
            continue
        m = int(round(sz[i] / h))
        hh = sz[i] / m
        if m > 64:
            m = 64; hh = sz[i] / 64
        for a in range(m):
            for b in range(m):
                ok = False
                for u in range(3):
                    for v in range(3):
                        px = x0[i] + (a + (u + 0.5) / 3) * hh
                        py = y0[i] + (b + (v + 0.5) / 3) * hh
                        if px * px + py * py > R * R:
                            continue
                        cov = False
                        for j in range(cnt[i]):
                            dx = px - lst[i, j, 0]; dy = py - lst[i, j, 1]
                            if dx * dx + dy * dy < lst[i, j, 2] * lst[i, j, 2]:
                                cov = True; break
                        if not cov:
                            ok = True; break
                    if ok:
                        break
                if ok:
                    cxm = x0[i] + (a + 0.5) * hh; cym = y0[i] + (b + 0.5) * hh
                    ix = int(math.floor((cxm + R) / h)); iy = int(math.floor((cym + R) / h))
                    keys[nk] = (ix << 31) + iy; nk += 1
    if nk == 0:
        return 0, hist, 0
    keys = np.unique(keys[:nk])
    nk = keys.shape[0]
    par = np.arange(nk)
    for t in range(nk):
        ix = keys[t] >> 31; iy = keys[t] - (ix << 31)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                kk = ((ix + dx) << 31) + (iy + dy)
                j = np.searchsorted(keys, kk)
                if j < nk and keys[j] == kk:
                    # union
                    a = t
                    while par[a] != a:
                        par[a] = par[par[a]]; a = par[a]
                    b = j
                    while par[b] != b:
                        par[b] = par[par[b]]; b = par[b]
                    if a != b:
                        par[a] = b
    mind = np.full(nk, 1e9)
    for t in range(nk):
        a = t
        while par[a] != a:
            a = par[a]
        ix = keys[t] >> 31; iy = keys[t] - (ix << 31)
        px = (ix + 0.5) * h - R; py = (iy + 0.5) * h - R
        dd = R - math.sqrt(px * px + py * py)
        if dd < 0:
            dd = 0.0
        if dd < mind[a]:
            mind[a] = dd
    ncomp = 0
    for t in range(nk):
        if par[t] == t:
            ncomp += 1
            dd = mind[t]
            if dd < rN:
                bi = 0
            else:
                bi = 1 + int(math.floor(math.log2(dd / rN)))
            if bi >= nbins:
                bi = nbins - 1
            hist[bi] += 1
    return ncomp, hist, nk


@njit(cache=True)
def perm_fail(wx, wy, stat, nleaf, rnext):
    """R>1: a live leaf whose certified-uncovered witness is at distance >= r_next from the
    unit disk can never be covered (all future disks have centres in the unit disk)."""
    for i in range(nleaf):
        if stat[i] == 1:
            d = math.sqrt(wx[i] ** 2 + wy[i] ** 2) - 1.0
            if d >= rnext:
                return True
    return False


# ---------------------------------------------------------------- driver
class Sim:
    def __init__(self, cap=600000):
        self.cap = cap
        self.A = new_pool(cap)
        self.Bp = new_pool(cap)

    def run(self, seed, R=1.0, Nmax_log2=50, thin=True, record_disks=False, count=True,
            nbins=40, stream=None, track_from=None):
        rng = np.random.default_rng(seed)
        self.track = []
        A, Bp, cap = self.A, self.Bp, self.cap
        st = np.zeros(8)
        # root leaf
        A['x0'][0] = -R; A['y0'][0] = -R; A['sz'][0] = 2 * R
        A['wx'][0] = 0.0; A['wy'][0] = 0.0; A['child'][0] = -1
        A['stat'][0] = 1; A['cnt'][0] = 0
        st[0] = 1; st[1] = 1
        ia = np.zeros(1 << 16); ib = np.zeros(1 << 16)
        ia[0] = 0.0; ib[0] = 2 * math.pi
        rimst = np.array([1.0, -1.0])
        T = -1
        fail_at = -1
        holes = []        # per checkpoint k: (k, ncomp, hist)
        disks = [] if record_disks else None
        nproc = 0
        nleaf = 1
        for k in range(0, Nmax_log2):
            N = 1 << k
            M = N
            s = 1.0 / math.sqrt(N)
            # compact into Bp then swap
            nleaf = compact(A['x0'], A['y0'], A['sz'], A['wx'], A['wy'], A['child'], A['stat'], A['cnt'], A['lst'], st,
                            Bp['x0'], Bp['y0'], Bp['sz'], Bp['wx'], Bp['wy'], Bp['child'], Bp['stat'], Bp['cnt'], Bp['lst'])
            A, Bp = Bp, A
            st[0] = nleaf; st[1] = nleaf
            if count and k >= 1:
                nc, hist, ncell = count_holes(A['x0'], A['y0'], A['sz'], A['wx'], A['wy'], A['stat'], A['cnt'], A['lst'],
                                               nleaf, R, s, nbins)
                holes.append((k, int(nc), hist.tolist(), int(nleaf)))
            if R > 1 and k >= 1 and perm_fail(A['wx'], A['wy'], A['stat'], nleaf, s):
                fail_at = N
                break
            uk, off, ids = register(A['x0'], A['y0'], A['sz'], nleaf, s)
            areaE = len(uk) * s * s
            p = areaE / math.pi
            if stream is not None:
                Ns = len(stream[0])
                if N > Ns:
                    break
                hi = min(2 * N, Ns + 1)
                ns = np.arange(N, hi, dtype=np.float64)
                cx = np.ascontiguousarray(stream[0][N - 1:hi - 1]); cy = np.ascontiguousarray(stream[1][N - 1:hi - 1])
            elif (not thin) or p >= 0.25 or M <= 2048:
                # direct: all M disks, centres uniform in the unit disk
                m = M
                rr = np.sqrt(rng.random(m)); th = rng.random(m) * 2 * math.pi
                cx = rr * np.cos(th); cy = rr * np.sin(th)
                ns = np.arange(N, 2 * N, dtype=np.float64)
            else:
                Kd = int(rng.binomial(M, p))
                if Kd > 0:
                    idx = np.sort(rng.choice(M, size=Kd, replace=False)).astype(np.float64)
                    sq = rng.integers(0, len(uk), Kd)
                    ixs = (uk[sq] >> 32).astype(np.float64); iys = (uk[sq] - ((uk[sq] >> 32) << 32)).astype(np.float64)
                    cx = (ixs + rng.random(Kd)) * s - B
                    cy = (iys + rng.random(Kd)) * s - B
                    keep = cx * cx + cy * cy <= 1.0
                    ns = idx[keep] + N; cx = cx[keep]; cy = cy[keep]
                else:
                    ns = np.zeros(0); cx = np.zeros(0); cy = np.zeros(0)
            if record_disks:
                disks.append(np.stack([ns, cx, cy], 1))
            nproc += len(ns)
            i0 = 0
            while True:
                if track_from is not None and len(ns) and ns[-1] >= track_from:
                    # one disk at a time from track_from on: record hole count after each disk that kills/refines leaves
                    j1 = int(np.searchsorted(ns, track_from))
                    code, i = run_disks(ns[:j1], cx[:j1], cy[:j1], i0, uk, off, ids, s, R,
                                        A['x0'], A['y0'], A['sz'], A['wx'], A['wy'], A['child'], A['stat'], A['cnt'], A['lst'],
                                        st, cap, ia, ib, rimst)
                    if code in (2, 3):
                        raise RuntimeError('pool full in tracking mode; increase cap')
                    if code == 1:
                        T = int(ns[i]); break
                    for j in range(j1, len(ns)):
                        before = st[1]; bx, by = st[3], st[4]
                        code, i = run_disks(ns[j:j + 1], cx[j:j + 1], cy[j:j + 1], 0, uk, off, ids, s, R,
                                            A['x0'], A['y0'], A['sz'], A['wx'], A['wy'], A['child'], A['stat'], A['cnt'], A['lst'],
                                            st, cap, ia, ib, rimst)
                        if code in (2, 3):
                            raise RuntimeError('pool full in tracking mode; increase cap')
                        if code == 1:
                            T = int(ns[j]); self.track.append((T, 0, float(st[3]), float(st[4]))); break
                        if st[1] != before or st[3] != bx:
                            stt = st.copy()
                            nl = compact(A['x0'], A['y0'], A['sz'], A['wx'], A['wy'], A['child'], A['stat'], A['cnt'], A['lst'], stt,
                                         Bp['x0'], Bp['y0'], Bp['sz'], Bp['wx'], Bp['wy'], Bp['child'], Bp['stat'], Bp['cnt'], Bp['lst'])
                            nc, _, _ = count_holes(Bp['x0'], Bp['y0'], Bp['sz'], Bp['wx'], Bp['wy'], Bp['stat'], Bp['cnt'], Bp['lst'],
                                                   nl, R, 1 / math.sqrt(ns[j]), nbins)
                            self.track.append((int(ns[j]), int(nc), float(st[3]), float(st[4])))
                            continue
                            self.track.append((int(ns[j]), -1, float(st[3]), float(st[4])))
                    break
                code, i = run_disks(ns, cx, cy, i0, uk, off, ids, s, R,
                                    A['x0'], A['y0'], A['sz'], A['wx'], A['wy'], A['child'], A['stat'], A['cnt'], A['lst'],
                                    st, cap, ia, ib, rimst)
                if code == 1:
                    T = int(ns[i]); break
                if code == 0:
                    break
                if code == 3:
                    raise RuntimeError('pool overflow inside refine')
                # code 2: compact and continue
                nleaf = compact(A['x0'], A['y0'], A['sz'], A['wx'], A['wy'], A['child'], A['stat'], A['cnt'], A['lst'], st,
                                Bp['x0'], Bp['y0'], Bp['sz'], Bp['wx'], Bp['wy'], Bp['child'], Bp['stat'], Bp['cnt'], Bp['lst'])
                A, Bp = Bp, A
                st[0] = nleaf; st[1] = nleaf
                if nleaf * 2 > cap:
                    raise RuntimeError('too many leaves')
                uk, off, ids = register(A['x0'], A['y0'], A['sz'], nleaf, s)
                i0 = i
            if T > 0:
                break
        self.A, self.Bp = A, Bp
        res = dict(seed=int(seed), R=R, T=T, censored_at=(1 << Nmax_log2) if (T < 0 and fail_at < 0) else None,
                   fail_at=fail_at, Trim=int(rimst[1]),
                   last=[float(st[3]), float(st[4])] if T > 0 else None,
                   ambiguous=int(st[2]), overflowcap=int(st[5]), nproc=int(nproc), holes=holes)
        if record_disks:
            res['disks'] = np.concatenate(disks) if disks else np.zeros((0, 3))
        return res


if __name__ == '__main__':
    sim = Sim()
    t = time.time()
    for sd in range(5):
        r = sim.run(sd, Nmax_log2=30)
        print(sd, r['T'], r['Trim'], r['last'], r['ambiguous'], r['nproc'], [h[1] for h in r['holes']], time.time() - t)
