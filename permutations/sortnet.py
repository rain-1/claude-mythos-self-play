import numpy as np

def w0_word(n):
    """canonical reduced word for the longest element w0 of S_n (staircase): letters s_i, i in 1..n-1."""
    w=[]
    for k in range(1,n):       # build reversal
        for i in range(k,0,-1):
            w.append(i)
    return w   # length n(n-1)/2

def apply_word(word,n):
    p=list(range(n))           # p[slot]=wire-label start identity
    for i in word:             # s_i swaps slots i-1,i (1-indexed letter)
        p[i-1],p[i]=p[i],p[i-1]
    return p

def is_reduced_reversal(word,n):
    p=apply_word(word,n)
    return p==list(range(n-1,-1,-1)) and len(word)==n*(n-1)//2

def mcmc(word,n,steps,seed=0):
    """random walk on reduced words via commutation + braid (Yang-Baxter) moves."""
    rng=np.random.default_rng(seed)
    w=word[:]; L=len(w)
    for _ in range(steps):
        j=rng.integers(0,L)
        # try braid at j (needs w[j],w[j+1],w[j+2] = a,a+1,a or a,a-1,a)
        if j+2<L:
            a,b,c=w[j],w[j+1],w[j+2]
            if a==c and abs(a-b)==1:
                w[j],w[j+1],w[j+2]=b,a,b
                continue
        # try commutation at j (|w[j]-w[j+1]|>=2)
        if j+1<L and abs(w[j]-w[j+1])>=2:
            w[j],w[j+1]=w[j+1],w[j]
    return w

def trajectories(word,n):
    """return array T[n, L+1] = slot of each wire over time."""
    L=len(word)
    slot=list(range(n))            # slot[wire]=current slot
    pos=np.zeros((n,L+1))
    pos[:,0]=slot
    for t,i in enumerate(word):
        # wires currently at slots i-1, i
        wa=slot.index(i-1); wb=slot.index(i)
        slot[wa],slot[wb]=i,i-1
        pos[:,t+1]=slot
    return pos

if __name__=="__main__":
    n=6
    w=w0_word(n)
    print("canonical reduced word len",len(w),"= n(n-1)/2 =",n*(n-1)//2)
    print("is reduced reversal:",is_reduced_reversal(w,n))
    w2=mcmc(w,n,20000,seed=1)
    print("after MCMC still reduced reversal:",is_reduced_reversal(w2,n))
    print("word changed:",w!=w2)
