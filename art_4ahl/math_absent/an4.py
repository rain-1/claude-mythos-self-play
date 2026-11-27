# differences: Sidon check, density by octave vs the law, gap statistics, survival of an open difference
import numpy as np, math, json
from mpmath import mp, quad, mpf, gamma, pi, sqrt, identify, pslq, log
a=np.array([int(l.split()[1]) for l in open('b005282.txt') if l.strip() and l[0]!='#'],dtype=np.int64)
n=len(a)
# --- constants
mp.dps=25
third=mpf(1)/3
def inner(z):
    w=z**3
    if w==0: w=mpf(10)**-40
    return quad(lambda u:(u*(1+w-u))**(-2*third),[w,(1+w)/2,1])
I=3*quad(inner,[0,mpf(1)/8,mpf(1)/2,1]); print('I =',I)
K=quad(lambda t: t**(-mpf(1)/3)-t**(-mpf(2)/3)*(t-1)**(mpf(1)/3),[1,2,10,mp.inf]); J=mpf(1)/2+K/3; print('J =',J)
G=gamma(mpf(1)/3)
for name,val in [('I',I),('J',J)]:
    r=None if not mp.isfinite(val) else pslq([val,G**3,G**3/pi,G**3/sqrt(3),G**3/(pi*sqrt(3)),G**6/pi**2,pi,sqrt(3)*pi,1],maxcoeff=2000,maxsteps=100000); print(name,'pslq',r)
I=float(I); J=float(J); kap=I/54
# --- all differences up to XMAX
XMAX=1<<27
ds=[]
for i in range(1,n):
    j0=np.searchsorted(a,a[i]-XMAX,'left'); ds.append(a[i]-a[j0:i])
D=np.sort(np.concatenate(ds)); print('diffs<=2^27:',len(D),'distinct:',len(np.unique(D))==len(D))
allcnt=n*(n-1)//2
# full Sidon check via sums
print('octave  observed-density   J*(L X)^(2/3)/X  ratio')
rows=[]
for k in range(5,27):
    lo,hi=1<<k,1<<(k+1)
    c=np.searchsorted(D,hi)-np.searchsorted(D,lo)
    # law: N(X)=J*(L(X) X)^(2/3), L evaluated at the term nearest X
    def N(X):
        m=np.searchsorted(a,X); m=max(m,2); L=m**3/float(a[m-1]); return J*(L*X)**(2/3)
    pred=(N(hi)-N(lo))/(hi-lo)
    rows.append((k,c/(hi-lo),pred)); print(k,'%.5f %.5f %.3f'%(c/(hi-lo),pred,c/(hi-lo)/pred))
json.dump(rows,open('octaves.json','w'))
# cumulative
for k in [10,14,18,22,26]:
    X=1<<k; c=np.searchsorted(D,X,'right'); m=np.searchsorted(a,X); L=m**3/float(a[m-1])
    print('X=2^%d |D|=%d  /X^(2/3)=%.3f  J*L^(2/3)=%.3f'%(k,c,c/X**(2/3),J*L**(2/3)))
# --- gap statistics: u=g/gbar
gp=np.diff(a).astype(float); h=50
gb=np.array([ (a[min(i+h,n-1)]-a[max(i-h,0)])/(min(i+h,n-1)-max(i-h,0)) for i in range(n-1)])
u=(gp/gb)[500:]
for t in [0.003,0.01,0.03,0.1,0.3,1,2,4]:
    print('P(g/gbar<%.3f)=%.4f  exp:%.4f'%(t,(u<t).mean(),1-math.exp(-t)))
# --- hazard for an open small difference: T(N)=sum_{m>N} 1/gbar_m (+ tail integral L/(3N)-ish)
inv=1/gb; tail=lambda N: (N**3/float(a[N-1]))/(3*N)   # crude tail beyond data
T=lambda N: inv[N-1:].sum()+ (n**3/float(a[-1]))/(2.84*n)
for N in [50,100,200,500,1000,3000,10000]:
    print('T(%d)=%.4f'%(N,T(N) if N<n else (n**3/float(a[-1]))/(2.84*n)))
# test: open d<=Dm at time N, how many closed later?
def openclose(N,Dm):
    S=set()
    for i in range(N):
        for j in range(i): 
            d=int(a[i]-a[j])
            if d<=Dm:S.add(d)
    op=[d for d in range(1,Dm+1) if d not in S]
    later=set(D[D<=Dm].tolist())
    cl=[d for d in op if d in later]; return len(op),len(cl)
for N,Dm in [(60,200),(100,400),(200,1500),(400,5000),(800,20000)]:
    o,c=openclose(N,Dm); print('N=%d d<=%d open=%d closed later=%d frac=%.4f  T(N)=%.4f  gbar=%.0f'%(N,Dm,o,c,c/o,T(N),gb[N]))
