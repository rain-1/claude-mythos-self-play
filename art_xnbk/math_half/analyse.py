import csv, sys, collections
from util import factor, divisors
f = sys.argv[1]
r = list(csv.DictReader(open(f)))
ok = [x for x in r if x['half_ok'] == '1']; bad = [x for x in r if x['half_ok'] == '0']
print('odd abundant', len(r), 'counterexamples', len(bad))
def sig(m): return sum(divisors(m))
types = collections.Counter(); rows = []
for x in bad:
    n = int(x['n']); fa = factor(n); p = max(fa); e = fa[p]; m = n // p**e
    sm = sig(m); ab = sm > 2*m; perf = sm == 2*m
    rows.append((n, m, p, e, sm, p/sm))
    types[(m, e, 'abund' if ab else ('perfect' if perf else 'DEFICIENT'))] += 1
print('cofactor m = n/p^e (p largest prime):')
for k, v in sorted(types.items()): print('  ', k, 'sigma(m)=', sig(k[0]), 'count', v,
     'p range', min(r_[2] for r_ in rows if r_[1]==k[0] and r_[3]==k[1]), max(r_[2] for r_ in rows if r_[1]==k[0] and r_[3]==k[1]))
print('min p/sigma(m) among counterexamples', min(r_[5] for r_ in rows))
# among numbers n = m*p with these m: which p pass?
# h/n among good
hn = sorted(int(x['h'])/int(x['n']) for x in ok)
print('h/n among non-counterexamples: min %.5f  median %.5f  max %.5f' % (hn[0], hn[len(hn)//2], hn[-1]))
w = min(ok, key=lambda x: int(x['h'])/int(x['n'])); print('argmin', w, factor(int(w['n'])))
c = collections.Counter(int(x['nonrep']) for x in r)
print('nonrep count distribution (top):', sorted(c.items())[:12], '... number with nonrep<=8:', sum(v for k,v in c.items() if k<=8))
Lc = collections.Counter(int(x['L']) for x in ok); print('L (largest nonrep below n/2) among good, most common:', Lc.most_common(15))
print('good n with L>100:', sum(1 for x in ok if int(x['L'])>100))
