"""Vectorized-ish domino-shuffling sampler for a uniform random tiling of the
Aztec diamond (Elkies-Kuperberg-Larsen-Propp).  Faithful to pywonderland:
  codes 1=n,2=s (HORIZONTAL dominoes sliding up/down),
        3=e,4=w (VERTICAL dominoes sliding right/left).
  array[row=y+off, col=x+off]; block BL=(r,c) -> cells [BL,BR,TL,TR]=
     [(r,c),(r,c+1),(r+1,c),(r+1,c+1)].
delete bad blocks (n,n,s,s)/(e,w,e,w); slide; create: fill empty 2x2 blocks
with a fair coin -> (s,s,n,n) horizontal or (w,e,w,e) vertical.

Both delete and create are done GREEDILY in boundary-first (row,col) scan order
with an O(1) recheck, which uniquely resolves the 2x2 partition of the empty /
bad regions (exactly as the reference's ordered scan does).  Candidate blocks
are found vectorized; only the handful of candidates are looped in python.
A full perfect-tiling assertion runs at every order.
"""
import numpy as np

def shuffle(N, seed=0, verify=False):
    rng = np.random.default_rng(seed)
    M = 2*N + 4
    off = N + 2
    T = np.zeros((M, M), dtype=np.int8)
    XX = (np.arange(M) - off)[None, :]
    YY = (np.arange(M) - off)[:, None]
    def din(order):
        return (np.abs(2*XX+1) + np.abs(2*YY+1)) <= 2*order

    for order in range(1, N+1):
        # --- delete bad blocks (greedy, scan order) ---
        if order >= 2:
            bl = T[:-1,:-1]; br = T[:-1,1:]; tl = T[1:,:-1]; tr = T[1:,1:]
            hbad = (bl==1)&(br==1)&(tl==2)&(tr==2)
            vbad = (bl==3)&(br==4)&(tl==3)&(tr==4)
            rr, cc = np.where(hbad | vbad)
            for r, c in zip(rr.tolist(), cc.tolist()):
                a,b,d2,e2 = T[r,c],T[r,c+1],T[r+1,c],T[r+1,c+1]
                if (a==1 and b==1 and d2==2 and e2==2) or (a==3 and b==4 and d2==3 and e2==4):
                    T[r,c]=0; T[r,c+1]=0; T[r+1,c]=0; T[r+1,c+1]=0
        # --- slide (order-1 -> order) ---
        T2 = np.zeros_like(T)
        T2[1:, :]  = np.where(T[:-1, :] == 1, 1, T2[1:, :])    # n up
        T2[:-1, :] = np.where(T[1:, :]  == 2, 2, T2[:-1, :])   # s down
        T2[:, 1:]  = np.where(T[:, :-1] == 3, 3, T2[:, 1:])    # e right
        T2[:, :-1] = np.where(T[:, 1:]  == 4, 4, T2[:, :-1])   # w left
        T = T2
        # --- create: fill empty 2x2 blocks (greedy, scan order, recheck) ---
        d = din(order)
        bl = T[:-1,:-1]; br = T[:-1,1:]; tl = T[1:,:-1]; tr = T[1:,1:]
        empty = (bl==0)&(br==0)&(tl==0)&(tr==0)
        ind = d[:-1,:-1]&d[:-1,1:]&d[1:,:-1]&d[1:,1:]
        rr, cc = np.where(empty & ind)
        coins = rng.random(rr.size) > 0.5
        for r, c, hor in zip(rr.tolist(), cc.tolist(), coins.tolist()):
            if T[r,c]==0 and T[r,c+1]==0 and T[r+1,c]==0 and T[r+1,c+1]==0:
                if hor:
                    T[r,c]=2; T[r,c+1]=2; T[r+1,c]=1; T[r+1,c+1]=1
                else:
                    T[r,c]=4; T[r,c+1]=3; T[r+1,c]=4; T[r+1,c+1]=3
        if verify:
            d = din(order)
            assert ((T==0)&d).sum()==0, f"order {order}: empty in diamond"
            assert ((T!=0)&~d).sum()==0, f"order {order}: domino outside"
    return T, off


def validate_full(T, off, order):
    M = T.shape[0]
    XX=(np.arange(M)-off)[None,:]; YY=(np.arange(M)-off)[:,None]
    d=(np.abs(2*XX+1)+np.abs(2*YY+1))<=2*order
    used=np.zeros((M,M),bool); cov=np.zeros((M,M),int)
    for r in range(M):
        for c in range(M-1):
            if not used[r,c] and T[r,c] in (1,2) and T[r,c+1]==T[r,c] and not used[r,c+1]:
                used[r,c]=used[r,c+1]=True; cov[r,c]+=1; cov[r,c+1]+=1
    for c in range(M):
        for r in range(M-1):
            if not used[r,c] and T[r,c] in (3,4) and T[r+1,c]==T[r,c] and not used[r+1,c]:
                used[r,c]=used[r+1,c]=True; cov[r,c]+=1; cov[r+1,c]+=1
    return int(((cov!=1)&d).sum()), int(((cov!=0)&~d).sum()), int(((T!=0)&~used).sum())


if __name__ == "__main__":
    import time
    for N in [1,2,3,4,5,6,8,12,20,40,80]:
        for s in range(6):
            T, off = shuffle(N, seed=s, verify=True)
            bi,bo,lo = validate_full(T, off, N)
            assert bi==bo==lo==0, f"N={N} s={s}: invalid {bi},{bo},{lo}"
        print(f"N={N} VALID (6 seeds)  filled={int((T!=0).sum())} expected={2*N*(N+1)}")
    t0=time.time(); T,off=shuffle(256, seed=1); print(f"N=256 time={time.time()-t0:.1f}s")
