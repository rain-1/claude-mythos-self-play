"""Random equilateral polygons in R^3 (crankshaft folds, optional confinement) and their knot type
via the Alexander polynomial at t = -1, i, exp(2 pi i/3).  MO 394427."""
import numpy as np, numba as nb, sys, json, time

@nb.njit(cache=True)
def crossings(V):
    """projection to xy.  returns arrays: for each crossing (over edge, s_over, under edge, s_under, sign)"""
    n = V.shape[0]
    out = np.zeros((n * n, 5))
    m = 0
    for i in range(n):
        a = V[i]; b = V[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1: continue
            c = V[j]; d = V[(j + 1) % n]
            r0 = b[0] - a[0]; r1 = b[1] - a[1]; s0 = d[0] - c[0]; s1 = d[1] - c[1]
            den = r0 * s1 - r1 * s0
            if den == 0.0: continue
            t = ((c[0] - a[0]) * s1 - (c[1] - a[1]) * s0) / den
            w = ((c[0] - a[0]) * r1 - (c[1] - a[1]) * r0) / den
            if t <= 0 or t >= 1 or w <= 0 or w >= 1: continue
            z1 = a[2] + t * (b[2] - a[2]); z2 = c[2] + w * (d[2] - c[2])
            if z1 > z2:
                out[m, 0] = i; out[m, 1] = t; out[m, 2] = j; out[m, 3] = w; out[m, 4] = 1.0 if den > 0 else -1.0
            else:
                out[m, 0] = j; out[m, 1] = w; out[m, 2] = i; out[m, 3] = t; out[m, 4] = 1.0 if -den > 0 else -1.0
            m += 1
    return out[:m]

@nb.njit(cache=True)
def cdet(M, k):
    d = 1.0 + 0.0j
    for c in range(k):
        p = c; best = abs(M[c, c])
        for r in range(c + 1, k):
            if abs(M[r, c]) > best: best = abs(M[r, c]); p = r
        if best < 1e-12: return 0.0 + 0.0j
        if p != c:
            for q in range(k):
                tmp = M[c, q]; M[c, q] = M[p, q]; M[p, q] = tmp
            d = -d
        d *= M[c, c]
        for r in range(c + 1, k):
            f = M[r, c] / M[c, c]
            for q in range(c, k):
                M[r, q] -= f * M[c, q]
    return d

@nb.njit(cache=True)
def fingerprint(V):
    """(|D(-1)|, |D(i)|^2, |D(w)|^2) rounded; (1,1,1) for the unknot (and anything Alexander cannot see)."""
    X = crossings(V)
    c = X.shape[0]
    res = np.ones(3)
    if c < 3: return res
    # position of each crossing along the curve, as under-passage: key = under edge + s_under
    ukey = X[:, 2] + X[:, 3]
    order = np.argsort(ukey)              # under-passages in order along the knot
    # arc a (0..c-1) runs from under-passage order[a] to under-passage order[a+1]
    # the over strand at crossing q lies at position okey = X[q,0]+X[q,1]: find its arc
    sk = ukey[order]
    ts = np.array([-1.0 + 0.0j, 0.0 + 1.0j, -0.5 + 0.8660254037844386j])
    for it in range(3):
        t = ts[it]
        M = np.zeros((c, c), dtype=np.complex128)
        for r in range(c):
            q = order[r]                  # crossing whose under-passage is the r-th
            inc = (r - 1) % c             # arc arriving at this under-passage
            outg = r                      # arc leaving
            ok = X[q, 0] + X[q, 1]
            # arc containing position ok: last under-passage with key < ok (cyclic)
            a = -1
            for z in range(c):
                if sk[z] < ok: a = z
            if a == -1: a = c - 1
            if X[q, 4] > 0:
                M[r, a] += 1 - t; M[r, inc] += t; M[r, outg] += -1
            else:
                M[r, a] += 1 - t; M[r, inc] += -1; M[r, outg] += t
        d = cdet(M[:c - 1, :c - 1].copy(), c - 1)
        res[it] = abs(d) if it == 0 else abs(d) ** 2
    return np.round(res)

@nb.njit(cache=True)
def alex_at(V, t):
    X = crossings(V)
    c = X.shape[0]
    if c < 2: return 1.0 + 0.0j
    ukey = X[:, 2] + X[:, 3]
    order = np.argsort(ukey); sk = ukey[order]
    M = np.zeros((c, c), dtype=np.complex128)
    for r in range(c):
        q = order[r]; inc = (r - 1) % c; outg = r
        ok = X[q, 0] + X[q, 1]
        a = -1
        for z in range(c):
            if sk[z] < ok: a = z
        if a == -1: a = c - 1
        if X[q, 4] > 0:
            M[r, a] += 1 - t; M[r, inc] += t; M[r, outg] += -1
        else:
            M[r, a] += 1 - t; M[r, inc] += -1; M[r, outg] += t
    return cdet(M[:c - 1, :c - 1].copy(), c - 1)

def alexander(V, M=64):
    """integer coefficients of the Alexander polynomial, by interpolation at the M-th roots of unity"""
    vals = np.array([alex_at(np.ascontiguousarray(V), np.exp(2j * np.pi * k / M)) for k in range(M)])
    co = np.fft.fft(vals) / M           # coefficient of t^j is sum vals * exp(-2 pi i jk/M) / M
    assert np.abs(co.imag).max() < 1e-6 and np.abs(co.real - np.round(co.real)).max() < 1e-6, co
    co = np.round(co.real).astype(int)
    nz = np.nonzero(co)[0]
    co = co[nz[0]:nz[-1] + 1]
    if co[0] < 0: co = -co
    return co.tolist()

@nb.njit(cache=True)
def rot(P, a, b, ang):
    """rotate point P about axis a->b"""
    k = b - a; k = k / np.sqrt((k * k).sum())
    v = P - a
    c = np.cos(ang); s = np.sin(ang)
    kxv = np.array([k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0]])
    return a + v * c + kxv * s + k * (k * v).sum() * (1 - c)

@nb.njit(cache=True)
def seg_dist(p1, q1, p2, q2):
    d1 = q1 - p1; d2 = q2 - p2; r = p1 - p2
    a = (d1 * d1).sum(); e = (d2 * d2).sum(); f = (d2 * r).sum()
    c = (d1 * r).sum(); b = (d1 * d2).sum(); den = a * e - b * b
    s = 0.0
    if den > 1e-14: s = min(1.0, max(0.0, (b * f - c * e) / den))
    t = (b * s + f) / e
    if t < 0: t = 0.0; s = min(1.0, max(0.0, -c / a))
    elif t > 1: t = 1.0; s = min(1.0, max(0.0, (b - c) / a))
    x = p1 + d1 * s - p2 - d2 * t
    return np.sqrt((x * x).sum())

@nb.njit(cache=True)
def thickness(V):
    n = V.shape[0]; best = 1e9
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1: continue
            d = seg_dist(V[i], V[(i + 1) % n], V[j], V[(j + 1) % n])
            if d < best: best = d
    return best

@nb.njit(cache=True)
def rg2(W):
    n = W.shape[0]
    cx = np.zeros(3)
    for k in range(n): cx += W[k]
    cx /= n
    m = 0.0
    for k in range(n):
        d = W[k] - cx
        m += (d * d).sum()
    return m / n

@nb.njit(cache=True)
def maxrad(W):
    n = W.shape[0]
    cx = np.zeros(3)
    for k in range(n): cx += W[k]
    cx /= n
    m = 0.0
    for k in range(n):
        d = W[k] - cx
        m = max(m, (d * d).sum())
    return np.sqrt(m)

@nb.njit(cache=True)
def anneal(V, iters, seed, sig0):
    """maximise the minimum distance between non-adjacent sticks without changing the knot type"""
    np.random.seed(seed)
    n = V.shape[0]
    f0 = fingerprint(V); th = thickness(V); bth = th; B = V.copy()
    for it in range(iters):
        sig = sig0 * (1 - 0.9 * it / iters)
        i = np.random.randint(n); j = np.random.randint(n)
        if i > j: i, j = j, i
        if j - i < 2 or (i == 0 and j == n - 1): continue
        ang = np.random.normal() * sig
        W = V.copy()
        for k in range(i + 1, j): W[k] = rot(V[k], V[i], V[j], ang)
        t2 = thickness(W)
        temp = 0.004 * (1 - it / iters) ** 2
        if t2 < th and (temp <= 0 or np.random.random() > np.exp((t2 - th) / temp)): continue
        # no stick passed through another if the move was small and thickness stayed positive; check anyway
        f = fingerprint(W)
        if f[0] != f0[0] or f[1] != f0[1] or f[2] != f0[2]: continue
        V[:] = W; th = t2
        if th > bth: bth = th; B[:] = V
    V[:] = B
    return bth

@nb.njit(cache=True)
def fold(V, R):
    n = V.shape[0]
    i = np.random.randint(n); j = np.random.randint(n)
    if i == j: return
    if i > j: i, j = j, i
    if j - i < 2 and not (i == 0 and j == n - 1): 
        pass
    ang = np.random.uniform(-np.pi, np.pi)
    W = V.copy()
    for k in range(i + 1, j):
        W[k] = rot(V[k], V[i], V[j], ang)
    if R > 0:
        # soft compaction: Metropolis weight exp(-R * n * Rg^2)   (R plays the role of a pressure)
        d = R * n * (rg2(W) - rg2(V))
        if d > 0 and np.random.random() > np.exp(-d): return
    V[:] = W

@nb.njit(cache=True)
def census(n, R, nsamp, seed, nfold):
    np.random.seed(seed)
    V = np.zeros((n, 3))
    for k in range(n):
        V[k, 0] = np.cos(2 * np.pi * k / n); V[k, 1] = np.sin(2 * np.pi * k / n)
    V /= 2 * np.sin(np.pi / n)
    for _ in range(2000): fold(V, R)
    keys = np.zeros((64, 3)); cnt = np.zeros(64, np.int64); bestth = np.zeros(64); bestV = np.zeros((64, n, 3)); nk = 0
    for s in range(nsamp):
        for _ in range(nfold): fold(V, R)
        f = fingerprint(V)
        if f[0] == 1 and f[1] == 1 and f[2] == 1: continue
        idx = -1
        for z in range(nk):
            if keys[z, 0] == f[0] and keys[z, 1] == f[1] and keys[z, 2] == f[2]: idx = z
        if idx == -1:
            if nk == 64: continue
            idx = nk; nk += 1; keys[idx] = f
        cnt[idx] += 1
        th = thickness(V)
        if th > bestth[idx]: bestth[idx] = th; bestV[idx] = V
    return keys[:nk], cnt[:nk], bestth[:nk], bestV[:nk]

def poly_fp(coeffs):
    out = []
    for t, sq in [(-1, False), (1j, True), (np.exp(2j * np.pi / 3), True)]:
        v = abs(np.polyval(coeffs, t)); out.append(round(v * v if sq else v))
    return tuple(out)
TABLE = {'3_1': [1, -1, 1], '4_1': [1, -3, 1], '5_1': [1, -1, 1, -1, 1], '5_2': [2, -3, 2], '6_1': [2, -5, 2],
         '6_2': [1, -3, 3, -3, 1], '6_3': [1, -3, 5, -3, 1], '8_19': [1, -1, 0, 1, 0, -1, 1],
         '3_1#3_1 / 8_20': [1, -2, 3, -2, 1], '7_1': [1, -1, 1, -1, 1, -1, 1], '3_1#4_1': [1, -4, 5, -4, 1]}
FP = {poly_fp(c): k for k, c in TABLE.items()}

def torus(p, q, N=400):
    t = np.linspace(0, 2 * np.pi, N, endpoint=False)
    r = 2 + np.cos(q * t)
    V = np.c_[r * np.cos(p * t), r * np.sin(p * t), np.sin(q * t)]
    # random rotation so the projection is generic
    rng = np.random.default_rng(1); Q, _ = np.linalg.qr(rng.standard_normal((3, 3)))
    return V @ Q

if __name__ == "__main__":
    if sys.argv[1] == 'test':
        print(FP)
        for (p, q) in [(2, 3), (2, 5), (3, 4), (2, 7), (3, 5)]:
            print('torus', p, q, fingerprint(torus(p, q)))
    else:
        n = int(sys.argv[2]); R = float(sys.argv[3]); ns = int(sys.argv[4]); seed = int(sys.argv[5])
        t0 = time.time()
        keys, cnt, th, bv = census(n, R, ns, seed, n)
        res = []
        for k, c, t_, v in zip(keys, cnt, th, bv):
            res.append(dict(fp=[int(x) for x in k], name=FP.get(tuple(int(x) for x in k), '?'), count=int(c), thick=float(t_), V=v.tolist()))
        res.sort(key=lambda r: -r['count'])
        json.dump(dict(n=n, R=R, samples=ns, seed=seed, res=res), open('census_n%d_R%g_s%d.json' % (n, R, seed), 'w'))
        print('n', n, 'R', R, 'samples', ns, 'time %.0fs' % (time.time() - t0))
        for r in res: print('  ', r['name'], r['fp'], r['count'], 'thick %.3f' % r['thick'])
