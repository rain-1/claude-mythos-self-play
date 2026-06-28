import numpy as np, sys, time, pickle

# Coding Theorem Method: approximate the universal distribution m(x) by sampling many
# small (n-state, 2-symbol) Turing machines, running each on a blank tape with a step
# bound, and tallying the output strings of those that HALT.  Output frequency D(x)
# approximates m(x); algorithmic complexity K(x) ~ -log2(D(x)/N).   (Vectorised across
# all machines in a batch -> millions of TMs in seconds.)
# Output convention: the tape content over the range of cells the head VISITED (so
# internal/edge zeros are faithfully kept), trimmed to length<=Lmax.

n     = int(sys.argv[1]) if len(sys.argv)>1 else 5      # states
K     = int(sys.argv[2]) if len(sys.argv)>2 else 2_000_000
B     = int(sys.argv[3]) if len(sys.argv)>3 else 4      # batches
T     = int(sys.argv[4]) if len(sys.argv)>4 else 600    # step cap
seed  = int(sys.argv[5]) if len(sys.argv)>5 else 1
W     = 384
Lmax  = 24
out   = sys.argv[6] if len(sys.argv)>6 else f"tally_n{n}.pkl"
rng=np.random.default_rng(seed)

from collections import Counter
tally=Counter()
N_sampled=0; N_halt=0; N_escape=0; N_loop=0; N_empty=0; N_toolong=0
t0=time.time()
for b in range(B):
    ii=np.arange(K)
    # transition tables: index [K, state, sym] -> write, move(+/-1), next(0..n ; n=HALT)
    wr=rng.integers(0,2,size=(K,n,2),dtype=np.int8)
    mv=(rng.integers(0,2,size=(K,n,2))*2-1).astype(np.int16)
    nx=rng.integers(0,n+1,size=(K,n,2),dtype=np.int16)   # n == HALT
    tape=np.zeros((K,W),np.int8)
    head=np.full(K,W//2,np.int32)
    state=np.zeros(K,np.int16)
    lo=head.copy(); hi=head.copy()
    halted=np.zeros(K,bool); escaped=np.zeros(K,bool)
    active=np.ones(K,bool)
    for t in range(T):
        if not active.any(): break
        sym=tape[ii,head]
        w =wr[ii,state,sym]
        m =mv[ii,state,sym]
        ns=nx[ii,state,sym]
        upd=active
        # write
        tape[ii[upd],head[upd]]=w[upd]
        newhead=head+m
        esc=upd&((newhead<0)|(newhead>=W))
        halt=upd&(ns>=n)
        mvok=upd&~esc
        head=np.where(mvok,newhead,head)
        lo=np.minimum(lo,np.where(mvok,newhead,lo))
        hi=np.maximum(hi,np.where(mvok,newhead,hi))
        state=np.where(mvok&~halt,ns,state)
        halted|=halt; escaped|=esc
        active=active&~halted&~escaped
    didhalt=halted&~escaped
    N_sampled+=K; N_escape+=int(escaped.sum()); N_loop+=int((active).sum())
    H=tape[didhalt]; L0=lo[didhalt]; H1=hi[didhalt]
    M=H.shape[0]; N_halt+=M
    if M:
        length=(H1-L0+1)
        # gather aligned [M,Lmax] starting at lo
        idx=L0[:,None]+np.arange(Lmax)[None,:]
        idx=np.clip(idx,0,W-1)
        aligned=H[np.arange(M)[:,None],idx]            # [M,Lmax]
        validpos=np.arange(Lmax)[None,:]<length[:,None]
        aligned=aligned*validpos
        # key per row
        pw=(1<<np.arange(Lmax)).astype(np.int64)
        val=(aligned.astype(np.int64)*pw).sum(1)
        toolong=length>Lmax
        empty=(aligned.sum(1)==0)&~toolong
        N_toolong+=int(toolong.sum()); N_empty+=int(empty.sum())
        good=~toolong&~empty
        key=(length.astype(np.int64)<<32)|val
        ks,cs=np.unique(key[good],return_counts=True)
        for k,c in zip(ks.tolist(),cs.tolist()):
            tally[k]+=int(c)
    print(f"batch {b+1}/{B}: halt={M} ({100*M/K:.1f}%) escape={int(escaped.sum())} loop={int(active.sum())} distinct={len(tally)} t={time.time()-t0:.1f}s")

# decode keys -> bitstrings
def decode(k):
    length=k>>32; val=k&0xffffffff
    return ''.join(str((val>>j)&1) for j in range(length))
dist={decode(k):c for k,c in tally.items()}
meta=dict(n=n,K=K,B=B,T=T,seed=seed,N_sampled=N_sampled,N_halt=N_halt,
          N_escape=N_escape,N_loop=N_loop,N_empty=N_empty,N_toolong=N_toolong)
with open(f"/home/user/claude-mythos-self-play/art_oua4/{out}","wb") as f:
    pickle.dump((dist,meta),f)
print("meta:",meta)
print("distinct nonempty outputs:",len(dist))
top=sorted(dist.items(),key=lambda x:-x[1])[:25]
print("TOP outputs (string : count):")
for s,c in top: print(f"  {repr(s):>16}  {c:>9}  len={len(s)}")
