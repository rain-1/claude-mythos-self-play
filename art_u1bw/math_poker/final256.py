import sys,time,numpy as np
from core import *
def cluster(rs,tol=0.01):
    reps=[]
    for r in sorted(rs,key=lambda x:x['regret']):
        if all(np.abs(r['S']-q['S']).mean()>tol for q in reps): reps.append(r)
    return reps
def runset(N,lams,initnames,out):
    g,H=grid(N); rng=np.random.default_rng(2); t0=time.time()
    allreps=[]; prev=None
    for lam in lams:
        inits={'call':np.ones((N,N)),'fold':np.zeros((N,N)),'rand':(lambda R:(R+R.T)/2)(rng.random((N,N)))}
        inits={k:inits[k] for k in initnames}
        if prev is not None: inits['cont']=prev
        rs=[]
        for k,S0 in inits.items():
            S,D,r,res=robust(S0,H,lam); rs.append(dict(S=S,D=D,regret=r,res=res))
        good=[x for x in rs if x['regret']<5e-4]
        reps=cluster(good); allreps.append(reps); prev=reps[0]['S']
        print(N,'%.4f'%lam,'distinct',len(reps),'regrets',['%.1e'%x['regret'] for x in rs],'res',['%.0e'%x['res'] for x in rs],'%.0fs'%(time.time()-t0),flush=True)
    K=max(len(r) for r in allreps); L=len(lams)
    sig=np.full((L,K,N,N),np.nan,np.float32); dl=np.full((L,K,N,N),np.nan,np.float32); reg=np.full((L,K),np.nan)
    for i,reps in enumerate(allreps):
        for k,r in enumerate(reps): sig[i,k]=r['S']; dl[i,k]=r['D']; reg[i,k]=r['regret']
    np.savez_compressed(out,lam=np.array(lams),sig=sig,delta=dl,count=np.array([len(r) for r in allreps]),regret=reg,grid=g,T_final=1e-3)
runset(256,np.array([0.1,0.6,1.5]),['call'],'maps.npz')
print('done')
