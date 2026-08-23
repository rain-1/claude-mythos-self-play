import sympy

def member(n):
    """n a norm of Z[sqrt2]: primes p = 3,5 mod 8 appear to even powers."""
    f = sympy.factorint(n)
    bad = {p: e for p, e in f.items() if p % 8 in (3, 5) and e % 2 == 1}
    return len(bad) == 0, f

start = 458171603806
print("start mod 144 =", start % 144, " (gate theorem demands 94)")
print("start mod 16  =", start % 16, " (demands 14);  mod 9 =", start % 9, " (demands 4)")
for k in range(-1, 6):
    n = start + 25*k
    ok, f = member(n)
    fs = '*'.join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    print(f"k={k:+d} n={n} member={ok}  {fs}")
# straddler check: any l=5 g=25 run with start in [4e11-124, 4e11)?
lo = 400000000000-124
for s in range(lo, 400000000000):
    if s % 144 == 94:
        run = all(member(s+25*j)[0] for j in range(5))
        print("straddler candidate", s, "l5run:", run)
print("straddler scan done")
