"""MO 514605 — dynasty analysis of the Collatz delay-record breakers.

Mechanism: if n ≡ 1 (mod 3), then m = (4n-1)/3 is odd and its full-map
trajectory is m -> 3m+1 = 4n -> 2n -> n, so delay(m) = delay(n) + 3 and
m/n = 4/3 - 1/(3n).  Likewise delay(2n) = delay(n) + 1 (ratio 2).
A record breaker that inherits its trajectory from the previous one this way
is a *dynasty child*; the 4/3 median in the record ratios is inheritance.

Input: b006877.txt (Roosendaal delay records, n <= 1.47e19), independently
verified below our census bound by collatz.c.
"""
import json

def delay_and_odd(n):
    d = o = 0
    while n != 1:
        if n & 1: n = 3*n+1; o += 1
        else: n >>= 1
        d += 1
    return d, o

def trajectory_hits(m, target, cap=3000):
    """steps j such that full trajectory of m reaches target (or None)."""
    j = 0
    while m != 1 and j < cap:
        if m == target: return j
        if m & 1: m = 3*m+1
        else: m >>= 1
        j += 1
    return j if m == target else None

R = [int(l.split()[1]) for l in open('b006877.txt') if l.strip() and not l.startswith('#')]
print(f"{len(R)} records, last = {R[-1]:.3e}")

recs = []
for n in R:
    d, o = delay_and_odd(n)
    recs.append((n, d, o))
# monotonicity check (they are records of d)
assert all(b[1] > a[1] for a, b in zip(recs, recs[1:])), "delay not increasing!"
print("delay strictly increasing across all 148: OK")

links = []
for (n1, d1, o1), (n2, d2, o2) in zip(recs, recs[1:]):
    ratio = n2 / n1
    if n2 == 2*n1:
        typ = 'double'          # delay +1
    elif 3*n2 == 4*n1 - 1:
        typ = 'four-thirds'     # delay +3
    else:
        j = trajectory_hits(n2, n1)
        typ = f'desc@{j}' if j is not None else 'founder'
    links.append((n1, n2, d2-d1, ratio, typ))

from collections import Counter
cnt = Counter(t if not t.startswith('desc') else 'desc' for *_, t in links)
print("link types:", dict(cnt))
print("descendant distances:", [t for *_, t in links if t.startswith('desc')])

import statistics
ratios = [r for *_, r, _t in links]
print(f"ratios: median={statistics.median(ratios):.6f} mean={statistics.mean(ratios):.4f} "
      f"min={min(ratios):.4f} max={max(ratios):.2f}")
ft = [r for *_, r, t in links if t=='four-thirds']
print(f"four-thirds links: {len(ft)}/{len(links)}, their ratios all = 4/3 - 1/(3n): "
      f"max dev from 4/3 = {max(abs(x-4/3) for x in ft):.2e}")

# dynasty chains: maximal runs of consecutive four-thirds (or double) links
chains = []; cur = 1
for *_, t in links:
    if t in ('four-thirds','double') or t.startswith('desc'):
        cur += 1
    else:
        chains.append(cur); cur = 1
chains.append(cur)
print(f"dynasties (chains between founders): {len(chains)}, lengths: {sorted(chains, reverse=True)[:12]}...")
print(f"founders: {sum(1 for *_,t in links if t=='founder')+1} of {len(R)}")

# per-window statistics of the ratio (does the 4/3 share grow?)
H = len(links)//3
for i,(a,b) in enumerate([(0,H),(H,2*H),(2*H,len(links))]):
    part = links[a:b]
    fr = sum(1 for *_,t in part if t=='four-thirds')/len(part)
    med = statistics.median([r for *_,r,_ in part])
    print(f"third {i+1}: 4/3-link share {fr:.2f}, median ratio {med:.6f}")

json.dump([(str(a),str(b),dd,r,t) for a,b,dd,r,t in links], open('links.json','w'))
print("wrote links.json")
