import sys
from math import gcd
from sympy import factorint
def trace(n):
    m=n+1;T=1;ev=[]
    for k in range(0,n-1):
        g=gcd(T,m*k+1)
        if g>1: ev.append((k,T,g,T-k,(m*(T-k)-1)))
        T+=g
    return ev,T
for n in map(int,sys.argv[1:]):
    ev,T=trace(n); c=T-(n-1); a=(n+1)*c-1
    print('n',n,'final c',c,'a',a,factorint(a))
    for k,T,g,c,N in ev: print('  k',k,'T',T,'g',g,'c',c,'N',N,dict(factorint(N)),'T/g',T//g, 'ratio T/k %.3f'%(T/max(k,1)))
