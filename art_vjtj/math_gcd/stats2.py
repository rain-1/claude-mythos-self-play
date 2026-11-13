import numpy as np,sys
d=np.load(sys.argv[1]); A,C,L,F,P,G=[d[k] for k in 'ACLFPG']; lo=int(d['lo'])
n=np.arange(lo,lo+len(A))
W=n-2-L
cert=((W+1).astype(np.float64)**2>A)
comp=P==0
print('composites',n[comp].tolist())
print('  their c/n',np.round(C[comp]/n[comp],3).tolist())
print('  their W/n',np.round(W[comp]/n[comp],3).tolist())
print('  firings',F[comp].tolist())
print('  log a/log(W+1)',np.round(np.log(A[comp])/np.log(W[comp]+1.0001),2).tolist())
edges=[2,10,100,1000,10**4,10**5,10**6,2*10**6,10**7]
for lo_,hi_ in zip(edges[:-1],edges[1:]):
    s=(n>=lo_)&(n<hi_)
    if s.sum()==0: continue
    np_=np.array([True]) 
    print('[%d,%d)'%(lo_,hi_),'count',s.sum(),'composite',comp[s].sum(),'uncertified',(~cert[s]).sum(),'= %.4f'%((~cert[s]).mean()),'a(n)=n (n prime) %.3f'%(A[s]==n[s]).mean(),
      'median c',np.median(C[s]),'mean firings %.2f'%F[s].mean(),'P(c>n) %.5f'%(C[s]>n[s]).mean(),'max c/n %.2f'%(C[s]/n[s]).max())
unc=~cert
print('among uncertified: composite fraction',comp[unc].mean())
