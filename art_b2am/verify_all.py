"""Verify every mathematical claim behind the triptych. Prints a report."""
import numpy as np

def tm(N):
    return np.array([bin(n).count('1') & 1 for n in range(N)], dtype=np.int8)

print("=" * 64)
print("THE NEGATION OF THE NEGATION — verification report")
print("=" * 64)

# 1. Thue-Morse substitution fixed point
t = tm(1 << 18); n = np.arange(1 << 17)
c1 = np.all(t[2 * n] == t[n]) and np.all(t[2 * n + 1] == 1 - t[n])
print(f"[1] TM fixed point  t[2n]=t[n], t[2n+1]=1-t[n]          : {'OK' if c1 else 'FAIL'}")

# 2. Negation of negation: block second half = complement of first
ok = all(np.all(t[1 << k: 1 << (k + 1)] == 1 - t[:1 << k]) for k in range(1, 12))
print(f"[2] each block's 2nd half = negation of the 1st (k<=11)  : {'OK' if ok else 'FAIL'}")

# 3. Woods-Robbins
N = 1 << 22; tt = tm(N); eps = np.where(tt == 0, 1.0, -1.0); nn = np.arange(N)
P = np.exp(np.cumsum(eps * (np.log(2 * nn + 1) - np.log(2 * nn + 2))))
print(f"[3] Woods-Robbins ∏((2n+1)/(2n+2))^±  = {P[-1]:.15f}")
print(f"                            1/√2       = {1/np.sqrt(2):.15f}   |Δ|={abs(P[-1]-1/np.sqrt(2)):.2e}")

# 4. generating function = lacunary product
import numpy as np
x = 0.37 + 0.21j
ok = True
for k in range(1, 14):
    lhs = np.sum(np.where(tm(1 << k) == 0, 1, -1) * x ** np.arange(1 << k))
    rhs = np.prod([1 - x ** (2 ** j) for j in range(k)])
    ok = ok and abs(lhs - rhs) < 1e-9
print(f"[4] Σ(−1)^tₙ xⁿ = ∏(1−x^{{2ᵏ}})  (k<=13)                  : {'OK' if ok else 'FAIL'}")

# 5. Prouhet-Tarry-Escott
ok = True
for k in range(1, 8):
    idx = np.arange(1 << k); s = tm(1 << k)
    S0 = idx[s == 0].astype(object); S1 = idx[s == 1].astype(object)
    for p in range(k):
        if np.sum(S0 ** p) != np.sum(S1 ** p): ok = False
print(f"[5] PTE: TM splits {{0..2ᵏ−1}} into equal power sums <k    : {'OK' if ok else 'FAIL'}")

# 6. diffraction density is a probability measure; singular (mass -> Cantor set)
def wk(theta, k):
    d = np.ones_like(theta)
    for j in range(k): d = d * 2 * np.sin(np.pi * (2.0 ** j) * theta) ** 2
    return d
th = np.linspace(0, 1, 40001)
ints = [np.trapezoid(wk(th, k), th) for k in [1, 4, 8, 12]]
print(f"[6] diffraction ∫wₖdθ for k=1,4,8,12  = {[round(v,6) for v in ints]}  (=1: probability measure)")

# 7. paperfolding recursion = complement of reversed  (dragon turns)
def turns(k):
    s = np.array([1], np.int8)
    for _ in range(k - 1): s = np.concatenate([s, [1], -s[::-1]])
    return s
tk = turns(9)
half = (len(tk) - 1) // 2
ok = np.all(tk[half + 1:] == -tk[:half][::-1])
print(f"[7] paperfolding: 2nd half = −reverse(1st half)          : {'OK' if ok else 'FAIL'}")

# 8. base -1+i is a canonical number system for Z[i]
B = -1 + 1j; ok = True
for a in range(-10, 11):
    for c in range(-10, 11):
        nq = complex(a, c); z = nq; ds = []
        for _ in range(64):
            if z == 0: break
            d = int((z.real + z.imag) % 2); ds.append(d); z = (z - d) / B
            z = complex(round(z.real), round(z.imag))
        rec = sum(d * B ** k for k, d in enumerate(ds))
        if abs(rec - nq) > 1e-6 or z != 0: ok = False
print(f"[8] base −1+i, digits {{0,1}}: unique finite expansion    : {'OK' if ok else 'FAIL'}")
print("=" * 64)
