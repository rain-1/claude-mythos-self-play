"""First nonzero Neumann eigenfunction on a smooth simply connected planar domain (5-point graph Laplacian on a
mask = Neumann). openai/math family 369 claims: no interior critical point, extrema on the boundary."""
import numpy as np, scipy.sparse as sp
from scipy.sparse.linalg import eigsh
def domain(kind,N):
    y,x=np.mgrid[-1.2:1.2:N*1j,-1.2:1.2:N*1j]; r=np.hypot(x,y); t=np.arctan2(y,x)
    if kind=='bean':    R=0.82+0.16*np.cos(t)-0.10*np.cos(2*t)+0.05*np.sin(3*t)
    elif kind=='peanut':R=0.60+0.36*np.cos(t)**2-0.05*np.sin(t)+0.03*np.cos(3*t)
    elif kind=='star':  R=0.80+0.13*np.cos(5*t)+0.06*np.cos(2*t+0.4)
    elif kind=='pear':  R=0.78+0.20*np.sin(t)+0.06*np.cos(3*t)
    elif kind=='blob':  R=0.80+0.10*np.cos(2*t+0.5)+0.08*np.cos(3*t+1.3)+0.05*np.cos(5*t+0.2)
    elif kind=='comma': R=0.75+0.22*np.cos(t)+0.12*np.sin(2*t)+0.05*np.cos(4*t)
    return (r<R),x,y
def neumann_mode(mask):
    idx=-np.ones(mask.shape,int); idx[mask]=np.arange(mask.sum()); n=mask.sum()
    rows=[];cols=[];vals=[]; deg=np.zeros(n)
    for dy,dx in ((0,1),(1,0)):
        a=mask[:mask.shape[0]-dy,:mask.shape[1]-dx]&mask[dy:,dx:]
        i=idx[:mask.shape[0]-dy,:mask.shape[1]-dx][a]; j=idx[dy:,dx:][a]
        rows+= [i,j]; cols+=[j,i]; vals+=[-np.ones(len(i))]*2
        np.add.at(deg,i,1); np.add.at(deg,j,1)
    L=sp.csr_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(n,n))+sp.diags(deg)
    w,V=eigsh(L,k=3,sigma=-1e-3,which='LM')
    o=np.argsort(w); u=V[:,o[1]]; lam=w[o[1]]; lam2=w[o[2]]
    U=np.full(mask.shape,np.nan); U[mask]=u
    if np.nanmax(U)<-np.nanmin(U): U=-U
    return U,lam,lam2
if __name__=="__main__":
    for k in ['bean','peanut','star','pear','blob','comma']:
        m,x,y=domain(k,240); U,l,l2=neumann_mode(m)
        # interior critical point check: max/min distance to boundary
        from scipy.ndimage import distance_transform_edt
        dist=distance_transform_edt(m)
        imx=np.nanargmax(U); imn=np.nanargmin(U)
        print(k, 'lam %.5f gap %.4f'%(l,l2/l), 'max at dist',dist.flat[imx],'min at dist',dist.flat[imn])
