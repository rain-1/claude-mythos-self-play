def factor(n):
    f = {}; p = 2
    while p*p <= n:
        while n % p == 0: f[p] = f.get(p, 0)+1; n //= p
        p += 1
    if n > 1: f[n] = f.get(n, 0)+1
    return f
def divisors(n):
    ds = [1]
    for p, e in factor(n).items():
        ds = [d*p**k for d in ds for k in range(e+1)]
    return sorted(ds)
def subset_bits(ds, M=None):
    b = 1
    if M is None: M = sum(ds)
    mask = (1 << (M+1)) - 1
    for d in ds: b |= (b << d) & mask
    return b
def nonrep(n):
    ds = divisors(n); s = sum(ds); b = subset_bits(ds)
    return [x for x in range(s+1) if not (b >> x) & 1]
