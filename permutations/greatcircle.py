import numpy as np
from eg import uniform_syt_staircase, word_from_Q, trajectories

def lift(n, seed=2):
    rng=np.random.default_rng(seed)
    Q=uniform_syt_staircase(n,rng); w=word_from_Q(Q)
    pos=trajectories(w,n); L=pos.shape[1]-1
    th=np.pi*np.arange(L+1)/L                      # time -> [0,pi]
    H=(pos-(n-1)/2)/((n-1)/2)                        # heights -> [-1,1]
    circles=[]; r2s=[]
    for k in range(n):
        h=H[k]; a=h[0]                              # = h0 (start), and h(pi)=-a holds
        # fit h(theta) = a cos th + b sin th  -> solve b by least squares on residual
        resid=h-a*np.cos(th); sden=np.sum(np.sin(th)**2)
        b=np.sum(resid*np.sin(th))/sden
        # R^2 of full model
        model=a*np.cos(th)+b*np.sin(th)
        ss_res=np.sum((h-model)**2); ss_tot=np.sum((h-h.mean())**2)
        r2=1-ss_res/ss_tot if ss_tot>1e-12 else 1.0
        r2s.append(r2)
        # clamp a^2+b^2<=1
        amp2=a*a+b*b
        if amp2>1: f=np.sqrt(0.999/amp2); a*=f; b*=f
        circles.append((a,b,k))
    return circles, np.array(r2s), w

def build_great_circle(a,b,alpha):
    s=np.sqrt(max(0,1-a*a))
    u=np.array([s*np.cos(alpha), s*np.sin(alpha), a])
    w1=np.array([np.cos(alpha),np.sin(alpha)]); w1p=np.array([-np.sin(alpha),np.cos(alpha)])
    P=-a*b/s if s>1e-9 else 0.0
    Q=1-b*b
    perp=np.sqrt(max(0,Q-P*P))
    vxy=P*w1+perp*w1p
    v=np.array([vxy[0],vxy[1],b])
    # verify orthonormal
    return u/np.linalg.norm(u), v/np.linalg.norm(v)

if __name__=="__main__":
    circles,r2s,w=lift(40,seed=2)
    print(f"n=40 sine-fit R^2: mean={r2s.mean():.4f} min={r2s.min():.4f}")
    # verify each lift is a great circle: |C(theta)|==1 and planar (through origin)
    maxoff=0; maxplane=0
    for i,(a,b,k) in enumerate(circles):
        u,v=build_great_circle(a,b, 2*np.pi*i/len(circles))
        th=np.linspace(0,2*np.pi,200)
        C=np.cos(th)[:,None]*u+np.sin(th)[:,None]*v
        maxoff=max(maxoff, abs(np.linalg.norm(C,axis=1)-1).max())   # on unit sphere
        # plane through origin: normal = u x v; C.normal should be ~0
        nrm=np.cross(u,v); nrm/=np.linalg.norm(nrm)
        maxplane=max(maxplane, abs(C@nrm).max())
        # projection onto z = a cos + b sin ?
    print(f"great-circle checks: max||C|-1| = {maxoff:.2e} ; max |C . planenormal| = {maxplane:.2e}")
