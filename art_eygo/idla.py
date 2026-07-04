"""Internal DLA via vectorized lockstep walkers (abelian property).
N particles from the origin; each SRWs until it steps onto an empty site, then
occupies it. Final set -> near-perfect disk radius sqrt(N/pi); boundary is
log-correlated (the 'free' trembling edge). visit[] = occupation measure (local time).
"""
import numpy as np, sys, time

def idla(N, R, B=2048, seed=1):
    M=int(2.7*R)+40; c=M//2      # generous void so the edge is never wall-clipped
    occ=np.zeros((M,M), bool); occ[c,c]=True
    visit=np.zeros((M,M), np.int32)
    rng=np.random.default_rng(seed)
    px=np.full(B, c, np.int32); py=np.full(B, c, np.int32)
    active=np.ones(B, bool)                       # all start active at center
    deposited=0; order=np.zeros((M,M), np.int32)   # settle order (arrival time)
    DX=np.array([1,-1,0,0],np.int32); DY=np.array([0,0,1,-1],np.int32)
    t0=time.time(); step=0
    while deposited<N:
        step+=1
        idx=np.where(active)[0]
        if idx.size==0: break
        d=rng.integers(0,4,size=idx.size)
        nx=px[idx]+DX[d]; ny=py[idx]+DY[d]
        np.clip(nx,0,M-1,out=nx); np.clip(ny,0,M-1,out=ny)
        px[idx]=nx; py[idx]=ny
        visit[nx,ny]+=1
        empty = ~occ[nx,ny]                        # stepped onto empty -> wants to settle
        if empty.any():
            si=idx[empty]; ex=nx[empty]; ey=ny[empty]
            flat=ex.astype(np.int64)*M+ey
            uniq,first=np.unique(flat,return_index=True)
            # occupy each unique target once (only if still empty & budget remains)
            take=first[:max(0,N-deposited)]
            tx=ex[take]; ty=ey[take]
            newly = ~occ[tx,ty]
            tx=tx[newly]; ty=ty[newly]
            occ[tx,ty]=True
            order[tx,ty]=deposited+1+np.arange(tx.size)
            deposited+=tx.size
            # retire walkers that settled on a site that is now occupied by THEM;
            # simplest correct rule: any settler whose target is now occupied retires.
            settled = occ[ex,ey]
            ret=si[settled]
            active[ret]=False
        # refill retired walkers with new center particles (keep batch full) while budget remains
        nact=active.sum()
        need=B-nact
        if need>0 and deposited<N:
            free=np.where(~active)[0][:need]
            px[free]=c; py[free]=c; active[free]=True
        if step%20000==0:
            r_est=np.sqrt(deposited/np.pi)
            print(f"  step {step} dep {deposited}/{N} r~{r_est:.1f} t={time.time()-t0:.1f}s",flush=True)
    print(f"IDLA done: dep={deposited} steps={step} t={time.time()-t0:.1f}s",flush=True)
    return occ, visit, order, c

if __name__=="__main__":
    R=int(sys.argv[1]) if len(sys.argv)>1 else 180
    B=int(sys.argv[2]) if len(sys.argv)>2 else 2048
    N=int(np.pi*R*R)
    occ,visit,order,c=idla(N,R,B)
    r=np.sqrt(occ.sum()/np.pi)
    print(f"R_target={R} R_measured={r:.2f} area={occ.sum()} N={N}")
    np.save("art_eygo/idla_occ.npy",occ); np.save("art_eygo/idla_visit.npy",visit)
    np.save("art_eygo/idla_order.npy",order)
    # quick look
    from PIL import Image
    v=np.log1p(visit).astype(float); v/=v.max()
    Image.fromarray((255*v**0.6).astype(np.uint8)).save("art_eygo/idla_proto.png")
    print("saved idla_proto.png")
