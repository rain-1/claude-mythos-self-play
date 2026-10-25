import json
from util import divisors
n = 945; ds = divisors(n); S = sum(ds); T = (n+1)//2
counts = [0]*(S+1); counts[0] = 1
for d in ds:
    for x in range(S, d-1, -1): counts[x] += counts[x-d]
subs = []
def rec(i, rem, cur):
    if rem == 0: subs.append(list(cur)); return
    if i < 0 or rem < 0: return
    if sum(ds[:i+1]) < rem: return
    cur.append(ds[i]); rec(i-1, rem-ds[i], cur); cur.pop()
    rec(i-1, rem, cur)
rec(len(ds)-1, T, [])
subs = [sorted(s, reverse=True) for s in subs]
subs.sort(key=lambda s: (len(s), [-x for x in s]))
assert len(subs) == counts[T] and all(sum(s) == T for s in subs)
nonrep = [x for x in range(S+1) if counts[x] == 0]
out = dict(n=n, divisors=ds, proper_divisors=ds[:-1], sigma=S, target=T,
           counts_note="counts[x] = number of subsets of ALL 16 divisors of 945 with sum x, x=0..1920 (length 1921); counts[x]==counts[1920-x]",
           counts=counts, nonrepresentable=nonrep, total_subsets=sum(counts),
           subsets_473=subs, n_subsets_473=len(subs),
           n_subsets_473_without_1=sum(1 for s in subs if 1 not in s),
           subsets_473_by_size={k: sum(1 for s in subs if len(s) == k) for k in sorted({len(s) for s in subs})},
           max_count=max(counts), argmax_count=[x for x in range(S+1) if counts[x] == max(counts)])
json.dump(out, open('945.json', 'w'))
print(len(subs), out['n_subsets_473_without_1'], out['subsets_473_by_size'], nonrep, max(counts), out['argmax_count'], counts[T])
print(subs[:5])
