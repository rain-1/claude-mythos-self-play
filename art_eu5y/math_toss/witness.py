"""witness.py NMAX : for every n = r*a*b (r>=2, a>=3, b>=3, n != 18) build a stutter pair (w, w'),
check the tossprints are equal and that w' is NOT in the BTvW (ribbon) class of w."""
import sys
from collections import Counter
from verify import comp, cls
def bag(w):
    p=[(0,0)]
    for c in w: p.append((p[-1][0]+(c=='0'), p[-1][1]+(c=='1')))
    return Counter((p[j][0]-p[i][0], p[j][1]-p[i][1]) for i in range(len(p)) for j in range(i+1,len(p)))
def witness(n):
    for b in range(3, n):
        if n % b: continue
        for a in range(3, n//b):
            if (n//b) % a: continue
            r = n//(a*b)
            if r < 2: continue
            if b == 3 and r == 2: continue
            al = '0'*(a-2)+'1'
            if b >= 4: bl = ['0'*(b-2)+'1'] + ['0'*(b-3)+'10']*(r-1)
            else:      bl = ['01']*(r-1) + ['10']
            g = '0'*(r-1)
            mk = lambda A: comp(comp(g,[A]*r), [x for x in bl for _ in range(a)])
            return (r,a,b), mk(al), mk(al[::-1])
    return None
NMAX=int(sys.argv[1]); good=[]; 
for n in range(2, NMAX+1):
    t = witness(n)
    if t is None: continue
    (r,a,b), w, w2 = t
    assert len(w)==n-1 and bag(w)==bag(w2), n
    assert w2 not in cls(w, True), (n, 'ribbon-equal!')
    good.append(n)
print('n with a verified new coincidence:', good)
print(len(good), 'values up to', NMAX)
