import numpy as np, sys, rsn, tubes, time
from scipy import ndimage as ndi
from PIL import Image
def hexrgb(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
WHEEL=[hexrgb(h) for h in ['f58ba3','f8a98a','f7d27a','bfe08a','86d9bd','8cc8f0','a3acf2','c79ff0','f3a1d6']]
def wheel(u):
    u=np.clip(u,0,1)*(len(WHEEL)-1); i=np.minimum(u.astype(int),len(WHEEL)-2); f=(u-i)[:,None]
    A=np.array(WHEEL)
    return np.exp(np.log(A[i])*(1-f)+np.log(A[i+1])*f)
def render(n=120,seed=1,W=1600,H=1000,out='flat.png',ss=2,rad=None,margin=0.06,bold=12,bfac=3.2,fade=0.55):
    w=rsn.network(n,seed); P=rsn.trajectories(n,w); N=len(w)
    W2,H2=W*ss,H*ss
    x0,x1=margin*W2,(1-margin)*W2; y0,y1=0.07*H2,0.80*H2
    zb=np.full((H2,W2),-1e9); nrm=np.zeros((H2,W2,3)); ib=np.full((H2,W2),-1,np.int64); ub=np.zeros((H2,W2),np.int64)
    if rad is None: rad=0.30*(y1-y0)/n
    sig=N/n*0.6; sigb=N/n*1.6
    Xs=[];Ys=[];Zs=[];Rs=[];Cs=[]
    t=np.arange(N+1)
    for i in range(n):
        y=ndi.gaussian_filter1d(P[:,i].astype(float),sigb if (i%bold==bold//2) else sig,mode='nearest')
        dy=np.gradient(y)
        Q=np.stack([x0+(x1-x0)*t/N, y0+(y1-y0)*(y+0.5)/n, np.tanh(dy*n/4)],1)
        Q=tubes.resample(Q,0.35*rad)
        isb=(i%bold==bold//2)
        rr_=rad*(bfac if isb else 1.0)
        Q=tubes.resample(Q[::1],0.35*rr_) if isb else Q
        Xs.append(Q[:,0]);Ys.append(Q[:,1]);Zs.append(Q[:,2]*rad*1.5+(1000 if isb else 0));Rs.append(np.full(len(Q),rr_));Cs.append(np.full(len(Q),i+(n if isb else 0)))
    X=np.concatenate(Xs);Y=np.concatenate(Ys);Z=np.concatenate(Zs);R=np.concatenate(Rs);C=np.concatenate(Cs)
    tubes.splat(X,Y,Z,R,C,W2,H2,zb,nrm,ib,ub)
    # shadow
    M=np.zeros((H2,W2)); big=R>rad*1.5; tubes.splat_mask(X[big]+1.2*R[big],Y[big]+1.8*R[big],R[big]*1.05,W2,H2,M,np.ones(big.sum()))
    M=ndi.gaussian_filter(M,1.0*rad*bfac)
    paper=np.array([0.992,0.985,0.975])
    img=np.ones((H2,W2,3))*paper
    img=img*(1-0.22*M[...,None]*np.array([1.0,0.95,0.7])[None,None])   # lavender-ish shadow
    c0=wheel(np.arange(n)/(n-1)); cols=np.concatenate([1-(1-c0)*fade,c0])
    on=ib>=0
    L=np.array([-0.45,-0.55,0.70]); L/=np.linalg.norm(L)
    lam=np.clip(nrm@L,0,1); Hh=L+np.array([0,0,1]); Hh/=np.linalg.norm(Hh)
    spec=np.clip(nrm@Hh,0,1)**40
    base=cols[np.maximum(ib,0)]
    shade=0.55+0.5*lam
    tube=base*shade[...,None]+0.45*spec[...,None]
    # rim darkening at silhouette for separation
    tube*= (0.86+0.14*np.clip(nrm[...,2],0,1)**0.5)[...,None]
    img[on]=tube[on]
    img=np.clip(img,0,1)
    im=Image.fromarray((img*255).astype(np.uint8)).resize((W,H),Image.LANCZOS); im.save(out); return im
if __name__=='__main__':
    t=time.time(); render(n=int(sys.argv[1]),seed=int(sys.argv[2]),out=sys.argv[3]); print(time.time()-t)
