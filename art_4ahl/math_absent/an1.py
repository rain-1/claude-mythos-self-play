# first look: growth of Mian-Chowla, small differences, absences
import numpy as np, math
a=np.array([int(l.split()[1]) for l in open('b005282.txt') if l.strip() and l[0]!='#'],dtype=np.int64)
n=len(a); print(n,a[:12],a[-1])
for k in [100,300,1000,3000,10000]:
    x=a[k-1]; L=math.log(k)
    print(k,x,'a/n^3=%.5f a*log/n^3=%.5f a*log^2/n^3=%.4f'%(x/k**3,x*L/k**3,x*L*L/k**3))
# local exponent
for k in [100,300,1000,3000,9000]:
    k2=int(k*1.1); print('alpha',k,(math.log(a[k2-1])-math.log(a[k-1]))/(math.log(k2)-math.log(k)))
# small differences: which d<=X present, with which pair
X=4096
first={}
for i in range(n):
    j=i-1
    while j>=0 and a[i]-a[j]<=X:
        first[int(a[i]-a[j])]=(i+1,j+1); j-=1
miss=[d for d in range(1,X+1) if d not in first]
print('missing <=256:',[d for d in miss if d<=256])
for k in range(1,12):
    lo,hi=2**k,2**(k+1); print(k,sum(1 for d in range(lo,hi) if d in first)/(hi-lo))
late=sorted(((first[d][0],d) for d in first if d<=256),reverse=True)[:12]; print('latest closers <=256',late)
print('max index used for d<=128:',max(first[d][0] for d in first if d<=128), 'for <=4096', max(first[d][0] for d in first))
g=np.diff(a); print('min gaps late:', [(int(g[k:].min()),k) for k in [100,1000,5000]])
