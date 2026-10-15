import numpy as np, sys
R=255; W=2*R+1
F={m:np.fromfile(f'g{m}.bin',dtype=np.int64).reshape(W,W) for m in (0,1,2)}
np.save('f_rc.npy',F[0]); np.save('f_window.npy',F[1]); np.save('f_rcda.npy',F[2])
def at(A,x,y): return A[y+R,x+R]
for m,name in [(0,'rc'),(1,'rcd'),(2,'rcda')]:
    A=F[m]
    print('==',name)
    # injectivity checks
    lines={'row':[A[i,:] for i in range(W)],'col':[A[:,i] for i in range(W)]}
    lines['diag']=[np.diagonal(A,k) for k in range(-W+1,W)]
    lines['anti']=[np.diagonal(A[:,::-1],k) for k in range(-W+1,W)]
    for k,Ls in lines.items():
        bad=sum(len(set(l.tolist()))!=len(l) for l in Ls)
        print(f' {k}: lines with repeats {bad}')
    # coverage: for central lines |k|<=20, which values in [-50,50] missing
    for k in ('row','col','diag','anti'):
        c=W//2 if k in('row','col') else W-1
        miss=[]
        for off in range(-20,21):
            s=set(lines[k][c+off].tolist())
            miss.append(sum(v not in s for v in range(-50,51)))
        print(f' {k} |k|<=20: #values in [-50,50] missing per line: max {max(miss)} total {sum(miss)}')
    print(' centre 9x9 (rows y=4..-4):')
    print(A[R-4:R+5,R-4:R+5][::-1])
