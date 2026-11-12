import numpy as np
def dragon(k):
    x=np.zeros(1,np.int32); y=np.zeros(1,np.int32)
    for _ in range(k):
        bx=x-y; by=x+y; x=np.concatenate([bx,1-bx]); y=np.concatenate([by,-by])
    return x,y
def closed(k):
    if k<2: return 1
    j=(k-2)//4; r=(k-2)%4; u=(2**(2*j+1)+1)//3
    return [(u*u+1)//2,u*u,2*u*u,4*u*u][r]
def label_grid(k, bits=9):
    x,y=dragon(k); x0,x1,y0,y1=x.min(),x.max(),y.min(),y.max()
    G=np.full((y1-y0+1,x1-x0+1),-1,np.int16)
    G[y-y0,x-x0]=(np.arange(len(x))>>(k-bits)).astype(np.int16)
    return G,(-x0,-y0)
if __name__=='__main__':
    from PIL import Image
    for k in (15,16,17,18):
        G,(ox,oy)=label_grid(k,3); print(k,G.shape,'origin',ox,oy,'r',closed(k)**.5,(G>=0).sum()==2**k)
        pal=np.array([[20,30,60],[160,200,180],[140,200,210],[110,140,165],[145,175,95],[240,150,130],[250,195,140],[230,190,110],[120,80,115]],np.uint8)
        im=pal[G+1]; yy,xx=np.mgrid[0:G.shape[0],0:G.shape[1]]
        r=np.hypot(xx-ox,yy-oy); im[np.abs(r-closed(k)**.5)<1.2]=255
        Image.fromarray(im[::-1]).resize((G.shape[1]*700//max(G.shape),G.shape[0]*700//max(G.shape))).save(f'proto/dr{k}.png')
