import numpy as np
def window(k, x0, x1, y0, y1):
    """membership of Gaussian integers in D_k via the digit shift T; returns (inD, digits[k,H,W] int8)
    rows = y from y1 down to y0 (image orientation), cols = x from x0 to x1"""
    X,Y=np.meshgrid(np.arange(x0,x1+1,dtype=np.int64),np.arange(y1,y0-1,-1,dtype=np.int64))
    x=X.copy(); y=Y.copy(); dig=np.zeros((k,)+x.shape,np.int8)
    for i in range(k):
        odd=((x+y)&1)==1; dig[i]=odd
        ex,ey=(x+y)//2,(y-x)//2
        ox,oy=(1-x-y)//2,(x-y-1)//2
        x=np.where(odd,ox,ex); y=np.where(odd,oy,ey)
    return (x==0)&(y==0), dig
if __name__=='__main__':
    from PIL import Image
    k=27; u=(2**(2*((k-2)//4)+1)+1)//3
    inD,dig=window(k,-u-110,-u+110,-50,170)
    m=10; cls=dig[m]+2*dig[m+1]+4*dig[m+2]
    pal=np.array([[160,200,180],[250,195,140],[140,200,210],[245,225,140],[190,180,220],[240,150,130],[145,175,95],[180,215,225]],np.uint8)
    im=np.where(inD[...,None],pal[cls],np.array([25,45,95],np.uint8))
    H,W=inD.shape
    ys=np.arange(170,-51,-1); xs=np.arange(-u-110,-u+111)
    XX,YY=np.meshgrid(xs,ys); r2=XX.astype(float)**2+YY.astype(float)**2
    im[(r2<u*u)]=(im[(r2<u*u)]*0.5+np.array([250,240,200])*0.5).astype(np.uint8)
    im[(~inD)&(XX==-u)]=[220,50,30]
    Image.fromarray(im).resize((W*4,H*4),Image.NEAREST).save('proto/fjord_a.png')
    print(sorted(YY[(~inD)&(XX==-u)].tolist()))
