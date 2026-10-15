import numpy as np,sys
for fn,R in [('g0_big.bin',1500),('g1_big.bin',1500),('g2_big.bin',1500)]:
    W=2*R+1; A=np.fromfile(fn,dtype=np.int64).reshape(W,W)
    ys,xs=np.nonzero(A==0); xs=xs-R; ys=ys-R
    print(fn,'zeros:',len(xs),'on x+y=0:',np.sum(xs+ys==0),'on x=y:',np.sum(xs==ys))
