import numpy as np
L=np.memmap('math_collatz/basin.u8',dtype=np.uint8,mode='r')
M=len(L)
# local density of each basin in bins of log2(n), 64 bins/octave
B=128
res={}
for k in range(12,32):
    lo=2**k//2; hi=2**(k+1)//2   # odd n in [2^k,2^{k+1})
    seg=np.asarray(L[lo:hi])
    idx=(np.log2(2*np.arange(lo,hi,dtype=np.float64)+1)-k)*B
    idx=np.minimum(idx.astype(int),B-1)
    for c in (1,2,3):
        res.setdefault(c,[]).append(np.bincount(idx,weights=(seg==c),minlength=B)/np.bincount(idx,minlength=B))
for c in (1,2,3):
    d=np.concatenate(res[c]);  # density vs log2 n from 2^12..2^32
    np.save(f'math_collatz/dens{c}.npy',d)
    x=d-d.mean(); F=np.abs(np.fft.rfft(x*np.hanning(len(x))))
    f=np.fft.rfftfreq(len(x),1/B)  # cycles per octave
    top=np.argsort(F)[::-1][:6]
    print(c,'mean',d.mean().round(4),'peaks (cyc/octave, amp):',[(round(f[i],3),round(F[i],1)) for i in top])
    # per-octave amplitude of oscillation
    print('   osc std by octave', [round(np.std(r),4) for r in res[c][::3]])
