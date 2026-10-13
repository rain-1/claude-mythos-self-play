"""Check the lemma F_m(x) = x^{m^2} Phi(x^{4m+6};x^4)/Phi(x^6;x^4) term by term,
where F_m = GF of half-paths (P_0=0, P_j>=1 for j>=1) ending at height m."""
N = 800
M = N + 80
def Phi(a0, step):
    res = [0] * (M + 1); j = 0
    while step * j * (j - 1) + a0 * j <= M:
        e = step * j * (j - 1) + a0 * j
        inv = [0] * (M + 1); inv[0] = 1
        for k in range(1, j + 1):
            for i in range(step * k, M + 1):
                inv[i] += inv[i - step * k]
        for i in range(M + 1 - e):
            res[i + e] += (-1) ** j * inv[i]
        j += 1
    return res
def mul(a, b):
    r = [0] * (M + 1)
    for i, ai in enumerate(a):
        if ai:
            for k in range(M + 1 - i):
                r[i + k] += ai * b[k]
    return r
def inv(a):
    r = [0] * (M + 1); r[0] = 1
    nz = [k for k in range(1, M + 1) if a[k]]
    for n in range(1, M + 1):
        r[n] = -sum(a[k] * r[n - k] for k in nz if k <= n)
    return r
# enumeration by end height
W = {1: [0, 0, 1] + [0] * (M - 2)}
F = {}
while W:
    for m, w in W.items():
        f = F.setdefault(m, [0] * (M + 1))
        for i in range(m, M + 1):
            f[i - m] += w[i]
    new = {}
    for m in set(k + s for k in W for s in (-1, 1)):
        if m < 1 or 2 * m > M: continue
        s = [0] * (M + 1)
        for p in (m - 1, m + 1):
            if p in W:
                for i in range(M + 1 - 2 * m):
                    s[i + 2 * m] += W[p][i]
        if any(s): new[m] = s
    W = new
ip = inv(Phi(6, 4))
ok = True
for m in sorted(F):
    if m * m > N: break
    pred = [0] * (m * m) + mul(Phi(4 * m + 6, 4), ip)[:M + 1 - m * m]
    if pred[:N + 1] != F[m][:N + 1]:
        ok = False; print("FAIL m =", m)
print("lemma verified for all m with m^2 <= %d, coefficients up to x^%d:" % (N, N), ok)
