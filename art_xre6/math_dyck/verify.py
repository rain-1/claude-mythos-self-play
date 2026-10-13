"""Enumerate d(n) via half-path transfer and verify the MO 515969 conjecture exactly."""
import sys, json, time
import numpy as np
N0 = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
N = N0 + int(2 * N0 ** 0.5) + 10  # headroom: final step divides by x^m

def shift(a, k):  # multiply series by x^k (k may be negative), truncate to deg N
    out = np.zeros(N + 1, dtype=object)
    if k >= 0:
        out[k:] = a[:N + 1 - k]
    else:
        out[:N + 1 + k] = a[-k:]
    return out

# --- 1. transfer-matrix enumeration ---
t = time.time()
A = np.zeros(N + 1, dtype=object)
W = {1: shift(np.array([1] + [0] * N, dtype=object), 2)}  # W[m]: weight x^{2 sum_{i<=j} P_i}
while W:
    for m, w in W.items():          # end here: last vertex weighs x^m, not x^{2m}
        A += shift(w, -m)
    new = {}
    for m in set(k + d for k in W for d in (-1, 1)):
        if m < 1 or 2 * m > N:
            continue
        s = np.zeros(N + 1, dtype=object)
        for p in (m - 1, m + 1):
            if p in W:
                s = s + W[p]
        s = shift(s, 2 * m)
        if any(s):
            new[m] = s
    W = new
d = [int(v) for v in A][:N0 + 1]
print("enumeration done", time.time() - t, "s")

# --- 2. conjectured formula, exact integer series in x ---
def inv_qpoch(j, step):  # 1/(x^step; x^step)_j
    a = [0] * (N + 1); a[0] = 1
    for k in range(1, j + 1):
        s = step * k
        for i in range(s, N + 1):
            a[i] += a[i - s]
    return a

def Phi(a0, step):  # Phi(x^a0; x^step) truncated
    res = [0] * (N + 1)
    j = 0
    while True:
        e = step * j * (j - 1) + a0 * j
        if e > N:
            break
        inv = inv_qpoch(j, step)
        sg = (-1) ** j
        for i in range(N + 1 - e):
            res[i + e] += sg * inv[i]
        j += 1
    return res

def mul(a, b):
    r = [0] * (N + 1)
    for i, ai in enumerate(a):
        if ai:
            for k in range(N + 1 - i):
                r[i + k] += ai * b[k]
    return r

def inv(a):
    assert a[0] == 1
    r = [0] * (N + 1); r[0] = 1
    for n in range(1, N + 1):
        r[n] = -sum(a[k] * r[n - k] for k in range(1, n + 1) if a[k])
    return r

t = time.time()
S = [0] * (N + 1)
r = 0
while r * (r + 2) + 1 <= N:
    e = r * (r + 2) + 1
    ph = Phi(4 * r + 10, 4)
    for i in range(N + 1 - e):
        S[i + e] += ph[i]
    r += 1
conj = mul(S, inv(Phi(6, 4)))
print("formula done", time.time() - t, "s")
print("first terms", d[:40])
bad = [n for n in range(N0 + 1) if d[n] != conj[n]]
print("N =", N0, "mismatches:", bad[:10])
json.dump(d, open(f"d_upto_{N0}.json", "w"))
