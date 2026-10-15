import numpy as np
R=1500;W=2*R+1
A=np.fromfile('g0_big.bin',dtype=np.int64).reshape(W,W)
def unsig(s): return (s+1)//2 if s%2 else -(s//2)
def F(x,y):
    X,Y=x-1,y-1; k=X^Y
    if k==0: return 0
    j=k.bit_length()-1
    up = (X>Y) if X>=0 else (X<Y)   # quadrant x,y<=0: roles swapped
    s = (1<<(j+1))+k if up else (1<<(j+2))-1-k
    return unsig(s)
bad=0;tot=0
for x in range(-R,R+1):
    for y in range(-R,R+1):
        if (x>=1)==(y>=1):
            tot+=1
            if F(x,y)!=A[y+R,x+R]: bad+=1
print('same-sign-quadrant cells',tot,'mismatches',bad)
