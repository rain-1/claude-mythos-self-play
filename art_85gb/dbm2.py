import numpy as np, time

def dbm(N, steps, eta=1.5, Rout_frac=0.99, kill_frac=0.80, seed=0,
        warm_sweeps=4, full_every=80, omega=1.9, rng=None):
    """Radial DBM. Records parent index per cell -> tree. Stops a branch's
    dominance by a 'kill radius': candidates beyond kill_frac*Rout are barred
    until cluster mean radius approaches it (keeps envelope ~circular)."""
    if rng is None: rng=np.random.default_rng(seed)
    phi=np.zeros((N,N)); yy,xx=np.mgrid[0:N,0:N]; c=(N-1)/2
    r=np.sqrt((xx-c)**2+(yy-c)**2); Rout=Rout_frac*(N/2)
    outer=r>=Rout; phi[outer]=1.0
    cluster=np.zeros((N,N),bool); ci=N//2
    cluster[ci,ci]=True
    age=np.full((N,N),-1,np.int32); age[ci,ci]=0
    parent=np.full((N,N),-1,np.int64)
    rb=(xx+yy)%2; red=(rb==0)&~outer; black=(rb==1)&~outer
    def sweep(nsw):
        for _ in range(nsw):
            for mask in (red,black):
                nb=np.zeros_like(phi)
                nb[1:-1,1:-1]=phi[:-2,1:-1]+phi[2:,1:-1]+phi[1:-1,:-2]+phi[1:-1,2:]
                m=mask&~cluster
                phi[m]=(1-omega)*phi[m]+omega*0.25*nb[m]
            phi[cluster]=0.0; phi[outer]=1.0
    sweep(500)
    rmax=0.0
    for s in range(1,steps+1):
        peri=np.zeros((N,N),bool)
        peri[1:-1,1:-1]=(cluster[:-2,1:-1]|cluster[2:,1:-1]|cluster[1:-1,:-2]|cluster[1:-1,2:])
        peri&=~cluster&~outer
        # keep envelope circular: bar candidates far beyond current cluster radius
        rlim=min(0.80*Rout, max(rmax+0.045*Rout, 0.05*Rout))
        peri&=(r<=rlim)
        idx=np.flatnonzero(peri.ravel())
        if len(idx)==0: 
            rmax=min(rmax+2, Rout); continue
        w=np.clip(phi.ravel()[idx],0,None)**eta
        tot=w.sum()
        if tot<=0: break
        pick=idx[rng.choice(len(idx),p=w/tot)]
        yi,xi=divmod(pick,N)
        # parent = adjacent cluster cell with smallest age (oldest)
        best=-1;bo=1<<30
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            ny,nx=yi+dy,xi+dx
            if 0<=ny<N and 0<=nx<N and cluster[ny,nx] and age[ny,nx]<bo:
                bo=age[ny,nx]; best=ny*N+nx
        cluster[yi,xi]=True; phi[yi,xi]=0.0; age[yi,xi]=s; parent[yi,xi]=best
        rmax=max(rmax, r[yi,xi])
        sweep(warm_sweeps)
        if s%full_every==0: sweep(25)
    return age, parent, phi, cluster

if __name__=="__main__":
    from PIL import Image
    for eta in (1.0,1.5,2.5):
        t0=time.time()
        age,parent,phi,cl=dbm(300, 3500, eta=eta, seed=7, warm_sweeps=3)
        print(f"eta={eta} time {time.time()-t0:.1f}s size {cl.sum()}")
        a=age.astype(float); v=np.where(age>=0, a/max(1,age.max()), 0)
        img=np.zeros((300,300,3))
        ramp=np.array([(0.15,0.25,0.95),(0.3,0.85,1.0),(0.95,0.97,0.75),(1.0,0.55,0.18),(1,0.25,0.35)])
        xr=np.linspace(0,1,len(ramp))
        for cc in range(3): img[...,cc]=np.interp(v,xr,ramp[:,cc])
        img[age<0]=0
        Image.fromarray((img*255).astype(np.uint8)).save(f'dbm_eta{eta}.png')
