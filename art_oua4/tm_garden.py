import numpy as np, sys, time, pickle

# Garden of small Turing-machine space-times. Run a big population (vectorised, lockstep)
# for a fixed window in a tape wide enough that no head escapes; curate the visually
# RICHEST ones (heads that bounce and build structure) for full space-time rendering.
n   = int(sys.argv[1]) if len(sys.argv)>1 else 5
K   = int(sys.argv[2]) if len(sys.argv)>2 else 1_500_000
T   = int(sys.argv[3]) if len(sys.argv)>3 else 300
seed= int(sys.argv[4]) if len(sys.argv)>4 else 23
W   = 2*T+80                                   # no escape possible within T steps
rng=np.random.default_rng(seed)
ii=np.arange(K)
wr=rng.integers(0,2,size=(K,n,2),dtype=np.int8)
mv=(rng.integers(0,2,size=(K,n,2))*2-1).astype(np.int16)
nx=rng.integers(0,n+1,size=(K,n,2),dtype=np.int16)
tape=np.zeros((K,W),np.int8)
head=np.full(K,W//2,np.int32)
state=np.zeros(K,np.int16)
lo=head.copy(); hi=head.copy()
halted=np.zeros(K,bool); active=np.ones(K,bool)
haltstep=np.full(K,T,np.int32)
prevm=np.zeros(K,np.int16); dirchg=np.zeros(K,np.int32)
t0=time.time()
for t in range(T):
    if not active.any(): break
    sym=tape[ii,head]
    w=wr[ii,state,sym]; m=mv[ii,state,sym]; ns=nx[ii,state,sym]
    upd=active
    tape[ii[upd],head[upd]]=w[upd]
    chg=upd&(prevm!=0)&(m!=prevm)
    dirchg+=chg
    prevm=np.where(upd,m,prevm)
    newhead=head+m
    halt=upd&(ns>=n)
    head=np.where(upd&~halt,newhead,head)
    lo=np.minimum(lo,np.where(upd&~halt,newhead,lo)); hi=np.maximum(hi,np.where(upd&~halt,newhead,hi))
    state=np.where(upd&~halt,ns,state)
    haltstep=np.where(halt&active,t+1,haltstep)
    halted|=halt; active=active&~halted
    if t%100==0: print(f"  t={t} active={int(active.sum())}",flush=True)
width=(hi-lo+1)
print(f"scan {time.time()-t0:.0f}s  halted={int(halted.sum())}  maxwidth={int(width.max())}")

def respin(idx,maxr=T):
    Wr=wr[idx];Mv=mv[idx];Nx=nx[idx]
    tp=np.zeros(W,np.int8); h=W//2; st=0
    steps=min(int(haltstep[idx]),maxr)
    rows=np.zeros((steps+1,W),np.int8); heads=np.zeros(steps+1,np.int32)
    end=steps
    for t in range(steps):
        rows[t]=tp; heads[t]=h
        sy=tp[h]; tp[h]=Wr[st,sy]; nh=h+int(Mv[st,sy]); ns=int(Nx[st,sy]); h=nh
        if ns>=n: rows[t+1]=tp; heads[t+1]=h; end=t+1; break
        st=ns
    else:
        rows[steps]=tp; heads[steps]=h
    rows=rows[:end+1]; heads=heads[:end+1]
    L=int(lo[idx]); R=int(hi[idx])
    return rows[:,L:R+1].copy(), (heads-L)

# curate by COMPLEXITY: gzip-density of the spacetime (Kolmogorov-flavoured). The most
# beautiful machines are MID-complexity: structured (low compressibility => not a trivial
# sweep) but not noise. Filter active+bounded, sample a pool, compute complexity, pick a
# band and spread.
import zlib
cand=np.where((width>=55)&(width<=int(0.75*W)))[0]
rng2=np.random.default_rng(7)
if len(cand)>16000: cand=rng2.choice(cand,16000,replace=False)
print("complexity pool:",len(cand))
rows_cache={}; comp=np.zeros(len(cand)); aspect=np.zeros(len(cand))
tt=time.time()
for k,idx in enumerate(cand):
    ST,HD=respin(idx)
    rows_cache[int(idx)]=(ST,HD)
    R,C=ST.shape
    by=np.packbits(ST.astype(np.uint8)).tobytes()
    comp[k]=len(zlib.compress(by,6))/max(1,(R*C/8))
    aspect[k]=C/max(1,R)
    if k%4000==0: print("  complexity",k,f"{time.time()-tt:.0f}s",flush=True)
# SPAN the full complexity range (drop only near-empty bottom & pure-noise top), so the
# garden runs from the simplest sweeps to the most intricate computations.
good=np.where(aspect>=0.30)[0]
ordr=good[np.argsort(comp[good])]
n0=int(0.05*len(ordr)); n1=int(0.992*len(ordr))
pool=ordr[n0:n1]
# dedup by coarse signature
sig=set(); ded=[]
for k in pool:
    idx=int(cand[k]); ST,_=rows_cache[idx]
    s=(ST.shape[0]//14, ST.shape[1]//7, round(float(comp[k]),2))
    if s in sig: continue
    sig.add(s); ded.append(k)
ded=np.array(ded)
# pick 64 evenly across the (complexity-sorted) deduped pool
NT=64
ix=np.round(np.linspace(0,len(ded)-1,min(NT,len(ded)))).astype(int)
sel=[(int(cand[ded[i]]),float(comp[ded[i]])) for i in ix]
print(f"pool {len(pool)} dedup {len(ded)} -> selected {len(sel)}; "
      f"comp {sel[0][1]:.3f}..{sel[-1][1]:.3f}")
specimens=[]
for idx,c in sel:
    ST,HD=rows_cache[idx]
    specimens.append(dict(st=ST,hd=HD,steps=ST.shape[0]-1,width=int(width[idx]),
                          comp=round(c,3),halted=bool(halted[idx])))
with open(f"/home/user/claude-mythos-self-play/art_oua4/garden_n{n}.pkl","wb") as f:
    pickle.dump(specimens,f)
print("saved",len(specimens),"specimens; complexity range",
      min(s['comp'] for s in specimens),"->",max(s['comp'] for s in specimens))
