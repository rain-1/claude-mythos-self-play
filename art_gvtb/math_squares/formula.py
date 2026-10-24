# Check exact formula for b when n > m^2/4 - 1, and the iff-theorem (a=2b <=> gcd in c and N nonsquare)
import math
from sympy import factorint, divisor_count
from verify import b_brute, inc
def r2(N):
    r=4
    for p,e in factorint(N).items():
        if p%4==1: r*=e+1
        elif p%4==3 and e%2: return 0
    return r
bad=0;cnt=0
for m in range(1,61):
    for n in range(max(1,(m*m+3)//4), m*m//2+1001):
        N=n*n+m*m; sq=math.isqrt(N)**2==N
        if (n-m)%2: f=(r2(N)//4+sq)//2
        elif n%2: f=r2(N)//4
        else: f=r2(N//4)//4
        b=b_brute(n,m); a=int(divisor_count(N)); cnt+=1
        if b!=f: bad+=1; print("formula fail",n,m)
        if (a==2*b)!=(inc(math.gcd(n,m)) and not sq): bad+=1; print("iff fail",n,m)
print("cases",cnt,"failures",bad)
