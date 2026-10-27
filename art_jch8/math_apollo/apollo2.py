import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, sys, time
def build(m):
    E=[np.array([(0,1),(1,2),(0,2),(0,3),(1,3),(2,3)])]
    F=np.array([(0,1,3),(1,2,3),(0,2,3)]); n=4
    for _ in range(m):
        k=len(F); v=np.arange(n,n+k); n+=k
        E.append(np.stack([np.repeat(v,3),F.ravel()],1))
        F=np.concatenate([np.stack([F[:,0],F[:,1],v],1),np.stack([F[:,1],F[:,2],v],1),np.stack([F[:,0],F[:,2],v],1)])
    e=np.concatenate(E).astype(np.int32)
    A=sp.csr_matrix((np.ones(len(e),np.float64),(e[:,0],e[:,1])),shape=(n,n)); return (A+A.T).tocsr(),n
for m in map(int,sys.argv[1:]):
    t=time.time(); A,n=build(m)
    w,V=sla.eigsh(A,k=4,which='LA',tol=1e-10); o=np.argsort(-w); w=w[o]; V=V[:,o]
    v=V[:,1]; s=2**(m/2)
    print(m,n,' '.join(f'{x:.6f}' for x in w),'th2/2^(m/2)=%.6f th2-sqrt(2^(m+1))=%.6f'%(w[1]/s,w[1]-np.sqrt(2**(m+1))),
      'v[a,b,c,o]=',np.round(v[:4],4),'%.0fs'%(time.time()-t),flush=True)
    if m<=9: np.savez(f'mode_m{m}.npz',w=w,V=V)
