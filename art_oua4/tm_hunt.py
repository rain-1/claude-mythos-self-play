import numpy as np, sys, time, pickle, zlib

# Hunt for NON-triangular small-TM space-times. A triangle is a single-pass drift cone:
# width ~ steps. We instead want CONFINED machines whose head revisits each column many
# times (steps >> width) AND whose space-time is incompressible (real structure, not a
# period-2 twitch). Wide tape so nothing escapes; score = confinement gate + gzip complexity.
n   = int(sys.argv[1]) if len(sys.argv)>1 else 5
K   = int(sys.argv[2]) if len(sys.argv)>2 else 1_200_000
T   = int(sys.argv[3]) if len(sys.argv)>3 else 700
seed= int(sys.argv[4]) if len(sys.argv)>4 else 31
W   = 2*T+80
rng=np.random.default_rng(seed)
ii=np.arange(K)
wr=rng.integers(0,2,size=(K,n,2),dtype=np.int8)
mv=(rng.integers(0,2,size=(K,n,2))*2-1).astype(np.int16)
nx=rng.integers(0,n+1,size=(K,n,2),dtype=np.int16)
tape=np.zeros((K,W),np.int8); head=np.full(K,W//2,np.int32); state=np.zeros(K,np.int16)
lo=head.copy(); hi=head.copy(); halted=np.zeros(K,bool); active=np.ones(K,bool)
haltstep=np.full(K,T,np.int32); prevm=np.zeros(K,np.int16); dirchg=np.zeros(K,np.int32)
t0=time.time()
for t in range(T):
    if not active.any(): break
    sym=tape[ii,head]; w=wr[ii,state,sym]; m=mv[ii,state,sym]; ns=nx[ii,state,sym]
    upd=active
    tape[ii[upd],head[upd]]=w[upd]
    dirchg+=upd&(prevm!=0)&(m!=prevm); prevm=np.where(upd,m,prevm)
    newhead=head+m; halt=upd&(ns>=n)
    head=np.where(upd&~halt,newhead,head)
    lo=np.minimum(lo,np.where(upd&~halt,newhead,lo)); hi=np.maximum(hi,np.where(upd&~halt,newhead,hi))
    state=np.where(upd&~halt,ns,state)
    haltstep=np.where(halt&active,t+1,haltstep); halted|=halt; active=active&~halted
    if t%100==0: print(f"  t={t} active={int(active.sum())}",flush=True)
width=(hi-lo+1); steps=haltstep
confine=steps/np.maximum(1,width)
print(f"scan {time.time()-t0:.0f}s  maxwidth={int(width.max())} maxdirchg={int(dirchg.max())} maxconfine={confine.max():.1f}")

# CONFINEMENT gate: each column revisited >=3x on average (kills triangles), bounded but
# not a tiny twitch, ran a good while.
cand=np.where((confine>=3.0)&(width>=22)&(width<=800)&(steps>=250)&(dirchg>=60))[0]
print("confined candidate pool:",len(cand))
rng2=np.random.default_rng(3)
if len(cand)>30000: cand=rng2.choice(cand,30000,replace=False)

def respin(idx):
    Wr=wr[idx];Mv=mv[idx];Nx=nx[idx]
    tp=np.zeros(W,np.int8); h=W//2; st=0; steps_=int(haltstep[idx])
    rows=np.zeros((steps_+1,W),np.int8); heads=np.zeros(steps_+1,np.int32); end=steps_
    for t in range(steps_):
        rows[t]=tp; heads[t]=h
        sy=tp[h]; tp[h]=Wr[st,sy]; nh=h+int(Mv[st,sy]); ns=int(Nx[st,sy]); h=nh
        if ns>=n: rows[t+1]=tp; heads[t+1]=h; end=t+1; break
        st=ns
    else: rows[steps_]=tp; heads[steps_]=h
    rows=rows[:end+1]; heads=heads[:end+1]; L=int(lo[idx]); R=int(hi[idx])
    return rows[:,L:R+1].copy(), (heads-L)

comp=np.zeros(len(cand)); cache={}
tt=time.time()
for k,idx in enumerate(cand):
    ST,HD=respin(idx); cache[int(idx)]=(ST,HD)
    R,C=ST.shape; by=np.packbits(ST.astype(np.uint8)).tobytes()
    comp[k]=len(zlib.compress(by,6))/max(1,(R*C/8))
    if k%5000==0: print("  comp",k,f"{time.time()-tt:.0f}s",flush=True)
# keep mid-high complexity (structured, not noise-fill, not period-2), spread, dedup
loB,hiB=np.percentile(comp,[55,99.5])
keep=np.where((comp>=loB)&(comp<=hiB))[0]
ordr=keep[np.argsort(-comp[keep])]
sig=set(); sel=[]
for k in ordr:
    idx=int(cand[k]); ST,_=cache[idx]
    s=(ST.shape[0]//20, ST.shape[1]//6, int(dirchg[idx])//8, round(float(comp[k]),2))
    if s in sig: continue
    sig.add(s); sel.append((idx,float(comp[k]),int(dirchg[idx]),int(width[idx]),int(steps[idx])))
    if len(sel)>=140: break
print(f"band[{loB:.3f},{hiB:.3f}] kept {len(keep)} -> shortlist {len(sel)}")
specimens=[]
for idx,c,dc,wd,stp in sel:
    ST,HD=cache[idx]
    specimens.append(dict(st=ST,hd=HD,steps=ST.shape[0]-1,width=wd,comp=round(c,3),
                          dirchg=dc,confine=round(stp/max(1,wd),2),halted=bool(halted[idx])))
with open(f"/home/user/claude-mythos-self-play/art_oua4/hunt_n{n}.pkl","wb") as f:
    pickle.dump(specimens,f)
print("saved",len(specimens),"specimens; comp",min(s['comp'] for s in specimens),"->",
      max(s['comp'] for s in specimens),"; confine up to",max(s['confine'] for s in specimens))
