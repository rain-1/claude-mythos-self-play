import numpy as np, colorsys
from tiles import tile
WHEEL=np.array([[0.98,0.55,0.62],[1.00,0.72,0.55],[1.00,0.88,0.50],[0.70,0.88,0.52],[0.50,0.86,0.72],[0.52,0.78,0.97],[0.62,0.64,0.97],[0.80,0.60,0.94],[0.97,0.58,0.84]])
CREAM=np.array([0.985,0.965,0.93])
CORAL=np.array([0.98,0.45,0.42])
def design(W=73, bands=7, bh=13, gap=4):
    H=bands*bh+(bands+1)*gap
    C=np.zeros((H,W,3)); C[:]=CREAM
    info=np.zeros((H,W),int)  # 0 bg, 1 tile, 2 centre, 3 peerie
    xs=np.arange(W)-W//2
    y0=gap
    for k in range(bands):
        a,b=(2,3) if k%2==0 else (3,2)
        col=WHEEL[(k*2)%9] if True else None
        col=WHEEL[[0,2,5,1,4,7,3,6,8][k%9]]
        ys=np.arange(bh)-bh//2
        X,Y=np.meshgrid(xs,-ys)
        U,V,K=tile(X,Y,a,b)
        ring=np.array([0,1,1,1,1,2,2,2,2,3,3,3,3])[K]
        light=col*0.3+CREAM*0.7
        on=((U+V)%2==0)
        tip=col*0.7+CREAM*0.3
        c=np.where(on[...,None],np.where((ring==3)[...,None],tip,col),CREAM)
        c=np.where((on&(ring==0))[...,None],CREAM,c)
        c=np.where((~on&(ring==0))[...,None],light*0.4+col*0.6,c)
        # both lattices meet at 13Z^2: coral centres
        both=(X%13==0)&(Y%13==0)
        c=np.where(both[...,None],CORAL,c)
        C[y0:y0+bh]=c; info[y0:y0+bh]=np.where(ring==0,2,1)
        y0+=bh
        # peerie: cream, dotted row in next band colour, cream
        if k<bands-1:
            nc=WHEEL[[0,2,5,1,4,7,3,6,8][(k+1)%9]]
            row=y0+gap//2
            for x in range(W):
                if (x+k)%4==0: C[row,x]=nc*0.8+CREAM*0.2; info[row,x]=3
                if (x+k+2)%4==0 and gap>3: 
                    C[row-1,x]=col*0.6+CREAM*0.4; C[row+1,x]=col*0.6+CREAM*0.4
        y0+=gap
    return C,info
if __name__=='__main__':
    from PIL import Image
    C,_=design()
    Image.fromarray((C*255).astype(np.uint8)).resize((C.shape[1]*7,C.shape[0]*7),Image.NEAREST).save('/tmp/claude-0/design.png')
    print(C.shape)
