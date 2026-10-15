import numpy as np
R=1500; W=2*R+1
A=np.fromfile('g2_big.bin',dtype=np.int64).reshape(W,W)
fams={'row':lambda k:A[k+R,:],'col':lambda k:A[:,k+R],'diag':lambda k:np.diagonal(A,k),'anti':lambda k:np.diagonal(A[:,::-1],k)}
for name,g in fams.items():
    tot=0; worst=0
    for k in range(-50,51):
        l=g(k); s=set(l.tolist()); m=[v for v in range(-200,201) if v not in s]; tot+=len(m)
        # how far from centre must you go to see all |v|<=100
        c=len(l)//2
        pos={}
        for i,v in enumerate(l.tolist()):
            if abs(v)<=100: pos.setdefault(v,[]).append(abs(i-c))
        if len(pos)==201: worst=max(worst,max(min(p) for p in pos.values()))
        else: worst=None if worst is None else 10**9
    print(name,'missing |v|<=200 over |k|<=50:',tot,' max distance from centre needed to see all |v|<=100:',worst)
