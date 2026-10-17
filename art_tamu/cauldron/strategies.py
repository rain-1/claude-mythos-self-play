"""Exact expectations of simple strategies for permutation Wordle, n <= 8 (enumerate all n! secrets).
  CircularShift (Kutin-Smithline): guess identity; keep correct entries, rotate the wrong values one step
      right cyclically among the wrong positions.  Claimed: #guesses = exc(w)+1, distribution = Eulerian A(n,k).
  FirstConsistent: guess the lexicographically first permutation consistent with all feedback so far
      (Stanley's 'simple observation'-type strategy, deterministic tie-break)."""
import itertools, sys
from math import factorial
from fractions import Fraction
from collections import Counter

def circular_shift(w):
    n = len(w); g = list(range(n)); k = 0
    while True:
        k += 1
        wrong = [i for i in range(n) if g[i] != w[i]]
        if not wrong: return k
        vals = [g[i] for i in wrong]
        vals = vals[-1:] + vals[:-1]          # shift wrong values one step right (cyclically)
        for i, v in zip(wrong, vals): g[i] = v

def first_consistent(w):
    n = len(w); known = [None]*n; banned = [set() for _ in range(n)]; k = 0
    while True:
        # lexicographically first permutation with g[i]=known[i] and g[i] not in banned[i]
        g = [None]*n; used = [False]*n
        def bt(i):
            if i == n: return True
            opts = [known[i]] if known[i] is not None else range(n)
            for v in opts:
                if not used[v] and v not in banned[i]:
                    used[v] = True; g[i] = v
                    if bt(i+1): return True
                    used[v] = False
            return False
        assert bt(0)
        k += 1
        if list(g) == list(w): return k
        for i in range(n):
            if g[i] == w[i]: known[i] = g[i]
            else: banned[i].add(g[i])

def exc(w): return sum(1 for i, x in enumerate(w) if x > i)

if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    for n in range(1, N+1):
        for name, f in (('CircularShift', circular_shift), ('FirstConsistent', first_consistent)):
            if name == 'FirstConsistent' and n > 7: continue
            dist = Counter(); tot = 0; excok = True
            for w in itertools.permutations(range(n)):
                k = f(w); dist[k] += 1; tot += k
                if name == 'CircularShift' and k != exc(w)+1: excok = False
            E = Fraction(tot, factorial(n))
            extra = ('  k==exc+1 for all w: %s' % excok) if name == 'CircularShift' else ''
            print('n=%d %-15s E=%s (=(n+1)/2? %s) dist=%s%s' % (n, name, E, E == Fraction(n+1, 2),
                  [dist[i] for i in range(1, max(dist)+1)], extra), flush=True)
