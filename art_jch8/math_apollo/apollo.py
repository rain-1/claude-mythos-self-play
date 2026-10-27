import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, sys, time
def build(m):
    # vertices 0=a,1=b,2=c,3=o ; faces inner
    edges=[(0,1),(1,2),(0,2),(0,3),(1,3),(2,3)]
    faces=[(0,1,3),(1,2,3),(0,2,3)]; n=4
    for _ in range(m):
        nf=[]
        for (x,y,z) in faces:
            v=n; n+=1; edges+= [(v,x),(v,y),(v,z)]
            nf+=[(x,y,v),(y,z,v),(x,z,v)]
        faces=nf
    e=np.array(edges); A=sp.coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(n,n)); A=(A+A.T).tocsr()
    return A,n
for m in range(1,int(sys.argv[1])+1):
    A,n=build(m); t=time.time()
    k=min(4,n-2)
    w=np.sort(sla.eigsh(A,k=k,which='LA',tol=1e-12)[0])[::-1] if n>50 else np.sort(np.linalg.eigvalsh(A.toarray()))[::-1][:4]
    s=2**(m/2)
    print(m,n,' '.join(f'{x:.6f}' for x in w), ' th2/2^(m/2)=%.6f th2-sqrt(2^(m+1))=%.6f th1^2/2^m=%.4f'%(w[1]/s,w[1]-np.sqrt(2**(m+1)),w[0]**2/2**m),'%.1fs'%(time.time()-t),flush=True)
