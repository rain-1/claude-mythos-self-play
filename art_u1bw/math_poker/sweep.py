import sys, time, pickle
from core import *
N=int(sys.argv[1]); L=int(sys.argv[2]); lo=float(sys.argv[3]); hi=float(sys.argv[4]); out=sys.argv[5]
nrand=int(sys.argv[6]) if len(sys.argv)>6 else 3
g,H=grid(N); X=g[:,None]; Y=g[None,:]
lams=np.geomspace(lo,hi,L)
rng=np.random.default_rng(1)
def sym(R): return (R+R.T)/2
base={'call':np.ones((N,N)),'fold':np.zeros((N,N)),
 'max<.3':(np.maximum(X,Y)<.3)*1.,'max<.7':(np.maximum(X,Y)<.7)*1.,
 'diag.1':(np.abs(X-Y)<.1)*1.,'diag.3':(np.abs(X-Y)<.3)*1.,'min>.5':(np.minimum(X,Y)>.5)*1.,
 'sq+diag':((np.maximum(X,Y)<.4)|(np.abs(X-Y)<.05))*1.}
results={}
def run(lam,name,S0):
    S,D,r,res=robust(S0,H,lam)
    return dict(S=S,D=D,regret=r,res=res,init=name)
t0=time.time()
prev=None
for i,lam in enumerate(lams):
    inits=dict(base)
    for k in range(nrand): inits[f'rand{k}']=sym(rng.random((N,N)))
    inits['rand_blocky']=sym(np.kron(rng.random((8,8)),np.ones((N//8,N//8)))>0.5)*1.
    if prev is not None: inits['cont_up']=prev
    results[lam]=[run(lam,k,S0) for k,S0 in inits.items()]
    good=[x for x in results[lam] if x['res']<1e-3 and x['regret']<5e-4]
    prev=min(results[lam],key=lambda x:x['regret'])['S']
    print(i,'%.4f'%lam,len(good),'/',len(inits),' means',sorted(set(round(x['S'].mean(),3) for x in good)),'%.0fs'%(time.time()-t0),flush=True)
# downward continuation
prev=None
for lam in lams[::-1]:
    if prev is not None:
        results[lam].append(run(lam,'cont_down',prev))
    prev=min(results[lam],key=lambda x:x['regret'])['S']
pickle.dump(dict(lams=lams,N=N,results=results),open(out,'wb'))
print('done',time.time()-t0)
