"""Drive the C knapsack DP for n=2..24; verify small n by brute force; reconstruct champions."""
import subprocess, math
from math import lcm
from fractions import Fraction as F

def brute(n):
    # BFS over reachable fractions < 1 (small n only)
    L = lcm(*range(1, n+1))
    reach = {0}
    for k in range(2, n+1):
        w = L // k
        new = set(reach)
        # unbounded: repeat adds
        frontier = reach
        while frontier:
            nxt = set()
            for s in frontier:
                t = s + w
                if t < L and t not in new:
                    new.add(t); nxt.add(t)
            frontier = nxt
        reach = new
    return L, max(reach)

results = {}
for n in range(2, 13):
    L, best = brute(n)
    results[n] = (L, best)
    print("brute", n, L, L-best)
