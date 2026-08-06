"""Factor-certify an l=5 equal-gap run of consecutive members of
S = { n : v_p(n) even for all primes p ≡ 3,5 mod 8 }  (norms of Z[sqrt2]).
Usage: python3 certify_run.py START GAP [L]
Checks: all L posts in S (full factorization printed), all inter-post windows
contain NO member of S, and the flanking neighbours break the pattern."""
import sys
from sympy import factorint

def inS(n):
    if n <= 0:
        return False
    return all(e % 2 == 0 for p, e in factorint(n).items() if p % 8 in (3, 5))

def main():
    start, gap = int(sys.argv[1]), int(sys.argv[2])
    L = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    posts = [start + i * gap for i in range(L)]
    ok = True
    for p in posts:
        f = factorint(p)
        good = all(e % 2 == 0 for q, e in f.items() if q % 8 in (3, 5))
        print(f"  {p} = {' * '.join(f'{q}^{e}' if e>1 else str(q) for q,e in sorted(f.items()))}"
              f"   {'IN S' if good else 'NOT IN S  <-- FAIL'}")
        ok &= good
    for i in range(L - 1):
        for m in range(posts[i] + 1, posts[i + 1]):
            if inS(m):
                print(f"  WINDOW VIOLATION: {m} in S inside ({posts[i]}, {posts[i+1]})")
                ok = False
    lo = next(m for m in range(posts[0] - 1, 0, -1) if inS(m))
    hi = next(m for m in range(posts[-1] + 1, posts[-1] + 10**6) if inS(m))
    print(f"  flanking members: {lo} (gap {posts[0]-lo}), {hi} (gap {hi-posts[-1]})")
    if posts[0] - lo == gap or hi - posts[-1] == gap:
        print("  NOT MAXIMAL (flank continues the pattern)")
        ok = False
    print("CERTIFIED" if ok else "FAILED")

if __name__ == "__main__":
    main()
