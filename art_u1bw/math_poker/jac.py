import pickle,numpy as np
from core import *
d=pickle.load(open('sweep64.pkl','rb')); N=64; g,H=grid(N)
out=[]
for lam in d['lams']:
  S=min(d['results'][lam],key=lambda x:x['regret'])['S']; D=delta(S,H,lam)
  M=np.argwhere((S>0.02)&(S<0.98)); M=M[M[:,0]<=M[:,1]]
  n=len(M); J=np.zeros((n,n)); eps=1e-6
  for k,(i,j) in enumerate(M):
    E=np.zeros((N,N)); E[i,j]+=eps; E[j,i]=eps
    J[:,k]=((delta(S+E,H,lam)-D)/eps)[M[:,0],M[:,1]]
  sv=np.linalg.svd(J,compute_uv=False)
  # call-square side and diagonal band width at x=y=0.75
  i75=int(0.75*N); row=S[i75]; band=np.sum(row>0.5)/N
  a=0
  for t in range(N):
    if S[:t+1,:t+1].min()>0.5: a=(t+1)/N
  out.append((lam,n,sv[0],sv[-1],np.sum(sv<1e-3*sv[0]),np.sum(sv<1e-2*sv[0]),S.mean(),a,band))
  print('%.4f n=%d cond=%.1e n<1e-3:%d n<1e-2:%d mean=%.3f square=%.3f band@.75=%.3f'%(lam,n,sv[0]/sv[-1],out[-1][4],out[-1][5],S.mean(),a,band),flush=True)
np.save('jac64.npy',np.array(out))
