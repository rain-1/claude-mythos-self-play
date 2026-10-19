import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "1")
import numpy as np
from numba import njit
import math


@njit(cache=True)
def xs(s):
    s ^= (s << np.uint64(13)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    s ^= s >> np.uint64(7)
    s ^= (s << np.uint64(17)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    return s


@njit(cache=True)
def run(p, N, seed, stride):
    """Simulate N rows (row 0 = single 1). Float64 values with per-row
    log-rescaling. Returns per-row arrays (every `stride` rows):
    logS (ln of row sum), logM (ln of row max), zfrac (fraction of zeros),
    plus cumulative ln(sum of all entries in rows 0..n)."""
    thr = np.uint64(int(p * 4294967296.0))
    s = np.uint64(seed * 2654435761 + 88172645463325252)
    for _ in range(10):
        s = xs(s)
    cur = np.zeros(N + 2)
    nxt = np.zeros(N + 2)
    cur[0] = 1.0
    L = 0.0  # log scale: true value = stored * exp(L)
    K = N // stride + 1
    logS = np.empty(K)
    logM = np.empty(K)
    zf = np.empty(K)
    logC = np.empty(K)
    cum = 1.0
    cumL = 0.0
    logS[0] = 0.0; logM[0] = 0.0; zf[0] = 0.0; logC[0] = 0.0
    edge = 1.0
    for n in range(1, N + 1):
        edge = math.exp(-L)
        nxt[0] = edge
        nxt[n] = edge
        S = 2 * edge
        M = edge
        z = 0
        r = np.uint64(0)
        for k in range(1, n):
            if (k & 1) == 1:
                s = xs(s)
                r = s & np.uint64(0xFFFFFFFF)
            else:
                r = s >> np.uint64(32)
            a = cur[k - 1]
            b = cur[k]
            if r < thr:
                v = a + b
            else:
                v = abs(a - b)
            nxt[k] = v
            S += v
            if v > M:
                M = v
            if v == 0.0:
                z += 1
        # rescale
        if M > 1e150:
            f = 1.0 / M
            for k in range(n + 1):
                nxt[k] *= f
            S *= f
            L += math.log(M)
            M = 1.0
        tmp = cur; cur = nxt; nxt = tmp
        lS = math.log(S) + L
        # cumulative sum in log domain
        if lS > cumL:
            cum = cum * math.exp(cumL - lS) + 1.0
            cumL = lS
        else:
            cum += math.exp(lS - cumL)
        if n % stride == 0:
            i = n // stride
            logS[i] = lS
            logM[i] = math.log(M) + L
            zf[i] = z / (n + 1)
            logC[i] = math.log(cum) + cumL
    return logS, logM, zf, logC


@njit(cache=True)
def triangle(p, N, seed):
    thr = np.uint64(int(p * 4294967296.0))
    s = np.uint64(seed * 2654435761 + 88172645463325252)
    for _ in range(10):
        s = xs(s)
    T = -np.ones((N, N))
    C = np.zeros((N, N), dtype=np.uint8)
    T[0, 0] = 1.0
    for n in range(1, N):
        T[n, 0] = 1.0
        T[n, n] = 1.0
        for k in range(1, n):
            s = xs(s)
            a = T[n - 1, k - 1]
            b = T[n - 1, k]
            if (s >> np.uint64(32)) < thr:
                T[n, k] = a + b
                C[n, k] = 1
            else:
                T[n, k] = abs(a - b)
    return T, C


@njit(cache=True)
def triangle_int(p, N, seed):
    """exact int64 version (for small N/p), returns overflow flag"""
    thr = np.uint64(int(p * 4294967296.0))
    s = np.uint64(seed * 2654435761 + 88172645463325252)
    for _ in range(10):
        s = xs(s)
    T = -np.ones((N, N), dtype=np.int64)
    C = np.zeros((N, N), dtype=np.uint8)
    T[0, 0] = 1
    ov = False
    for n in range(1, N):
        T[n, 0] = 1
        T[n, n] = 1
        for k in range(1, n):
            s = xs(s)
            a = T[n - 1, k - 1]
            b = T[n - 1, k]
            if (s >> np.uint64(32)) < thr:
                if a > 4611686018427387903 or b > 4611686018427387903:
                    ov = True
                T[n, k] = a + b
                C[n, k] = 1
            else:
                T[n, k] = abs(a - b)
    return T, C, ov


@njit(cache=True)
def ring(p, W, T, seed, init, stride):
    """Periodic ring of width W, x'_k = f(x_{k-1}, x_k). init: 0=all ones,
    1=uniform random in (0,1), 2=single 1 at site 0 (others 0).
    Returns ln(row sum) and ln(row max) every stride rows, and zero fraction."""
    thr = np.uint64(int(p * 4294967296.0))
    s = np.uint64(seed * 2654435761 + 88172645463325252)
    for _ in range(10):
        s = xs(s)
    x = np.zeros(W)
    y = np.zeros(W)
    for k in range(W):
        if init == 0:
            x[k] = 1.0
        elif init == 1:
            s = xs(s)
            x[k] = ((s >> np.uint64(11)) + 1) / 9007199254740993.0
    if init == 2:
        x[0] = 1.0
    L = 0.0
    K = T // stride + 1
    lS = np.empty(K); lM = np.empty(K); zf = np.empty(K)
    lS[0] = math.log(x.sum()); lM[0] = math.log(x.max()); zf[0] = 0.0
    r = np.uint64(0)
    for t in range(1, T + 1):
        S = 0.0; M = 0.0; z = 0
        for k in range(W):
            if (k & 1) == 0:
                s = xs(s)
                r = s & np.uint64(0xFFFFFFFF)
            else:
                r = s >> np.uint64(32)
            a = x[k - 1] if k > 0 else x[W - 1]
            b = x[k]
            if r < thr:
                v = a + b
            else:
                v = abs(a - b)
            y[k] = v
            S += v
            if v > M:
                M = v
            if v == 0.0:
                z += 1
        if M == 0.0:
            # died
            for i in range(t // stride + 1, K):
                lS[i] = -np.inf; lM[i] = -np.inf; zf[i] = 1.0
            break
        if M > 1e100 or M < 1e-100:
            f = 1.0 / M
            for k in range(W):
                y[k] *= f
            S *= f
            L += math.log(M)
            M = 1.0
        tmp = x; x = y; y = tmp
        if t % stride == 0:
            i = t // stride
            lS[i] = math.log(S) + L
            lM[i] = math.log(M) + L
            zf[i] = z / W
    return lS, lM, zf


@njit(cache=True)
def ring_from(p, x0, T, seed, stride):
    """Same as ring but from given state x0 (copied); returns lS,lM,zf,final state (normalized)."""
    thr = np.uint64(int(p * 4294967296.0))
    s = np.uint64(seed * 2654435761 + 88172645463325252)
    for _ in range(10):
        s = xs(s)
    W = x0.shape[0]
    x = x0.copy()
    y = np.zeros(W)
    L = 0.0
    K = T // stride + 1
    lS = np.full(K, -np.inf); lM = np.full(K, -np.inf); zf = np.ones(K)
    lS[0] = math.log(x.sum()); lM[0] = math.log(x.max()); zf[0] = 0.0
    r = np.uint64(0)
    for t in range(1, T + 1):
        S = 0.0; M = 0.0; z = 0
        for k in range(W):
            if (k & 1) == 0:
                s = xs(s)
                r = s & np.uint64(0xFFFFFFFF)
            else:
                r = s >> np.uint64(32)
            a = x[k - 1] if k > 0 else x[W - 1]
            b = x[k]
            if r < thr:
                v = a + b
            else:
                v = abs(a - b)
            y[k] = v
            S += v
            if v > M:
                M = v
            if v == 0.0:
                z += 1
        if M == 0.0:
            break
        if M > 1e100 or M < 1e-100:
            f = 1.0 / M
            for k in range(W):
                y[k] *= f
            S *= f
            L += math.log(M)
            M = 1.0
        tmp = x; x = y; y = tmp
        if t % stride == 0:
            i = t // stride
            lS[i] = math.log(S) + L
            lM[i] = math.log(M) + L
            zf[i] = z / W
    return lS, lM, zf, x / x.max()


@njit(cache=True)
def cloning(p, N, P, seed):
    """Population-dynamics estimate of ln E[S_n] for n=0..N (triangle from single 1).
    P copies, multinomial-systematic resampling each row proportional to S_n/S_{n-1}.
    Returns array lnES[n]."""
    thr = np.uint64(int(p * 4294967296.0))
    s = np.uint64(seed * 2654435761 + 88172645463325252)
    for _ in range(10):
        s = xs(s)
    A = np.zeros((P, N + 2))
    B = np.zeros((P, N + 2))
    Ls = np.zeros(P)       # log scale of each copy
    lSold = np.zeros(P)    # ln S of each copy (true)
    for i in range(P):
        A[i, 0] = 1.0
    out = np.zeros(N + 1)
    lw = np.zeros(P)
    lSnew = np.zeros(P)
    idx = np.zeros(P, dtype=np.int64)
    acc = 0.0
    for n in range(1, N + 1):
        for i in range(P):
            edge = math.exp(-Ls[i])
            row = A[i]
            nrow = B[i]
            nrow[0] = edge; nrow[n] = edge
            S = 2 * edge; M = edge
            for k in range(1, n):
                s = xs(s)
                a = row[k - 1]; b = row[k]
                if (s >> np.uint64(32)) < thr:
                    v = a + b
                else:
                    v = abs(a - b)
                nrow[k] = v
                S += v
                if v > M:
                    M = v
            if M > 1e150:
                f = 1.0 / M
                for k in range(n + 1):
                    nrow[k] *= f
                S *= f
                Ls[i] += math.log(M)
            lSnew[i] = math.log(S) + Ls[i]
            lw[i] = lSnew[i] - lSold[i]
        mx = lw.max()
        tot = 0.0
        for i in range(P):
            tot += math.exp(lw[i] - mx)
        acc += mx + math.log(tot / P)
        out[n] = acc
        # systematic resampling
        s = xs(s)
        u = ((s >> np.uint64(11)) / 9007199254740992.0) / P
        c = 0.0; j = 0
        cw = math.exp(lw[0] - mx) / tot
        for i in range(P):
            target = u + i / P
            while cw < target and j < P - 1:
                j += 1
                cw += math.exp(lw[j] - mx) / tot
            idx[i] = j
        # copy B[idx] -> A
        for i in range(P):
            j = idx[i]
            for k in range(n + 1):
                A[i, k] = B[j, k]
        Ls2 = Ls.copy(); l2 = lSnew.copy()
        for i in range(P):
            Ls[i] = Ls2[idx[i]]
            lSold[i] = l2[idx[i]]
    return out


@njit(cache=True)
def ring_from2(p, x0, T, seed, stride):
    """Same as ring but from given state x0 (copied); returns lS,lM,zf,final state (normalized)."""
    thr = np.uint64(int(p * 4294967296.0))
    s = np.uint64(seed * 2654435761 + 88172645463325252)
    for _ in range(10):
        s = xs(s)
    W = x0.shape[0]
    x = x0.copy()
    y = np.zeros(W)
    L = 0.0
    K = T // stride + 1
    lS = np.full(K, -np.inf); lM = np.full(K, -np.inf); zf = np.ones(K); lG = np.zeros(K); fs = np.zeros(K)
    lS[0] = math.log(x.sum()); lM[0] = math.log(x.max()); zf[0] = 0.0
    r = np.uint64(0)
    for t in range(1, T + 1):
        S = 0.0; M = 0.0; z = 0
        for k in range(W):
            if (k & 1) == 0:
                s = xs(s)
                r = s & np.uint64(0xFFFFFFFF)
            else:
                r = s >> np.uint64(32)
            a = x[k - 1] if k > 0 else x[W - 1]
            b = x[k]
            if r < thr:
                v = a + b
            else:
                v = abs(a - b)
            y[k] = v
            S += v
            if v > M:
                M = v
            if v == 0.0:
                z += 1
        if M == 0.0:
            break
        if M > 1e100 or M < 1e-100:
            f = 1.0 / M
            for k in range(W):
                y[k] *= f
            S *= f
            L += math.log(M)
            M = 1.0
        tmp = x; x = y; y = tmp
        if t % stride == 0:
            i = t // stride
            lS[i] = math.log(S) + L
            lM[i] = math.log(M) + L
            zf[i] = z / W
            ml = 0.0; cnt = 0; small = 0
            for k in range(W):
                if x[k] > 0:
                    ml += math.log(x[k]); cnt += 1
                if x[k] < 1e-20 * M:
                    small += 1
            lG[i] = ml / max(cnt, 1) + L
            fs[i] = small / W
    return lS, lM, zf, lG, fs, x / x.max()
