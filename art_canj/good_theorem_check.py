"""Certificate for the zigzag window theorem, all odd p in [3, 401]:

Predicted violating (start,L) pairs for Z_p = (1, p-1, p, p-3, p-2, ..., 2, 3):
  - only PREFIX windows (start index 0) can violate;
  - odd L (1<L<p):  violation  <=>  L | p
  - even L (2<=L<=p-1): violation <=> p ≡ L/2 - 1 (mod L)
Also checks: even-L violation exists  <=>  p not of form 2^m-1,
and the minimal violating even L equals 2^(t+1), t = trailing 1-bits of p
(when p is not all-ones).
"""
def constr(p):
    a = [1]
    x = p - 1
    while x >= 2:
        a += [x, x + 1]
        x -= 2
    return a

bad_total = 0
for p in range(3, 402, 2):
    a = constr(p)
    n = p
    pre = [0]
    for v in a:
        pre.append(pre[-1] + v)
    actual = set()
    for L in range(2, n):
        for i in range(0, n - L + 1):
            if (pre[i + L] - pre[i]) % L == 0:
                actual.add((i, L))
    pred = set()
    for L in range(3, n, 2):
        if p % L == 0:
            pred.add((0, L))
    for L in range(2, n, 2):
        if p % L == L // 2 - 1:
            pred.add((0, L))
    assert actual == pred, (p, actual ^ pred)
    # even-death iff not all-ones
    evenL = sorted(L for (i, L) in pred if L % 2 == 0)
    allones = (p & (p + 1)) == 0
    assert (len(evenL) == 0) == allones, p
    if not allones:
        t = 0
        q = p
        while q & 1:
            t += 1
            q >>= 1
        assert evenL[0] == 2 ** (t + 1), (p, evenL, t)
    bad_total += len(pred)
print("ALL PREDICTIONS EXACT for odd p in [3,401];",
      "total predicted=actual violations:", bad_total)
